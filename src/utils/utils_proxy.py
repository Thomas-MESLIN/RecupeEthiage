import os
import requests
from dotenv import load_dotenv
from functools import cache
from src.config.logging_config import setup_logger

# Initialiser le logger
logger = setup_logger(name="utils_proxy")

def test_connection(
    url: str,
    timeout: int = 5,
) -> bool:
    """
    Retourne True si la connexion fonctionne.
    """
    try:
        response = requests.get(
            url,
            timeout=timeout,
            verify=False,
            allow_redirects=True,
        )

        logger.debug(f"STATUS: {response.status_code}")

        return response.ok

    except requests.RequestException:
        return False

# URL de test du Proxy
TEST_URL = "https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/sites.xml?size=20"

@cache
def set_up_working_proxy():
    """
    Détermine automatiquement si le proxy doit être utilisé.

    Le proxy sert à accéder à internet sur le réseau interne de la DREAL.
    Il est éxécuté une seule fois, même si plusieurs appels arrivent.
    """
    logger.info("CONNEXION A INTERNET - TEST PROXY")
    logger.info("Configuration du proxy...")

    logger.info("Test avec les paramètres d'environnement...")
    # Charge le fichier .env
    load_dotenv()
    if test_connection(TEST_URL):
        logger.info("Connexion proxy OK - CONNECTE")
        return

    logger.info("Test en supprimant HTTP_PROXY et HTTPS_PROXY")
    os.unsetenv("HTTP_PROXY")
    os.unsetenv("HTTPS_PROXY")
    if test_connection(TEST_URL):
        logger.info("Connexion Direct OK - CONNECTE")
        return

    logger.warning("Proxy KO - Aucune connexion réseau disponible")

    # raise RuntimeError(
    #     "Aucune connexion réseau disponible"
    # )
