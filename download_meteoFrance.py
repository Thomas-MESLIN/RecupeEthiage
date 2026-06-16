from datagouv import Dataset, Resource, Organization
from pathlib import Path
import gzip
import shutil
import calendar

import utils
import re
import pandas as pd
from datetime import datetime

# TODO Téléchargerl es données de météofrance d'une manière ou d'une autre
# Pour l'instant on passe par data gouv, mais on pourrait passer dans l'avenir par l'API de météoFrance directement.
# L'api de météoFrance est un peu plus capricieuse malheursement. car il n'u a pas de Python sympathique déjà fait.

# Néanmoins, passer par data gouv semble sympathique et à l'air de pas si mal fonctionner,
# en plus ils indiquent facilement si les données sont à jour ou non,
# On peut donc facilement mettre en cache les données et invalider le cache si besoin.
# Le problème est qu'il va falloir faire la liste exhaustive de tous les couples
# [Département] : [Lien vers le département]
# Car le dataset contient des centaines de fichiers et télécharger ne serait-ce que juste leur métadonnées est trop lent.


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
    ressource = Resource(id_ressource_data_gouv)

    chemin_telechargement = Path(
        f"output/meteoFrance/downloaded_data/mens_historique_archive/MENS_departement_{numero_departement}_historique.csv.gz")
    ressource.download(chemin_telechargement)

    chemin_extrait = Path(f"output/meteoFrance/downloaded_data/mens_historique/MENS_departement_{numero_departement}_historique.csv")

    with gzip.open(chemin_telechargement, "rb") as archive:
        with open(chemin_extrait, "wb") as final:
            shutil.copyfileobj(archive, final)


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


def get_df_decennie_to_id_datagouv():
    chemin_decennie_id = Path("output/meteoFrance/QUOT_decennie_to_id_datagouv.csv")
    df_decennie_to_id = pd.read_csv(chemin_decennie_id)
    return df_decennie_to_id


def get_quot_sim2_data_in_range(date_debut: datetime, date_end: datetime) -> pd.DataFrame:
    """
    Renvoie toutes les données quotidiennes de SIM2 entre la date de début et la date de fin.

    :param date_debut: La date de début de la fenêtre à récupérer
    :param date_end:  La date de fin de la fenêtre à récupérer
    :return: Un dataframe contenant toutes les données quotidiennes de SIM2 entre date_debut et date_fin inclus.
    """
    # Faire une première selection mois par mois.
    # On parcours décénnie par décénnie les données, on récupère les fichiers associés, on fiat une grosse query dessus pour enlever toute ambiguité.
    if date_end < date_debut:
        raise ValueError("La date de fin est plut tot que la date de début !")

    df_decenie_to_id = get_df_decennie_to_id_datagouv()
    dico_decennie_to_id = df_decenie_to_id.to_dict(orient="index")
    file_to_gather = []
    for row in dico_decennie_to_id:
        date_debut_row = datetime.strptime(dico_decennie_to_id[row]["debut_decennie"],"%Y-%m-%d")
        date_fin_row = datetime.strptime(dico_decennie_to_id[row]["fin_decennie"],"%Y-%m-%d")
        id = dico_decennie_to_id[row]["id_ressource_datagouv"]
        if is_date_overlapping(date_debut_row, date_fin_row, date_debut, date_end):
            file_to_gather.append((date_debut_row, date_fin_row, id))

    print(file_to_gather)




def is_date_overlapping(debut_1: datetime, fin_1: datetime, debut_2: datetime, fin_2: datetime):
    return debut_2 <=  debut_1 <= fin_2 or debut_2 <= fin_1 <= fin_2


# print(is_departement_dico_complet())
if __name__ == "__main__":
    # download_and_extract_departement(2)
    # dico_departement_id = get_dico_departement_id()
    # print(is_departement_dico_complet(dico_departement_id))
    # for departement_code in departement_list:
    #     download_and_extract_departement(departement_code, dico_departement_id)
    pass
    #retrieve_sim_quot_decenie_ressource_id()
    res = get_quot_sim2_data_in_range(datetime.strptime("1952-03-25", "%Y-%m-%d"), datetime.strptime("2026-06-14", "%Y-%m-%d"))
    print(res)