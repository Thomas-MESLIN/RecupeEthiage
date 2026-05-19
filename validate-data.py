import pandas as pd
from pathlib import Path

output_folder = Path("output")

def get_df_hubeau_period_qmm(date_a_filtrer: str) -> pd.DataFrame:
    """
    Va chercher le fichier des observations qmm dans les fichiers téléchargé.
    Charge les données et prendre uniquement les données correspondantes à la date en paramètre
    :param date_a_filtrer: La date qui servira de filtre au format YYYY-MM-DD
    :return: Renvoie un pd.DataFrame représentant le QmM sur de la date YYYY-MM-DD via l'API Hubeau
    """
    fichier_hubeau = output_folder / "observations-QmM-france-1991-2020.csv"
    colonne_date = "date_obs_elab"

    # === LECTURE DES CSV ===
    df_hubeau = pd.read_csv(fichier_hubeau)

    # Filtrage pour avoir uniquement les enregistrements aux bonnes dates
    df_hubeau_janvier_2001 = df_hubeau[df_hubeau[colonne_date] == date_a_filtrer]

    return df_hubeau_janvier_2001


def get_df_stations_hubeau_filtre_code_sandre(code_sandre: str) -> pd.DataFrame:
    """
    Renvoie un dataFrame correspondant à toutes les stations Hubeau filtré par leur code sandre
    :param code_sandre: Un code Sandre correspondant aux listes de stations Hydrométriques
    :return: Renvoie un pd.DataFrame correspondant à toutes les stations Hubeau appartennant à la liste du même code_sandre
    """
    fichier_station_hubeau = output_folder / "stations.csv"

    # Lecture des stations hubeau
    df_stations_hubeau = pd.read_csv(fichier_station_hubeau)

    # Filtrage pour avoir uniquement les stations du code SANDRE correspondant
    colonne_code_sandre = "code_sandre_reseau_station"
    df_stations_hubeau_filtre_code_sandre = df_stations_hubeau[
        df_stations_hubeau[colonne_code_sandre].astype(str).str.contains(code_sandre, na=False)
    ]
    return df_stations_hubeau_filtre_code_sandre

# Code Sandre
sandre_code = "BSH001"

# Date à filtrer (format YYYY-MM-DD)
date_a_filtrer = "2001-01-01"
annee_mois_a_filtrer = "2001-01"

# Récupération df hydroportail
fichier_hydroportail = output_folder / "hydroportail" / f"{annee_mois_a_filtrer}-{sandre_code}-only-validated-qmm.csv"

df_hydroportail = pd.read_csv(fichier_hydroportail)


df_hubeau = get_df_hubeau_period_qmm(date_a_filtrer)
df_stations_hubeau_filtre_code_sandre = get_df_stations_hubeau_filtre_code_sandre(sandre_code)

# Sauvegarde pour inspection manuelle
ficher_sortie_extrait_sandre_hubeau = output_folder / "hubeau" / (date_a_filtrer + "-" + sandre_code + "-qmm.csv")
df_stations_hubeau_filtre_code_sandre.to_csv(ficher_sortie_extrait_sandre_hubeau, index=False)

# Récupération de l'ensemble des code de site correspondant à chaque dataFrame
colonne_code_hubeau = "code_site"
codes_hubeau = set(df_hubeau[colonne_code_hubeau].dropna())
codes_stations_BSH001 = set(df_stations_hubeau_filtre_code_sandre[colonne_code_hubeau].dropna())

colonne_code_hydroportail = "Code de l'entité"
codes_hydroportail = set(df_hydroportail[colonne_code_hydroportail].dropna())

# On fais l'intersection de ces deux ensemble
# code_hubeau_date_correcte_code_filtre = codes_hubeau.intersection(codes_stations_BSH001)
code_hubeau_date_correcte_code_filtre = codes_stations_BSH001
#if code_hubeau_date_correcte_code_filtre == codes_hubeau:
#    print("La liste BSH Entière est")

# On fais les différences
uniquement_dans_hubeau = code_hubeau_date_correcte_code_filtre - codes_hydroportail
uniquement_dans_hydro = codes_hydroportail - code_hubeau_date_correcte_code_filtre

# === AFFICHAGE DES RÉSULTATS ===
print(f"\nCodes présents dans 'observations-QmM-france-1991-2020.csv' mais absents de {fichier_hydroportail} :")
print(uniquement_dans_hubeau)
print("Nombre uniquement dans Hubeau : ")
print(len(uniquement_dans_hubeau))
print("Sur un total dans Hubeau : ")
print(len(code_hubeau_date_correcte_code_filtre))


print(f"\nCodes présents dans {fichier_hydroportail} mais absents de 'observations-QmM-france-1991-2020.csv' :")
#for code in sorted(uniquement_dans_hydro):
#    print(code)
print(uniquement_dans_hydro)
print("Nombre uniquement dans Hydroportail : ")
print(len(uniquement_dans_hydro))
print("Sur un total dans Hydroportail : ")
print(len(codes_hydroportail))
