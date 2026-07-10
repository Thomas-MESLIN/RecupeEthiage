import logging
import os
from logging.handlers import RotatingFileHandler
from src.config.paths import OUTPUT_DIR


# Créer le dossier logs s'il n'existe pas
os.makedirs(OUTPUT_DIR / "logs", exist_ok=True)

def setup_logger(name: str = "app", log_file: str = OUTPUT_DIR/"logs/app.log", level: int = logging.INFO) -> logging.Logger:
    """
    Configure et retourne un logger avec :
    - Un handler pour la console (niveau INFO)
    - Un handler pour un fichier (niveau DEBUG)
    - Un handler pour les erreurs (niveau ERROR)
    - Rotation des fichiers de logs (10 Mo max, 5 fichiers de backup)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Éviter les doublons de handlers
    if logger.handlers:
        return logger
    
    # Désactiver la propagation pour éviter les doublons (messages affichés 2x)
    logger.propagate = False

    # Formattage des logs
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler pour le fichier principal
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 Mo
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler pour les erreurs
    error_handler = RotatingFileHandler(
        OUTPUT_DIR / "logs" / "errors.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger