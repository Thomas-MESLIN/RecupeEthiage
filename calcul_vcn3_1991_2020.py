import datetime
from datetime import timedelta
import calendar
import numpy as np
import pandas as pd
from pathlib import Path
import clean_historic_data
import clean_data
import utils
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
# Effectue la moyenne des moyennes sur toutes la période de 1991 à 2020.

def calcul_vcn3_frequence_retour(annee_mois:str, code_sandre:str):
    """
    :param annee_mois:
    :param code_sandre:
    :return:
    """
    df_mois_actuel_et_precedent = get_df_moyenne_glissante(annee_mois, code_sandre)
    all_stations_code = df_mois_actuel_et_precedent["code_station"].drop_duplicates()
    mois = int(annee_mois[5:7])
    annee = int(annee_mois[0:4])
    rows = []

    path_moyenne_minimum_historique = utils.get_path_vcn3_moyenne_historique(code_sandre)
    df_moyen_minimum_historique = pd.read_csv(path_moyenne_minimum_historique)

    for station_code in all_stations_code:
        minimum_moyenne_glissante = get_vcn3_station_mois(df_mois_actuel_et_precedent, station_code, annee, mois)
        serie_df_min_historique = df_moyen_minimum_historique[
            (df_moyen_minimum_historique["code_station"] == station_code) &
            (df_moyen_minimum_historique["mois"] == mois)
        ]["moyenne_minimum_glissant"]

        valeur_df_min_historique = serie_df_min_historique.iloc[0] if not serie_df_min_historique.empty else pd.NA

        valeur_vcn3 = minimum_moyenne_glissante / valeur_df_min_historique

        row = {
            "code_station": station_code,
            "mois": mois,
            "moyenne_minimum_glissant": minimum_moyenne_glissante,
            "moyenne_minimum_historique": valeur_df_min_historique,
            "vcn3": valeur_vcn3,
            #"frequence":
        }
        rows.append(row)

    df_qmm_moyennes = pd.DataFrame(rows)

    print(df_qmm_moyennes)

    # ==========================================
    # EXPORT CSV
    # ==========================================

    output_file = utils.get_path_vcn3(code_sandre, annee_mois)

    df_qmm_moyennes.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )
    print(f"Calcul Terminée pour {code_sandre}-{annee_mois} : {output_file}")

_cache_qmnj = {}
def get_qmnj(code_sandre:str, date_mois:str) -> pd.DataFrame:
    """
    Renvoie les qmnj à partir des données nettoyés. clean-QmnJ-SANDRE_CODE-AAAA-MM.csv
    :param code_sandre: Code sandre
    :param date_mois: L'annee et le mois au format AAAA-MM
    :return: Renvoie un Dataframe contenant les code des stations et les valeurs observés.
    """
    if code_sandre not in _cache_qmnj:
        _cache_qmnj[code_sandre] = {}
    if date_mois not in _cache_qmnj[code_sandre]:
        chemin_fichier = utils.get_path_clean_csv(code_sandre, date_mois, "QmnJ")
        if not chemin_fichier.exists():
            if utils.is_date_historique(date_mois):
                clean_historic_data.clean_historic_data(code_sandre,"QmnJ")
            else:
                clean_data.clean_single_month(date_mois, code_sandre, "QmnJ")
        df_hubeau = pd.read_csv(chemin_fichier)
        _cache_qmnj[code_sandre][date_mois] = df_hubeau
    return _cache_qmnj[code_sandre][date_mois]

def get_all_stations(code_sandre:str) -> pd.DataFrame:
    """
    Renvoie un DataFrame contenant toute les stations de la période 1991-2020, en ajoutant 1990-12
    De la liste de station avec le code_sandre suivant.
    :param code_sandre: code_sandre
    :return: Un dataframe contenant toute les données au même format que les extractions Hubeau
    """
    all_df = get_qmnj(code_sandre,"1990-12")["code_station"].drop_duplicates()
    for annee in range(1991,2021):
        for mois in range(1,13):
            annee_mois = f"{annee}-{mois}"
            if mois <= 9:
                annee_mois = f"{annee}-0{mois}"

            df = get_qmnj(code_sandre, annee_mois)["code_station"].drop_duplicates()
            all_df = pd.concat([all_df, df], ignore_index=True)
    return all_df.drop_duplicates()

