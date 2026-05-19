import pandas as pd
import csv
from pathlib import Path

output_folder = Path("output")

def get_df_hubeau_period_qmm(date_a_filtrer: str) -> pd.DataFrame:
    """
    Va chercher le fichier des observations qmm dans les fichiers téléchargé.
    Charge les données et prendre uniquement les données correspondantes à la date en paramètre
    :param date_a_filtrer: La date qui servira de filtre au format YYYY-MM-DD
    :return: Renvoie un pd.DataFrame représentant le QmM sur de la date YYYY-MM-DD via l'API Hubeau
    """
    fichier_hubeau = output_folder / "observations-QmM-france-1991-2020.csv"
    colonne_date = "date_obs_elab"

    # === LECTURE DES CSV ===
    df_hubeau = pd.read_csv(fichier_hubeau)

    # Filtrage pour avoir uniquement les enregistrements aux bonnes dates
    df_hubeau_filtre_date = df_hubeau[df_hubeau[colonne_date] == date_a_filtrer]

    return df_hubeau_filtre_date


def get_df_stations_hubeau_filtre_code_sandre(code_sandre: str) -> pd.DataFrame:
    """
    Renvoie un dataFrame correspondant à toutes les stations Hubeau filtré par leur code sandre
    :param code_sandre: Un code Sandre correspondant aux listes de stations Hydrométriques
    :return: Renvoie un pd.DataFrame correspondant à toutes les stations Hubeau appartennant à la liste du même code_sandre
    """
    fichier_station_hubeau = output_folder / "stations.csv"

    # Lecture des stations hubeau
    df_stations_hubeau = pd.read_csv(fichier_station_hubeau)

    # Filtrage pour avoir uniquement les stations du code SANDRE correspondant
    colonne_code_sandre = "code_sandre_reseau_station"
    df_stations_hubeau_filtre_code_sandre = df_stations_hubeau[
        df_stations_hubeau[colonne_code_sandre].astype(str).str.contains(code_sandre, na=False)
    ]
    return df_stations_hubeau_filtre_code_sandre


def find_difference_hubeau_hydroportail_filtre(sandre_code : str, annee_mois_a_filtrer: str) -> dict:
    """
    Ce code prend un code sandre et une date au format AAAA-MM.
    Il écrit dans la console :
        - Le nombre de stations hubeau apparaissant dans les stations globale mais pas dans les enregistrements hubeau.
        - Le nombre de stations qui apparaissent dans Hubeau mais qui n'apparaissent pas dans Hydroportail
        - Le nombre de stations qui apparaissent dans Hydroportail mais qui n'apparaissent pas dans Hubeau
    :param code_sandre: Un code sandre correspondant a une liste de station hydrométrique
    :param date_a_filtre: Une date au format AAAA-MM correspondant à l'année et au mois que l'on souhaite regarder
    Le script à besoin de l'extraction de QmM d'hydroportail avec le nom AAAA-MM-sandre_code-qmm.csv et du fichier
    observations-QmM-france-1991-2020.csv, qui est généré avec le script recuperation-QmM-1991-2020.py.
    :return
    """
    if len(annee_mois_a_filtrer) != 7:
        print("L'année et le mois doivent être au format AAAA-MM")
        return {}
    # On prend le premier jour du mois
    date_a_filtrer = annee_mois_a_filtrer + "-01"

    #print("annee mois correspondant :" + annee_mois_a_filtrer)

    # Récupération df hydroportail
    nom_fichier_hydroportail = f"{annee_mois_a_filtrer}-{sandre_code}-only-validated-qmm.csv"
    fichier_hydroportail = output_folder / "hydroportail" / nom_fichier_hydroportail

    df_hydroportail_enregistrement = pd.read_csv(fichier_hydroportail)

    df_hubeau_record = get_df_hubeau_period_qmm(date_a_filtrer)
    df_stations_hubeau = get_df_stations_hubeau_filtre_code_sandre(sandre_code)

    # Sauvegarde pour inspection manuelle
    ficher_sortie_extrait_sandre_hubeau = output_folder / "hubeau" / (date_a_filtrer + "-" + sandre_code + "-qmm.csv")
    df_stations_hubeau.to_csv(ficher_sortie_extrait_sandre_hubeau, index=False)


    # Récupération de l'ensemble des code de site correspondant à chaque dataFrame
    colonne_code_hubeau = "code_site"
    codes_hubeau_enregistrements = set(df_hubeau_record[colonne_code_hubeau].dropna())
    codes_hubeau_stations = set(df_stations_hubeau[colonne_code_hubeau].dropna())

    colonne_code_hydroportail = "Code de l'entité"
    codes_hydroportail = set(df_hydroportail_enregistrement[colonne_code_hydroportail].dropna())

    # On fais l'intersection de ces deux ensemble
    # code_hubeau_date_correcte_code_filtre = codes_hubeau.intersection(codes_stations_BSH001)
    code_hubeau_date_correcte_code_filtre = codes_hubeau_enregistrements.intersection(codes_hubeau_stations)

    station_non_presente_enregistrement_hubeau = codes_hubeau_stations - codes_hubeau_enregistrements
    print("Stations apparaissant dans les liste Sandre des stations Hubeau mais n'apparaissant pas dans les enregistrement : ")
    print(station_non_presente_enregistrement_hubeau)
    print(len(station_non_presente_enregistrement_hubeau))
    # On fais les différences
    uniquement_dans_hubeau = code_hubeau_date_correcte_code_filtre - codes_hydroportail
    uniquement_dans_hydro = codes_hydroportail - code_hubeau_date_correcte_code_filtre

    # === AFFICHAGE DES RÉSULTATS ===
    print(f"\nCodes présents dans 'observations-QmM-france-1991-2020.csv' mais absents du fichier hydroportail :")
    print(uniquement_dans_hubeau)
    print(str(len(uniquement_dans_hubeau)) + "/" + str(len(code_hubeau_date_correcte_code_filtre)))

    print(f"\nCodes présents dans le fichier hydroportail mais absents de 'observations-QmM-france-1991-2020.csv' :")
    print(uniquement_dans_hydro)
    print(str(len(uniquement_dans_hydro)) + "/" + str(len(codes_hydroportail)))
    dict_diff = {
        "code_sandre": sandre_code,
        "annee_mois": annee_mois_a_filtrer,
        "station_hubeau_absente": len(station_non_presente_enregistrement_hubeau),
        "station_uniquement_hubeau": len(uniquement_dans_hubeau),
        "station_total_hubeau": len(code_hubeau_date_correcte_code_filtre),
        "station_uniquement_hydroportail": len(uniquement_dans_hydro),
        "station_total_hydroportail": len(codes_hydroportail),
    }
    return dict_diff

# Code Sandre
#sandre_code = "BSH001"

# Date à filtrer (format YYYY-MM-DD)
#date_a_filtrer = "2001-01-01"
#annee_mois_a_filtrer = "2001-01"
total = []
elt = find_difference_hubeau_hydroportail_filtre("BSH001", "2001-01")
total.append(elt)
print("\n\n\n---------------------------\n\n\n")
elt = find_difference_hubeau_hydroportail_filtre("BSH101", "2001-01")
total.append(elt)
print("\n\n\n---------------------------\n\n\n")

file_name = "diff_hydro_hubeau.csv"
path_output_file = output_folder / "res-validation" / file_name

# Conversion liste de dict -> DataFrame
df_resultats = pd.DataFrame(total)

# Export CSV
df_resultats.to_csv(
    path_output_file,
    index=False,
    encoding="utf-8"
)

print(f"CSV écrit : {path_output_file}")
