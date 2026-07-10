from datetime import timedelta, datetime
import calendar
import numpy as np
import pandas as pd
import src.processing.clean as clean
import src.utils.utils as utils
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from functools import cache
import logging
import src.utils.utils_file as utils_file
from src.config.logging_config import setup_logger

# Initialiser le logger
logger = setup_logger(name="calcul_vcn3")

# Effectue la moyenne des moyennes sur toutes la période de 1991 à 2020.


@cache
def get_qmnj(code_sandre:str, date_mois:str) -> pd.DataFrame:
    """
    Renvoie les qmnj à partir des données nettoyés. clean-QmnJ-SANDRE_CODE-AAAA-MM.csv
    En cas de données historiques, on suppose qu'un check clean.ensure_data_historic_clean a été fait en amont.
    :param code_sandre: Code sandre
    :param date_mois: L'annee et le mois au format AAAA-MM
    :return: Renvoie un Dataframe contenant les code des stations et les valeurs observés.
    """
    chemin_fichier = utils.get_path_clean_csv(code_sandre, date_mois, "QmnJ")
    if utils.is_date_historique(date_mois):
        clean.ensure_historic_cleaned(code_sandre, "QmnJ")
    else:
        clean.ensure_single_month_cleaned(date_mois, code_sandre, "QmnJ")
    df_hubeau = pd.DataFrame(pd.read_csv(chemin_fichier))
    return df_hubeau

def get_all_stations(code_sandre:str) -> pd.DataFrame:
    """
    Renvoie un DataFrame contenant toute les stations de la période 1991-2020, en ajoutant 1990-12
    De la liste de station avec le code_sandre suivant.
    :param code_sandre: code_sandre
    :return: Un dataframe contenant toute les données au même format que les extractions Hubeau
    """
    logging.info("Récupération du df pour le calcul de tous les VCN3.")
    clean.ensure_historic_cleaned(code_sandre, "QmnJ")
    all_df = []
    for date in pd.date_range("1990-12-01","2020-12-01", freq="MS"):
        annee_mois = date.strftime("%Y-%m")
        logging.debug(f"Récupération des station de {annee_mois} en cours.")
        df = get_qmnj(code_sandre, annee_mois)["code_station"].drop_duplicates()
        all_df.append(df)
    df_all_station = pd.concat(all_df, ignore_index=True)
    logging.info("df de toutes les stations récupéré.")
    return df_all_station.drop_duplicates()

def get_df_moyenne_glissante(annee_mois:str, code_sandre:str):
    """
    Renvoie un Dataframe contenant les données nettoyés du QmnJ du mois actuel et du mois précédent
    :param annee_mois: AAAA-MM
    :param code_sandre: Le code sandre
    :return: Un DataFrame contenant le mois actuel et le mois précédent
    """
    annee = int(annee_mois[0:4])
    mois = int(annee_mois[5:7])
    date_correspondante = datetime(annee, mois, 1)
    mois_precedent = date_correspondante - relativedelta(months=1)
    format_annee_mois_precedent = mois_precedent.strftime("%Y-%m")

    df_qmnj_mois_actuel = get_qmnj(code_sandre, annee_mois)
    df_qmnj_mois_precedent = get_qmnj(code_sandre, format_annee_mois_precedent)
    df_qmnj_all = pd.concat([df_qmnj_mois_precedent,  df_qmnj_mois_actuel], ignore_index=True)
    return df_qmnj_all

def get_vcn3_station_mois(df:pd.DataFrame, station_code: str, annee:int, mois: int):
    """
    Permet de récupérér le QmM moyen sur un mois réparti sur chaque année 1991-2020.
    Le mois et l'année doivent être des entier.
    :param df: Le DataFrame contenant tous les enregistrements nettoyés.
    :param station_code: Le code de la station dont on veut avoir le débit moyen d'un mois aggrégé par année
    :return: Un flottant représentant la moyenne des QmM sur le mois depuis 1991 à 2020.
    """

    # On selectionne les stations qui ont le bon code
    df_station = (df[df["code_station"] == station_code].copy())

    # On convertit les dates en datetime pour pouvoir faire des comparaisons
    df_station["date_obs_elab"] = pd.to_datetime(
        df_station["date_obs_elab"]
    )

    # On ne garde que les données du mois actuel et des 3 jours avant et après.
    datetime_first_day = datetime(annee, mois, 1)
    _, n_day = calendar.monthrange(annee, mois)

    datetime_first_day_minus_3 = pd.to_datetime(datetime_first_day - timedelta(days=3))
    datetime_last_day = pd.to_datetime(datetime(annee, mois, n_day))

    df_station_annee_mois = (df_station[(datetime_first_day_minus_3 < df_station["date_obs_elab"]) &
                                       (df_station["date_obs_elab"] <= datetime_last_day)].copy())
    #print("\nStations et date filtré")
    #print(df_station_annee_mois)
    #df_station_annee_mois.to_csv(Path(f"output/VCN3/test-premiere-filtre-date-station-{annee}-{mois}.csv"))

    # Moyenne glissante sur 3 jours
    df_station_annee_mois.sort_values("date_obs_elab", inplace=True)
    df_fenetre_glissante = df_station_annee_mois.rolling(timedelta(days=3),on="date_obs_elab",min_periods=3)
    #print("\nFenetre glissante : ")
    #print(df_fenetre_glissante)

    # On fait la moyenne sur les fenetres glissante !
    df_station_annee_mois["moyenne_glissante"] = df_fenetre_glissante["resultat_obs_elab"].mean()

    #print("\nMoyenne glissante : ")
    #print(df_station_annee_mois)
    #df_station_annee_mois.to_csv(Path(f"output/VCN3/test-premiere-moyenne-glissante-{annee}-{mois}.csv"))
    # On prend le minimum de ces moyennes
    return df_station_annee_mois["moyenne_glissante"].min()

