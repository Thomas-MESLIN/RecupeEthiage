from datagouv import Dataset, Resource, Organization
from pathlib import Path
import gzip
import shutil
import calendar
from functools import cache
import utils
import re
import pandas as pd
import geopandas as gpd
from datetime import datetime, timezone

departement_list = [
    1,
    4,
    5,
    6,
    7,
    9,
    11,
    12,
    13,
    21,
    25,
    26,
    30,
    34,
    38,
    39,
    42,
    43,
    48,
    52,
    66,
    69,
    70,
    71,
    73,
    74,
    81,
    83,
    84,
    88,
    90,
]


def get_dico_departement_id():
    chemin_df = utils.get_path_meteofrance_correspondance_departement_id_datagouv_mens_historique()
    if not chemin_df.exists():
        print("Le Dataframe n'existe pas !")
        retrieve_all_dataset_ressource_id()
    df_departement_id = pd.DataFrame(pd.read_csv(chemin_df))
    dico_df = df_departement_id.to_dict(orient='index')
    dico = {}
    for index_key in dico_df:
        numero_departement = dico_df[index_key]["numero_departement"]
        id_data_gouv = dico_df[index_key]["id_ressource_datagouv"]
        dico[numero_departement] = id_data_gouv
    return dico

def download_and_extract_departement(numero_departement:int, correspondance_departement_id: dict[int,str]):
    # Département au format DD.
    if numero_departement not in correspondance_departement_id:
        raise KeyError("Département ID non disponible !")
    print(f"Téléchargements des données du département : {numero_departement}")
    id_ressource_data_gouv = correspondance_departement_id[numero_departement]

    chemin_telechargement = Path(
        f"output/meteoFrance/downloaded_data/mens_historique_archive/MENS_departement_{numero_departement}_historique.csv.gz")
    chemin_extrait = Path(f"output/meteoFrance/downloaded_data/mens_historique/MENS_departement_{numero_departement}_historique.csv")

    download_and_extract(id_ressource_data_gouv, chemin_telechargement, chemin_extrait)


def retrieve_all_dataset_ressource_id():
    """
    Génère le dictionnaire des département -> ID_datagouv, à partir de la liste des département souhaitées.

    Enregistre toutes les associations département -> ID_datagouv dans un fichier csv.
    :return: Le dictionnaire généré.
    """
    utils.set_up_working_proxy()
    # Dataset contenant toutes les données mensuels météoFrance sur data.gouv.fr
    dataset_complet = Dataset("6569b3d7d193b4daf2b43edc")
    print(f"Dataset: {dataset_complet.title}")
    print(f"Resources: {len(dataset_complet.resources)}")

    # Expression régulière pour reconnaitre uniquement les données mensuelles historiques.
    pattern = re.compile("MENS_departement.*periode_1950-2...")

    tous_les_couples = []
    arr_lien = {}
    for res in dataset_complet.resources:
        titre_ressource = res.title
        if pattern.match(titre_ressource):
            print("Matching titre pattern : ")
            print(titre_ressource)
            numero_departement = titre_ressource.split("_")[2]
            print(numero_departement)

            arr_lien[numero_departement] = res.id
            tous_les_couples.append(
                {
                    "numero_departement": int(numero_departement),
                    "id_ressource_datagouv": res.id,
                }
            )

    print(arr_lien)
    print("{")
    for k in arr_lien:
        print(f"    {k}: {arr_lien[k]},")
    print("}")

    df_departement_id = pd.DataFrame(data=tous_les_couples)
    chemin_departement_id = utils.get_path_meteofrance_correspondance_departement_id_datagouv_mens_historique()
    df_departement_id.to_csv(chemin_departement_id, index=False)
    return arr_lien


def is_departement_dico_complet(dico_departement_id_datagouv: dict[int, str]) -> bool:
    """
    Vérifie que le dictionnaire département -> id_data_gouv correspond à la liste de département souhaité.
    :return: True si les départements à télécharger sont tous présent et qu'il n'y a pas de département en trop.
    """
    cle_departement_telecharge = set([int(k) for k in dico_departement_id_datagouv.keys()])
    cle_departement_souhaite = set(departement_list)
    cle_dans_les_deux = cle_departement_telecharge & cle_departement_souhaite
    cle_souhaite_pas_telecharge = cle_departement_souhaite - cle_dans_les_deux
    if len(cle_souhaite_pas_telecharge) != 0:
        print("Clé souhaite qui n'ont pas été téléchargé : ")
        print(cle_souhaite_pas_telecharge)
        return False
    return True


