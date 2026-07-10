import src.utils.utils as utils
import pandas as pd
import src.io.download_Hubeau as download_Hubeau
from src.config.paths import DATA_DIR
import src.utils.utils_file as utils_file
from src.config.logging_config import setup_logger

# Initialiser le logger
logger = setup_logger(name="station")

def get_stations(code_sandre:str|None = None, annee_mois_active:str|None=None) -> pd.DataFrame:
    """
    Renvoie toutes les stations associé au code sandre sous forme d'un DataFrame.
    Si on renseigne annee_mois_active, ne renvoie que les stations qui sont actives à ce moment là.

    S'assure que les listes de stations soient à jour.
    :param code_sandre: Le code sandre de ces stations.
    :param annee_mois_active: L'année et le mois actif.
    :return: Un dataframe contenant toute les stations associé au code sandre, étant active à cette date (si date renseignée)
    """
    # On charge toute les stations
    download_Hubeau.ensure_station_downloaded()
    stations_path = utils.get_path_stations()
    df_stations = pd.read_csv(stations_path)
    if code_sandre is None:
        df_stations_sandre = df_stations
    elif code_sandre == "custom":
        ensure_custom_list_up_to_date()
        df_liste_custom = pd.read_csv(utils.get_path_liste_site_station_custom())
        df_code_station = df_liste_custom["code_station"].drop_duplicates()
        df_stations_sandre = df_stations.merge(df_code_station, on="code_station", how="inner")
    else:
        # Filtre les stations pour avoir celle avec le bon code Sandre
        df_stations_sandre = df_stations[df_stations["code_sandre_reseau_station"].astype(str).str.contains(code_sandre)]

    # Si on a renseigné une date, on filtre uniquement les stations ouvertes à cette date là.
    if annee_mois_active is not None:
        # On filtre les stations qui sont ouverte à cette date là
        df_stations_sandre_ouverte = df_stations_sandre[
            ((annee_mois_active < df_stations_sandre["date_fermeture_station"].astype(str)) | (df_stations_sandre["date_fermeture_station"].isna())) &
            (df_stations_sandre["date_ouverture_station"].astype(str) < annee_mois_active)
        ]
    else:
        # Sinon on renvoie toute les stations
        df_stations_sandre_ouverte = df_stations_sandre

    return df_stations_sandre_ouverte

def ensure_custom_list_up_to_date():
    """
    Assure que la liste custom est à jour et correctement généré.
    :return:
    """
    chemin_liste_custom = utils.get_path_liste_site_station_custom()
    if (
        utils_file.is_file_need_download(chemin_liste_custom) or
        not utils_file.is_res_updated_with_source([get_path_liste_station_custom(), get_path_liste_site_custom()] + [utils.get_path_stations()], chemin_liste_custom)
    ):
        clean_custom_input_list()

def get_path_liste_station_custom():
    return DATA_DIR / "liste_station_custom.csv"

def get_path_liste_site_custom():
    return DATA_DIR / "liste_site_custom.csv"

