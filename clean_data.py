import pandas as pd
from pathlib import Path
from tqdm import tqdm
import clean_utils
import download_Hubeau_observations

def clean_single_month(annee_mois, code_sandre):
    """
    Clean a file containing a single month of data.
    Download it if the file does not exist.
    :param annee_mois: Année et mois au format AAAA-MM
    :param code_sandre: Code sandre à extraire
    """
    date_complete = f"{annee_mois}-01"
    complete_path = Path(f"output/hubeau/downloaded_data/observations_elaboree/observations-QmM-france-{annee_mois}.csv")
    if not complete_path.exists():
        print(f"Téléchargement du fichier en cours : {complete_path}")
        download_Hubeau_observations.download_hubeau_france_mois(annee_mois,"QmM")
        print(f"Téléchargement du fichier terminé : {complete_path}")

    df_clean = clean_utils.clean_hubeau_data(
        date_complete,
        code_sandre,
        path_file_to_clean=complete_path,
    )

    # Dossier de sortie
    output_folder = Path("output/hubeau/cleaned_data")
    output_file = output_folder / f"clean-QmM-{code_sandre}-{annee_mois}.csv"

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
    clean_all_data()
