import os
from pathlib import Path
import requests

GRANDEUR = {
    "QmM",
    "QmnJ",
}

def get_path_historique_raw_csv(grandeur:str):
    return Path(f"output/hubeau/downloaded_data/observations_elaboree/observations-{grandeur}-france-1991-2020.csv")

def get_path_mensuel_raw_csv(annee_mois:str, grandeur:str):
    return Path(f"output/hubeau/downloaded_data/observations_elaboree/observations-{grandeur}-AURA-{annee_mois}.csv")

def get_path_clean_csv(code_sandre:str,annee_mois:str, grandeur:str):
    if code_sandre == "":
        return Path(f"output/hubeau/cleaned_data/clean-{grandeur}-{annee_mois}.csv")
    return Path(f"output/hubeau/cleaned_data/clean-{grandeur}-{code_sandre}-{annee_mois}.csv")

def get_path_qmm_moyen_historique(code_sandre:str):
    return Path(f"output/hubeau/QmM_moyen/QmM_moyennes_{code_sandre}_1991_2020.csv")

def get_path_hydraulicite(code_sandre:str, annee_mois:str):
    return Path(f"output/hydraulicite/hydraulicite-{code_sandre}-{annee_mois}.csv")

def get_path_vcn3_moyenne_historique(code_sandre:str):
    return Path(f"output/hubeau/VCN3/VCN3-moyenne-{code_sandre}-1991-2020.csv")

def get_path_vcn3_mensuel(code_sandre:str, annee_mois:str):
    return Path(f"output/hubeau/VCN3/VCN3-{code_sandre}-{annee_mois}.csv")

def get_path_vcn3(code_sandre:str, annee_mois:str):
    return Path(f"output/VCN3/VCN3-{code_sandre}-{annee_mois}.csv")

def is_date_historique(annee_mois:str):
    return "1990-12" <= annee_mois <= "2020-12"

# SELECTION DU PROXY

PROXIES = {
    "http": "http://pfrie-std.proxy.e2.rie.gouv.fr:8080",
    "https": "http://pfrie-std.proxy.e2.rie.gouv.fr:8080",
    "HTTP": "http://pfrie-std.proxy.e2.rie.gouv.fr:8080",
    "HTTPS": "http://pfrie-std.proxy.e2.rie.gouv.fr:8080",
}

TEST_URL = "http://www.google.com"


def test_connection(
    url: str,
    proxies: dict | None = None,
    timeout: int = 5,
) -> bool:
    """
    Retourne True si la connexion fonctionne.
    """

    try:
        response = requests.get(
            url,
            proxies=proxies,
            timeout=timeout,
            verify=False,
            allow_redirects=True,
        )

        print("STATUS:", response.status_code)

        return response.ok

    except requests.RequestException:
        return False


def set_up_working_proxy():
    """
    Détermine automatiquement si le proxy doit être utilisé.
    """
    print("Configuration du proxy...\n")
    print("Test avec proxy...")

    if test_connection(TEST_URL, proxies=PROXIES):
        print("Proxy OK")
        os.environ['http_proxy'] = PROXIES['http']
        os.environ['HTTP_PROXY'] = PROXIES['HTTP']
        os.environ['https_proxy'] = PROXIES['https']
        os.environ['HTTPS_PROXY'] = PROXIES['HTTPS']
        return PROXIES

    print("Proxy KO")
    print("Test sans proxy...")

    if test_connection(TEST_URL):
        print("Connexion directe OK")
        os.environ['http_proxy'] = ""
        os.environ['HTTP_PROXY'] = ""
        os.environ['https_proxy'] = ""
        os.environ['HTTPS_PROXY'] = ""
        return None

    raise RuntimeError(
        "Aucune connexion réseau disponible"
    )
