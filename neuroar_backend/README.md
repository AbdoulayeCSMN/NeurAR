# NeuroAR Backend

Backend FastAPI/PyTorch pour l'application de réalité augmentée **NeuroAR**, qui visualise
en 3D (via Unity) un réseau de neurones MLP en train de fonctionner (forward pass, backward
pass, etc.).

## Installation

```bash
cd neuroar_backend
pip install -r requirements.txt
```

## Lancement

⚠️ Le dossier du projet s'appelle `neuroar_backend` (package Python), donc lance
uvicorn depuis le dossier **parent** de `neuroar_backend/` :

```bash
python -m uvicorn neuroar_backend.app.main:app --reload
```

Le serveur démarre par défaut sur `0.0.0.0:8000` (configurable via le fichier `.env`).
Au premier lancement, le dataset MNIST est téléchargé automatiquement dans `./data`.

## URLs

- **API REST** : `http://TON_IP:8000`
- **WebSocket** : `ws://TON_IP:8000/ws`

Remplace `TON_IP` par l'adresse IP locale de la machine qui exécute le serveur
(visible avec `ipconfig` sous Windows ou `ifconfig`/`ip addr` sous Linux/Mac),
afin que le téléphone/casque Unity puisse s'y connecter sur le même réseau Wi-Fi.

## Tester le serveur

```bash
curl http://localhost:8000/health
curl http://localhost:8000/architecture
curl http://localhost:8000/network
```

## Endpoints REST

| Méthode | Route          | Description                                         |
|---------|----------------|-----------------------------------------------------|
| GET     | `/health`      | Vérifie que le serveur et le modèle sont opérationnels |
| GET     | `/network`     | Retourne un instantané complet du réseau (`NetworkData`) |
| POST    | `/forward`     | Exécute un forward pass : `{"input": [784 floats]}` |
| GET     | `/architecture`| Retourne la configuration du réseau et le nombre de paramètres |

## WebSocket (`/ws`)

Envoie un message JSON contenant un champ `"action"` :

```json
{ "action": "get_network" }
{ "action": "forward_pass" }
{ "action": "backward_pass" }
{ "action": "reset" }
```

- `get_network` : envoie l'état complet du réseau avec `phase: "init"`.
- `forward_pass` : exécute un forward pass sur un échantillon MNIST aléatoire et diffuse
  le résultat **couche par couche** (avec un délai de 100ms entre chaque couche, pour
  l'animation Unity), puis l'état final complet.
- `backward_pass` : exécute un backward pass (mise à jour des poids) et diffuse le résultat.
- `reset` : réinitialise le modèle (nouveaux poids) et diffuse le nouvel état.

Le format JSON envoyé correspond exactement aux classes C# Unity `NetworkData`,
`LayerData` et `NeuronData` (champs en camelCase).

> ⚠️ **Taille des messages** : le snapshot complet du réseau (poids inclus, ex.
> couche 784→128 = ~100 000 valeurs) pèse environ 2,4 Mo en JSON. Si le client
> Unity utilise une librairie WebSocket avec une limite de taille de message
> (ex. `NativeWebSocket`, `websocket-sharp`), pense à l'augmenter au-delà de
> cette taille pour éviter une déconnexion sur `get_network` ou en fin de
> `forward_pass`.

## Configuration (`.env`)

```
HOST=0.0.0.0
PORT=8000
MODEL_ARCHITECTURE=784,128,64,10
LOG_LEVEL=info
```
