import numpy as np
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

def cleaned_hydroportail_data(annee_mois_a_filtrer: str, sandre_code: str) -> pd.DataFrame:
    """"""
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

    # TODO REDUIRE
    # Récupérations nom colonne contenant les code des entités.
    nom_colonne_entite_hydroportail = ""
    possibilite_nom_colonne_donnee_entite = ["Code de l'entité", "code"]
    is_nom_colonne_trouve = False
    for nom_colonne in possibilite_nom_colonne_donnee_entite:
        if nom_colonne in df_hydroportail_enregistrement.columns:
            is_nom_colonne_trouve = True
            nom_colonne_entite_hydroportail = nom_colonne

    if not is_nom_colonne_trouve:
        print("Le nom de la colonne n'a pas été trouvé pour le fichier hydroportail !")
        print(f"nom possible : {possibilite_nom_colonne_donnee_entite}, fichier : {nom_fichier_hydroportail}")
        exit(1)

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
    :return
    """
    if len(annee_mois_a_filtrer) != 7:
        print("L'année et le mois doivent être au format AAAA-MM")
        return {}
    # On prend le premier jour du mois
    date_a_filtrer = annee_mois_a_filtrer + "-01"

    df_hydroportail_enregistrement = cleaned_hydroportail_data(annee_mois_a_filtrer, sandre_code)

    # Récupérations des enregistrement hydroportail sans données
    try:
        colonne_donnee_hydroportail = "Débit (m³/s)"
        df_hydroportail_enregistrement_no_data = df_hydroportail_enregistrement[
            np.isnan(df_hydroportail_enregistrement[colonne_donnee_hydroportail])
            | abs(df_hydroportail_enregistrement[colonne_donnee_hydroportail]) < 0.00001
        ]
    except KeyError:
        colonne_donnee_hydroportail = "value"
        df_hydroportail_enregistrement_no_data = df_hydroportail_enregistrement[
            np.isnan(df_hydroportail_enregistrement[colonne_donnee_hydroportail])
            | abs(df_hydroportail_enregistrement[colonne_donnee_hydroportail]) < 0.00001
        ]

    # Récupération des enregistrements Hub'eau
    df_hubeau_record = get_df_hubeau_period_qmm(date_a_filtrer)
    # Récupération de toutes les stations avec le bon code sandre.
    df_stations_hubeau = get_df_stations_hubeau_filtre_code_sandre(sandre_code)
    # Filtre pour avoir toute les stations avec aucune données
    l = []
    for r in df_hubeau_record["resultat_obs_elab"]:
        obs = r
        #print(obs)
        if obs not in l:
            l.append(obs)
    l.sort()
    #print(l)
    df_hubeau_no_data = df_hubeau_record[np.isnan(df_hubeau_record["resultat_obs_elab"])]

    # Sauvegarde pour inspection manuelle

    nom_fichier = (date_a_filtrer + "-" + sandre_code + "-qmm.csv")
    if sandre_code == "":
        nom_fichier =  (date_a_filtrer + "-qmm.csv")

    ficher_sortie_extrait_sandre_hubeau = output_folder / "hubeau" / nom_fichier
    df_stations_hubeau.to_csv(ficher_sortie_extrait_sandre_hubeau, index=False)

    no_data_nom_fichier = "no-data-" + nom_fichier
    ficher_sortie_extrait_sandre_hubeau_no_data = output_folder / "hubeau" / no_data_nom_fichier
    df_hubeau_no_data.to_csv(ficher_sortie_extrait_sandre_hubeau_no_data, index=False)

    # Récupération de l'ensemble des code de site correspondant à chaque dataFrame
    colonne_code_hubeau = "code_station"
    codes_hubeau_enregistrements = set(df_hubeau_record[colonne_code_hubeau].dropna())
    codes_hubeau_stations = set(df_stations_hubeau[colonne_code_hubeau].dropna())
    codes_hubeau_enregistrements_no_data = set(df_hubeau_no_data[colonne_code_hubeau].dropna())

    try:
        colonne_code_hydroportail = "Code de l'entité"
        set_codes_hydroportail = set(df_hydroportail_enregistrement[colonne_code_hydroportail].dropna())
        set_codes_hydroportail_no_data = set(df_hydroportail_enregistrement_no_data[colonne_code_hydroportail].dropna())
    except KeyError:
        colonne_code_hydroportail = "code"
        set_codes_hydroportail = set(df_hydroportail_enregistrement[colonne_code_hydroportail].dropna())
        set_codes_hydroportail_no_data = set(df_hydroportail_enregistrement_no_data[colonne_code_hydroportail].dropna())

    # On fais l'intersection de ces deux ensemble
    # code_hubeau_date_correcte_code_filtre = codes_hubeau.intersection(codes_stations_BSH001)
    set_code_hubeau_date_correcte_code_filtre = codes_hubeau_enregistrements.intersection(codes_hubeau_stations)
    set_code_hubeau_date_correcte_code_filtre_no_data = codes_hubeau_enregistrements_no_data.intersection(codes_hubeau_stations)
    # === AFFICHAGE DES RÉSULTATS ===
    print(f"Résultat de {annee_mois_a_filtrer} de la liste {sandre_code}: ")

    # Station présente dans Hubeau
    set_station_non_presente_enregistrement_hubeau = codes_hubeau_stations - codes_hubeau_enregistrements

    print("Stations apparaissant dans les liste Sandre des stations Hubeau mais n'apparaissant pas dans les enregistrement : ")
    print(set_station_non_presente_enregistrement_hubeau)
    print(len(set_station_non_presente_enregistrement_hubeau))

    # On fais les différences
    uniquement_dans_hubeau = set_code_hubeau_date_correcte_code_filtre - set_codes_hydroportail
    print(f"\nCodes présents dans hubeau 'observations-QmM-france-1991-2020.csv' mais absents du fichier hydroportail :")
    print(uniquement_dans_hubeau)
    print(str(len(uniquement_dans_hubeau)) + "/" + str(len(set_code_hubeau_date_correcte_code_filtre)))
    uniquement_dans_hubeau_et_no_data = uniquement_dans_hubeau.intersection(set_code_hubeau_date_correcte_code_filtre_no_data)
    print(f"Parmis les stations présente uniquement dans Hubeau, il y a {len(uniquement_dans_hubeau_et_no_data)} stations qui n'ont pas de donées.")

    uniquement_dans_hydro = set_codes_hydroportail - set_code_hubeau_date_correcte_code_filtre
    # Station présente dans Hydroportail
    print(f"\nCodes présents dans le fichier hydroportail mais absents de hubeau 'observations-QmM-france-1991-2020.csv' :")
    print(uniquement_dans_hydro)
    print(str(len(uniquement_dans_hydro)) + "/" + str(len(set_codes_hydroportail)))
    uniquement_dans_hydro_et_no_data = uniquement_dans_hydro.intersection(set_codes_hydroportail_no_data)
    print(f"Parmis les stations présente uniquement dans Hydroportail, il y a {len(uniquement_dans_hydro_et_no_data)} stations qui n'ont pas de données.")

    dict_diff = {
        "code_sandre": sandre_code,
        "annee_mois": annee_mois_a_filtrer,
        "station_hubeau_dans_liste_sandre_absente_des_observations": len(set_station_non_presente_enregistrement_hubeau),
        "station_uniquement_hubeau": len(uniquement_dans_hubeau),
        "station_uniquement_hubeau_et_no_data": len(uniquement_dans_hubeau_et_no_data),
        "total_station_hubeau": len(set_code_hubeau_date_correcte_code_filtre),
        "station_uniquement_hydroportail": len(uniquement_dans_hydro),
        "station_uniquement_hydroportail_et_no_data": len(uniquement_dans_hydro_et_no_data),
        "total_station_hydroportail": len(set_codes_hydroportail),
    }
    return dict_diff

# Code Sandre
#sandre_code = "BSH001"

# Date à filtrer (format YYYY-MM-DD)
#date_a_filtrer = "2001-01-01"

total = []

for annee in range(1999,2021):
    if annee == 2002:
        break
    for mois in range(1,13):
        mois_str = str(mois)
        if mois < 10:
            mois = "0" + str(mois)

        annee_mois_filtre = f"{annee}-{mois}"

        elt = find_difference_hubeau_hydroportail_filtre("BSH001", annee_mois_filtre)
        total.append(elt)
        print("\n\n\n---------------------------\n\n\n")
        elt = find_difference_hubeau_hydroportail_filtre("BSH101", annee_mois_filtre)
        total.append(elt)
        print("\n\n\n---------------------------\n\n\n")
        #elt = find_difference_hubeau_hydroportail_filtre("", annee_mois_filtre)
        #total.append(elt)
        #print("\n\n\n---------------------------\n\n\n")
        #break
    #break

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
print(df_resultats.columns)
print(df_resultats.head())
print(df_resultats.tail())

print(f"CSV écrit : {path_output_file}")
