"""
Gestion des connexions WebSocket pour NeuroAR.
Le ConnectionManager gère plusieurs clients Unity simultanés et permet
de diffuser (broadcast) les mises à jour du réseau de neurones.
"""
import asyncio
import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

from neuroar_backend.app.config import LOG_PREFIX
from neuroar_backend.app.models.model_manager import get_model_manager

logger = logging.getLogger("neuroar")

# Délai entre l'envoi de chaque couche pendant l'animation du forward pass
LAYER_ANIMATION_DELAY_SECONDS = 0.1


class ConnectionManager:
    """Gère l'ensemble des connexions WebSocket actives et leur diffusion."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accepte une nouvelle connexion WebSocket et l'enregistre."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"{LOG_PREFIX} Nouveau client WebSocket connecté ({len(self.active_connections)} actifs)")

    def disconnect(self, websocket: WebSocket):
        """Retire une connexion de la liste des connexions actives."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"{LOG_PREFIX} Client WebSocket déconnecté ({len(self.active_connections)} actifs)")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Envoie un message JSON à un client spécifique."""
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        """Diffuse un message JSON à tous les clients connectés."""
        disconnected_clients = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as exc:
                logger.warning(f"{LOG_PREFIX} Échec d'envoi à un client, déconnexion programmée ({exc})")
                disconnected_clients.append(connection)

        for connection in disconnected_clients:
            self.disconnect(connection)


# Instance unique partagée du gestionnaire de connexions
connection_manager = ConnectionManager()


async def handle_get_network(websocket: WebSocket):
    """Traite l'action 'get_network' : envoie le NetworkData complet (phase=init)."""
    logger.info(f"{LOG_PREFIX} Action reçue : get_network")
    manager = get_model_manager()
    network_data = manager.get_network_data(phase="init")
    await connection_manager.send_personal_message(
        json.loads(network_data.model_dump_json(by_alias=True)), websocket
    )


async def handle_forward_pass(websocket: WebSocket):
    """
    Traite l'action 'forward_pass' : exécute un forward pass sur un échantillon
    MNIST aléatoire et diffuse le résultat couche par couche, avec un délai
    de 100ms entre chaque couche pour permettre l'animation côté Unity.
    """
    logger.info(f"{LOG_PREFIX} Action reçue : forward_pass")
    manager = get_model_manager()

    # Calcule le forward pass complet (met à jour l'état interne du modèle)
    full_network_data = manager.forward_pass()

    # Diffuse ensuite les couches une par une pour l'animation
    for layer_index in range(full_network_data.total_layers):
        layer_network_data = manager.get_layer_network_data(layer_index, phase="forward")
        await connection_manager.broadcast(
            json.loads(layer_network_data.model_dump_json(by_alias=True))
        )
        await asyncio.sleep(LAYER_ANIMATION_DELAY_SECONDS)

    # Diffuse enfin l'état complet final (loss, accuracy, toutes les couches)
    await connection_manager.broadcast(
        json.loads(full_network_data.model_dump_json(by_alias=True))
    )


async def handle_backward_pass(websocket: WebSocket):
    """Traite l'action 'backward_pass' : exécute un backward pass et diffuse le résultat."""
    logger.info(f"{LOG_PREFIX} Action reçue : backward_pass")
    manager = get_model_manager()
    network_data = manager.backward_pass()
    await connection_manager.broadcast(
        json.loads(network_data.model_dump_json(by_alias=True))
    )


async def handle_reset(websocket: WebSocket):
    """Traite l'action 'reset' : réinitialise le modèle et diffuse le nouvel état."""
    logger.info(f"{LOG_PREFIX} Action reçue : reset")
    manager = get_model_manager()
    network_data = manager.reset()
    await connection_manager.broadcast(
        json.loads(network_data.model_dump_json(by_alias=True))
    )


# Table de routage : associe chaque action à son gestionnaire
ACTION_HANDLERS = {
    "get_network": handle_get_network,
    "forward_pass": handle_forward_pass,
    "backward_pass": handle_backward_pass,
    "reset": handle_reset,
}


async def websocket_endpoint(websocket: WebSocket):
    """
    Point d'entrée principal du WebSocket (ws://HOST:PORT/ws).
    Reçoit des messages JSON contenant un champ "action" et délègue
    le traitement au handler correspondant.
    """
    await connection_manager.connect(websocket)
    try:
        while True:
            raw_message = await websocket.receive_text()
            try:
                payload = json.loads(raw_message)
            except json.JSONDecodeError:
                logger.warning(f"{LOG_PREFIX} Message WebSocket invalide (JSON mal formé) : {raw_message}")
                await connection_manager.send_personal_message(
                    {"error": "JSON invalide"}, websocket
                )
                continue

            action = payload.get("action")
            handler = ACTION_HANDLERS.get(action)

            if handler is None:
                logger.warning(f"{LOG_PREFIX} Action WebSocket inconnue : {action}")
                await connection_manager.send_personal_message(
                    {"error": f"Action inconnue : {action}"}, websocket
                )
                continue

            try:
                await handler(websocket)
            except Exception as exc:
                logger.error(f"{LOG_PREFIX} Erreur lors du traitement de l'action '{action}' : {exc}")
                await connection_manager.send_personal_message(
                    {"error": f"Erreur lors du traitement de l'action '{action}' : {exc}"}, websocket
                )

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as exc:
        logger.error(f"{LOG_PREFIX} Erreur WebSocket inattendue : {exc}")
        connection_manager.disconnect(websocket)
