"""
Modèles Pydantic correspondant EXACTEMENT aux classes C# Unity côté client.
Tous les modèles sérialisent leurs champs en camelCase via `alias_generator`
afin que le JSON produit corresponde au format attendu par Unity (NeuronData,
LayerData, NetworkData).
"""
from typing import List
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """
    Classe de base qui génère automatiquement des alias camelCase
    pour chaque champ (ex: layer_index -> layerIndex).
    `populate_by_name` permet de construire les objets en Python avec
    les noms snake_case tout en sérialisant en camelCase pour Unity.
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        protected_namespaces=(),
    )


class NeuronData(CamelModel):
    """Représente un neurone unique dans une couche du réseau."""
    layer_index: int
    neuron_index: int
    activation_value: float
    bias_value: float
    activation_function: str


class LayerData(CamelModel):
    """Représente une couche complète du réseau (entrée, cachée ou sortie)."""
    layer_index: int
    layer_type: str  # "input", "hidden", "output"
    neurons: List[NeuronData]
    weights: List[float]


class NetworkData(CamelModel):
    """Représente l'état complet du réseau de neurones envoyé à Unity."""
    model_name: str
    total_layers: int
    layers: List[LayerData]
    phase: str  # "init", "forward", "backward", "idle"
    loss: float
    accuracy: float
