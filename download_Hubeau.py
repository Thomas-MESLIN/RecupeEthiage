import pandas as pd
from cl_hubeau import hydrometry
from pathlib import Path
import os
from datetime import datetime
import calendar
import init_project
import utils

# TELECHARGEMENT DONNEES MENSUELLES

def ensure_grandeur_mensuel_downloaded(annee_mois:str, grandeur:str):
    """
    S'assure que le fichier contenant la grandeur mensuel est téléchargé et à jour
    :param annee_mois: AAAA-MM
    :param grandeur: Une grandeur à télécharger
    :return: Rien
    """
    complete_path = utils.get_path_mensuel_raw_csv(annee_mois,grandeur)
    if utils.is_file_need_download(complete_path):
        print(f"Téléchargement du fichier en cours : {complete_path}")
        download_hubeau_AURA_mois(annee_mois,grandeur)
        print(f"Téléchargement du fichier terminé : {complete_path}")


def download_hubeau_AURA_mois(annee_mois : str, grandeur : str):
    """
    Télécharge les observations élaboré via l'api Hubeau dans le dossier output/hubeau/downloaded_data/observations_elaboree.
    :param annee_mois: L'année et le mois à télécharger au format AAAA-MM
    :param grandeur: La grandeur à télécharger parmis -> HIXM, HIXnJ, QINM, QINnJ, QixM, QIXnJ, QmM ou QmnJ
    """
    # initialisation du proxy
    utils.set_up_working_proxy()

    # Bounding box grossière du bassin versant Auvergne-Rhône-Alpes
    bounding_box_grossiere = [1.142578, 42.039587, 8.481445, 49.612271]

    dernier_jour = calendar.monthrange(int(annee_mois[0:4]), int(annee_mois[5:7]))[1]

    date_debut_observation = f"{annee_mois}-01"
    date_fin_observation = f"{annee_mois}-{dernier_jour}"

    print(f"Téléchargement de la période  : {date_debut_observation}->{date_fin_observation}")
    print(f"Téléchargement de la grandeur : {grandeur}")

    grandeur_hydro = [grandeur]

    # Format des données souhaité, pour n'avoir que les bons champs parmi
    # code_site,code_station,date_obs_elab,resultat_obs_elab,date_prod,code_statut,libelle_statut,code_methode,libelle_methode,code_qualification,libelle_qualification,longitude,latitude,grandeur_hydro_elab
    format_attendu = [
        "code_site",
        "code_station",
        "date_obs_elab",
        "resultat_obs_elab",
        "date_prod",
        "libelle_statut",
        "libelle_methode",
        "libelle_qualification",
    ]

    dataframe_observation = hydrometry.get_observations(
        date_debut_obs_elab=date_debut_observation,
        date_fin_obs_elab=date_fin_observation,
        grandeur_hydro_elab=grandeur_hydro,
        bbox=bounding_box_grossiere,
        fields=format_attendu,
    )

    chemin_fichier = utils.get_path_mensuel_raw_csv(annee_mois,grandeur)
    dataframe_observation.to_csv(chemin_fichier)
    print(f"Fichier téléchargé : {chemin_fichier}")


def ensure_grandeur_historique_downloaded(grandeur:str):
    """
    Garantie que les données historiques pour la grandeur sont téléchargées.
    :param grandeur: La grandeur téléchargée souhaitée
    :return: Rien
    """
    path_grandeur = utils.get_path_historique_raw_csv(grandeur)
    if grandeur != "QmnJ" and utils.is_file_need_download(path_grandeur):
        download_hubeau_1991_2020(grandeur)
    if grandeur == "QmnJ":
        for date in pd.date_range("1990-12-01", "2020-12-01", freq="MS"):
            annee_mois = date.strftime("%Y-%m")
            ensure_grandeur_mensuel_downloaded(annee_mois, "QmnJ")


# TELECHARGEMENT DONNEES HISTORIQUE