def clean_custom_input_list():
    """
    Remove the duplicates entries from customs list, merge it with the custom site,
    rewrite it.
    Fill the missing stations of every site. Check if sites exist or not.
    If a site have mutiple stations candidate, they are all added.
    To select the station that is added to the site, add it to the 'liste_station_custom.csv'
    :return: Rien
    """
    logger.info("MISE A JOUR DE LA LISTE DE STATION ET SITES CUSTOM.")
    logger.info("=" * 50)
    df_station = pd.read_csv(get_path_liste_station_custom())
    df_site = pd.read_csv(get_path_liste_site_custom())
    df_station_no_duplicate = df_station.drop_duplicates()
    df_site_no_duplicate = df_site.drop_duplicates()

    # Load the huge station list.
    download_Hubeau.ensure_station_downloaded()
    df_all_station = pd.DataFrame(pd.read_csv(utils.get_path_stations()))

    df_station_custom_full = df_station_no_duplicate.merge(df_all_station, on="code_station", how="left")
    df_all_code_site_from_station = df_station_custom_full["code_site"].drop_duplicates().dropna()

    df_all_sites = df_site_no_duplicate.merge(df_all_code_site_from_station, on="code_site", how="outer")
    # df_sites_custom_full = df_site_no_duplicate.merge(df_all_station, on="code_site", how="left")
    logger.info(f"Nombre de nouveaux sites : abs({len(df_site_no_duplicate)} - {len(df_all_sites)}) = {abs(len(df_site_no_duplicate) - len(df_all_sites))}")

    code_site_et_station = df_all_sites.merge(df_station_custom_full, on="code_site", how="outer")
    logger.debug(f"DataFrame code_site_et_station :\n{code_site_et_station}")
    code_site_et_station_uniquement = code_site_et_station[["code_site","code_station"]].sort_values(by="code_site")
    logger.info("Nettoyage terminé")

    logger.info("Sites sans station indiqués dans liste_station_custom.csv")
    code_site_station_manquante = code_site_et_station_uniquement[pd.isna(code_site_et_station_uniquement["code_station"])]
    list_site_station_manquante = code_site_station_manquante["code_site"].drop_duplicates().dropna().to_list()
    logger.info(f"Sites manquants : {list_site_station_manquante}")
    logger.info("Récupération des stations manquantes.")
    df_resultat = find_perfect_station(list_site_station_manquante)

    code_site_et_station_total = pd.concat([df_resultat, code_site_et_station_uniquement], ignore_index=True)
    code_site_et_station_total.sort_values(by="code_site", inplace=True)
    code_site_et_station_total.dropna(subset=["code_station"], inplace=True)
    code_site_et_station_total.to_csv(utils.get_path_liste_site_station_custom(), index=False)
    logger.info("=" * 50)
    logger.info("MISE A JOUR DE LA LISTE DE STATION ET SITES TERMINEE.")


def find_perfect_station(code_site_list:list[str]) -> pd.DataFrame:
    """
    Trouve le code station qui serait le plus probablement associé à ce code site.
    :param code_site_list: Une liste de code site où il faut trouver la station correspondante
    :return: Renvoie un dataframe qui associe a un code_site une station
    """
    download_Hubeau.ensure_station_downloaded()
    download_Hubeau.ensure_sites_downloaded()
    df_all_site = pd.DataFrame(pd.read_csv(utils.get_path_sites()))
    df_all_station = pd.DataFrame(pd.read_csv(utils.get_path_stations()))
    df_all_station = df_all_station[df_all_station["en_service"]]
    nombre_site_inexistant = 0
    nombre_absent = 0
    nombre_unique = 0
    nombre_plusieurs = 0
    list_correspondance = []
    for code_site in code_site_list:
        if len(df_all_site[df_all_site["code_site"] == code_site]) == 0:
            logger.warning(f"Le site n'existe pas. - {code_site}")
            nombre_site_inexistant += 1
            continue
        df_stations_lie = df_all_station[df_all_station["code_site"] == code_site]
        if len(df_stations_lie) == 0:
            nombre_absent += 1
            logger.info(f"Il n'y a aucune station associé. - {code_site}")
        elif len(df_stations_lie) == 1:
            nombre_unique +=1
            code_station = df_stations_lie["code_station"].iloc[0]
            row = {"code_site": code_site, "code_station": code_station}
            list_correspondance.append(row)
            # logger.debug("Il y a exactement une station associé.")
        else:
            nombre_plusieurs += 1
            logger.info(f"Il y a plus d'une station associé. - {code_site}")
            logger.debug(f"Stations disponibles : {df_stations_lie['code_station'].tolist()}")
            for code_station in df_stations_lie["code_station"]:
                row = {"code_site": code_site, "code_station": code_station}
                list_correspondance.append(row)

    logger.info(f"\nNombre site inexistant {nombre_site_inexistant}, \n"
          f"Nombre pas de stations correspondante {nombre_absent}, \n"
          f"Nombre 1 station correspondant {nombre_unique}, \n"
          f"Nombre plusieurs stations correspondantes {nombre_plusieurs}\n")
    df_final = pd.DataFrame(data=list_correspondance)
    return df_final


if __name__ == "__main__":
    res = get_stations("custom", "2026-04")
    logger.info(f"Resultat get_stations :\n{res}")
    logger.debug("miaou")

    clean_custom_input_list()
