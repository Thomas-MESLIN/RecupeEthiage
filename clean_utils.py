import pandas as pd
import download_Hubeau_1991_2020
import download_Hubeau
from pathlib import Path
import utils

colonne_date_hubeau = "date_obs_elab"
colonne_code_station_hubeau = "code_station"

_cache = {}
def get_grandeur_historique_df(grandeur:str):
    """
    Renvoie le dataframe correspondant à la grandeur sur la période 1991-2020.
    S'assure que la données est téléchargé, si ce n'est pas le cas, la télécharge.
    :param grandeur: Une grandeur à télécharger
    :return: Une DataFrame des données de 1991 à 2020 sur la grandeur correspondante.
    """
    if grandeur not in _cache:
        print("Reading files...")
        download_Hubeau_1991_2020.ensure_grandeur_historique_downloaded(grandeur)
        if utils.get_path_historique_raw_csv(grandeur).exists():
            _cache[grandeur] = pd.read_csv(utils.get_path_historique_raw_csv(grandeur))
        else:
            # Le fichier des données n'est pas contenu dans un gros document, mais dans plein de petit, on dois tous les lire et les concaténer.
            all_opened_df= []
            download_Hubeau.ensure_grandeur_mensuel_downloaded("1990-12", grandeur)
            all_opened_df.append(pd.read_csv(utils.get_path_mensuel_raw_csv("1990-12", grandeur)))
            for annee in range(1991, 2021):
                for mois in range(1, 13):
                    annee_mois = f"{annee}-{mois}"
                    if mois <= 9:
                        annee_mois = f"{annee}-0{mois}"
                    download_Hubeau.ensure_grandeur_mensuel_downloaded(annee_mois, grandeur)
                    all_opened_df.append(pd.read_csv(utils.get_path_mensuel_raw_csv(annee_mois,grandeur)))
            all_df = pd.concat(all_opened_df, ignore_index=True)
            _cache[grandeur] = all_df
        print("Files Reading Complete")
    return _cache[grandeur]

def clean_hubeau_data(date_a_filtrer: str, code_sandre: str, path_file_to_clean=Path(""), grandeur_a_filtrer="", fichier_station_hubeau="output/hubeau/downloaded_data/stations/stations.csv") -> pd.DataFrame:
    """
    Va chercher le fichier des observations qmm dans les fichiers téléchargé.
    Charge les données et prendre uniquement les données correspondantes à la date en paramètre.
    On nettoie les rangs dupliqué et ceux qui n'ont pas de données.
    :param grandeur_a_filtrer: Une grandeur à filtrer, utile uniquement lorsque l'on souhaite nettoyer des données historiques
    :param path_file_to_clean: Fichier vers le csv à nettoyer
    :param code_sandre: Le code sandre correspondant à la liste de station à extraire
    :param fichier_station_hubeau: Le nom du fichier à ouvrir et nettoyer.
    :param date_a_filtrer: La date qui servira de filtre au format YYYY-MM
    :return: Renvoie un pd.DataFrame représentant la grandeur souhaité sur de la date YYYY-MM-DD via l'API Hubeau
    """

    if path_file_to_clean != Path(""):
        # Delimiteur temportiare
        df_hubeau = pd.read_csv(path_file_to_clean)
    elif grandeur_a_filtrer in utils.GRANDEUR:
        if grandeur_a_filtrer == "QmnJ":
            download_Hubeau.ensure_grandeur_mensuel_downloaded(date_a_filtrer, grandeur_a_filtrer)
            df_hubeau = pd.read_csv(utils.get_path_mensuel_raw_csv(date_a_filtrer, grandeur_a_filtrer))
        else:
            df_hubeau = get_grandeur_historique_df(grandeur_a_filtrer)
    else:
        print("Path à nettoyer vide et grandeur inexistante.")
        raise NameError

    # Filtrage pour avoir uniquement les enregistrements aux bonnes dates tous le bon mois.
    df_hubeau_filtre_date = df_hubeau[df_hubeau[colonne_date_hubeau].astype(str).str.contains(date_a_filtrer)]

    # Ouverture et lecture du fichier des stations hubeau.
    # fichier_station_hubeau = output_folder / "stations.csv"
    df_stations_hubeau = utils.get_stations(code_sandre, date_a_filtrer)
    # df_stations_hubeau = pd.read_csv(fichier_station_hubeau)

    # Filtrage pour avoir uniquement les stations du code SANDRE correspondant
    # colonne_code_sandre = "code_sandre_reseau_station"
    # df_stations_hubeau_filtre_code_sandre = df_stations_hubeau[
    #     df_stations_hubeau[colonne_code_sandre].astype(str).str.contains(code_sandre, na=False)
    # ]

    # Garder uniquement les données qui correspondent au code Sandre.
    df_stations_hubeau_code_sandre = df_hubeau_filtre_date[
        # On garde les colonnes où les données apparaissent dans les station-filtré
        df_hubeau_filtre_date[colonne_code_station_hubeau].isin(
            df_stations_hubeau[colonne_code_station_hubeau]
        )
    ]

    colonne_donnee_hubeau = "resultat_obs_elab"
    # On supprime les stations où il n'y a pas de données.
    #df_stations_hubeau_code_sandre_with_data = df_stations_hubeau_code_sandre[
    #    ~(pd.isna(df_stations_hubeau_code_sandre[colonne_donnee_hubeau]))
    #]

    # On supprime les doublons du DataFrame
    df_code_sandre_with_data_no_duplicate = df_stations_hubeau_code_sandre.drop_duplicates(subset=["code_station","date_obs_elab"])

    return df_code_sandre_with_data_no_duplicate

