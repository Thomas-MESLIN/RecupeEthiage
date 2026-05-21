import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

output_folder = Path("output")

fichier_hubeau = output_folder / "observations-QmM-france-1991-2020.csv"
colonne_date = "date_obs_elab"

# === LECTURE DES CSV ===
df_hubeau = pd.read_csv(fichier_hubeau)


def get_df_hubeau_period_qmm(date_a_filtrer: str) -> pd.DataFrame:
    """
    Va chercher le fichier des observations qmm dans les fichiers téléchargé.
    Charge les données et prendre uniquement les données correspondantes à la date en paramètre
    :param date_a_filtrer: La date qui servira de filtre au format YYYY-MM-DD
    :return: Renvoie un pd.DataFrame représentant le QmM sur de la date YYYY-MM-DD via l'API Hubeau
    """

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

# TODO Créer fonction pour nettoryer les doublons de hubeau et s'assurer qu'il n'y a pas de trou.

def cleaned_hydroportail_data(annee_mois_a_filtrer: str, sandre_code: str) -> pd.DataFrame:
    """
    Renvoie les données de Hydroportail en copiant les données des sites dans les stations (si la station n'a pas de donnée)
    Puis en enlevant tous les sites.
    :param annee_mois_a_filtrer: Format AAAA-MM
    :param sandre_code: code sandre à filtrer
    :return: Un dataframe panda contenant le csv 'export_hydroportail/{annee_mois_a_filtrer}-{sandre_code}-only-validated-qmm.csv'
    """
    # Récupération df hydroportail
    nom_fichier_hydroportail = f"{annee_mois_a_filtrer}-{sandre_code}-only-validated-qmm.csv"
    if sandre_code == "":
        nom_fichier_hydroportail = f"{annee_mois_a_filtrer}-only-validated-qmm.csv"

    chemin_fichier_hydroportail = output_folder / "exports_hydroportail" / nom_fichier_hydroportail

    df_hydroportail_enregistrement = pd.read_csv(chemin_fichier_hydroportail)

    # Récupérations nom colonne contenant les données de débits.
    nom_colonne_donnee_hydroportail = ""
    possibilite_nom_colonne_donnee_debit = ["Débit (m³/s)", "value"]
    is_nom_colonne_trouve = False
    for nom_colonne in possibilite_nom_colonne_donnee_debit:
        if nom_colonne in df_hydroportail_enregistrement.columns:
            is_nom_colonne_trouve = True
            nom_colonne_donnee_hydroportail = nom_colonne

    if not is_nom_colonne_trouve:
        print("Le nom de la colonne n'a pas été trouvé pour le fichier hydroportail !")
        print(f"nom possible : {possibilite_nom_colonne_donnee_debit}, fichier : {nom_fichier_hydroportail}")
        exit(1)

    # Récupérations nom colonne contenant les code des entités.
    nom_colonne_entite_hydroportail = "Code de l'entité"
    if "code" in df_hydroportail_enregistrement.columns:
        nom_colonne_entite_hydroportail = "code"

    # REMPLISSAGE DES TROUS
    # Avant de filtrer sur la donnée, on veut faire en sorte que :
    # - Si il y a une donnée à la station, on la considère comme référence
    # - Si il n'y a pas de donnée à la station, on prend la donnée du site
    # - Si il n'y a pas de donnée à la station ou au site, on élimine l'enregistrement.

    for idx in range(len(df_hydroportail_enregistrement)):
        df_res = df_hydroportail_enregistrement.loc[idx,[nom_colonne_entite_hydroportail,nom_colonne_donnee_hydroportail]]

        code_entite = str(df_res[nom_colonne_entite_hydroportail])
        donne_entite = df_res[nom_colonne_donnee_hydroportail]

        # On ne regarde que les entites qui sont des stations
        if len(code_entite) <= 8 or not pd.isna(donne_entite):
            continue

        #print(f"On continue la recherche avec {code_entite}-{donne_entite}")

        # On ne choisi que les stations.
        if len(code_entite) == 10:
            code_station_correspondant = code_entite[0:8] # Prend les 8 premier caractère
            # On récupère les noms des stations correspondant
            df_res_query = df_hydroportail_enregistrement[df_hydroportail_enregistrement[nom_colonne_entite_hydroportail] == code_station_correspondant]
            if len(df_res_query) == 0:
                print("Pas de site correspondante")
                continue
            elif len(df_res_query) >= 2:
                print(f"Plusieurs site correspondantes trouvée ?!! {code_entite}")
                exit(1)
            else:
                #print("Site correspondante trouvée")
                donnee_site = df_res_query[nom_colonne_donnee_hydroportail].iloc[0]
                if not pd.isna(donnee_site):
                    # On remplace la donnée inexistante par une donnée existante.
                    df_hydroportail_enregistrement.at[idx, nom_colonne_donnee_hydroportail] = donnee_site
    # A partir de ce moment la, les trous qui pouvaient être remplis ont été remplis
    df_hydroportail_enregistrement.to_csv(Path(f"output/test/res-completion-{sandre_code}-{annee_mois_filtre}.csv"))

    # On veut a présent retirer les entity de type site.
    # TODO cover other file entry
    df_hydroportail_station = df_hydroportail_enregistrement[df_hydroportail_enregistrement["entityType"] == "station"]
    df_hydroportail_station.to_csv(Path(f"output/test/res-only-completed-station-{sandre_code}-{annee_mois_filtre}.csv"))
    #df_hydroportail_enregistrement_with_data = df_hydroportail_enregistrement[
    #    not np.isnan(df_hydroportail_enregistrement[nom_colonne_donnee_hydroportail])
    #    or abs(df_hydroportail_enregistrement[nom_colonne_donnee_hydroportail]) < 0.00001
    #]

    return df_hydroportail_station

