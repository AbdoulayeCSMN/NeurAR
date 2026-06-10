# NeurAR

NeurAR est un projet de réalité augmentée qui visualise en 3D l'exécution d'un réseau de neurones MLP.

## Structure

- `Assets/` : projet Unity
- `Packages/` : dépendances Unity
- `ProjectSettings/` : configuration du projet Unity
- `neuroar_backend/` : backend FastAPI/PyTorch

## Démarrage rapide

1. Ouvrir le projet avec Unity.
2. Consulter `neuroar_backend/README.md` pour lancer le backend.
3. Connecter l'application Unity au serveur lancé localement.

## Backend

Le backend expose une API REST et un WebSocket pour piloter la visualisation du réseau.
Voir `neuroar_backend/README.md` pour l'installation, les endpoints et la configuration.