def convert_chaine_to_date(chaine:str, is_start:bool) -> datetime:
    """
    Convertis un chaine de caractere en une datetime
    :param chaine: La chaine de caractere a convertir
    :param is_start: Si on veut le début du mois/année, mettre à True, si on veut la fin du mois, mettre à False
    :return:
    """
    if is_start:
        default_month = 1
        default_day = 1
    else:
        default_month = 12
        default_day = 31

    if len(chaine) == 4:
        return datetime(year=int(chaine), month=default_month, day=default_day)
    elif len(chaine) == 6:
        annee = int(chaine[0:4])
        mois = int(chaine[4:6])
        if not is_start:
            default_day = calendar.monthrange(annee, mois)[1]
        return datetime(year=int(chaine[0:4]), month=int(chaine[4:6]), day=default_day)
    else:
        return datetime.strptime(chaine, "%Y%m%d")


def retrieve_sim_quot_decenie_ressource_id():
    """
    Va récupérer à partir de l'id du dataset donnees-changement-climatique-sim-quotidienne
    Tous les id des décénies de chaque ressources associé.
    :return: Rien.
    """
    id_dataset_quot_sim = "6569b27598256cc583c917a7"
    utils.set_up_working_proxy()
    # Dataset contenant toutes les données mensuels météoFrance sur data.gouv.fr
    dataset_complet = Dataset(id_dataset_quot_sim)
    # Expression régulière pour reconnaitre uniquement les données mensuelles historiques.
    pattern = re.compile("QUOT_SIM2_....-....")

    tous_les_couples = []
    for res in dataset_complet.resources:
        titre_ressource = res.title
        if pattern.match(titre_ressource):
            print("Matching titre pattern : ")
            print(titre_ressource)
            debut_fin_decenie = titre_ressource.split("_")[-1]
            date_debut = debut_fin_decenie.split("-")[0]
            date_fin = debut_fin_decenie.split("-")[1]
            tous_les_couples.append(
                {
                    "debut_decennie": convert_chaine_to_date(date_debut, True),
                    "fin_decennie": convert_chaine_to_date(date_fin, False),
                    "id_ressource_datagouv": res.id,
                }
            )

    df_decennie_id = pd.DataFrame(data=tous_les_couples)
    chemin_decennie_id = Path("output/meteoFrance/QUOT_decennie_to_id_datagouv.csv")
    df_decennie_id.to_csv(chemin_decennie_id, index=False)


def get_quot_df_decennie_to_id_datagouv():
    chemin_decennie_id = Path("output/meteoFrance/QUOT_decennie_to_id_datagouv.csv")
    df_decennie_to_id = pd.read_csv(chemin_decennie_id)
    return df_decennie_to_id

def update_quot_decennie_to_id_datagouv():
    """
    Met a jour l'index décenie -> id datagouv.
    Supprime les fichiers qui n'apparaissent plus dedans.
    :return: Rien
    """
    old_df_decennie_to_id_datagouv = get_quot_df_decennie_to_id_datagouv()
    # Télécharger le nouveau
    retrieve_sim_quot_decenie_ressource_id()
    new_df_decennie_to_id_datagouv = get_quot_df_decennie_to_id_datagouv()
    # On cherche les différences entre les deux df.
    df_difference = pd.concat([old_df_decennie_to_id_datagouv,new_df_decennie_to_id_datagouv]).drop_duplicates(keep=False)
    if df_difference.empty:
        print("Pas de différence entre les dataframe")
    else:
        print("Des choses on changé !")
        print(df_difference)

