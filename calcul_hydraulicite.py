import pandas as pd
import clean
import utils
import logging
# Ce script sert à récupérer les données nettoyée et les exploiter pour calculer l'hydraulicité.
# On a besoin pour cela de l'hydraulicité historique.

def calcul_hydraulicite_mensuel(annee_mois: str, code_sandre: str):
    """
    Calcul l'hydraulicité à partir des données historiques et des données nettoyées
    Le sauvegarde ensuite dans un .csv dans le dossier hydraulicité.
    :param annee_mois: Année et mois de l'hydraulicité souhaité au format AAAA-MM
    :param code_sandre: Code Sandre de la liste à traiter
    """
    # On récupère les données nettoyés historique
    clean.ensure_single_month_cleaned(annee_mois, code_sandre, "QmM")
    chemin_data_du_mois_clean = utils.get_path_clean_csv(code_sandre, annee_mois,"QmM")
    df_mois = pd.DataFrame(pd.read_csv(chemin_data_du_mois_clean))

    # Récupération du QmM moyen historique.
    ensure_QmM_moyen_historic_calculated(code_sandre)
    chemin_qmm_moyen_historic = utils.get_path_qmm_moyen_historique(code_sandre)
    df_qmm_moyen_historique = pd.DataFrame(pd.read_csv(chemin_qmm_moyen_historic))

    mois_a_trouver = int(annee_mois[5:7])
    df_moyenne = df_qmm_moyen_historique[df_qmm_moyen_historique["mois"] == mois_a_trouver]

    # Fusion sur code_station
    df_final = pd.merge(
        df_mois,
        df_moyenne,
        on="code_station",
        how="inner"
    )

    df_final["hydraulicite"] = (
        df_final["resultat_obs_elab"] /
        df_final["QmM_moyenne"]
    )

    chemin_save = utils.get_path_hydraulicite(code_sandre,annee_mois)
    df_final.to_csv(chemin_save, index=False)
    logging.info(f"Fichier sauvegardé dans {chemin_save}.")

def get_qmm(code_sandre:str, date_mois:str) -> pd.DataFrame:
    """
    Renvoie les qmm à partir des données nettoyés. clean-QmM-SANDRE_CODE-AAAA-MM.csv
    :param code_sandre: Code sandre
    :param date_mois: L'annee et le mois au format AAAA-MM
    :return: Renvoie un Dataframe contenant les code des stations et les valeurs observés.
    """
    chemin_fichier = utils.get_path_clean_csv(code_sandre, date_mois, "QmM")
    df_hubeau = pd.DataFrame(pd.read_csv(chemin_fichier))
    return df_hubeau

def get_all_qmm(code_sandre:str) -> pd.DataFrame:
    """
    Renvoie un DataFrame contenant toute les données qmm de la période 1991-2020.
    De la liste de station avec le code_sandre suivant.
    :param code_sandre: code_sandre
    :return: Un dataframe contenant toute les données au même format que les extractions Hubeau
    """
    clean.ensure_historic_cleaned(code_sandre, "QmM")
    all_df = []
    for date in pd.date_range("1991-01-01", "2020-12-01", freq="MS"):
        annee_mois = date.strftime("%Y-%m")
        df = get_qmm(code_sandre, annee_mois)
        all_df.append(df)
    df_concat_all = pd.concat(all_df, ignore_index=True)
    return df_concat_all

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


def calcule_QmM_moyen_historic(code_sandre:str):
    """
    Calcule le QmM moyen historique allant de 1991 à 2020.
    Sauvegarde le résultat dans QmM_moyennes_{code_sandre}_1991_2020.csv
    code_sandre: Le code Sandre de la liste à calculer la moyenne.
    """
    logging.info(f"Calcul du QmM moyen historique - {code_sandre}")
    # On récupère et on aggrège toutes les années.
    df_all_qmm = get_all_qmm(code_sandre)

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


    df_qmm_moyennes = pd.DataFrame(rows)
    logging.debug(df_qmm_moyennes)

    output_file = utils.get_path_qmm_moyen_historique(code_sandre)
    df_qmm_moyennes.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    logging.info(f"\nCSV sauvegardé : {output_file}")

def ensure_QmM_moyen_historic_calculated(code_sandre):
    """
    S'assure que le QmM moyen est calculé et à jour pour ce code Sandre.
    :param code_sandre: Le code Sandre du QmM moyen à calculer
    :return: Rien
    """
    chemin_qmm_moyen_historic = utils.get_path_qmm_moyen_historique(code_sandre)
    chemin_source_qmm_moyen = utils.get_paths_source_historique("QmM")
    if not utils.is_res_updated_with_source(chemin_source_qmm_moyen, chemin_qmm_moyen_historic):
        calcule_QmM_moyen_historic(code_sandre)

if __name__ == "__main__":
    #calcul_hydraulicite_mensuel("2026-04","BSH001")
    #calcul_hydraulicite_mensuel("2026-05","BSH001")
    #calcul_hydraulicite_mensuel("2026-04","custom")
    calcul_hydraulicite_mensuel("2026-05","custom")
    # calcul_hydraulicite_mensuel("2025-11","custom")