def download_hubeau_1991_2020(grandeur_souhaite):
    """
    Télécharge les observations de 1991 à 2020 de la grandeur souhaite et de toute la france
    :param grandeur_souhaite: La grandeur souhaité à télécharger parmis : HIXM, HIXnJ, QINM, QINnJ, QixM, QIXnJ, QmM ou QmnJ.
    """
    print(f"Téléchargement des données historiques : 1991 à 2020 de la grandeur {grandeur_souhaite}")
    # Permet d'accéder à internet via le réseau interne de la DREAL
    # initialisation du proxy
    utils.set_up_working_proxy()

    # Bounding box grossière du bassin versant Auvergne-Rhône-Alpes
    bounding_box_grossiere = [1.142578, 42.039587, 8.481445, 49.612271]

    # Format de date AAAA-MM-JJ
    date_debut_observation = "1991-01-01"
    date_fin_observation = "2020-12-31"

    # Format des données souhaité, pour n'avoir que les bons champs parmi
    # code_site,code_station,date_obs_elab,resultat_obs_elab,date_prod,code_statut,libelle_statut,code_methode,libelle_methode,code_qualification,libelle_qualification,longitude,latitude,grandeur_hydro_elab
    format_attendu = [
        "code_site",
        "code_station",
        "date_obs_elab",
        "resultat_obs_elab",
        "date_prod",
        "libelle_statut",
        "libelle_methode",
        "libelle_qualification",
    ]

    if grandeur_souhaite == "QmM":
        dataframe_observation = hydrometry.get_observations(
            date_debut_obs_elab=date_debut_observation,
            date_fin_obs_elab=date_fin_observation,
            grandeur_hydro_elab=[grandeur_souhaite],
            bbox=bounding_box_grossiere,
            fields=format_attendu,
        )

        dataframe_observation.to_csv(utils.get_path_historique_raw_csv(grandeur_souhaite), index=False)
    else:
        ensure_grandeur_historique_downloaded("QmnJ")

# TELECHARGEMENT DONNEES STATIONS ET SITES

def download_stations():
    """
    Télécharge toute les stations de France qui ont existé.
    :return: Rien
    """
    print("Téléchargement des stations.")
    utils.set_up_working_proxy()

    df_all_stations = hydrometry.get_all_stations()
    df_all_stations.to_csv(utils.get_path_stations())
    print(f"Stations téléchargées -> {utils.get_path_stations()}")

def download_sites():
    """
    Télécharges tous les sites de France.
    :return: Rien
    """
    print("Téléchargement des sites.")
    utils.set_up_working_proxy()

    df_all_sites = hydrometry.get_all_sites()
    df_all_sites.to_csv(utils.get_path_sites())
    print(f"Sites téléchargées -> {utils.get_path_sites()}")

def ensure_station_downloaded():
    """
    Assure que toutes les stations sont téléchargés.
    :return: Rien
    """
    chemin = utils.get_path_stations()
    if utils.is_file_need_download(chemin):
        download_stations()

def ensure_sites_downloaded():
    """
    Assure que tous les sites sont téléchargés.
    :return: Rien
    """
    chemin = utils.get_path_sites()
    if utils.is_file_need_download(chemin):
        download_sites()

# Code executé uniquement si on lance ce fichier individuellement, pas si on l'importe à l'aide d'un autre fichier.
if __name__ == "__main__":
    # Données Mensuels
    ensure_grandeur_mensuel_downloaded("2025-06","QmnJ")
    ensure_grandeur_mensuel_downloaded("2025-07","QmnJ")
    ensure_grandeur_mensuel_downloaded("2025-08","QmnJ")
    # Données Historiques
    ensure_grandeur_historique_downloaded("QmM")
    ensure_grandeur_historique_downloaded("QmnJ")
    # Stations et sites
    ensure_station_downloaded()
    ensure_sites_downloaded()
