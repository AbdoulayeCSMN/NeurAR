"""
Fonctions utilitaires liées aux fonctions d'activation.
Utilisées pour annoter les neurones avec le nom de leur fonction d'activation
et pour normaliser les valeurs envoyées à Unity.
"""
import torch

# Nom de la fonction d'activation utilisée pour les couches cachées
HIDDEN_ACTIVATION_NAME = "relu"

# Nom de la fonction d'activation utilisée pour la couche de sortie
OUTPUT_ACTIVATION_NAME = "softmax"


def activation_name_for_layer(layer_index: int, total_layers: int) -> str:
    """
    Retourne le nom de la fonction d'activation associée à une couche,
    selon sa position dans le réseau (entrée, cachée, sortie).
    """
    if layer_index == 0:
        return "linear"
    if layer_index == total_layers - 1:
        return OUTPUT_ACTIVATION_NAME
    return HIDDEN_ACTIVATION_NAME


def normalize_to_unit_range(tensor: torch.Tensor) -> torch.Tensor:
    """
    Normalise un tenseur d'activations entre 0 et 1.
    Utilise un min-max scaling robuste aux valeurs constantes.
    """
    min_val = tensor.min()
    max_val = tensor.max()
    span = (max_val - min_val).clamp(min=1e-8)
    return (tensor - min_val) / span


def normalize_weights_tanh(tensor: torch.Tensor) -> torch.Tensor:
    """
    Normalise un tenseur de poids entre -1 et 1 via la fonction tanh.
    Cela conserve le signe des poids tout en bornant leur amplitude.
    """
    return torch.tanh(tensor)
