from pathlib import Path
import pandas as pd
import calcul_hydraulicite_1991_2020
import clean_data
import plot_carte_hydraulicite
import utils
# Ce script sert à récupérer les données nettoyée et les exploiter pour calculer l'hydraulicité.
# On a besoin pour cela de l'hydraulicité historique.

def calcul_hydraulicite(annee_mois: str, code_sandre: str):
    """
    Calcul l'hydraulicité à partir des données historiques et des données nettoyées
    Le sauvegarde ensuite dans un .csv dans le dossier hydraulicité.
    :param annee_mois: Année et mois de l'hydraulicité souhaité
    :param code_sandre: Code Sandre de la liste à traiter
    """
    # On va juste utiliser le mois de janvier 2020
    chemin_data_du_mois_clean = utils.get_path_clean_csv(code_sandre, annee_mois,"QmM")
    if not chemin_data_du_mois_clean.exists():
        print(f"Nettoyage du fichier en cours : {chemin_data_du_mois_clean}")
        clean_data.clean_single_month(annee_mois,code_sandre, "QmM")
        print(f"Nettoyage du fichier terminé : {chemin_data_du_mois_clean}")
    df_mois = pd.read_csv(chemin_data_du_mois_clean)

    data_moyenne_path = utils.get_path_qmm_moyen_historique(code_sandre)
    # Si le calcul historique n'a pas été fait, on le réalise.
    if not data_moyenne_path.exists():
        print("Calcul du QmM_moyen de 1991 à 2020...")
        calcul_hydraulicite_1991_2020.calcule_QmM_moyen_1991_2020()
        print("Calcul du QmM_moyen de 1991 à 2020 terminé.")

    df_moyenne = pd.read_csv(data_moyenne_path)

    df_moyenne = df_moyenne[df_moyenne["mois"] == 1]
    data_mois_correct = df_moyenne["QmM_moyenne"]
    #print(data_mois_correct)

    # Fusion sur code_station
    df_final = pd.merge(
        df_mois,
        df_moyenne,
        on="code_station",
        how="inner"   # ou "left" selon ce que tu veux
    )

    df_final["hydraulicite"] = (
        df_final["resultat_obs_elab"] /
        df_final["QmM_moyenne"]
    )

    # print(df_final)
    # print(df_final.columns)

    chemin_save = utils.get_path_hydraulicite(code_sandre,annee_mois)
    df_final.to_csv(chemin_save, index=False)
    print(f"Fichier sauvegardé dans {chemin_save}.")

def calcul_et_plot_hydraulicite_mensuel(annee_mois: str, code_sandre: str):
    """
    Effectue le calcul d'hydraulicité et le transforme immédiatement en geojson.
    :param annee_mois: AAAA-MM
    :param code_sandre: Un code sandre
    """
    calcul_hydraulicite(annee_mois,code_sandre)
    plot_carte_hydraulicite.create_geojson_from_hydraulicite(annee_mois,code_sandre)

if __name__ == "__main__":
    #calcul_et_plot_hydraulicite_mensuel("2026-04","BSH001")
    calcul_et_plot_hydraulicite_mensuel("2026-05","BSH001")
    calcul_et_plot_hydraulicite_mensuel("2026-04","BSH001")
    #calcul_et_plot_hydraulicite_mensuel("2026-04","BSH101")
    #calcul_et_plot_hydraulicite_mensuel("2024-02","BSH001")
