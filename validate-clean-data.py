import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

output_folder = Path("output")

def get_nom_fichier_import(sandre_code:str, annee_mois_a_filtrer:str) -> str:
    """
    Renvoie le nom du fichier à importer. Le nom est le même pour Hydroportail et Hubeau mais leur position est différente.
    :param sandre_code: Un code sandre
    :param annee_mois_a_filtrer: L'année et le mois au format AAAA-MM
    :return: La chaine de caractère représentant le nom du fichier
    """
    nom_fichier = f"clean-QmM-{sandre_code}-{annee_mois_a_filtrer}.csv"
    if sandre_code == "":
        nom_fichier = f"clean-QmM-{annee_mois_a_filtrer}.csv"
    return nom_fichier

def get_clean_df_hubeau(date_a_filtrer: str, sandre_code: str) -> pd.DataFrame:
    """
    Charge les données nettoyé importé via l'API Hub'Eau
    :param sandre_code: Code sandre correspondant à une liste de station hydroportail
    :param date_a_filtrer: La date qui servira de filtre au format YYYY-MM-DD
    :return: Renvoie un pd.DataFrame représentant le QmM sur de la date YYYY-MM-DD via l'API Hubeau
    """
    # Récupération df hubeau
    nom_fichier_hubeau = get_nom_fichier_import(sandre_code, date_a_filtrer)
    chemin_fichier_hydroportail = output_folder / "hubeau" / "cleaned_data" / nom_fichier_hubeau

    df_hubeau = pd.read_csv(chemin_fichier_hydroportail)

    return df_hubeau

def get_clean_df_hydroportail(annee_mois_a_filtrer: str, sandre_code: str) -> pd.DataFrame:
    """
    Renvoie les données de Hydroportail en copiant les données des sites dans les stations (si la station n'a pas de donnée)
    Puis en enlevant tous les sites.
    :param annee_mois_a_filtrer: Format AAAA-MM
    :param sandre_code: code sandre à filtrer
    :return: Un dataframe panda contenant le csv 'export_hydroportail/{annee_mois_a_filtrer}-{sandre_code}-only-validated-qmm.csv'
    """
    # Récupération df hubeau
    nom_fichier_hydroportail = get_nom_fichier_import(sandre_code, annee_mois_a_filtrer)
    chemin_fichier_hydroportail = output_folder / "hydroportail" / "cleaned_data" / nom_fichier_hydroportail

    df_hydroportail = pd.read_csv(chemin_fichier_hydroportail)

    return df_hydroportail

def find_difference_hubeau_hydroportail_filtre(sandre_code : str, annee_mois_a_filtrer: str) -> dict:
    """
    Ce code prend un code sandre et une date au format AAAA-MM.
    Il écrit dans la console :
        - Le nombre de stations qui apparaissent dans Hubeau mais qui n'apparaissent pas dans Hydroportail
        - Le nombre de stations qui apparaissent dans Hydroportail mais qui n'apparaissent pas dans Hubeau
    :param sandre_code: Le code de la liste sandre à utiliser, peut-être vide.
    :param annee_mois_a_filtrer: L'année et le mois à filtrer au format AAAA-MM
    Le script a besoin des données nettoyé par clean-historic-data.py
    :return La liste de stations avec des données uniquement dans hydroportail et la liste de stations avec des données uniquement dans hubeau
    """
    if len(annee_mois_a_filtrer) != 7:
        print("L'année et le mois doivent être au format AAAA-MM")
        return {}
    # On prend le premier jour du mois
    date_a_filtrer = annee_mois_a_filtrer

    df_hydroportail_enregistrement = get_clean_df_hydroportail(annee_mois_a_filtrer, sandre_code)

    # Récupérations des enregistrement hydroportail sans données
    colonne_donnee_hydroportail = "Débit (m³/s)"
    if "value" in df_hydroportail_enregistrement.columns:
        colonne_donnee_hydroportail = "value"

    # Récupération des enregistrements Hub'eau
    df_hubeau_record = get_clean_df_hubeau(date_a_filtrer, sandre_code)

    # Sauvegarde pour inspection manuelle
    nom_fichier = (date_a_filtrer + "-" + sandre_code + "-qmm.csv")
    if sandre_code == "":
        nom_fichier =  (date_a_filtrer + "-qmm.csv")

    # Récupération de l'ensemble des code de site correspondant à chaque dataFrame
    colonne_code_hubeau = "code_station"
    set_codes_hubeau = set(df_hubeau_record[colonne_code_hubeau])

    colonne_code_hydroportail = "Code de l'entité"
    if "code" in df_hydroportail_enregistrement.columns:
        colonne_code_hydroportail = "code"
    set_codes_hydroportail = set(df_hydroportail_enregistrement[colonne_code_hydroportail])

    # On fais les différences
    # print("\n\nDifférence pour le code sandre : " + sandre_code)
    uniquement_dans_hubeau = set_codes_hubeau - set_codes_hydroportail
    # print(f"\nCodes présents dans hubeau mais absents d'hydroportail :")
    # print(uniquement_dans_hubeau)
    # print(str(len(uniquement_dans_hubeau)) + "/" + str(len(set_codes_hubeau)))

    uniquement_dans_hydro = set_codes_hydroportail - set_codes_hubeau
    # Station présente dans Hydroportail
    # print(f"\nCodes présents dans hydroportail mais absents de hubeau :")
    # print(uniquement_dans_hydro)
    # print(str(len(uniquement_dans_hydro)) + "/" + str(len(set_codes_hydroportail)))

    dict_diff = {
        "code_sandre": sandre_code,
        "annee_mois": annee_mois_a_filtrer,
        "station_uniquement_hubeau": len(uniquement_dans_hubeau),
        "total_station_hubeau": len(set_codes_hubeau),
        "station_uniquement_hydroportail": len(uniquement_dans_hydro),
        "total_station_hydroportail": len(set_codes_hydroportail),
        "list_uniquement_hubeau_with_data":uniquement_dans_hubeau.copy(),
        "list_uniquement_hydroportail_with_data" : uniquement_dans_hydro.copy(),
    }
    return dict_diff

