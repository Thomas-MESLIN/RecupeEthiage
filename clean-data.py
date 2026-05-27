import pandas as pd
from pathlib import Path
from tqdm import tqdm
import clean_utils

# ============================================================
# CONFIGURATION
# ============================================================

# Code SANDRE
code_sandre_a_nettoyer = ["BSH001", "BSH101"]

# Dossier contenant les fichiers téléchargés
input_folder = Path("output/hubeau/downloaded_data/observations_elaboree")

# Dossier de sortie
output_folder = Path("output/hubeau/cleaned_data")

# ============================================================
# RECUPERATION DES FICHIERS
# ============================================================

# Tous les fichiers CSV du dossier
fichiers_csv = sorted(input_folder.glob("*.csv"))

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

            nom_fichier = fichier_csv.stem

            # Récupération AAAA-MM
            annee_mois = nom_fichier.split("-")[-2] + "-" + nom_fichier.split("-")[-1]

            # Format YYYY-MM-DD
            date_complete = f"{annee_mois}-01"

            print(f"\nTraitement : {nom_fichier}")

            # ====================================================
            # NETTOYAGE
            # ====================================================

            df_clean = clean_utils.clean_hubeau_data(
                date_complete,
                sandre_code,
                path_file_to_clean=fichier_csv,
            )

            # ====================================================
            # EXPORT
            # ====================================================

            output_file = output_folder / f"clean-QmM-{sandre_code}-{annee_mois}.csv"

            df_clean.to_csv(output_file, index=False)

            print(f"Fichier créé : {output_file}")

            pbar.update(1)

print("\nTraitement terminé.")