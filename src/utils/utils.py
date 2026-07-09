from pathlib import Path
import pandas as pd
import locale
from datetime import datetime, timedelta
from functools import cache
import logging
from src.config.paths import OUTPUT_DIR
from src.model.enums import GeographicScaleClip

loc = locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")

# Permet de changer le niveau d'information DEBUG, INFO ou autre...
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

GRANDEUR = {
    "QmM",
    "QmnJ",
}

def get_path_historique_raw_csv(grandeur:str):
    return OUTPUT_DIR / Path(f"hubeau/downloaded_data/observations_elaboree/observations-{grandeur}-AURA-1991-2020.csv")

def get_path_mensuel_raw_csv(annee_mois:str, grandeur:str):
    return OUTPUT_DIR / Path(f"hubeau/downloaded_data/observations_elaboree/observations-{grandeur}-AURA-{annee_mois}.csv")

def get_path_clean_csv(code_sandre:str,annee_mois:str, grandeur:str):
    if code_sandre == "":
        return OUTPUT_DIR / Path(f"hubeau/cleaned_data/clean-{grandeur}-{annee_mois}.csv")
    return OUTPUT_DIR / Path(f"hubeau/cleaned_data/clean-{grandeur}-{code_sandre}-{annee_mois}.csv")

def get_path_qmm_moyen_historique(code_sandre:str):
    return OUTPUT_DIR / Path(f"hubeau/QmM_moyen/QmM_moyennes_{code_sandre}_1991_2020.csv")

def get_path_hydraulicite(code_sandre:str, annee_mois:str):
    return OUTPUT_DIR / Path(f"hydraulicite/hydraulicite-{code_sandre}-{annee_mois}.csv")

def get_path_vcn3_moyenne_historique(code_sandre:str):
    return OUTPUT_DIR / Path(f"VCN3/moyenne_historique/VCN3-moyenne-{code_sandre}-1991-2020.csv")

def get_path_vcn3_mensuel(code_sandre:str, annee_mois:str):
    return OUTPUT_DIR / Path(f"VCN3/mensuel/VCN3-{code_sandre}-{annee_mois}.csv")

def get_path_vcn3_station(code_station:str):
    return OUTPUT_DIR / Path(f"VCN3/stations/VCN3-station-{code_station}.csv")

def get_path_periode_de_retour(code_sandre:str, annee_mois:str):
    return OUTPUT_DIR / Path(f"VCN3/analyse_frequence_periode/periode-de-retour-{code_sandre}-{annee_mois}.csv")

def is_date_historique(annee_mois:str):
    return "1990-12" <= annee_mois <= "2020-12"

def get_path_stations():
    return OUTPUT_DIR / Path("hubeau/downloaded_data/stations/stations.csv")

def get_path_sites():
    return OUTPUT_DIR / Path("hubeau/downloaded_data/sites/sites.csv")

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
    return OUTPUT_DIR / Path("site_station_custom/liste_site_et_station_custom.csv")

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
    return OUTPUT_DIR / Path("meteoFrance/departement_id_datagouv/MENS_departement_id_datagouv_historique.csv")

def get_path_campagne_onde() -> Path:
    """
    :return: Le chemin où est stocké toutes les campagnes ONDE
    """
    return OUTPUT_DIR / Path("hubeau/downloaded_data/onde/campagnes_onde.csv")


def get_path_observation_onde(date_debut:datetime, date_fin:datetime, onde_zone:GeographicScaleClip, code_associe:str) -> Path:
    """
    Renvoie le chemin où est stocké la zone géographic des observations ONDE allant de date_debut jusqua date_fin.
    :param date_debut: La date de début des observations
    :param date_fin: La date de fin des observations
    :param onde_zone: La zone géographique associées
    :param code_associe: Le code associé à la zone géographique
    :return: Un chemin vers le fichier correspondant.
    """
    lettre_zone = f"{onde_zone[0]}{code_associe}"

    return OUTPUT_DIR / Path(f"hubeau/downloaded_data/onde/observation_onde_{lettre_zone}_{date_debut.strftime('%Y%m%d')}_{date_fin.strftime('%Y%m%d')}.csv")

def get_path_stations_onde(onde_zone:GeographicScaleClip, code_associe:str) -> Path:
    """
    Renvoie le chemin où est stocké la zone géographic des observations ONDE allant de date_debut jusqua date_fin.
    :param date_debut: La date de début des observations
    :param date_fin: La date de fin des observations
    :param onde_zone: La zone géographique associées
    :param code_associe: Le code associé à la zone géographique
    :return: Un chemin vers le fichier correspondant.
    """
    lettre_zone = f"{onde_zone[0]}{code_associe}"

    return OUTPUT_DIR / Path(f"hubeau/downloaded_data/onde/stations_onde_{lettre_zone}.csv")
