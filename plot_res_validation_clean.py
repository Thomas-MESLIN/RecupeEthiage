import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Exemple : chargement du CSV
df = pd.read_csv(Path("output/res-validation/diff_hydro_hubeau_clean.csv"))

# Conversion de la colonne date
df["annee_mois"] = pd.to_datetime(df["annee_mois"], format="%Y-%m")

# Colonnes numériques à tracer
colonnes_a_plot = [
    "station_uniquement_hubeau",
    "total_station_hubeau",
    "station_uniquement_hydroportail",
    "total_station_hydroportail",
]

# Optionnel : filtrer les lignes sans code_sandre
# df = df[df["code_sandre"].notna() & (df["code_sandre"] != "")]

# Un graphique par colonne
for col in colonnes_a_plot:
    plt.figure(figsize=(12, 5))

    # Si plusieurs code_sandre, on trace une courbe par code
    for code, group in df.groupby("code_sandre"):
        group = group.sort_values("annee_mois")

        label = code if code != "" else "GLOBAL"

        plt.plot(
            group["annee_mois"],
            group[col],
            marker="o",
            label=label
        )

    plt.title(col)
    plt.xlabel("Date")
    plt.ylabel(col)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    xmin, xmax, ymin, ymax = plt.axis()
    plt.axis( (xmin, xmax, 0, ymax) )
    plt.show()
def do_plot_hubeau_hydroportail(col_hubeau : str, col_hydroportail : str, titre :str):
    # Création des plots avec les différence entre Hubeau et Hydroportail
    for code, group in df.groupby("code_sandre"):
        plt.figure(figsize=(12, 5))
        group = group.sort_values("annee_mois")

        plt.plot(
            group["annee_mois"],
            group[col_hubeau],
            marker="o",
            label=col_hubeau
        )
        plt.plot(
            group["annee_mois"],
            group[col_hydroportail],
            marker="o",
            label=col_hydroportail
        )

        plt.title(titre + str(code))
        plt.xlabel("Date du relevé (QmM - mensuel)")
        plt.ylabel("Nombre de stations")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        xmin, xmax, ymin, ymax = plt.axis()
        #plt.axis( (xmin, xmax, 0, ymax) )
        plt.show()

do_plot_hubeau_hydroportail("station_uniquement_hubeau", "station_uniquement_hydroportail", "Stations uniquement dans Hubeau ou hydroportail, contenant de la donnée, par mois, de la liste ")

do_plot_hubeau_hydroportail("total_station_hubeau", "total_station_hydroportail", "Nombre total de station dans Hubeau ou hydroportail, contenant de la donnée, par mois, de la liste ")