def calcule_minimum_glissant_moyen_1991_2020(code_sandre:str):
    """
    Calcule la moyenne des minimum glissant historique allant de 1991 à 2020.
    Sauvegarde le résultat dans QmnJ_moyennes_{code_sandre}_1991_2020.csv
    """

    # On récupère et on aggrège toutes les années.
    df_all_stations = get_all_stations(code_sandre)

    # On va faire un gros tableau csv qui contient pour chaques stations, pour chaque mois [1-12]. La moyenne du débit moyen mensuel.
    # En essayant de garder le format des csv Hub'eau de préférence.
    # code_station, date_osb_elab, QmM_moyenne

    # boucle sur chaque station
    save_vc3_station = {}
    rows = []
    # boucle sur les 12 mois
    with tqdm(total=12*len(df_all_stations), desc="Calcul des VCN3 Historique") as pbar:
        for mois in range(1, 13):
            mois_str = f"{mois:02d}"
            for station_code in df_all_stations:
                vcn3_mensuel_1991_2020 = []
                for annee in range(1991,2021):
                    if not annee in save_vc3_station:
                        save_vc3_station[annee] = {}
                    if not mois_str in save_vc3_station[annee]:
                        save_vc3_station[annee][mois_str] = []
                    annee_mois = f"{annee}-{mois_str}"
                    df_mois_actuel = get_df_moyenne_glissante(annee_mois, code_sandre)
                    vcn3_mensuel = get_vcn3_station_mois(df_mois_actuel, station_code, annee, mois)

                    # Sauvegarde du VCN3 mensuel calculé.
                    save_vc3_station[annee][mois_str].append(
                        {
                            "code_station": station_code,
                            "vcn3_mensuel": vcn3_mensuel,
                        }
                    )

                    vcn3_mensuel_1991_2020.append(vcn3_mensuel)

                moyenne_mininmum_glissant = np.mean(vcn3_mensuel_1991_2020)

                row = {
                    "code_station": station_code,
                    "mois": mois_str,
                    "moyenne_minimum_glissant": moyenne_mininmum_glissant
                }

                rows.append(row)
                pbar.update(1)

    # ==========================================
    # DATAFRAME FINAL
    # ==========================================

    df_qmm_moyennes = pd.DataFrame(rows)

    logger.debug(f"DataFrame df_qmm_moyennes :\n{df_qmm_moyennes}")

    # ==========================================
    # EXPORT CSV
    # ==========================================

    output_file = utils.get_path_vcn3_moyenne_historique(code_sandre)

    df_qmm_moyennes.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    logger.info(f"\nCSV sauvegardé : {output_file}")

    # Export des vcn3 mensuel
    for annee in save_vc3_station:
        for mois in save_vc3_station[annee]:
            data_frame = pd.DataFrame(save_vc3_station[annee][mois])
            data_frame.to_csv(utils.get_path_vcn3_mensuel(code_sandre, f"{annee}-{mois}"), index=False)

    logger.info(f"\nCSV vcn mensuel sauvegardé.")

def test():

    logger.info("TESTS MOYENNE GLISSANTE GENTILLE : ")
    logger.info("echantillon : ")
    d = {
        "date_obs_elab" : ["1990-12-30","1990-12-31","1991-01-01","1991-01-02","1991-01-03","1991-01-04"],
        "resultat_obs_elab" : [6,7,1,2,3,4],
        "code_station": ["station1","station1","station1","station1","station1","station1"]
    }
    df = pd.DataFrame(data=d)
    logger.debug(f"DataFrame test 1 :\n{df}")
    res = get_vcn3_station_mois(df, "station1", 1991, 1)
    logger.info(f"Resultat test 1 : {res}")


    logger.info("TESTS MOYENNE GLISSANTE A FILTRER : ")
    logger.info("echantillon : ")
    d3 = {
        "date_obs_elab" : ["1990-12-30","1990-12-31","1990-12-29","1990-12-28","1990-12-27","1990-12-26","1990-12-31","1991-01-01","1991-01-02","1991-01-03","1991-01-04"],
        "resultat_obs_elab" : [6,7,1,2,5,6,7,8,3,4,5],
        "code_station": ["station1","station1","station1","station1","station1","station1","station2","station1","station1","station1","station3"]
    }
    df2 = pd.DataFrame(data=d3)
    logger.debug(f"DataFrame test 2 :\n{df2}")
    res = get_vcn3_station_mois(df2, "station1", 1991, 1)
    logger.info(f"Resultat test 2 : {res}")

    df_qmnj_2025_07 = get_df_moyenne_glissante("2025-07","BSH001")
    res = get_vcn3_station_mois(df_qmnj_2025_07, "U401402001", 2025, 7)
    logger.info(f"Resultat test 3 (2025-07) : {res}")
    df_qmnj_2025_08 = get_df_moyenne_glissante("2025-08","BSH001")
    res = get_vcn3_station_mois(df_qmnj_2025_08, "U401402001", 2025, 8)
    logger.info(f"Resultat test 4 (2025-08) : {res}")

