from cl_hubeau import hydrometry
from pathlib import Path
import os
import utils
import init_project
import download_Hubeau

def ensure_grandeur_historique_downloaded(grandeur:str):
    """
    Garantie que les données historiques pour la grandeur sont téléchargées.
    :param grandeur: La grandeur téléchargée souhaitée
    :return: Rien
    """
    path_grandeur = utils.get_path_historique_raw_csv(grandeur)
    if grandeur != "QmnJ" and utils.is_file_need_download(path_grandeur):
        download_hubeau_1991_2020(grandeur)
    if grandeur == "QmnJ":
        download_Hubeau.ensure_grandeur_mensuel_downloaded("1990-12", "QmnJ")
        download_Hubeau.ensure_grandeur_mensuel_downloaded("2021-01", "QmnJ")
        for annee in range(1991, 2021):
            for mois in range(1,13):
                annee_mois = f"{annee}-{mois}"
                if mois <= 9:
                    annee_mois = f"{annee}-0{mois}"
                download_Hubeau.ensure_grandeur_mensuel_downloaded(annee_mois, "QmnJ")
        print("Données téléchargées avec succès.")


def download_hubeau_1991_2020(grandeur_souhaite):
    """
    Télécharge les observations de 1991 à 2020 de la grandeur souhaite et de toute la france
    :param grandeur_souhaite: La grandeur souhaité à télécharger parmis : HIXM, HIXnJ, QINM, QINnJ, QixM, QIXnJ, QmM ou QmnJ.
    """
    print(f"Téléchargement des données historiques : 1991 à 2020 de la grandeur {grandeur_souhaite}")
    # Permet d'accéder à internet via le réseau interne de la DREAL
    # initialisation du proxy
    utils.set_up_working_proxy()

    # Bounding box grossière du bassin versant Auvergne-Rhône-Alpes
    bounding_box_grossiere = [1.142578, 42.039587, 8.481445, 49.612271]

    # Format de date AAAA-MM-JJ
    date_debut_observation = "1991-01-01"
    date_fin_observation = "2020-12-31"

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

    if grandeur_souhaite == "QmM":
        dataframe_observation = hydrometry.get_observations(
            date_debut_obs_elab=date_debut_observation,
            date_fin_obs_elab=date_fin_observation,
            grandeur_hydro_elab=[grandeur_souhaite],
            bbox=bounding_box_grossiere,
            fields=format_attendu,
        )

        dataframe_observation.to_csv(utils.get_path_historique_raw_csv(grandeur_souhaite), index=False)
    else:
        ensure_grandeur_historique_downloaded("QmnJ")

if __name__ == "__main__":
    ensure_grandeur_historique_downloaded("QmM")
    ensure_grandeur_historique_downloaded("QmnJ")
    #download_hubeau_1991_2020("QmM")