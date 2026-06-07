"""
Point d'entrée principal de l'application NeuroAR Backend.
Initialise FastAPI, configure CORS, monte les routes REST et WebSocket,
et charge le modèle PyTorch au démarrage.
"""
import logging

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from neuroar_backend.app.config import HOST, PORT, CORS_ORIGINS, LOG_PREFIX, LOG_LEVEL
from neuroar_backend.app.api.routes import router as rest_router
from neuroar_backend.app.api.websocket_handler import websocket_endpoint
from neuroar_backend.app.models.model_manager import get_model_manager

# Configuration du logging global de l'application
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("neuroar")

# Création de l'application FastAPI
app = FastAPI(title="NeuroAR Backend")

# Configuration CORS (ouverte pour le développement, à restreindre en production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montage des routes REST
app.include_router(rest_router)


@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    """Point d'entrée WebSocket : ws://HOST:PORT/ws"""
    await websocket_endpoint(websocket)


@app.on_event("startup")
async def on_startup():
    """Charge le modèle PyTorch au démarrage du serveur."""
    logger.info(f"{LOG_PREFIX} Démarrage du serveur NeuroAR Backend...")
    manager = get_model_manager()
    logger.info(
        f"{LOG_PREFIX} Modèle '{manager.model_name}' chargé avec architecture {manager.architecture} "
        f"({manager.get_total_params()} paramètres)"
    )
    logger.info(f"{LOG_PREFIX} Serveur prêt sur http://{HOST}:{PORT} et ws://{HOST}:{PORT}/ws")


if __name__ == "__main__":
    uvicorn.run("neuroar_backend.app.main:app", host=HOST, port=PORT, reload=True)
