import os
from pathlib import Path
import requests
import pandas as pd

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

def get_path_vcn3_station(code_station:str):
    return Path(f"output/VCN3/stations/VCN3-station-{code_station}.csv")

def get_path_vcn3(code_sandre:str, annee_mois:str):
    """
    Renvoie le chemin d'un VCN3 calculé et pas historique
    # TODO changer le nom
    :param code_sandre:
    :param annee_mois:
    :return:
    """
    return Path(f"output/VCN3/VCN3-{code_sandre}-{annee_mois}.csv")

def is_date_historique(annee_mois:str):
    return "1990-12" <= annee_mois <= "2020-12"

def get_path_stations():
    return Path("output/hubeau/downloaded_data/stations/stations.csv")

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

# Manipulation des listes de stations
def get_stations(code_sandre:str, annee_mois_active:str|None=None) -> pd.DataFrame:
    """
    Renvoie toutes les stations associé au code sandre sous forme d'un DataFrame.
    Si on renseigne
    :param code_sandre: Le code sandre de ces stations.
    :param annee_mois_active: L'année et le mois actif.
    :return: Un dataframe contenant toute les stations associé au code sandre, étant active à cette date (si date renseignée)
    """
    # On charge toute les stations
    stations_path = get_path_stations()
    df_stations = pd.read_csv(stations_path)

    # Filtre les stations pour avoir celle avec le bon code Sandre
    df_stations_sandre = df_stations[df_stations["code_sandre_reseau_station"].astype(str).str.contains(code_sandre)]

    # Si on a renseigné une date, on filtre uniquement les stations ouvertes à cette date là.
    if annee_mois_active is not None:
        # On filtre les stations qui sont ouverte à cette date là
        df_stations_sandre_ouverte = df_stations_sandre[
            (annee_mois_active < df_stations_sandre["date_fermeture_station"].astype(str)) &
            (df_stations_sandre["date_ouverture_station"].astype(str) < annee_mois_active)
        ]
    else:
        # Sinon on renvoie toute les stations
        df_stations_sandre_ouverte = df_stations_sandre

    return df_stations_sandre_ouverte
