import os
from pathlib import Path
import requests
import pandas as pd
import locale
from datetime import datetime, timedelta
import dateutil

loc = locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")

GRANDEUR = {
    "QmM",
    "QmnJ",
}

def get_path_historique_raw_csv(grandeur:str):
    return Path(f"output/hubeau/downloaded_data/observations_elaboree/observations-{grandeur}-AURA-1991-2020.csv")

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
    return Path(f"output/VCN3/moyenne_historique/VCN3-moyenne-{code_sandre}-1991-2020.csv")

def get_path_vcn3_mensuel(code_sandre:str, annee_mois:str):
    return Path(f"output/VCN3/mensuel/VCN3-{code_sandre}-{annee_mois}.csv")

def get_path_vcn3_station(code_station:str):
    return Path(f"output/VCN3/stations/VCN3-station-{code_station}.csv")

def get_path_periode_de_retour(code_sandre:str, annee_mois:str):
    return Path(f"output/VCN3/analyse_frequence_periode/analyse-frequence-{code_sandre}-{annee_mois}.csv")

def is_date_historique(annee_mois:str):
    return "1990-12" <= annee_mois <= "2020-12"

def get_path_stations():
    return Path("output/hubeau/downloaded_data/stations/stations.csv")

def get_path_sites():
    return Path("output/hubeau/downloaded_data/sites/sites.csv")

_cache_path_source_historique = {}
def get_paths_source_historique(grandeur:str) -> list[Path]:
    """
    Renvoie le chemin des fichiers contenant la source de donnée historique de la grandeur.
    :param grandeur: Une grandeur à spécifier
    :return: La liste des chemins nécessaire au calcul de cette grandeur
    """
    if grandeur in _cache_path_source_historique:
        return _cache_path_source_historique[grandeur].copy()
    path_list = []
    if grandeur == "QmnJ":
        for date in pd.date_range("1990-12", "2020-12", freq="MS"):
            annee_mois = date.strftime("%Y-%m")
            path_list.append(Path(f"output/hubeau/downloaded_data/observations_elaboree/observations-QmnJ-AURA-{annee_mois}.csv"))
    elif grandeur == "QmM":
        path_list.append(Path("output/hubeau/downloaded_data/observations_elaboree/observations-QmM-AURA-1991-2020.csv"))
    path_list.append(get_path_sites())
    path_list.append(get_path_stations())
    _cache_path_source_historique[grandeur] = path_list.copy()
    return path_list.copy()

def get_paths_source_mensuel(grandeur:str, annee_mois:str) -> list[Path]:
    """
    Renvoie le chemin des fichiers contenant la source de donnée de la grandeur mis en paramètre et de la date
    :param grandeur: Une grandeur.
    :param annee_mois: AAAA-MM
    :return: Une liste de chemin vers les sources des données mensuel.
    """
    list_chemin = [get_path_stations(), get_path_sites(), get_path_mensuel_raw_csv(annee_mois,grandeur)]
    return list_chemin.copy()

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

_cache_proxy = {}
def set_up_working_proxy():
    """
    Détermine automatiquement si le proxy doit être utilisé.

    Le proxy sert à accéder à internet sur le réseau interne de la DREAL.
    """
    if "proxy_set_up" in _cache_proxy:
        return _cache_proxy["proxy_set_up"]
    print("Configuration du proxy...\n")
    print("Test avec proxy...")

    if test_connection(TEST_URL, proxies=PROXIES):
        print("Proxy OK")
        os.environ['http_proxy'] = PROXIES['http']
        os.environ['HTTP_PROXY'] = PROXIES['HTTP']
        os.environ['https_proxy'] = PROXIES['https']
        os.environ['HTTPS_PROXY'] = PROXIES['HTTPS']
        _cache_proxy["proxy_set_up"] = PROXIES
        return PROXIES

    print("Proxy KO")
    print("Test sans proxy...")

    if test_connection(TEST_URL):
        print("Connexion directe OK")
        os.environ['http_proxy'] = ""
        os.environ['HTTP_PROXY'] = ""
        os.environ['https_proxy'] = ""
        os.environ['HTTPS_PROXY'] = ""
        _cache_proxy["proxy_set_up"] = None
        return None

    raise RuntimeError(
        "Aucune connexion réseau disponible"
    )

