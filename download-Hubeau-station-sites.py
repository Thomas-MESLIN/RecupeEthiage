from cl_hubeau import hydrometry
from pathlib import Path
import utils

# TODO, regarder de quand date les fichiers, si les fichiers sont trop vieux, (>1ans), proposer des les remplacer.

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
    :return:
    """
    chemin = utils.get_path_stations()
    if utils.is_file_need_download(chemin):
        download_stations()

def ensure_sites_downloaded():
    """
    Assure que tous les sites sont téléchargés.
    :return:
    """
    chemin = utils.get_path_sites()
    if utils.is_file_need_download(chemin):
        download_sites()

# Si on lance ce script, on re-télécharge toutes les stations et tous les sites.
if __name__ == "__main__":
    ensure_station_downloaded()
    ensure_sites_downloaded()
