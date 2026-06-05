import pandas as pd
from pathlib import Path
import clean_historic_data
import utils
# Effectue la moyenne des moyennes sur toutes la période de 1991 à 2020.

def get_qmm(code_sandre:str, date_mois:str) -> pd.DataFrame:
    """
    Renvoie les qmm à partir des données nettoyés. clean-QmM-SANDRE_CODE-AAAA-MM.csv
    :param code_sandre: Code sandre
    :param date_mois: L'annee et le mois au format AAAA-MM
    :return: Renvoie un Dataframe contenant les code des stations et les valeurs observés.
    """
    nom_fichier = f"clean-QmM-{date_mois}.csv"
    if code_sandre != '':
        nom_fichier = f"clean-QmM-{code_sandre}-{date_mois}.csv"

    chemin_fichier = Path(f"output/hubeau/cleaned_data/{nom_fichier}")
    if utils.is_file_need_download(chemin_fichier):
        clean_historic_data.clean_historic_data(code_sandre,"QmM")

    df_hubeau = pd.read_csv(chemin_fichier, )

    return df_hubeau

def get_all_qmm(code_sandre:str) -> pd.DataFrame:
    """
    Renvoie un DataFrame contenant toute les données qmm de la période 1991-2020.
    De la liste de station avec le code_sandre suivant.
    :param code_sandre: code_sandre
    :return: Un dataframe contenant toute les données au même format que les extractions Hubeau
    """
    all_df = get_qmm(code_sandre,"1991-01")
    for annee in range(1991,2021):
        for mois in range(1,13):
            annee_mois = f"{annee}-{mois}"
            if mois <= 9:
                annee_mois = f"{annee}-0{mois}"

            if annee_mois == "1991-01":
                continue

            df = get_qmm(code_sandre, annee_mois)
            all_df = pd.concat([all_df, df], ignore_index=True)

    return all_df


def get_QmM_moyenne_station_mois_from_df_all(df_all:pd.DataFrame, station_code: str, mois: str):
    """
    Permet de récupérér le QmM moyen sur un mois réparti sur chaque année 1991-2020.
    Le mois dois être au format MM, allant de 01 à 12.
    :param df_all: Le DataFrame contenant tous les enregistrements nettoyés.
    :param station_code: Le code de la station dont on veut avoir le débit moyen d'un mois aggrégé par année
    :param mois: Le mois auquel on veut extraire la moyenne.
    :return: Un flottant représentant la moyenne des QmM sur le mois depuis 1991 à 2020.
    """
    QmM_moyenne_station_mois = df_all[
        (df_all["date_obs_elab"].astype(str).str.contains(f"-{mois}-01")) &
        (df_all["code_station"] == station_code)]

    QmM_moyenne_station_mois_aggre = QmM_moyenne_station_mois["resultat_obs_elab"].agg('mean')

    return QmM_moyenne_station_mois_aggre

# TODO, faire en sorte que cette fonctione accepte un code SANDRE en paramètre.
def calcule_QmM_moyen_1991_2020(code_sandre:str):
    """
    Calcule le QmM moyen historique allant de 1991 à 2020.
    Sauvegarde le résultat dans QmM_moyennes_{code_sandre}_1991_2020.csv
    code_sandre: Le code Sandre de la liste à calculer la moyenne.
    """

    # On récupère et on aggrège toutes les années.
    df_all_qmm = get_all_qmm(code_sandre)
    # print(df_all_qmm)

    # On va faire un gros tableau csv qui contient pour chaques stations, pour chaque mois [1-12]. La moyenne du débit moyen mensuel.
    # En essayant de garder le format des csv Hub'eau de préférence.
    # code_station, date_osb_elab, QmM_moyenne

    # On prend tous les numéros de stations
    df_all_stations = df_all_qmm["code_station"].drop_duplicates()

    # boucle sur chaque station
    rows = []
    for station_code in df_all_stations:

        # boucle sur les 12 mois
        for mois in range(1, 13):

            mois_str = f"{mois:02d}"

            # calcul moyenne QmM
            qmm_moyenne = get_QmM_moyenne_station_mois_from_df_all(
                df_all=df_all_qmm,
                station_code=station_code,
                mois=mois_str
            )

            row = {
                "code_station": station_code,
                "mois": mois_str,
                "QmM_moyenne": qmm_moyenne
            }

            rows.append(row)

    # ==========================================
    # DATAFRAME FINAL
    # ==========================================

    df_qmm_moyennes = pd.DataFrame(rows)

    print(df_qmm_moyennes)

    # ==========================================
    # EXPORT CSV
    # ==========================================

    output_file = Path(f"output/hubeau/QmM_moyen/QmM_moyennes_{code_sandre}_1991_2020.csv")

    df_qmm_moyennes.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    print(f"\nCSV sauvegardé : {output_file}")
