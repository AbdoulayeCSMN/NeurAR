"""
Définition du réseau de neurones NeuroARNet utilisé par le ModelManager.
Architecture MLP entièrement connectée et configurable, avec BatchNorm
et ReLU sur les couches cachées, et Softmax sur la couche de sortie.
"""
from typing import Dict, List

import torch
import torch.nn as nn
import torch.nn.functional as F

from neuroar_backend.app.core.activation_functions import normalize_weights_tanh


class NeuroARNet(nn.Module):
    """
    Réseau de neurones MLP fully connected configurable.

    Pour une architecture [784, 128, 64, 10], le réseau est composé de :
      - Linear(784 -> 128) + BatchNorm + ReLU
      - Linear(128 -> 64)  + BatchNorm + ReLU
      - Linear(64  -> 10)  + Softmax (couche de sortie)
    """

    def __init__(self, architecture: List[int]):
        super().__init__()
        self.architecture = architecture

        self.linear_layers = nn.ModuleList()
        self.batch_norms = nn.ModuleList()

        # Construit dynamiquement les couches cachées (toutes sauf la dernière)
        for i in range(len(architecture) - 1):
            in_features = architecture[i]
            out_features = architecture[i + 1]
            self.linear_layers.append(nn.Linear(in_features, out_features))

            # Pas de BatchNorm sur la couche de sortie
            is_output_layer = (i == len(architecture) - 2)
            if not is_output_layer:
                self.batch_norms.append(nn.BatchNorm1d(out_features))
            else:
                self.batch_norms.append(None)

        # Stocke les activations de chaque couche après le dernier forward pass
        self._last_activations: Dict[str, torch.Tensor] = {}

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Effectue un forward pass complet et conserve les activations
        de chaque couche (y compris la couche d'entrée) pour pouvoir
        les exposer ensuite via get_activations().
        """
        self._last_activations = {"layer_0": x.detach()}

        current = x
        num_layers = len(self.linear_layers)

        for i, linear in enumerate(self.linear_layers):
            current = linear(current)
            is_output_layer = (i == num_layers - 1)

            if is_output_layer:
                current = F.softmax(current, dim=-1)
            else:
                batch_norm = self.batch_norms[i]
                if batch_norm is not None:
                    current = batch_norm(current)
                current = F.relu(current)

            self._last_activations[f"layer_{i + 1}"] = current.detach()

        return current

    def get_activations(self) -> Dict[str, torch.Tensor]:
        """
        Retourne un dictionnaire {nom_de_couche: tenseur_activations}
        contenant les activations capturées lors du dernier forward pass.
        """
        return self._last_activations

    def get_all_weights(self) -> Dict[str, torch.Tensor]:
        """
        Retourne un dictionnaire {nom_de_couche: tenseur_poids} contenant
        les poids de chaque couche linéaire, normalisés entre -1 et 1
        via la fonction tanh.
        """
        weights: Dict[str, torch.Tensor] = {}
        for i, linear in enumerate(self.linear_layers):
            weights[f"layer_{i + 1}"] = normalize_weights_tanh(linear.weight.detach())
        return weights

    def get_biases(self) -> Dict[str, torch.Tensor]:
        """
        Retourne un dictionnaire {nom_de_couche: tenseur_biais} contenant
        les biais de chaque couche linéaire.
        """
        biases: Dict[str, torch.Tensor] = {}
        for i, linear in enumerate(self.linear_layers):
            biases[f"layer_{i + 1}"] = linear.bias.detach()
        return biases
