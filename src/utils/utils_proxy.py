import os
import requests
from dotenv import load_dotenv
from functools import cache

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

        print("STATUS:", response.status_code)

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
    print()
    print("---------CONNEXION A INTERNET - TEST PROXY--------------")
    print("Configuration du proxy...\n")

    print("Test avec les paramètres d'environnement...")
    # Charge le fichier .env
    load_dotenv()
    if test_connection(TEST_URL):
        print("Connexion proxy OK")
        print("-------------CONNECTE--------------")
        return

    print("Test en supprimant HTTP_PROXY et HTTPS_PROXY")
    os.unsetenv("HTTP_PROXY")
    os.unsetenv("HTTPS_PROXY")
    if test_connection(TEST_URL):
        print("Connexion Direct OK")
        print("-------------CONNECTE--------------")
        return

    print("Proxy KO")

    # raise RuntimeError(
    #     "Aucune connexion réseau disponible"
    # )
