import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import utils
from src.config.logging_config import setup_logger
from src.config.paths import OUTPUT_DIR

# Initialiser le logger
logger = setup_logger(name="validate_clean_data")

output_folder = Path("output")
# TODO, reecrire au propre ce fichier...
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
    :param date_a_filtrer: La date qui servira de filtre au format YYYY-MM
    :return: Renvoie un pd.DataFrame représentant le QmM sur de la date YYYY-MM-DD via l'API Hubeau
    """
    # Récupération df hubeau
    chemin_fichier_hubeau = utils.get_path_clean_csv(sandre_code, date_a_filtrer, "QmM")

    df_hubeau = pd.read_csv(chemin_fichier_hubeau)

    return pd.DataFrame(df_hubeau)

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
        logger.error("L'année et le mois doivent être au format AAAA-MM")
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
            elt["annee_mois"] = annee_mois_filtre
            total.append(elt)
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
logger.info(f"CSV écrit : {path_output_file}")

station_unique_hubeau_BSH001 = {}
date_station_unique_hubeau_BSH001 = {}
station_unique_hydroportail_BSH001 = {}
date_station_unique_hydroportail_BSH001 = {}
station_unique_hubeau_BSH101 = {}
date_station_unique_hubeau_BSH101 = {}
station_unique_hydroportail_BSH101 = {}
date_station_unique_hydroportail_BSH101 = {}
for dico_donnee in total:
    list_hydro_data = dico_donnee["list_uniquement_hydroportail_with_data"]
    list_hubeau_data = dico_donnee["list_uniquement_hubeau_with_data"]
    date_mois = dico_donnee["annee_mois"]

    if dico_donnee["code_sandre"] == "BSH001":
        for station_hydro in list_hydro_data:
            if not station_hydro in station_unique_hydroportail_BSH001:
                station_unique_hydroportail_BSH001[station_hydro] = 0
            station_unique_hydroportail_BSH001[station_hydro] += 1
            if not station_hydro in date_station_unique_hydroportail_BSH001:
                date_station_unique_hydroportail_BSH001[station_hydro] = []
            date_station_unique_hydroportail_BSH001[station_hydro].append(date_mois)

        for station_hubeau in list_hubeau_data:
            if not station_hubeau in station_unique_hubeau_BSH001:
                station_unique_hubeau_BSH001[station_hubeau] = 0
            station_unique_hubeau_BSH001[station_hubeau] += 1
            if not station_hubeau in date_station_unique_hubeau_BSH001:
                date_station_unique_hubeau_BSH001[station_hubeau] = []
            date_station_unique_hubeau_BSH001[station_hubeau].append(date_mois)


def convert_anne_mois_list_to_intervalle(list_anne_mois:list[str]) -> list:
    if not list_anne_mois:
        return []
    liste_period = []
    for date in list_anne_mois:
        liste_period.append(pd.Period(date,freq="M"))
    liste_period.sort()
    liste_interval = []
    debut_intervalle = liste_period[0]
    fin_intervalle = liste_period[0]
    for date in liste_period[1:]:
        # Si on continue à avoir une suite continue de date
        if fin_intervalle + 1 == date:
            fin_intervalle = date
        else:
            liste_interval.append(str(debut_intervalle) + "->" + str(fin_intervalle))
            debut_intervalle = date
            fin_intervalle = date
    liste_interval.append(str(debut_intervalle) + "->" + str(fin_intervalle))
    return liste_interval

#logger.debug(convert_anne_mois_list_to_intervalle(['1993-12', '1994-01', '1994-02', '1994-03', '1994-04', '1994-05', '1994-06', '1994-07', '1994-08', '1994-09', '1994-10', '1994-11', '1994-12', '1995-01', '1995-02', '1995-03', '1995-04', '1995-05', '1995-06', '1995-07', '1995-08', '1995-09', '1995-11', '1995-12', '1996-01', '1996-02', '1996-03', '1996-04', '1996-05', '1996-06', '1996-07', '1996-08', '1996-09', '1996-10', '1996-11', '1996-12', '1997-01', '1997-02', '1997-03', '1997-04', '1997-05', '1997-06', '1997-07', '1997-08', '1997-09', '1997-10', '1997-11', '1997-12', '2005-12', '2006-01', '2006-02', '2006-03', '2006-04', '2006-05', '2006-06', '2006-07', '2006-08', '2006-09', '2006-10', '2006-11', '2006-12', '2007-01', '2007-02', '2007-03', '2007-04', '2007-05', '2007-06', '2007-07', '2007-08', '2007-09', '2007-10', '2007-11', '2007-12', '2019-12', '2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06', '2020-07', '2020-08', '2020-10', '2020-11', '2020-12']))

#logger.debug(convert_anne_mois_list_to_intervalle(['1993-12', '1994-01','1994-02','1994-05','1993-11']))

logger.info("\n")
logger.info("Station uniquement dans le BSH001 avec des données")
logger.info("Uniquement dans hubeau puis uniquement dans hydroportail")
logger.info(f"Stations uniques Hubeau BSH001 : {station_unique_hubeau_BSH001}")
#logger.debug(date_station_unique_hubeau_BSH001)
logger.info(f"Stations uniques Hubeau BSH001 (repetition) : {station_unique_hubeau_BSH001}")
#logger.debug(date_station_unique_hydroportail_BSH001)

list_total_station = list(station_unique_hubeau_BSH001.keys()) + list(station_unique_hydroportail_BSH001.keys())
list_total_station_unique = list(set(list_total_station))

list_total_station_unique.sort()

total_list = []
for code_station in list_total_station_unique:
    arr = [
        station_unique_hubeau_BSH001[code_station] if code_station in station_unique_hubeau_BSH001 else None,
        convert_anne_mois_list_to_intervalle(date_station_unique_hubeau_BSH001[code_station]) if code_station in date_station_unique_hubeau_BSH001 else None,
        station_unique_hydroportail_BSH001[code_station] if code_station in station_unique_hydroportail_BSH001 else None,
        convert_anne_mois_list_to_intervalle(date_station_unique_hydroportail_BSH001[code_station]) if code_station in date_station_unique_hydroportail_BSH001 else None,
    ]
    total_list.append(arr)

#logger.debug(total_list)
#logger.debug("\n")

dataframe_dico = pd.DataFrame(
    total_list,
    columns=pd.array([
        'nombre_occurence_unique_hubeau_BSH001',
        'intervalle_apparition_station_unique_hubeau_BSH001',
        'nombre_occurence_unique_hydroportailBSH001',
        'intervalle_apparition_station_unique_hydroportail_BSH001',
    ]),
    index=pd.array(list_total_station_unique)
)

chemin_resultat_difference = OUTPUT_DIR / "res-validation" / "res_station_unique_hubeau_hydroportail_BSH001_BSH101.csv"
dataframe_dico.to_csv(Path(chemin_resultat_difference), index_label="code_station", sep=';')
logger.info(f"\n\nRésultat enregistré dans {chemin_resultat_difference}")

# TODO try to inspect the duplicates.
