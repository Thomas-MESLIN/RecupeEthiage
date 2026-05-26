import clean_utils
from pathlib import Path
from tqdm import tqdm

# Code Sandre
#sandre_code = "BSH001"

sandre_code = input("Rentrez un code sandre à filtrer (BSH001 par défaut) : ")
if sandre_code == "":
    sandre_code = "BSH001"

total = []
total_iterations = (2021 - 1991) * 12

with tqdm(total=total_iterations, desc="Progression dates") as pbar:
    for annee in range(1991,2021):
        for mois in range(1,13):
            mois_str = str(mois)
            if mois < 10:
                mois = "0" + str(mois)

            annee_mois_filtre = f"{annee}-{mois}"
            annee_mois_jour_filtre = f"{annee}-{mois}-01"

            # Clean hydroportail data
            df_hydroportail_clean = clean_utils.clean_hydroportail_data(annee_mois_filtre,sandre_code)
            chemin_fichier_clean_hydroportail = Path(f"output/hydroportail/cleaned_data/clean-QmM-{sandre_code}-{annee_mois_filtre}.csv")
            df_hydroportail_clean.to_csv(chemin_fichier_clean_hydroportail, index=False)

            # Clean Hubeau data
            df_hubeau_clean = clean_utils.clean_hubeau_data(annee_mois_jour_filtre,sandre_code)
            chemin_fichier_clean_hubeau = Path(f"output/hubeau/cleaned_data/clean-QmM-{sandre_code}-{annee_mois_filtre}.csv")
            df_hubeau_clean.to_csv(chemin_fichier_clean_hubeau, index=False)

            pbar.update(1)
