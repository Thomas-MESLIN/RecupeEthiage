import pandas as pd
from pathlib import Path
from tqdm import tqdm
import clean_utils
import download_Hubeau_observations
import utils

def clean_single_month(annee_mois, code_sandre, grandeur:str):
    """
    Clean a file containing a single month of data.
    Download it if the file does not exist.
    :param grandeur: La grandeur a récupérer
    :param annee_mois: Année et mois au format AAAA-MM
    :param code_sandre: Code sandre à extraire
    """
    download_Hubeau_observations.ensure_grandeur_mensuel_downloaded(annee_mois, grandeur)
    complete_path = utils.get_path_mensuel_raw_csv(annee_mois, grandeur)
    if not complete_path.exists():
        print(f"Téléchargement du fichier en cours : {complete_path}")
        download_Hubeau_observations.download_hubeau_france_mois(annee_mois,grandeur)
        print(f"Téléchargement du fichier terminé : {complete_path}")

    df_clean = clean_utils.clean_hubeau_data(
        annee_mois,
        code_sandre,
        path_file_to_clean=complete_path,
    )

    # Dossier de sortie
    output_file = utils.get_path_clean_csv(code_sandre, annee_mois, grandeur)

    df_clean.to_csv(output_file, index=False)

    print(f"Fichier créé : {output_file}")


def clean_all_data():
    # ============================================================
    # CONFIGURATION
    # ============================================================

    # Code SANDRE
    code_sandre_a_nettoyer = ["BSH001", "BSH101"]

    # Dossier contenant les fichiers téléchargés
    input_folder = Path("output/hubeau/downloaded_data/observations_elaboree")

    # ============================================================
    # RECUPERATION DES FICHIERS
    # ============================================================

    # Tous les fichiers CSV du dossier
    fichiers_csv = sorted(input_folder.glob("*-????-??.csv"))

    print(f"{len(fichiers_csv)} fichier(s) trouvé(s).")

    # ============================================================
    # TRAITEMENT
    # ============================================================

    with tqdm(total=len(fichiers_csv)*len(code_sandre_a_nettoyer), desc="Nettoyage des fichiers") as pbar:

        for fichier_csv in fichiers_csv:

            for sandre_code in code_sandre_a_nettoyer:
                # ====================================================
                # EXTRACTION DATE DEPUIS LE NOM DU FICHIER
                # Exemple :
                # observations-QmM-france-2020-01.csv
                # ====================================================

                # Récupération AAAA-MM
                nom_fichier = fichier_csv.stem
                annee_mois = nom_fichier.split("-")[-2] + "-" + nom_fichier.split("-")[-1]

                # Nettoyage du fichier
                clean_single_month(annee_mois, sandre_code)

                pbar.update(1)

    print("\nTraitement terminé.")

if __name__ == "__main__":
    #clean_all_data()
    clean_single_month("2025-06", "BSH001","QmnJ")
    clean_single_month("2025-07", "BSH001","QmnJ")
    clean_single_month("2025-08", "BSH001","QmnJ")
