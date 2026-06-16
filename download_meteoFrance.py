from datagouv import Dataset, Resource, Organization
from pathlib import Path
import gzip
import shutil
import utils
import re
import pandas as pd

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

# print(is_departement_dico_complet())
if __name__ == "__main__":
    # download_and_extract_departement(2)
    dico_departement_id = get_dico_departement_id()
    print(is_departement_dico_complet(dico_departement_id))
    for departement_code in departement_list:
        download_and_extract_departement(departement_code, dico_departement_id)
