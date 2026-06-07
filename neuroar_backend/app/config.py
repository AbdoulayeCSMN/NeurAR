"""
Configuration de l'application NeuroAR Backend.
Charge les variables d'environnement depuis le fichier .env
"""
import os
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Adresse et port d'écoute du serveur
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "8000"))

# Niveau de log (info, debug, warning, error)
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# Architecture du réseau de neurones, ex: "784,128,64,10" -> [784, 128, 64, 10]
MODEL_ARCHITECTURE = [
    int(x.strip()) for x in os.getenv("MODEL_ARCHITECTURE", "784,128,64,10").split(",")
]

# Origines autorisées pour CORS (toutes les origines en développement)
CORS_ORIGINS = ["*"]

# Préfixe utilisé dans tous les logs de l'application
LOG_PREFIX = "[NeuroAR]"
