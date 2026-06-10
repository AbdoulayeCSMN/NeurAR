# NeurAR

NeurAR est un projet de réalité augmentée qui visualise un réseau de neurones en temps réel via Unity, avec un backend Python/FastAPI chargé d'exécuter le modèle PyTorch et d'envoyer les données au client.

## Contenu du projet

- **Unity** : interface AR, rendu du réseau et interactions utilisateur
- **Backend** : API REST + WebSocket pour piloter le modèle et transmettre les états du réseau

## Prérequis

- Unity **6000.4.3f1**
- Python 3.10+
- Un appareil compatible AR si vous ciblez le mobile

## Structure

- `Assets/` : projet Unity
- `Packages/` : dépendances Unity
- `ProjectSettings/` : configuration Unity
- `neuroar_backend/` : backend Python

## Démarrage du backend

La documentation détaillée du backend se trouve dans `neuroar_backend/README.md`.

Résumé rapide :

```bash
cd neuroar_backend
pip install -r requirements.txt
python -m uvicorn neuroar_backend.app.main:app --reload
```

Le serveur écoute par défaut sur `http://0.0.0.0:8000` et `ws://0.0.0.0:8000/ws`.

## Démarrage de Unity

1. Ouvrir le projet avec Unity Hub.
2. Lancer la scène principale dans `Assets/NeuroAR/Scenes/Main.unity`.
3. Configurer l'URL WebSocket du backend dans le script `WebSocketClient` si nécessaire.

## Fonctionnalités

- Visualisation du réseau de neurones couche par couche
- Animation des passes forward et backward
- Interaction AR avec rotation, zoom et sélection de neurones
- Communication temps réel entre Unity et le backend

## Documentation complémentaire

- `neuroar_backend/README.md` : détails complets sur l'API, le WebSocket et la configuration du backend