# Code Sandre
#sandre_code = "BSH001"

# Date à filtrer (format YYYY-MM-DD)
#date_a_filtrer = "2001-01-01"

total = []
total_iterations = (2021- 1991) * 12

with tqdm(total=total_iterations, desc="Progression dates") as pbar:
    for annee in range(1991,2021):
        for mois in range(1,13):
            mois_str = str(mois)
            if mois < 10:
                mois = "0" + str(mois)

            annee_mois_filtre = f"{annee}-{mois}"

            elt = find_difference_hubeau_hydroportail_filtre("BSH001", annee_mois_filtre)
            total.append(elt)
            #print("\n\n\n---------------------------\n\n\n")
            elt = find_difference_hubeau_hydroportail_filtre("BSH101", annee_mois_filtre)
            total.append(elt)
            #print("\n\n\n---------------------------\n\n\n")
            pbar.update(1)




file_name = "diff_hydro_hubeau_clean.csv"
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


# TODO Compter en fonction de BSH le nombre d'occurence d'absence de chaque station.
# Est ce que les stations qui n'ont pas de données ne sont jamais la,
# ou est-ce que les stations qui n'ont pas de données en on le reste du temps.
# Voir pourquoi certain stations ne sont pas dans Hubeau alors qu'elles sont dans Hydroportail.
station_unique_hubeau_BSH001 = {}
station_unique_hydroportail_BSH001 = {}
station_unique_hubeau_BSH101 = {}
station_unique_hydroportail_BSH101 = {}
for dico_donnee in total:
    list_hydro_data = dico_donnee["list_uniquement_hydroportail_with_data"]
    list_hubeau_data = dico_donnee["list_uniquement_hubeau_with_data"]
    if dico_donnee["code_sandre"] == "BSH001":
        for station_hydro in list_hydro_data:
            if not station_hydro in station_unique_hydroportail_BSH001:
                station_unique_hydroportail_BSH001[station_hydro] = 0
            station_unique_hydroportail_BSH001[station_hydro] += 1

        for station_hubeau in list_hubeau_data:
            if not station_hubeau in station_unique_hubeau_BSH001:
                station_unique_hubeau_BSH001[station_hubeau] = 0
            station_unique_hubeau_BSH001[station_hubeau] += 1

    if dico_donnee["code_sandre"] == "BSH101":
        for station_hydro in list_hydro_data:
            if not station_hydro in station_unique_hydroportail_BSH101:
                station_unique_hydroportail_BSH101[station_hydro] = 0
            station_unique_hydroportail_BSH101[station_hydro] += 1

        for station_hubeau in list_hubeau_data:
            if not station_hubeau in station_unique_hubeau_BSH101:
                station_unique_hubeau_BSH101[station_hubeau] = 0
            station_unique_hubeau_BSH101[station_hubeau] += 1

print("\n")
print("Station uniquement dans le BSH001 avec des données")
print("Uniquement dans hubeau puis uniquement dans hydroportail")
print(station_unique_hubeau_BSH001)
print(station_unique_hydroportail_BSH001)

print("\n")
print("Station uniquement dans le BSH101 avec des données")
print("Uniquement dans hubeau puis uniquement dans hydroportail")
print(station_unique_hubeau_BSH101)
print(station_unique_hydroportail_BSH101)

list_total_station = list(station_unique_hubeau_BSH001.keys()) + list(station_unique_hubeau_BSH101.keys()) + list(station_unique_hydroportail_BSH001.keys()) + list(station_unique_hydroportail_BSH101.keys())
list_total_station_unique = list(set(list_total_station))

total_list = []
for cle in list_total_station_unique:
    arr = [
        station_unique_hubeau_BSH101[cle] if cle in station_unique_hubeau_BSH101 else None,
        station_unique_hydroportail_BSH101[cle] if cle in station_unique_hydroportail_BSH101 else None,
        station_unique_hubeau_BSH001[cle] if cle in station_unique_hubeau_BSH001 else None,
        station_unique_hydroportail_BSH001[cle] if cle in station_unique_hydroportail_BSH001 else None,
    ]
    total_list.append(arr)

dataframe_dico = pd.DataFrame(np.array(total_list), columns=['hubeau_BSH101', 'hydroportailBSH101', 'hubeau_BSH001', 'hydroportailBSH001'], index=list_total_station_unique)
chemin_resultat_difference = "output/res-validation/res_station_unique.csv"
dataframe_dico.to_csv(Path(chemin_resultat_difference))
print("\n\nRésultat enregistré dans " + chemin_resultat_difference)
# TODO A séparer en 2 scripts (script nettoyage, script Validation des données initiales, script établissement de stats)

# TODO try to inspect the duplicates.