def get_df_moyenne_glissante(annee_mois:str, code_sandre:str):
    """
    Renvoie un Dataframe contenant les données nettoyés du QmnJ du mois actuel et du mois précédent
    :param annee_mois: AAAA-MM
    :param code_sandre: Le code sandre
    :return: Un DataFrame contenant le mois actuel et le mois précédent
    """
    annee = int(annee_mois[0:4])
    mois = int(annee_mois[5:7])
    date_correspondante = datetime.date(year=annee, month=mois, day=1)
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
    datetime_first_day = datetime.date(year=annee, month=mois, day=1)
    _, n_day = calendar.monthrange(annee, mois)

    datetime_first_day_minus_3 = pd.to_datetime(datetime_first_day - datetime.timedelta(days=3))
    datetime_last_day = pd.to_datetime(datetime.date(year=annee, month=mois, day=n_day))

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

def calcule_minimum_glissant_moyen_1991_2020():
    """
    Calcule la moyenne des minimum glissant historique allant de 1991 à 2020.
    Sauvegarde le résultat dans QmnJ_moyennes_{code_sandre}_1991_2020.csv
    """
    code_sandre_a_aggreger = ["BSH001", "BSH101"]

    for code_sandre in code_sandre_a_aggreger:
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

        print(df_qmm_moyennes)

        # ==========================================
        # EXPORT CSV
        # ==========================================

        output_file = utils.get_path_vcn3_moyenne_historique(code_sandre)

        df_qmm_moyennes.to_csv(
            output_file,
            index=False,
            encoding="utf-8"
        )

        print(f"\nCSV sauvegardé : {output_file}")

        # Export des vcn3 mensuel
        for annee in save_vc3_station:
            for mois in save_vc3_station[annee]:
                data_frame = pd.DataFrame(save_vc3_station[annee][mois])
                data_frame.to_csv(utils.get_path_vcn3_mensuel(code_sandre, f"{annee}-{mois}"), index=False)

        print(f"\nCSV vcn mensuel sauvegardé.")


def test():

    print("TESTS MOYENNE GLISSANTE GENTILLE : ")
    print("echantillon : ")
    d = {
        "date_obs_elab" : ["1990-12-30","1990-12-31","1991-01-01","1991-01-02","1991-01-03","1991-01-04"],
        "resultat_obs_elab" : [6,7,1,2,3,4],
        "code_station": ["station1","station1","station1","station1","station1","station1"]
    }
    df = pd.DataFrame(data=d)
    print(df)
    res = get_vcn3_station_mois(df, "station1", 1991, 1)
    print(res)


    print("TESTS MOYENNE GLISSANTE A FILTRER : ")
    print("echantillon : ")
    d3 = {
        "date_obs_elab" : ["1990-12-30","1990-12-31","1990-12-29","1990-12-28","1990-12-27","1990-12-26","1990-12-31","1991-01-01","1991-01-02","1991-01-03","1991-01-04"],
        "resultat_obs_elab" : [6,7,1,2,5,6,7,8,3,4,5],
        "code_station": ["station1","station1","station1","station1","station1","station1","station2","station1","station1","station1","station3"]
    }
    df2 = pd.DataFrame(data=d3)
    print(df2)
    res = get_vcn3_station_mois(df2, "station1", 1991, 1)
    print(res)

    df_qmnj_2025_07 = get_df_moyenne_glissante("2025-07","BSH001")
    res = get_vcn3_station_mois(df_qmnj_2025_07, "U401402001", 2025, 7)
    print(res)
    df_qmnj_2025_08 = get_df_moyenne_glissante("2025-08","BSH001")
    res = get_vcn3_station_mois(df_qmnj_2025_08, "U401402001", 2025, 8)
    print(res)

if __name__ == "__main__":
    calcule_minimum_glissant_moyen_1991_2020()
    calcul_vcn3_frequence_retour("2026-04","BSH001")
    calcul_vcn3_frequence_retour("2025-08","BSH001")
    calcul_vcn3_frequence_retour("2025-07","BSH001")
    calcul_vcn3_frequence_retour("2025-08","BSH101")
    calcul_vcn3_frequence_retour("2025-07","BSH101")
    calcul_vcn3_frequence_retour("2025-05","BSH001")