def clean_hydroportail_data(annee_mois_a_filtrer: str, sandre_code: str) -> pd.DataFrame:
    """
    Renvoie les données de Hydroportail en copiant les données des sites dans les stations (si la station n'a pas de donnée)
    Puis en enlevant tous les sites et les stations qui n'ont pas de données.
    :param annee_mois_a_filtrer: Format AAAA-MM
    :param sandre_code: code sandre à filtrer
    :return: Un dataframe panda contenant le csv 'export_hydroportail/{annee_mois_a_filtrer}-{sandre_code}-only-validated-qmm.csv'
    """
    # Récupération df hydroportail
    nom_fichier_hydroportail = f"{annee_mois_a_filtrer}-{sandre_code}-only-validated-qmm.csv"
    if sandre_code == "":
        nom_fichier_hydroportail = f"{annee_mois_a_filtrer}-only-validated-qmm.csv"

    chemin_fichier_hydroportail = Path("output/hydroportail/downloaded_data") / nom_fichier_hydroportail

    df_hydroportail_enregistrement = pd.read_csv(chemin_fichier_hydroportail)
    # Récupérations nom colonne contenant les données de débits.

    nom_colonne_donnee_hydroportail = "value"
    nom_colonne_code_hydroportail = "code"
    nom_colonne_entite_hydroportail = "entityType"

    # REMPLISSAGE DES TROUSs
    # Avant de filtrer sur la donnée, on veut faire en sorte que :
    # - Si il y a une donnée à la station, on la considère comme référence
    # - Si il n'y a pas de donnée à la station, on prend la donnée du site
    # - Si il n'y a pas de donnée à la station ou au site, on élimine l'enregistrement.

    for idx in range(len(df_hydroportail_enregistrement)):
        df_res = df_hydroportail_enregistrement.loc[idx,[nom_colonne_code_hydroportail,nom_colonne_donnee_hydroportail]]

        code_entite = str(df_res[nom_colonne_code_hydroportail])
        donne_entite = df_res[nom_colonne_donnee_hydroportail]

        # On ne regarde que les entites qui sont des stations
        if len(code_entite) <= 8 or not pd.isna(donne_entite):
            continue

        #print(f"On continue la recherche avec {code_entite}-{donne_entite}")
        # On ne choisi que les stations.
        if len(code_entite) == 10:
            code_station_correspondant = code_entite[0:8] # Prend les 8 premier caractère
            # On récupère les noms des stations correspondant
            df_res_query = df_hydroportail_enregistrement[df_hydroportail_enregistrement[nom_colonne_code_hydroportail] == code_station_correspondant]
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

    # A partir de ce moment la, les trous entre sites et stations correspondant qui pouvaient être remplis ont été remplis.

    # On veut a présent retirer les entity de type stations uniquement.
    df_hydroportail_station = df_hydroportail_enregistrement[df_hydroportail_enregistrement[nom_colonne_entite_hydroportail] == "station"]

    # On veut enlever toutes les entrées où il n'y a pas de donnée.
    df_hydroportail_station_with_data = df_hydroportail_station[~(pd.isna(df_hydroportail_station[nom_colonne_donnee_hydroportail]))]

    return df_hydroportail_station_with_data
