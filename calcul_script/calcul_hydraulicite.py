import pandas as pd
from pathlib import Path

# Effectue la moyenne des moyennes sur toutes la période de 1991 à 2020.

def get_qmm(code_sandre:str, date_mois:str) -> pd.DataFrame:
    """
    Renvoie les qmm à partir des données nettoyés.
    :param code_sandre: Code sandre
    :param date_mois: L'annee et le mois au format AAAA-MM
    :return: Renvoie un Dataframe contenant les code des stations et les valeurs observés.
    """
    nom_fichier = f"clean-QmM-{date_mois}.csv"
    if code_sandre != '':
        nom_fichier = f"clean-QmM-{code_sandre}-{date_mois}.csv"

    chemin_fichier = Path(f"../output/hubeau/cleaned_data/{nom_fichier}")

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



df_all_BSH001 = get_all_qmm("BSH001")
print(df_all_BSH001)

# On va faire un gros tableau csv qui ocntient pour chaque stations, pour chaque mois [1-12]. La moyenne du débit moyen mensuel.
# En essayant de garder le format des csv Hub'eau de préférence.
# code_station, date_osb_elab, QmM_moyenne
code_station = "W331501001"
mois = "01"
QmM_moyenne_station_mois = df_all_BSH001[(df_all_BSH001["date_obs_elab"].astype(str).str.contains(f"-{mois}-01")) & (df_all_BSH001["code_station"] == code_station)]
QmM_moyenne_station_mois.to_csv(Path("../output/hubeau/QmM_moyen/test.csv"))

QmM_moyenne_station_mois_aggre = QmM_moyenne_station_mois["resultat_obs_elab"].agg('mean')
print(QmM_moyenne_station_mois_aggre)
