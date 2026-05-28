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
    # Permet d'accéder à internet via le réseau interne de la DREAL
    os.environ['http_proxy'] = 'http://pfrie-std.proxy.e2.rie.gouv.fr:8080'
    os.environ['HTTP_PROXY'] = 'http://pfrie-std.proxy.e2.rie.gouv.fr:8080'
    os.environ['https_proxy'] = 'http://pfrie-std.proxy.e2.rie.gouv.fr:8080'
    os.environ['HTTPS_PROXY'] = 'http://pfrie-std.proxy.e2.rie.gouv.fr:8080'

    # dossier vers lequel mettre les résultats
    dest_folder = Path("output/hubeau/downloaded_data/observations_elaboree")

    # Bounding box grossière du bassin versant Auvergne-Rhône-Alpes
    bounding_box_grossiere = [2.307129,42.749916,7.734375,47.279318]

    # Format de date AAAA-MM-JJ
    date_debut_observation = "1991-01-01"
    date_fin_observation = "2020-12-31"

    # Données souhaitées parmi (HIXM, HIXnJ, QINM, QINnJ, QixM, QIXnJ, QmM ou QmnJ)
    grandeur_hydro = [grandeur_souhaite]

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
        grandeur_hydro_elab=grandeur_hydro,
        fields=format_attendu,
    )

    dataframe_observation.to_csv(dest_folder / 'observations-QmM-france-1991-2020.csv')

if __name__ == "__main__":
    download_hubeau_1991_2020("QmnJ")
    download_hubeau_1991_2020("QmM")