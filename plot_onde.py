import calendar
from datetime import datetime
import download_Hubeau
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

COULEUR_Moyenne = "#000000"  # noir

ANNEE_COULEURS : dict[int, str] = {
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
    2025: "#e3298a",
    2026: "#ee0000",
}

def plot_evolution_assecs(df: pd.DataFrame, date_depart:datetime, date_fin:datetime, annee_actuelle:int, output_path:Path=None):
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
    # On filtre la plage sélectionnée.
    df = df[(date_depart <= df["date_observation"]) & (df["date_observation"] <= date_fin)]
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
        lw = 2 # Largeur de la ligne
        ms = 6
        if annee == annee_actuelle:
            lw = 3.5
            ms = 8
            # On dessine la moyenne juste en dessous.
            ax.plot(
                moyenne.index,
                moyenne.values,
                color=COULEUR_Moyenne,
                linewidth=lw,
                marker="o",
                markersize=ms,
                label="Moyenne",
            )

        if annee not in ANNEE_COULEURS:
            print()
            print(f"ERREUR, LA COULEUR DE L'ANNEE '{annee}' N'A PAS ETE REMPLIE.")
            print("Veuillez l'ajouter à la variable 'ANNEE_COULEURS' dans le script plot_onde.py")
            print()
            exit(1)

        ax.plot(
            data.columns,
            data.loc[annee],
            color=ANNEE_COULEURS[annee],
            linewidth=lw,
            marker="o",
            markersize=ms,
            label=str(annee),
        )


    ax.set_xticks([5, 6, 7, 8, 9])
    ax.set_xticklabels([MOIS[m] for m in [5, 6, 7, 8, 9]])

    ax.set_xlabel("Mois")
    ax.set_ylabel("Nombre d'assecs")

    ax.grid(alpha=0.3)

    ax.legend(
        ncol=1,
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
    )
    ax.set_title(f"Nombres d'assecs lors des campagnes ONDE usuelles de {date_depart.year} à {date_fin.year}")
    plt.tight_layout()
    # plt.show()

    if output_path is not None:
        plt.savefig(output_path)
    plt.close()

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

def plot_evolution_ecoulements(df:pd.DataFrame,mois_souhaite:int, nb_mesures=None, output_path:Path=None):

    df = df.copy()

    df["date_observation"] = pd.to_datetime(df["date_observation"])
    df["annee"] = df["date_observation"].dt.year
    df["mois"] = df["date_observation"].dt.month

    df = df[df["mois"] == mois_souhaite]

    # Nombre total de stations (si non fourni)
    if nb_mesures is None:
        nb_mesures = df["code_station"].nunique()

    lignes = []
    for annee in sorted(df["annee"].dropna().unique()):

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
    tab = tab.apply(lambda x: round(100 * x / x.sum(), 1), axis=1)

    fig, ax = plt.subplots(figsize=(13.5, 7.5))

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
            if v < 0.01:
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

    ax.set_title(f"Répartition des écoulements observé lors des campagnes ONDE usuelles du mois de {MOIS[mois_souhaite]}.")
    ax.legend(
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=False,
    )

    plt.tight_layout()
    # plt.show()

    if output_path is not None:
        plt.savefig(output_path)

def get_df_complet_campagne_usuelle() -> pd.DataFrame:
    """
    Récupère les données des campagnes et des observations depuis 2012 jusqu'à today()
    :return:
    """
    df_observations = download_Hubeau.get_df_observations_geographic_zone(
        datetime(2012,1,1),
        datetime.today(),
        OndeGeographicZone.REGION,
        "84",
    )
    df_observations["code_campagne"] = df_observations["code_campagne"].astype("int64")
    df_campagnes = download_Hubeau.get_df_all_campagne()
    # On ne garde quie les colonnes utiles et on enlève les doublons. Les campgnes osnt enregistré pour chaque déparemetns.
    # On a besoin uniquement des modalités, donc on ne garde qu'un seul code.
    df_campagne_reduit = df_campagnes[["code_campagne","date_campagne","nombre_modalite_ecoulement",
                                       "code_type_campagne", "libelle_type_campagne", "code_reseau",
                                       "libelle_reseau", "uri_reseau"]].drop_duplicates(subset="code_campagne", ignore_index=True)
    df_join_campagne = df_observations.merge(df_campagne_reduit, on="code_campagne", how="left")
    df_join_campagne_usuelle = df_join_campagne[df_join_campagne["code_type_campagne"] == 1]
    return df_join_campagne_usuelle

def plot_everything(annee_mois:datetime):
    """
    Créer un plot ONDE à partir de l'année et du mois souhaité
    :param annee_mois:
    :return:
    """
    df_complet = get_df_complet_campagne_usuelle()
    dossier_chemin = Path(f"output/onde/BSH_{annee_mois.strftime('%Y-%m')}")
    dossier_chemin.mkdir(parents=True, exist_ok=True)
    # On prend l'extrait depuis 4 ans.
    plot_evolution_assecs(df_complet,
                          annee_mois.replace(year=annee_mois.year-4, month=5, day=1), # On prend le premier jour du mois de mai il y a 4 ans
                          annee_mois.replace(day=calendar.monthrange(annee_mois.year, annee_mois.month)[1]), # On prend le dernier jour du mois
                          annee_mois.year,
                          output_path=dossier_chemin / f"onde_evolution-assec_{annee_mois.year}.png")
    plot_evolution_ecoulements(df_complet, 6,nb_mesures=385,
                               output_path=dossier_chemin / f"onde_evolution-ecoulement_{MOIS[annee_mois.month]}_{annee_mois.year}.png")


if __name__ == "__main__":
    plot_everything(datetime(2026,6,1))
