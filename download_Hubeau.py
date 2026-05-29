from cl_hubeau import hydrometry
from pathlib import Path
import os
from datetime import datetime
import calendar
import init_project
import utils

def ensure_grandeur_mensuel_downloaded(annee_mois:str, grandeur:str):
    complete_path = utils.get_path_mensuel_raw_csv(annee_mois,grandeur)
    if not complete_path.exists():
        print(f"Téléchargement du fichier en cours : {complete_path}")
        download_hubeau_france_mois(annee_mois,grandeur)
        print(f"Téléchargement du fichier terminé : {complete_path}")


def download_hubeau_france_mois(annee_mois : str, grandeur : str):
    """
    Télécharge les observations élaboré via l'api Hubeau dans le dossier output/hubeau/downloaded_data/observations_elaboree.
    :param annee_mois: L'année et le mois à télécharger au format AAAA-MM
    :param grandeur: La grandeur à télécharger parmis -> HIXM, HIXnJ, QINM, QINnJ, QixM, QIXnJ, QmM ou QmnJ
    """
    try:
        datetime.strptime(annee_mois, "%Y-%M")
    except ValueError:
        print("Format de annee_mois invalide")
        help(download_hubeau_france_mois)

    # initialisation du proxy
    utils.set_up_working_proxy()

    # Bounding box grossière du bassin versant Auvergne-Rhône-Alpes
    bounding_box_grossiere = [1.142578, 42.039587, 8.481445, 49.612271]

    dernier_jour = calendar.monthrange(int(annee_mois[0:4]), int(annee_mois[5:]))[1]

    date_debut_observation = f"{annee_mois}-01"
    date_fin_observation = f"{annee_mois}-{dernier_jour}"

    print(f"Téléchargement de la période  : {date_debut_observation}->{date_fin_observation}")
    print(f"Téléchargement de la grandeur : {grandeur}")

    # Données souhaitées parmi (HIXM, HIXnJ, QINM, QINnJ, QixM, QIXnJ, QmM ou QmnJ)
    # Vérification de la grandeur souhaitée
    if grandeur not in ["HIXM", "HIXnJ", "QINM", "QINnJ", "QixM", "QIXnJ", "QmM", "QmnJ"]:
        print("Grandeur souhaitée invalide.")
        help(download_hubeau_france_mois)
        raise NameError

    grandeur_hydro = [grandeur]

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
        bbox=bounding_box_grossiere,
        fields=format_attendu,
    )

    chemin_fichier = utils.get_path_mensuel_raw_csv(annee_mois,grandeur)
    dataframe_observation.to_csv(chemin_fichier)
    print(f"Fichier téléchargé : {chemin_fichier}")

# Code executé uniquement si on lance ce fichier individuellement, pas si on l'importe à l'aide d'un autre fichier.
if __name__ == "__main__":
    date_actuelle = datetime.now().strftime("%Y-%m")

    # Format de date AAAA-MM-JJ
    annee_mois_souhaite = "-1"
    while len(annee_mois_souhaite) != 7 and annee_mois_souhaite != "":
        annee_mois_souhaite = input(
            f"Quelle année et mois souhaitez vous télécharger ? (AAAA-MM) (par défaut le mois actuel -> {date_actuelle}): ")
        if len(annee_mois_souhaite) != 7 and annee_mois_souhaite != "":
            print(f"Attention au format ! exemple {date_actuelle}")

    if len(annee_mois_souhaite) == 0:
        annee_mois_souhaite = date_actuelle

    # download_hubeau_france_mois(annee_mois_souhaite,"QmM")
    #download_hubeau_france_mois(annee_mois_souhaite, "QmnJ")
    ensure_grandeur_mensuel_downloaded("2025-06","QmnJ")
    ensure_grandeur_mensuel_downloaded("2025-07","QmnJ")
    ensure_grandeur_mensuel_downloaded("2025-08","QmnJ")

    # TODO, télécharger les autre données.