from datagouv import Dataset, Resource, Organization
from pathlib import Path
import gzip
import shutil

# TODO Téléchargerl es données de météofrance d'une manière ou d'une autre
# Pour l'instant on passe par data gouv, mais on pourrait passer dans l'avenir par l'API de météoFrance directement.
# L'api de météoFrance est un peu plus capricieuse malheursement. car il n'u a pas de Python sympathique déjà fait.

# Néanmoins, passer par data gouv semble sympathique et à l'air de pas si mal fonctionner,
# en plus ils indiquent facilement si les données sont à jour ou non,
# On peut donc facilement mettre en cache les données et invalider le cache si besoin.
# Le problème est qu'il va falloir faire la liste exhaustive de tous les couples
# [Département] : [Lien vers le département]
# Car le dataset contient des centaines de fichiers et télécharger ne serait-ce que juste leur métadonnées est trop lent.

# On instancie la ressource à partie de son ID trouvée dans les métadonnées de
# https://www.data.gouv.fr/datasets/donnees-climatologiques-de-base-mensuelles
ressource = Resource("22bf1eda-7aed-4282-a2a1-b16af691d7a2")

print(ressource.title)
print(ressource.url)  # this is the download URL of the resource
print(ressource.id)  # the id of the resource itself
print(ressource.dataset_id)  # the id of the dataset the resource belongs to
print(ressource)  # this displays all the attributes of the resource as a dict
print("Dernière modification : ")
print(ressource.last_modified)

chemin_archive = Path("output/test/metrofrance_first_test.csv.gz")
chemin_final = Path("output/test/metrofrance_first_test.csv")
ressource.download(chemin_archive)
# On extrait avec la librairie gzip.
with gzip.open(chemin_archive, "rb") as archive:
    with open(chemin_final, "wb") as final:
        shutil.copyfileobj(archive, final)
