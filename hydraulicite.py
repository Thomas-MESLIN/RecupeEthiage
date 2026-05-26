import clean_utils
from pathlib import Path
import pandas as pd
import os

# On va juste utiliser le mois de janvier 2020
df_janvier = clean_utils.clean_hubeau_data("2020-01-01","BSH001")

col_janvier = df_janvier["resultat_obs_elab"]
print(col_janvier)


data_moyenne_path = Path("output/hubeau/QmM_moyen/QmM_moyennes_1991_2020.csv")
df_moyenne = pd.read_csv(data_moyenne_path)

df_moyenne_janvier = df_moyenne[df_moyenne["mois"] == 1]
data_mois_correct = df_moyenne_janvier["QmM_moyenne"]
print(data_mois_correct)


# Fusion sur code_station
df_final = pd.merge(
    df_janvier,
    df_moyenne_janvier,
    on="code_station",
    how="inner"   # ou "left" selon ce que tu veux
)

print(df_final)
print(df_final.columns)

df_final["hydraulicite"] = (
    df_final["resultat_obs_elab"] /
    df_final["QmM_moyenne"]
)

print(df_final)
print(df_final.columns)

df_final.to_csv(Path("output/hydraulicite/hydraulicite-BSH001-2020-01.csv"), index=False)