def calcul_vcn3_historique_station(code_station:str, all_df:pd.DataFrame) -> pd.DataFrame:
    """
    Calcul le VCN3 mensuel d'une station et le stocke de manière à pouvoir y accéder en fonction du nom de la station, puisque chaque calcul se déroule station par station.
    Il faut que le dataframe associé contienne les données de la station.
    :param code_station: Le code de la station à calculer
    :param all_df: Le dataframe contenant au moins les données VCN3 de la station.
    :return: Un dataframe contenant les données de la station.
    """
    logger.info("Vérification des données historique...")
    df_station = all_df[all_df["code_station"] == code_station]
    all_rows = []
    for date in pd.date_range("1991-01-01", "2020-12-01", freq="MS"):
        annee_mois = date.strftime("%Y-%m")
        df_annee_mois = df_station[df_station["annee_mois"] == annee_mois]
        row = {
            "code_station" : code_station,
            "annee_mois": annee_mois,
            "vcn3_mensuel" : df_annee_mois["vcn3_mensuel"].iloc[0] if not df_annee_mois.empty else pd.NA,
        }
        all_rows.append(row)
    df_vcn3_station = pd.DataFrame(data=all_rows)
    df_vcn3_station.to_csv(utils.get_path_vcn3_station(code_station), index=False)
    logger.info("Données historiques vérifiées !")
    return df_vcn3_station

@cache
def get_all_df_mensuel(code_sandre:str):
    all_df = []
    for date in pd.date_range("1991-01-01", "2020-12-01", freq="MS"):
        annee_mois = date.strftime("%Y-%m")
        path_mensuel = utils.get_path_vcn3_mensuel(code_sandre, annee_mois)
        if not utils_file.is_res_updated_with_source(utils.get_paths_source_historique("QmnJ"), path_mensuel):
            calcule_minimum_glissant_moyen_1991_2020(code_sandre)
        df_mois = pd.read_csv(path_mensuel)
        df_mois["annee_mois"] = annee_mois
        all_df.append(df_mois)

    df_all_vcn3 = pd.concat(all_df, ignore_index=True)
    return df_all_vcn3.copy()

def ensure_calcul_vcn3_station(code_station:str, code_sandre:str):
    """
    S'asssure que le vcn3 de la station a bien été calculé
    :param code_sandre: Le code sandre dans lequel se trouve la station et qu'un vcn3 a été calculé.
    :param code_station: Le code de la station à calculer
    :return: Rien
    """
    path_vcn3_station = utils.get_path_vcn3_station(code_station)
    if not utils_file.is_res_updated_with_source(utils.get_paths_source_historique("QmnJ"), path_vcn3_station):
        df_all_vcn3 = get_all_df_mensuel(code_sandre).copy()
        calcul_vcn3_historique_station(code_station, df_all_vcn3)


def find_vcn3_min(date_debut:datetime,date_fin:datetime, mois_souhaite:int, code_sandre:str,station_code:str) -> tuple[float, datetime]:
    """
    Trouve le VCN3 minimum de la station appartenant au code sandre correspondant, sur la période date-début à date-fin
    :param date_debut:
    :param date_fin:
    :param mois_souhaite:
    :param code_sandre:
    :param station_code:
    :return:
    """
    logger.info("Recherche du vcn3 le plus bas pour la station...")
    val_min = 99999999999
    annee_min = datetime(1900,1,1)
    for date_annee in pd.date_range(date_debut, date_fin, freq="YS"):
        date_anne_mois_correcte = date_annee.replace(month=mois_souhaite)
        if date_anne_mois_correcte < date_debut or date_fin < date_anne_mois_correcte:
            continue
        annee_mois = date_anne_mois_correcte.strftime("%Y-%m")
        valeur = get_vcn3_station_mois(get_df_moyenne_glissante(annee_mois, code_sandre),
                                       station_code, annee=date_anne_mois_correcte.year, mois=date_anne_mois_correcte.month)
        if valeur < val_min:
            annee_min = date_anne_mois_correcte
            val_min = valeur
    logger.info("Recherche du vcn3 le plus bas pour la station terminé.")
    if val_min == 99999999999:
        val_min = pd.NA
        annee_min = pd.NA
    return val_min, annee_min

if __name__ == "__main__":
    #calcule_minimum_glissant_moyen_1991_2020()
    ensure_calcul_vcn3_station("U072401001", "BSH001")
    ensure_calcul_vcn3_station("U072401001", "custom")