# Manipulation des listes de stations
def get_stations(code_sandre:str, annee_mois_active:str|None=None) -> pd.DataFrame:
    """
    Renvoie toutes les stations associé au code sandre sous forme d'un DataFrame.
    Si on renseigne annee_mois_active, ne renvoie que les stations qui sont actives à ce moment là.
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



# Vérification de l'ancienneté des données.
def is_path_valid_age(chemin:Path) -> bool:
    """
    Renvoie vrai si le fichier est assez récent (< 1 ans)
    :param chemin: Un chemin sous forme de Path pointant vers un fichier.
    :return: Vrai si le fichier est récent (< 1 ans), faux sinon.
    """
    if not chemin.exists():
        raise FileNotFoundError(chemin)
    #one_year = timedelta(days=360) # 1 ans
    one_year = timedelta(seconds=10)  # 101 seconde pour le test
    time_modification_fichier = chemin.stat().st_mtime
    date_modification_fichier = datetime.fromtimestamp(time_modification_fichier)
    date_actuelle = datetime.now()
    delta = date_actuelle - date_modification_fichier
    return delta < one_year

_cache_prompt = {}
def prompt_renew_old_data(chemin:Path) -> bool:
    """
    Demande à l'utilisateur s'il souhaite renouveler le fichier pointé vers Path.
    :param chemin: Un chemin sous forme de Path pointant vers un fichier à renouveller.
    :return: Vrai si l'utilisateur accepte de renouveller le fichier, faux sinon.
    """
    # Si on a répondu à renouveller tous précédemment, on renvoie True sans rien re-demander à l'utilisateur.
    if "renouveler_tout" in _cache_prompt:
        return True
    elif "renouveler_rien" in _cache_prompt:
        return False

    res_prompt = input(f"\nLe fichier : {chemin.name} est vieux de plus d'un an, souhaitez vous : \n"
                       f"Ne rien renouveler ? (0)\n"
                       f"renouveler uniquement ce fichier ? (1)\n"
                       f"renouveler tous les fichiers trop vieux ? (2)\n"
                       f"Entrez votre réponse (0,1 ou 2) -> ")

    if res_prompt == "1": # On renouvelle uniquement un fichier
        return True
    elif res_prompt == "2": # On renouvelle tous les fichiers trop vieux.
        _cache_prompt["renouveler_tout"] = True
        return True
    else: # On ne renouvelle aucun fichier
        _cache_prompt["renouveler_rien"] = False
        print("\nAucun fichier ne sera renouvelé.\n")
        return False

def is_file_renewed(chemin:Path) -> bool:
    """
    Effectue un check complet sur le fichier pointé,
    Si celui ci est trop vieux, l'utilisateur est interrogé.
    :param chemin: Le fichier a potentiellement renouveler.
    :return: Renvoie True si l'utilisateur accepte de renouveler le fichier, False sinon.
    """
    if not is_path_valid_age(chemin):
        return prompt_renew_old_data(chemin)
    else:
        return True

def is_file_need_download(chemin:Path):
    """
    Vérifie qu'un fichier doit être téléchargé.
    Demande à l'utilisateur de renouveler le fichier si celui-ci est trop vieux.
    :param chemin: Le fichier a potentiellement renouveler.
    :return: Rien
    """
    if not chemin.exists():
        return True
    elif chemin.exists() and is_path_valid_age(chemin):
        return False
    elif prompt_renew_old_data(chemin):
        print(f"\nLe fichier {chemin.name} va être re-téléchargé. \n"
              "si le temps d'attente est trop long, vous pouvez annuler la commande avec ctrl+c.\n"
              "Il suffira de relancer le script et de refuser le prompt qui va s'afficher, \n"
              "l'ancien fichier sera alors utilisé.\n")
        return True
    else:
        return False

def is_res_updated_with_source(chemin_source_list:list[Path], chemin_resultat:Path) -> bool:
    """
    Compare la date de modification du fichier de résultat et du fichier source
    vérifie que le fichier de résultat est plus récent que celui d'entrée.
    Si c'est le fichier source qui est plus récent, alors le fichier résultat doit être mis à jour.
    Si la source n'existe pas, on renvoie False.
    :param chemin_source_list: Une liste de fichier qui sert à construire le résultat
    :param chemin_resultat: Le fichier résultat basé sur le fichier source.
    :return: Renvoie True si le fichier résultat est plus ancien que le fichier source. False sinon.
    """
    if not chemin_resultat.exists():
        return False
    is_resultat_plus_recent_que_source = True
    for chemin_source in chemin_source_list:
        if not chemin_source.exists():
            return False
        date_modification_source = chemin_source.stat().st_mtime
        date_modification_resultat = chemin_resultat.stat().st_mtime
        if not date_modification_source < date_modification_resultat:
            is_resultat_plus_recent_que_source = False
            break
    return is_resultat_plus_recent_que_source
