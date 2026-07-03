from datetime import datetime
import download_Hubeau
import pandas as pd
from pathlib import Path
import numpy as np

import matplotlib.pyplot as plt
import pandas as pd

from utils import OndeGeographicZone

MOIS = {
    5: "mai",
    6: "juin",
    7: "juillet",
    8: "août",
    9: "septembre"
}
ANNEE_COULEURS = {
    "Moyenne": "#000000",   # noir
    2012: "#1f77b4",
    2013: "#ff7f0e",
    2014: "#2ca02c",
    2015: "#d62728",
    2016: "#9467bd",
    2017: "#8c564b",
    2018: "#e377c2",
    2019: "#7f7f7f",
    2020: "#bcbd22",
    2021: "#17becf",
    2022: "#1b9e77",
    2023: "#d95f02",
    2024: "#7570b3",
    2025: "#e7298a",
    2026: "#66a61e",
}

def plot_evolution_assecs(df: pd.DataFrame):
    plt.rcParams.update({
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "--",
    })
    df = df.copy()

    df["date_observation"] = pd.to_datetime(df["date_observation"])
    df["annee"] = df["date_observation"].dt.year
    df["mois"] = df["date_observation"].dt.month

    # uniquement mai -> septembre
    df = df[df["mois"].between(5, 9)]

    # Assec
    assecs = df[df["libelle_ecoulement"] == "Assec"]

    data = (
        assecs.groupby(["annee", "mois"])
        .size()
        .unstack()
        .reindex(columns=[5, 6, 7, 8, 9])
    )

    moyenne = data.mean(axis=0)

    fig, ax = plt.subplots(figsize=(9, 5))



    for annee in sorted(data.index):
        lw = 3.5 if annee == 2026 else 2
        ms = 8 if annee == 2026 else 6

        ax.plot(
            data.columns,
            data.loc[annee],
            color=ANNEE_COULEURS[annee],
            linewidth=lw,
            marker="o",
            markersize=ms,
            label=str(annee),
        )

    # moyenne
    ax.plot(
        moyenne.index,
        moyenne.values,
        color=ANNEE_COULEURS["Moyenne"],
        linewidth=3.5,
        marker="o",
        markersize=8,
        label="Moyenne",
    )

    ax.set_xticks([5, 6, 7, 8, 9])
    ax.set_xticklabels([MOIS[m] for m in [5, 6, 7, 8, 9]])

    ax.set_xlabel("Mois")
    ax.set_ylabel("Nombre d'assecs")

    ax.grid(alpha=0.3)

    ax.legend(
        ncol=3,
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
    )

    plt.tight_layout()
    plt.show()

ORDRE = [
    "Pas de données",
    "Ecoulement visible acceptable",
    "Ecoulement visible faible",
    "Ecoulement non visible",
    "Assec"
]

COULEURS = {
    "Pas de données": "#D9D9D9",
    "Ecoulement visible acceptable": "#1f77b4",
    "Ecoulement visible faible": "#5dade2",
    "Ecoulement non visible": "#f39c12",
    "Assec": "#d62728",
}

def plot_evolution_ecoulements(df, nb_mesures=None):

    df = df.copy()

    df["date_observation"] = pd.to_datetime(df["date_observation"])
    df["annee"] = df["date_observation"].dt.year
    df["mois"] = df["date_observation"].dt.month

    # Nombre total de stations (si non fourni)
    if nb_mesures is None:
        nb_mesures = df["code_station"].nunique()

    lignes = []
    for annee in sorted(df["annee"].unique()):

        d = df[df["annee"] == annee]

        acceptable = d["code_ecoulement"].isin(["1", "1a"]).sum()
        faible = (d["code_ecoulement"] == "1f").sum()
        non_visible = (d["code_ecoulement"] == "2").sum()
        assec = (d["code_ecoulement"] == "3").sum()

        observes = acceptable + faible + non_visible + assec

        lignes.append({
            "annee": annee,
            "Pas de données": max(nb_mesures - observes, 0),
            "Ecoulement visible acceptable": acceptable,
            "Ecoulement visible faible": faible,
            "Ecoulement non visible": non_visible,
            "Assec": assec,
        })

    tab = (
        pd.DataFrame(lignes)
        .set_index("annee")
        .sort_index()
    )

    # Passage en pourcentage
    tab = tab / nb_mesures * 100

    fig, ax = plt.subplots(figsize=(12, 6))

    bottom = np.zeros(len(tab))

    for cat in ORDRE:

        valeurs = tab[cat].values

        bars = ax.bar(
            tab.index.astype(str),
            valeurs,
            bottom=bottom,
            color=COULEURS[cat],
            label=cat
        )

        for bar, v, b in zip(bars, valeurs, bottom):

            if v < 3:
                continue

            ax.text(
                bar.get_x() + bar.get_width() / 2,
                b + v / 2,
                f"{v:.1f}%",
                ha="center",
                va="center",
                fontsize=8,
                color="white"
            )

        bottom += valeurs

    ax.set_ylim(0, 100)
    ax.set_xlabel("Année")
    ax.set_ylabel("%")

    ax.legend(
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=False,
    )

    plt.tight_layout()
    plt.show()

def get_df_complet() -> pd.DataFrame:
    df_annee = download_Hubeau.get_df_observations_geographic_zone(
        datetime(2012,1,1),
        datetime.today(),
        OndeGeographicZone.REGION,
        "84",
    )
    return df_annee

if __name__ == "__main__":
    df_mois_juin_2026 = get_df_complet()
    plot_evolution_assecs(df_mois_juin_2026)
    df_stations = download_Hubeau.download_hubeau_onde_stations_geographic_zone(OndeGeographicZone.REGION,"84")
    nb_mesure = len(df_stations[df_stations["etat_station"] == "Active"])
    plot_evolution_ecoulements(df_mois_juin_2026,nb_mesures=nb_mesure*5)
