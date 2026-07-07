import os
from pathlib import Path
import requests
import pandas as pd
import locale
from datetime import datetime, timedelta
from functools import cache
import logging
from dotenv import load_dotenv
from enum import StrEnum

loc = locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")

# Permet de changer le niveau d'information DEBUG, INFO ou autre...
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

GRANDEUR = {
    "QmM",
    "QmnJ",
}

class OndeGeographicZone(StrEnum):
    BASSIN = "B",
    REGION = "R",
    DEPARTEMENT = "D",

class OndeCampagneType(StrEnum):
    USUELLE = "U",
    COMPLEMENTAIRE = "C",
    ALL_CAMPAGNE = "A",

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
    return Path(f"output/VCN3/analyse_frequence_periode/periode-de-retour-{code_sandre}-{annee_mois}.csv")

def is_date_historique(annee_mois:str):
    return "1990-12" <= annee_mois <= "2020-12"

def get_path_stations():
    return Path("output/hubeau/downloaded_data/stations/stations.csv")

def get_path_sites():
    return Path("output/hubeau/downloaded_data/sites/sites.csv")

@cache
def get_paths_source_historique(grandeur:str) -> list[Path]:
    """
    Renvoie le chemin des fichiers contenant la source de donnée historique de la grandeur.
    :param grandeur: Une grandeur à spécifier
    :return: La liste des chemins nécessaire au calcul de cette grandeur
    """
    path_list = []
    if grandeur == "QmnJ":
        for date in pd.date_range("1990-12", "2020-12", freq="MS"):
            annee_mois = date.strftime("%Y-%m")
            path_list.append(get_path_mensuel_raw_csv(annee_mois, grandeur))
    elif grandeur == "QmM":
        path_list.append(get_path_historique_raw_csv(grandeur))
    path_list.append(get_path_sites())
    path_list.append(get_path_stations())
    path_list.append(get_path_liste_site_station_custom())
    return path_list.copy()

@cache
def get_paths_source_mensuel(grandeur:str, annee_mois:str) -> list[Path]:
    """
    Renvoie le chemin des fichiers contenant la source de donnée de la grandeur mis en paramètre et de la date
    :param grandeur: Une grandeur.
    :param annee_mois: AAAA-MM
    :return: Une liste de chemin vers les sources des données mensuel.
    """
    list_chemin = [
        get_path_stations(),
        get_path_liste_site_station_custom(),
        get_path_sites(),
        get_path_mensuel_raw_csv(annee_mois,grandeur)
    ]
    return list_chemin.copy()

def get_path_liste_site_station_custom():
    return Path("output/site_station_custom/liste_site_et_station_custom.csv")

@cache
def get_path_sources(code_sandre: str, grandeur:str, annee_mois:str):
    """
    REnvoie le chemin des fichiers de stations, du fichier mensuel et des fichiers historiques associé à la grandeur.
    :param code_sandre: Le code sandre utilisé
    :param grandeur: La grandeur calculée
    :param annee_mois: L'année et le mois du calcul actuel
    :return: L'ensemble mensuel, historique et stations des sources utilisés
    """
    chemin_liste_station = get_path_stations()
    if code_sandre == "custom":
        chemin_liste_station = get_path_liste_site_station_custom()
    return [chemin_liste_station] + get_paths_source_historique(grandeur) + get_paths_source_mensuel(grandeur, annee_mois)

def get_path_meteofrance_correspondance_departement_id_datagouv_mens_historique() -> Path:
    return Path("output/meteoFrance/departement_id_datagouv/MENS_departement_id_datagouv_historique.csv")

def get_path_campagne_onde() -> Path:
    """
    :return: Le chemin où est stocké toutes les campagnes ONDE
    """
    return Path("output/hubeau/downloaded_data/onde/campagnes_onde.csv")


def get_path_observation_onde(date_debut:datetime, date_fin:datetime, onde_zone:OndeGeographicZone, code_associe:str) -> Path:
    """
    Renvoie le chemin où est stocké la zone géographic des observations ONDE allant de date_debut jusqua date_fin.
    :param date_debut: La date de début des observations
    :param date_fin: La date de fin des observations
    :param onde_zone: La zone géographique associées
    :param code_associe: Le code associé à la zone géographique
    :return: Un chemin vers le fichier correspondant.
    """
    lettre_zone = f"{onde_zone}{code_associe}"

    return Path(f"output/hubeau/downloaded_data/onde/observation_onde_{lettre_zone}_{date_debut.strftime('%Y%m%d')}_{date_fin.strftime('%Y%m%d')}.csv")

def get_path_stations_onde(onde_zone:OndeGeographicZone, code_associe:str) -> Path:
    """
    Renvoie le chemin où est stocké la zone géographic des observations ONDE allant de date_debut jusqua date_fin.
    :param date_debut: La date de début des observations
    :param date_fin: La date de fin des observations
    :param onde_zone: La zone géographique associées
    :param code_associe: Le code associé à la zone géographique
    :return: Un chemin vers le fichier correspondant.
    """
    lettre_zone = f"{onde_zone}{code_associe}"

    return Path(f"output/hubeau/downloaded_data/onde/stations_onde_{lettre_zone}.csv")

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


# Vérification de l'ancienneté des données.
def is_path_valid_age(chemin:Path) -> bool:
    """
    Renvoie vrai si le fichier est assez récent (< 1 ans)
    :param chemin: Un chemin sous forme de Path pointant vers un fichier.
    :return: Vrai si le fichier est récent (< 1 ans), faux sinon.
    """
    if not chemin.exists():
        raise FileNotFoundError(chemin)
    one_year = timedelta(days=360) # 1 ans
    #one_year = timedelta(seconds=1)  # 101 seconde pour le test
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

def is_file_need_download(chemin:Path):
    """
    Vérifie qu'un fichier doit être téléchargé.
    Demande à l'utilisateur de renouveler le fichier si celui-ci est trop vieux.
    :param chemin: Le fichier a potentiellement renouveler.
    :return: True si le fichier doit être téléchargé, False sinon.
    """
    if not chemin.exists():
        return True
    elif is_path_valid_age(chemin):
        return False # On a pas besoin de télécharger le fichier car il est assez récent
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
    :return: Renvoie True si le fichier résultat est plus récent que le fichier source. False sinon.
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
