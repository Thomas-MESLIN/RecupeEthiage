from cl_hubeau import hydrometry
from pathlib import Path
import os
import utils
import init_project


def ensure_grandeur_historique_downloaded(grandeur:str):
    path_grandeur = utils.get_path_historique_raw_csv(grandeur)
    if not path_grandeur.exists():
        download_hubeau_1991_2020(grandeur)

# TODO réduire la taille de la query.
def download_hubeau_1991_2020(grandeur_souhaite):
    """
    Télécharge les observations de 1991 à 2020 de la grandeur souhaite et de toute la france
    :param grandeur_souhaite: La grandeur souhaité à télécharger parmis : HIXM, HIXnJ, QINM, QINnJ, QixM, QIXnJ, QmM ou QmnJ.
    """
    print(f"Téléchargement des données historiques : 1991 à 2020 de la grandeur {grandeur_souhaite}")
    # Permet d'accéder à internet via le réseau interne de la DREAL
    # initialisation du proxy
    utils.set_up_working_proxy()

    # dossier vers lequel mettre les résultats
    dest_folder = Path("output/hubeau/downloaded_data/observations_elaboree")

    # Bounding box grossière du bassin versant Auvergne-Rhône-Alpes
    bounding_box_grossiere = [1.142578, 42.039587, 8.481445, 49.612271]

    # Format de date AAAA-MM-JJ
    date_debut_observation = "1990-12-25"
    date_fin_observation = "2021-01-05"

    # Format des données souhaité, pour n'avoir que les bons champs parmi
    # code_site,code_station,date_obs_elab,resultat_obs_elab,date_prod,code_statut,libelle_statut,code_methode,libelle_methode,code_qualification,libelle_qualification,longitude,latitude,grandeur_hydro_elab
    format_attendu = [
        "code_site",
        "code_station",
        "date_obs_elab",
        "resultat_obs_elab",
        "date_prod",
        "libelle_statut",
        "libelle_methode",
        "libelle_qualification",
    ]

    dataframe_observation = hydrometry.get_observations(
        date_debut_obs_elab=date_debut_observation,
        date_fin_obs_elab=date_fin_observation,
        grandeur_hydro_elab=[grandeur_souhaite],
        bbox=bounding_box_grossiere,
        fields=format_attendu,
    )

    dataframe_observation.to_csv(dest_folder / f'observations-{grandeur_souhaite}-france-1991-2020.csv')

if __name__ == "__main__":
    download_hubeau_1991_2020("QmnJ")
    #download_hubeau_1991_2020("QmM")