def get_quot_sim2_data_in_range(date_debut: datetime, date_end: datetime) -> pd.DataFrame:
    """
    Renvoie toutes les données quotidiennes de SIM2 entre la date de début et la date de fin.

    :param date_debut: La date de début de la fenêtre à récupérer
    :param date_end:  La date de fin de la fenêtre à récupérer
    :return: Un dataframe contenant toutes les données quotidiennes de SIM2 entre date_debut et date_fin inclus.
    """
    if date_end < date_debut:
        raise ValueError("La date de fin est plut tot que la date de début !")

    df_decenie_to_id = get_quot_df_decennie_to_id_datagouv()
    dico_decennie_to_id = df_decenie_to_id.to_dict(orient="index")
    file_to_gather = []
    # On parcours les décénnies connues et on les sauvegardes.
    for row in dico_decennie_to_id:
        # On récupère les données du dictionnaire.
        date_debut_row = datetime.strptime(dico_decennie_to_id[row]["debut_decennie"],"%Y-%m-%d")
        date_fin_row = datetime.strptime(dico_decennie_to_id[row]["fin_decennie"],"%Y-%m-%d")
        id = dico_decennie_to_id[row]["id_ressource_datagouv"]
        # Si la date correspond à notre intervalle d'extraction, on la récupère.
        if is_date_overlapping(date_debut_row, date_fin_row, date_debut, date_end):
            file_to_gather.append((date_debut_row, date_fin_row, id))

    print(file_to_gather)
    print("Loading files...")
    all_df = []
    for date_debut_fichier, date_fin_fichier, id_datagouv in file_to_gather:
        all_df.append(get_df_decennie_quot_sim2(date_debut_fichier, date_fin_fichier, id_datagouv))
    df_complet = pd.concat(all_df, ignore_index=True)
    print("Files loaded successfully...")
    print(df_complet)

    int_date_debut = int(date_debut.strftime("%Y%m%d"))
    int_date_end = int(date_end.strftime("%Y%m%d"))

    # Filtre les df pour qu'ils soient entre la date début et la date fin.
    df_reduit_bonne_date =  df_complet[(int_date_debut <= df_complet["DATE"]) & (df_complet["DATE"] <= int_date_end)]
    return df_reduit_bonne_date

@cache
def get_gouv_ressource(id_gouv_data:str) -> Resource:
    """
    Permet de récupérer les ressources sur data.gouv en gardant en mémoir les requetes déjà faite !
    :param id_gouv_data: L'id à récupérer.
    :return: La ressource correspondante.
    """
    return Resource(id_gouv_data)

def is_path_updated_with_datagouv(chemin_fichier:Path, id_gouv_data:str) -> bool:
    """
    Compare la date de dernière modification du fichier avec la date de dernière modification sur data.gouv
    Si la date de modification du fichier est plus récente que celle de data.gouv on renvoie True, sinon False
    :param chemin_fichier: Le chemin vers le fichier dont il faut comparer la date avec sa source sur data.gouv
    :param id_gouv_data: L'id de data.gouv pour aller chercher la date de dernière modification de la ressource.
    :return: Un booléen, True si le fichier est plus récent que data.gouv, false sinon.
    """
    nb_seconde_depuis_1991_modification = chemin_fichier.stat().st_mtime
    derniere_modification_fichier = datetime.fromtimestamp(nb_seconde_depuis_1991_modification, tz=timezone.utc)
    res = get_gouv_ressource(id_gouv_data)
    derniere_modification_gouv = datetime.fromisoformat(res.last_modified)
    return derniere_modification_gouv <= derniere_modification_fichier

def get_df_decennie_quot_sim2(start_date: datetime,end_date: datetime,id_gouv_data: str) -> pd.DataFrame:
    """
    Renvoie le dataframe contenant toutes les infosd du fichier de cette décénie.
    :param start_date:
    :param end_date:
    :param id_gouv_data:
    :return:
    """
    chemin = Path(f"output/meteoFrance/downloaded_data/quot_sim2/QUOT_SIM2_{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}.csv")
    chemin_archive = Path(f"output/meteoFrance/downloaded_data/quot_sim2_archive/QUOT_SIM2_{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}.csv.gz")
    print(f"Loading : {chemin}")
    if not chemin.exists():
        download_and_extract(id_gouv_data, chemin_archive, chemin)
    elif not is_path_updated_with_datagouv(chemin, id_gouv_data):
        # On met a jour nos indices et on supprimes les fichiers qui n'existent plus.
        # On vérifie que le fichier est à jour par rapport au métadonnées du site.
        download_and_extract(id_gouv_data, chemin_archive, chemin)

    df = pd.read_csv(chemin, delimiter=";")
    return df

def download_and_extract(id_datagouv:str, chemin_archive:Path,chemin_final:Path):
    utils.set_up_working_proxy()
    r = Resource(id_datagouv)
    r.download(chemin_archive)
    with gzip.open(chemin_archive, "rb") as archive:
        with open(chemin_final, "wb") as final:
            shutil.copyfileobj(archive, final)

def is_date_overlapping(debut_1: datetime, fin_1: datetime, debut_2: datetime, fin_2: datetime):
    return debut_2 <=  debut_1 <= fin_2 or debut_2 <= fin_1 <= fin_2 or (debut_1 <= debut_2 and fin_2 <= fin_1)

