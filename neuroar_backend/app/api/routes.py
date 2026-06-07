"""
Routes REST HTTP de l'API NeuroAR.
Fournit des endpoints de santé, de récupération de l'état du réseau,
de forward pass, et d'inspection de l'architecture du modèle.
"""
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from neuroar_backend.app.config import LOG_PREFIX
from neuroar_backend.app.models.model_manager import get_model_manager
from neuroar_backend.app.models.network_data import NetworkData

logger = logging.getLogger("neuroar")

router = APIRouter()


class ForwardRequest(BaseModel):
    """Corps de requête attendu pour POST /forward."""
    input: list[float] = Field(..., description="Vecteur d'entrée (ex: 784 valeurs pour MNIST)")


@router.get("/health")
async def health_check():
    """Vérifie que le serveur et le modèle sont opérationnels."""
    try:
        manager = get_model_manager()
        is_loaded = manager.network is not None
        logger.info(f"{LOG_PREFIX} Vérification de santé effectuée")
        return {"status": "ok", "model": "loaded" if is_loaded else "not_loaded"}
    except Exception as exc:
        logger.error(f"{LOG_PREFIX} Erreur lors du health check : {exc}")
        raise HTTPException(status_code=500, detail="Erreur lors de la vérification de santé") from exc


@router.get("/network", response_model=NetworkData, response_model_by_alias=True)
async def get_network():
    """Retourne un instantané (snapshot) complet de l'état actuel du réseau."""
    try:
        manager = get_model_manager()
        network_data = manager.get_network_data()
        logger.info(f"{LOG_PREFIX} Snapshot du réseau envoyé")
        return network_data
    except Exception as exc:
        logger.error(f"{LOG_PREFIX} Erreur lors de la récupération du réseau : {exc}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du réseau") from exc


@router.post("/forward", response_model=NetworkData, response_model_by_alias=True)
async def forward(request: ForwardRequest):
    """Exécute un forward pass sur les données fournies et retourne le NetworkData résultant."""
    try:
        manager = get_model_manager()
        expected_size = manager.architecture[0]

        if len(request.input) != expected_size:
            raise HTTPException(
                status_code=400,
                detail=f"Taille d'entrée invalide : attendu {expected_size}, reçu {len(request.input)}",
            )

        network_data = manager.forward_pass(request.input)
        logger.info(f"{LOG_PREFIX} Forward pass exécuté via REST")
        return network_data
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"{LOG_PREFIX} Erreur lors du forward pass : {exc}")
        raise HTTPException(status_code=500, detail="Erreur lors du forward pass") from exc


@router.get("/architecture")
async def get_architecture():
    """Retourne la configuration du réseau (couches et nombre total de paramètres)."""
    try:
        manager = get_model_manager()
        logger.info(f"{LOG_PREFIX} Architecture du réseau envoyée")
        return {
            "layers": manager.architecture,
            "total_params": manager.get_total_params(),
        }
    except Exception as exc:
        logger.error(f"{LOG_PREFIX} Erreur lors de la récupération de l'architecture : {exc}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de l'architecture") from exc
