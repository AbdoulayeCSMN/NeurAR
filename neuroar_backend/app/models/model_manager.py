"""
Gestionnaire du modèle PyTorch (singleton).
Charge le réseau NeuroARNet, le dataset MNIST, et expose des méthodes
pour récupérer l'état du réseau sous forme de NetworkData (compatible Unity).
"""
import logging
import random
from typing import List, Optional

import torch
import torch.nn.functional as F
from torchvision import datasets, transforms

from neuroar_backend.app.config import MODEL_ARCHITECTURE, LOG_PREFIX
from neuroar_backend.app.core.neural_network import NeuroARNet
from neuroar_backend.app.core.activation_functions import (
    activation_name_for_layer,
    normalize_to_unit_range,
)
from neuroar_backend.app.models.network_data import NetworkData, LayerData, NeuronData

logger = logging.getLogger("neuroar")


class ModelManager:
    """
    Gestionnaire central du modèle de réseau de neurones.
    Implémenté en singleton pour garantir une instance unique partagée
    entre les routes REST et les WebSockets.
    """

    _instance: Optional["ModelManager"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, architecture: Optional[List[int]] = None):
        # Empêche la ré-initialisation lors d'appels répétés au singleton
        if self._initialized:
            return

        self.architecture = architecture or MODEL_ARCHITECTURE
        self.model_name = "NeuroARNet"

        logger.info(f"{LOG_PREFIX} Initialisation du modèle avec architecture {self.architecture}")
        self.network = NeuroARNet(self.architecture)
        self.network.eval()

        # État courant : dernière entrée utilisée, dernière sortie, métriques
        self.last_input: Optional[torch.Tensor] = None
        self.last_output: Optional[torch.Tensor] = None
        self.last_target: Optional[int] = None
        self.current_phase = "init"
        self.current_loss = 0.0
        self.current_accuracy = 0.0

        self.mnist_dataset = None
        self._load_mnist_dataset()

        # Effectue un premier forward pass à vide pour peupler les activations
        self._run_initial_forward()

        self._initialized = True

    @classmethod
    def get_instance(cls) -> "ModelManager":
        """Retourne l'instance unique du ModelManager (créée si nécessaire)."""
        if cls._instance is None:
            cls._instance = ModelManager()
        return cls._instance

    # ------------------------------------------------------------------
    # Chargement des données
    # ------------------------------------------------------------------
    def _load_mnist_dataset(self):
        """
        Charge le dataset MNIST via torchvision pour servir d'exemples
        d'entrées au réseau (téléchargé dans ./data si nécessaire).
        """
        try:
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,)),
            ])
            self.mnist_dataset = datasets.MNIST(
                root="./data", train=True, download=True, transform=transform
            )
            logger.info(f"{LOG_PREFIX} Dataset MNIST chargé ({len(self.mnist_dataset)} échantillons)")
        except Exception as exc:
            logger.warning(f"{LOG_PREFIX} Impossible de charger MNIST ({exc}), utilisation de données aléatoires")
            self.mnist_dataset = None

    def _get_random_sample(self):
        """
        Retourne un échantillon (input_tensor, label) aléatoire.
        Si MNIST n'est pas disponible, génère un vecteur aléatoire.
        """
        input_size = self.architecture[0]
        if self.mnist_dataset is not None:
            index = random.randrange(len(self.mnist_dataset))
            image, label = self.mnist_dataset[index]
            return image.view(-1)[:input_size].clone(), label
        return torch.rand(input_size), random.randrange(self.architecture[-1])

    def _run_initial_forward(self):
        """Exécute un premier forward pass pour initialiser les activations."""
        sample_input, label = self._get_random_sample()
        self._forward(sample_input, label)
        self.current_phase = "init"

    # ------------------------------------------------------------------
    # Forward / Backward
    # ------------------------------------------------------------------
    def _forward(self, input_tensor: torch.Tensor, target_label: Optional[int] = None):
        """
        Exécute un forward pass interne et met à jour l'état du modèle
        (dernière entrée, dernière sortie, perte, précision).
        """
        with torch.no_grad():
            batched_input = input_tensor.unsqueeze(0)
            output = self.network(batched_input)

        self.last_input = input_tensor.detach()
        self.last_output = output.squeeze(0).detach()
        self.last_target = target_label

        if target_label is not None:
            target_tensor = torch.tensor([target_label])
            self.current_loss = float(F.nll_loss(torch.log(self.last_output.unsqueeze(0) + 1e-9), target_tensor))
            predicted = int(torch.argmax(self.last_output))
            self.current_accuracy = 1.0 if predicted == target_label else 0.0

        return output

    def forward_pass(self, input_data: Optional[List[float]] = None) -> NetworkData:
        """
        Lance un forward pass complet sur les données fournies (ou un
        échantillon MNIST aléatoire si aucune donnée n'est fournie),
        puis retourne le NetworkData correspondant avec phase="forward".
        """
        logger.info(f"{LOG_PREFIX} Lancement d'un forward pass")

        if input_data is not None:
            input_size = self.architecture[0]
            input_tensor = torch.tensor(input_data, dtype=torch.float32)[:input_size]
            target_label = None
        else:
            input_tensor, target_label = self._get_random_sample()

        self._forward(input_tensor, target_label)
        self.current_phase = "forward"
        return self.get_network_data(phase="forward")

    def backward_pass(self) -> NetworkData:
        """
        Lance un backward pass (calcul du gradient et mise à jour des poids
        via un optimiseur SGD simple) sur la dernière entrée utilisée,
        puis retourne le NetworkData correspondant avec phase="backward".
        """
        logger.info(f"{LOG_PREFIX} Lancement d'un backward pass")

        if self.last_input is None or self.last_target is None:
            self.last_input, self.last_target = self._get_random_sample()

        # Le réseau reste en mode eval : BatchNorm utilise alors ses statistiques
        # courantes (running stats), ce qui fonctionne avec un batch de taille 1
        # tout en laissant les gradients se propager normalement.
        optimizer = torch.optim.SGD(self.network.parameters(), lr=0.01)
        optimizer.zero_grad()

        batched_input = self.last_input.unsqueeze(0)
        target_tensor = torch.tensor([self.last_target])

        output = self.network(batched_input)
        loss = F.nll_loss(torch.log(output + 1e-9), target_tensor)
        loss.backward()
        optimizer.step()

        self.current_loss = float(loss.detach())
        predicted = int(torch.argmax(output.detach()))
        self.current_accuracy = 1.0 if predicted == self.last_target else 0.0

        # Recalcule les activations propres après la mise à jour des poids
        self._forward(self.last_input, self.last_target)
        self.current_phase = "backward"
        return self.get_network_data(phase="backward")

    def reset(self) -> NetworkData:
        """
        Réinitialise le modèle : recrée un réseau avec des poids neufs
        et relance un forward pass initial.
        """
        logger.info(f"{LOG_PREFIX} Réinitialisation du modèle")
        self.network = NeuroARNet(self.architecture)
        self.network.eval()
        self.current_loss = 0.0
        self.current_accuracy = 0.0
        self._run_initial_forward()
        self.current_phase = "idle"
        return self.get_network_data(phase="idle")

    # ------------------------------------------------------------------
    # Construction du NetworkData
    # ------------------------------------------------------------------
    def get_weights_as_list(self, layer: int) -> List[float]:
        """
        Retourne la liste des poids (aplatis) de la couche `layer`,
        normalisés entre -1 et 1 (via tanh, voir NeuroARNet.get_all_weights).
        `layer` correspond à l'index de la couche de DESTINATION
        (1 = première couche cachée, etc.). La couche d'entrée (0) n'a pas
        de poids entrants et retourne donc une liste vide.
        """
        if layer == 0:
            return []
        all_weights = self.network.get_all_weights()
        key = f"layer_{layer}"
        if key not in all_weights:
            return []
        return all_weights[key].flatten().tolist()

    def _build_layer_data(self, layer_index: int, total_layers: int) -> LayerData:
        """Construit l'objet LayerData pour une couche donnée."""
        activations_by_layer = self.network.get_activations()
        biases_by_layer = self.network.get_biases()

        activation_key = f"layer_{layer_index}"
        raw_activations = activations_by_layer.get(activation_key)

        if raw_activations is not None:
            # Les activations sont normalisées entre 0 et 1 pour Unity
            normalized_activations = normalize_to_unit_range(raw_activations.squeeze(0))
        else:
            normalized_activations = torch.zeros(self.architecture[layer_index])

        if layer_index == 0:
            biases = torch.zeros(self.architecture[layer_index])
            layer_type = "input"
        elif layer_index == total_layers - 1:
            biases = biases_by_layer.get(f"layer_{layer_index}", torch.zeros(self.architecture[layer_index]))
            layer_type = "output"
        else:
            biases = biases_by_layer.get(f"layer_{layer_index}", torch.zeros(self.architecture[layer_index]))
            layer_type = "hidden"

        activation_function_name = activation_name_for_layer(layer_index, total_layers)

        neurons = [
            NeuronData(
                layer_index=layer_index,
                neuron_index=neuron_index,
                activation_value=float(normalized_activations[neuron_index]),
                bias_value=float(biases[neuron_index]),
                activation_function=activation_function_name,
            )
            for neuron_index in range(self.architecture[layer_index])
        ]

        weights = self.get_weights_as_list(layer_index)

        return LayerData(
            layer_index=layer_index,
            layer_type=layer_type,
            neurons=neurons,
            weights=weights,
        )

    def get_network_data(self, phase: Optional[str] = None) -> NetworkData:
        """
        Construit et retourne l'objet NetworkData complet représentant
        l'état actuel du réseau (couches, neurones, poids, biais, métriques).
        """
        total_layers = len(self.architecture)
        layers = [self._build_layer_data(i, total_layers) for i in range(total_layers)]

        return NetworkData(
            model_name=self.model_name,
            total_layers=total_layers,
            layers=layers,
            phase=phase or self.current_phase,
            loss=self.current_loss,
            accuracy=self.current_accuracy,
        )

    def get_layer_network_data(self, layer_index: int, phase: str) -> NetworkData:
        """
        Construit un NetworkData ne contenant que la couche `layer_index`,
        utilisé pour l'animation layer-par-layer du forward pass dans Unity.
        """
        total_layers = len(self.architecture)
        layer = self._build_layer_data(layer_index, total_layers)

        return NetworkData(
            model_name=self.model_name,
            total_layers=total_layers,
            layers=[layer],
            phase=phase,
            loss=self.current_loss,
            accuracy=self.current_accuracy,
        )

    def get_total_params(self) -> int:
        """Retourne le nombre total de paramètres entraînables du réseau."""
        return sum(p.numel() for p in self.network.parameters() if p.requires_grad)


def get_model_manager() -> ModelManager:
    """Fonction d'accès au singleton ModelManager (utilisée par les routes)."""
    return ModelManager.get_instance()