def plot_geojson_from_lambert2(chemin_a_plot: Path):
    """
    Convertis le fichier pointé vers un fichier geojson dont les coordonnées sont au format EPSG:27572. (lambert2 étendu).
    :param chemin_a_plot: Le chemin vers le fichier csv à convertir en geojson.
    :return: Rien
    """
    if not chemin_a_plot.exists():
        raise ValueError("Le chemin n'existe pas.")

    nom_fichier_sans_extension = chemin_a_plot.stem
    chemin_fichier_converti = Path(f"output/QGIS/meteoFrance/{nom_fichier_sans_extension}.geojson")
    res = pd.read_csv(chemin_a_plot)
    # Les coordonnées sont ne Lambert2 étendue et en hm, on les convertis donc en m.
    gdf = gpd.GeoDataFrame(
        res, geometry=gpd.points_from_xy(res.LAMBX * 100, res.LAMBY * 100), crs="EPSG:27572"
    )

    geojson = gdf.to_json(to_wgs84=False)

    with open(str(chemin_fichier_converti), "w") as f:
        f.write(geojson)


def get_chemin_quot_sim2(debut_decenie:datetime,fin_decenie:datetime,is_archive: bool)->Path:
    """
    Renvoie le chemin vers le fichier contenant les données téléchargé pour la simulation quotidienne.
    :param debut_decenie: AAAA-MM-JJ
    :param fin_decenie: AAAA-MM-JJ
    :param is_archive: Si True, renvoie un .csv.gz, si faut, renvoie un .csv
    :return: Chemin vers le fichier sim2
    """
    if is_archive:
        return Path(f"output/meteoFrance/downloaded_data/quot_sim2_archive/QUOT_SIM2_{debut_decenie.strftime('%Y%m%d')}-{fin_decenie.strftime('%Y%m%d')}.csv.gz")
    else:
        return Path(f"output/meteoFrance/downloaded_data/quot_sim2/QUOT_SIM2_{debut_decenie.strftime('%Y%m%d')}-{fin_decenie.strftime('%Y%m%d')}.csv")

# print(is_departement_dico_complet())
if __name__ == "__main__":
    # annee = 2026
    # mois = 5
    # nombre_de_jour = calendar.monthrange(annee, mois)[1]
    #
    # res = get_quot_sim2_data_in_range(
    #     datetime(year=annee, month=mois, day=1),
    #     datetime(year=annee, month=mois, day=nombre_de_jour))
    # print(res)
    # is_it = is_path_updated_with_datagouv(Path("output\meteoFrance\downloaded_data\quot_sim2\QUOT_SIM2_20200101-20260531.csv"), "92065ec0-ea6f-4f5e-8827-4344179c0a7f")
    # print(is_it)
    # chemin = Path("output/test/df_reduit_quot_sim2_mois_precedent.csv")
    # plot_geojson_from_lambert2(chemin)
    #
    pass

    df_origine = pd.DataFrame({
        "debut_decennie": ["1958-01-01", "1960-01-01", "2020-01-01"],
        "fin_decennie": ["1959-12-31", "1969-12-31", "2026-05-31"],
        "id_ressource_datagouv": ["5dfb33b3-fae5-4d0e-882d-7db74142bcae", "eb0d6e42-cee6-4d7c-bc5b-646be4ced72e", "92065ec0-ea6f-4f5e-8827-4344179c0a7f"],
    })
    df_origine = df_origine.sort_values(by="debut_decennie")
    df_nouveau = pd.DataFrame({
        "debut_decennie": ["1958-01-01", "1960-01-01", "2020-01-01"],
        "fin_decennie": ["1959-12-31", "1969-12-31", "2026-06-31"],
        "id_ressource_datagouv": ["5dfb33b3-fae5-4d0e-882d-7db74142bcae", "eb0d6e42-cee6-4d7c-bc5b-646be4ced72e", "92065ec0-ea6f-4f5e-8827-4344179c0a7f"],
    })
    df_nouveau = df_nouveau.sort_values(by="debut_decennie")

    df_comparison = df_origine.compare(df_nouveau)
    if df_comparison.empty:
        print("Pas de différence entre les dataframe")
    else:
        print("Des choses on changé !")
        print(df_comparison)

    for i in df_comparison.index:
        print(i)
        row_a_supprimer = df_origine.loc[i]
        print(row_a_supprimer)
        date_debut = datetime.strptime(row_a_supprimer["debut_decennie"], "%Y-%m-%d")
        date_fin = datetime.strptime(row_a_supprimer["fin_decennie"], "%Y-%m-%d")
        chemin_a_supprimer_csv = get_chemin_quot_sim2(date_debut, date_fin, False)
        chemin_a_supprimer_gz = get_chemin_quot_sim2(date_debut, date_fin, True)
        print(chemin_a_supprimer_csv)
        print(chemin_a_supprimer_gz)
