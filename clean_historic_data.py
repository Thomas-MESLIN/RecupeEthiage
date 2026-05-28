import clean_utils
from pathlib import Path
from tqdm import tqdm
import utils

def clean_historic_data(code_sandre:str, grandeur:str):
    """
    Nettoie les données historiques de 1991 à 2020
    :param grandeur: Filtre la grandeur souhaitée
    :param code_sandre: Filtre les données avec les stations associées à code_sandre.
    """
    total_iterations = (2021 - 1991) * 12
    with (tqdm(total=total_iterations, desc="Progression dates") as pbar):
        for annee in range(1991,2021):
            for mois in range(1,13):
                if mois < 10:
                    mois = "0" + str(mois)

                annee_mois_filtre = f"{annee}-{mois}"
                annee_mois_jour_filtre = f"{annee}-{mois}-01"

                if grandeur == "QmM":
                    # Clean hydroportail data
                    df_hydroportail_clean = clean_utils.clean_hydroportail_data(annee_mois_filtre,code_sandre)
                    chemin_fichier_clean_hydroportail = Path(f"output/hydroportail/cleaned_data/clean-QmM-{code_sandre}-{annee_mois_filtre}.csv")
                    df_hydroportail_clean.to_csv(chemin_fichier_clean_hydroportail, index=False)

                # Clean Hubeau data
                df_hubeau_clean = clean_utils.clean_hubeau_data(annee_mois_jour_filtre,code_sandre, grandeur_a_filtrer=grandeur)
                chemin_fichier_clean_hubeau = utils.get_path_clean_csv(code_sandre,annee_mois_filtre,grandeur)
                df_hubeau_clean.to_csv(chemin_fichier_clean_hubeau, index=False)

                pbar.update(1)

if __name__ == "__main__":
    sandre_code = input("Rentrez un code sandre à filtrer (BSH001 par défaut) : ")
    if sandre_code == "":
        sandre_code = "BSH001"
    print(f"Code à filtrer : [{sandre_code}]")
    clean_historic_data(sandre_code, "QmM")