def check_is_hubeau_if_site_present_then_station_present_same_data(df_hubeau) -> bool:
    """
    Vérifie que si le site est présent. Celui-ci à toujours le même code qu'une de ses stations
    :param df_hubeau: Le dataFrame des donnée Hubeau
    :return: Renvoie vrai si pour tous site présent, une de ses stations affiche le même résultat.
    """
    # TODO
    return False

def find_difference_hubeau_hydroportail_filtre(sandre_code : str, annee_mois_a_filtrer: str) -> dict:
    """
    Ce code prend un code sandre et une date au format AAAA-MM.
    Il écrit dans la console :
        - Le nombre de stations hubeau apparaissant dans les stations globale mais pas dans les enregistrements hubeau.
        - Le nombre de stations qui apparaissent dans Hubeau mais qui n'apparaissent pas dans Hydroportail
        - Le nombre de stations qui apparaissent dans Hydroportail mais qui n'apparaissent pas dans Hubeau
    :param sandre_code: Le code de la liste sandre à utiliser, peut-être vide.
    :param annee_mois_a_filtrer: L'année et le mois à filtrer au format AAAA-MM
    :param code_sandre: Un code sandre correspondant a une liste de station hydrométrique
    :param date_a_filtre: Une date au format AAAA-MM correspondant à l'année et au mois que l'on souhaite regarder
    Le script à besoin de l'extraction de QmM d'hydroportail avec le nom AAAA-MM-sandre_code-qmm.csv et du fichier
    observations-QmM-france-1991-2020.csv, qui est généré avec le script recuperation-QmM-1991-2020.py.
    :return La liste de stations avec des données uniquement dans hydroportail et la liste de stations avec des données uniquement dans hubeau
    """
    if len(annee_mois_a_filtrer) != 7:
        print("L'année et le mois doivent être au format AAAA-MM")
        return {}
    # On prend le premier jour du mois
    date_a_filtrer = annee_mois_a_filtrer + "-01"

    df_hydroportail_enregistrement = cleaned_hydroportail_data(annee_mois_a_filtrer, sandre_code)

    # Récupérations des enregistrement hydroportail sans données
    colonne_donnee_hydroportail = "Débit (m³/s)"
    if "value" in df_hydroportail_enregistrement.columns:
        colonne_donnee_hydroportail = "value"

    # Tous les enregistrements qui n'ont pas de données.
    df_hydroportail_enregistrement_no_data = df_hydroportail_enregistrement[
        (pd.isna(df_hydroportail_enregistrement[colonne_donnee_hydroportail]))
    ]

    # Tous les enregistrements qui sont à zero.
    df_hydroportail_enregistrement_zero = df_hydroportail_enregistrement[
        abs(df_hydroportail_enregistrement[colonne_donnee_hydroportail]) < 0.001
    ]

    # Récupération des enregistrements Hub'eau
    df_hubeau_record = get_df_hubeau_period_qmm(date_a_filtrer)
    # Récupération de toutes les stations avec le bon code sandre.
    df_stations_hubeau = get_df_stations_hubeau_filtre_code_sandre(sandre_code)
    # Filtre pour avoir toute les stations avec aucune données
    df_hubeau_no_data = df_hubeau_record[pd.isna(df_hubeau_record["resultat_obs_elab"])]
    # Filtre pour avoir toute les station avec zero comme donnée
    df_hubeau_zero = df_hubeau_record[abs(df_hubeau_record["resultat_obs_elab"]) < 0.001]

    # Sauvegarde pour inspection manuelle
    nom_fichier = (date_a_filtrer + "-" + sandre_code + "-qmm.csv")
    if sandre_code == "":
        nom_fichier =  (date_a_filtrer + "-qmm.csv")

    no_data_nom_fichier = nom_fichier.replace(".csv", "-no-data.csv")
    zero_nom_fichier = nom_fichier.replace(".csv", "-zero.csv")

    ficher_sortie_extrait_sandre_hubeau = output_folder / "hubeau" / "validate_data_output"  / nom_fichier
    df_stations_hubeau.to_csv(ficher_sortie_extrait_sandre_hubeau, index=False)
    ficher_sortie_extrait_sandre_hubeau_no_data = output_folder / "hubeau" / "validate_data_output"  / no_data_nom_fichier
    df_hubeau_no_data.to_csv(ficher_sortie_extrait_sandre_hubeau_no_data, index=False)
    ficher_sortie_extrait_sandre_hubeau_zero = output_folder / "hubeau" / "validate_data_output"  / zero_nom_fichier
    df_hubeau_zero.to_csv(ficher_sortie_extrait_sandre_hubeau_zero, index=False)

    ficher_sortie_extrait_sandre_hydroportail = output_folder / "hydroportail" / "validate_data_output"  / nom_fichier
    df_hydroportail_enregistrement.to_csv(ficher_sortie_extrait_sandre_hydroportail, index=False)
    ficher_sortie_extrait_sandre_hydroportail_no_data = output_folder / "hydroportail" / "validate_data_output"  / no_data_nom_fichier
    df_hydroportail_enregistrement_no_data.to_csv(ficher_sortie_extrait_sandre_hydroportail_no_data, index=False)
    ficher_sortie_extrait_sandre_hydroportail_zero = output_folder / "hydroportail" / "validate_data_output"  / zero_nom_fichier
    df_hydroportail_enregistrement_zero.to_csv(ficher_sortie_extrait_sandre_hydroportail_zero, index=False)

    # Récupération de l'ensemble des code de site correspondant à chaque dataFrame
    colonne_code_hubeau = "code_station"
    codes_hubeau_enregistrements = set(df_hubeau_record[colonne_code_hubeau].dropna())
    codes_hubeau_stations = set(df_stations_hubeau[colonne_code_hubeau].dropna())
    codes_hubeau_enregistrements_no_data = set(df_hubeau_no_data[colonne_code_hubeau].dropna())

    colonne_code_hydroportail = "Code de l'entité"
    if "code" in df_hydroportail_enregistrement.columns:
        colonne_code_hydroportail = "code"
    set_codes_hydroportail = set(df_hydroportail_enregistrement[colonne_code_hydroportail].dropna())
    set_codes_hydroportail_no_data = set(df_hydroportail_enregistrement_no_data[colonne_code_hydroportail].dropna())

    # On fais l'intersection de ces deux ensemble
    # code_hubeau_date_correcte_code_filtre = codes_hubeau.intersection(codes_stations_BSH001)
    set_code_hubeau_date_correcte_code_filtre = codes_hubeau_enregistrements.intersection(codes_hubeau_stations)
    set_code_hubeau_date_correcte_code_filtre_no_data = codes_hubeau_enregistrements_no_data.intersection(codes_hubeau_stations)
    # === AFFICHAGE DES RÉSULTATS ===
    #print(f"Résultat de {annee_mois_a_filtrer} de la liste {sandre_code}: ")

    # Station présente dans Hubeau
    set_station_non_presente_enregistrement_hubeau = codes_hubeau_stations - codes_hubeau_enregistrements

    #print("Stations apparaissant dans les liste Sandre des stations Hubeau mais n'apparaissant pas dans les enregistrement : ")
    #print(set_station_non_presente_enregistrement_hubeau)
    #print(len(set_station_non_presente_enregistrement_hubeau))

    # On fais les différences
    uniquement_dans_hubeau = set_code_hubeau_date_correcte_code_filtre - set_codes_hydroportail
    #print(f"\nCodes présents dans hubeau 'observations-QmM-france-1991-2020.csv' mais absents du fichier hydroportail :")
    #print(uniquement_dans_hubeau)
    #print(str(len(uniquement_dans_hubeau)) + "/" + str(len(set_code_hubeau_date_correcte_code_filtre)))
    uniquement_dans_hubeau_et_no_data = uniquement_dans_hubeau.intersection(
        set_code_hubeau_date_correcte_code_filtre_no_data)
    #print(f"Parmis les stations présente uniquement dans Hubeau, il y a {len(uniquement_dans_hubeau_et_no_data)} stations qui n'ont pas de donées.")

    uniquement_dans_hydro = set_codes_hydroportail - set_code_hubeau_date_correcte_code_filtre
    # Station présente dans Hydroportail
    #print(f"\nCodes présents dans le fichier hydroportail mais absents de hubeau 'observations-QmM-france-1991-2020.csv' :")
    #print(uniquement_dans_hydro)
    #print(str(len(uniquement_dans_hydro)) + "/" + str(len(set_codes_hydroportail)))
    uniquement_dans_hydro_et_no_data = uniquement_dans_hydro.intersection(set_codes_hydroportail_no_data)
    #print(f"Parmis les stations présente uniquement dans Hydroportail, il y a {len(uniquement_dans_hydro_et_no_data)} stations qui n'ont pas de données.")

    # On garde uniquement les code qui ont des données.
    set_uniquement_dans_hubeau_with_data = set_code_hubeau_date_correcte_code_filtre - set_code_hubeau_date_correcte_code_filtre_no_data - set_codes_hydroportail
    #print(f"\nCodes présents dans hubeau avec des données 'observations-QmM-france-1991-2020.csv' mais absents du fichier hydroportail :")
    #print(set_uniquement_dans_hubeau_with_data)
    #print(str(len(set_uniquement_dans_hubeau_with_data)) + "/" + str(len(set_code_hubeau_date_correcte_code_filtre)))

    set_uniquement_dans_hydro_with_data = set_codes_hydroportail - set_codes_hydroportail_no_data - set_code_hubeau_date_correcte_code_filtre
    # Station présente dans Hydroportail
    #print(f"\nCodes présents dans le fichier hydroportail avec des données mais absents de hubeau 'observations-QmM-france-1991-2020.csv' :")
    #print(set_uniquement_dans_hydro_with_data)
    #print(str(len(set_uniquement_dans_hydro_with_data)) + "/" + str(len(set_codes_hydroportail)))


    dict_diff = {
        "code_sandre": sandre_code,
        "annee_mois": annee_mois_a_filtrer,
        "station_hubeau_dans_liste_sandre_absente_des_observations": len(set_station_non_presente_enregistrement_hubeau),
        "station_uniquement_hubeau": len(uniquement_dans_hubeau),
        "station_uniquement_hubeau_with_data": len(set_uniquement_dans_hubeau_with_data),
        "station_uniquement_hubeau_et_no_data": len(uniquement_dans_hubeau_et_no_data),
        "total_station_hubeau": len(set_code_hubeau_date_correcte_code_filtre),
        "station_uniquement_hydroportail": len(uniquement_dans_hydro),
        "station_uniquement_hydroportail_with_data": len(set_uniquement_dans_hydro_with_data),
        "station_uniquement_hydroportail_et_no_data": len(uniquement_dans_hydro_et_no_data),
        "total_station_hydroportail": len(set_codes_hydroportail),
        "list_uniquement_hydroportail_with_data" : set_uniquement_dans_hydro_with_data.copy(),
        "list_uniquement_hubeau_with_data": set_uniquement_dans_hubeau_with_data.copy(),
    }
    return dict_diff

# Code Sandre
#sandre_code = "BSH001"

# Date à filtrer (format YYYY-MM-DD)
#date_a_filtrer = "2001-01-01"

total = []
total_iterations = (2007 - 1999) * 12

with tqdm(total=total_iterations, desc="Progression dates") as pbar:

    for annee in range(1999,2021):
        if annee == 2007:
            break
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
            #elt = find_difference_hubeau_hydroportail_filtre("", annee_mois_filtre)
            #total.append(elt)
            #print("\n\n\n---------------------------\n\n\n")
            pbar.update(1)



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
#print(df_resultats.columns)
#print(df_resultats.head())
#print(df_resultats.tail())

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

print("\n\n")
print("Station uniquement dans le BSH001 avec des données")
print("Uniquement dans hubeau puis uniquement dans hydroportail")
print(station_unique_hubeau_BSH001)
print(station_unique_hydroportail_BSH001)

print("\n\n")
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
dataframe_dico.to_csv(Path("output/res-validation/res_station_unique.csv"))

# TODO A séparer en 2 scripts (script nettoyage, script Validation des données initiales, script établissement de stats)
