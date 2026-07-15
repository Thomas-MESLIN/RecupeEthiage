import calendar
from datetime import datetime
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from src.model.enums import GeographicScaleClip
from src.model.enums import OndeCampagneType
import src.processing.process_onde as process_onde
from src.config.styles import COULEUR_MOYENNE, ANNEE_COULEURS
from src.config.logging_config import setup_logger
from src.config.paths import OUTPUT_DIR

# Initialiser le logger
logger = setup_logger(name="plot_onde")


## Traduction du numéro en nom de mois
MOIS = {
    5: "mai",
    6: "juin",
    7: "juillet",
    8: "août",
    9: "septembre"
}

## Les mois souhaité.
MOIS_CIBLE = [5, 6, 7, 8, 9]

def configure_matplotlib():
    plt.rcParams.update({
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "--",
    })

def save_and_close_plot(output_path:Path|None):
    if output_path:
        plt.savefig(output_path)
    plt.close()
    logger.info("Plot Sauvegardé à " + str(output_path))

def plot_evolution_assecs(df: pd.DataFrame, date_depart:datetime, date_fin:datetime, annee_actuelle:int, campagne_type:OndeCampagneType, output_path:Path=None):
    df = df.copy()

    # On filtre la plage sélectionnée.
    df = df[df["date_observation"].between(date_depart, date_fin)]

    # uniquement mai -> septembre
    df = df[df["mois"].isin(MOIS_CIBLE)]

    # Assec
    assecs = df[df["libelle_ecoulement"] == "Assec"]

    configure_matplotlib()
    data = (
        assecs.groupby(["annee", "mois"])
        .size()
        .unstack()
        .reindex(columns=MOIS_CIBLE)
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
                color=COULEUR_MOYENNE,
                linewidth=lw,
                marker="o",
                markersize=ms,
                label="Moyenne",
            )

        if annee not in ANNEE_COULEURS:
            logger.error(f"ERREUR, LA COULEUR DE L'ANNEE '{annee}' N'A PAS ETE REMPLIE.")
            logger.error("Veuillez l'ajouter à la variable 'ANNEE_COULEURS' dans le script styles.py")
            raise ValueError(f"Aucune couleur définie pour l'année {annee}")

        ax.plot(
            data.columns,
            data.loc[annee],
            color=ANNEE_COULEURS[annee],
            linewidth=lw,
            marker="o",
            markersize=ms,
            label=str(annee),
        )


    ax.set_xticks(MOIS_CIBLE)
    ax.set_xticklabels([MOIS[m] for m in MOIS_CIBLE])

    ax.set_xlabel("Mois")
    ax.set_ylabel("Nombre d'assecs")

    ax.legend(
        ncol=1,
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
    )
    ax.set_title(f"Nombres d'assecs lors des campagnes ONDE {get_titre_from_campagne_type(campagne_type)} de {date_depart.year} à {date_fin.year}")
    plt.tight_layout()
    # plt.show()

    save_and_close_plot(output_path)

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

def get_titre_from_campagne_type(campagne_type:OndeCampagneType):
    match campagne_type:
        case OndeCampagneType.COMPLEMENTAIRE:
            return "Complémentaire"
        case OndeCampagneType.USUELLE:
            return "Usuelle"
        case OndeCampagneType.ALL_CAMPAGNE:
            return "Usuelle et Complémentaire"
        case _:
            raise NotImplementedError(f"Campagne Type inconnu : {campagne_type}")

def plot_evolution_ecoulements(df:pd.DataFrame, campagne_type:OndeCampagneType, mois_souhaite:int, nb_mesures=None, output_path:Path=None):

    df = df.copy()

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

    configure_matplotlib()
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

    ax.set_title(f"Répartition des écoulements observé lors des campagnes ONDE {get_titre_from_campagne_type(campagne_type)} du mois de {MOIS[mois_souhaite]}.")
    ax.legend(
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=False,
    )

    plt.tight_layout()
    # plt.show()

    save_and_close_plot(output_path)

def plot_everything(campagne_type:OndeCampagneType, annee_mois:datetime, geographic_scale:GeographicScaleClip, zone_code:str):
    """
    Créer les plot ONDE à partir de l'année et du mois souhaité
    Va créer des plots sur l'évolutions des écoulements et l'évolutions des assecs.
    L'évolution des assecs prend en compte les 4 dernière année avant annee_mois.
    :param campagne_type: Le Type de Campagne Onde souhaité
    :param annee_mois: L'année et le mois que l'on défini comme fin de l'extrait
    :param geographic_scale: La zone géographique que l'on souhaite récupérer
    :param zone_code: Le code associé à cette zone géographique
    :return: Rien.
    """
    if zone_code is None:
        raise ValueError("Le code pour la zone géographique n'est pas précisé.")
    dossier_chemin = OUTPUT_DIR / "onde" / f"BSH_{annee_mois.strftime('%Y-%m')}" / f"{geographic_scale[0]}{zone_code}"
    dossier_chemin.mkdir(parents=True, exist_ok=True)
    df_complet = process_onde.load_and_prepare_onde_data(campagne_type, annee_mois, geographic_scale, zone_code)
    # On prend l'extrait depuis 4 ans.
    plot_evolution_assecs(df_complet,
                          annee_mois.replace(year=annee_mois.year-4, month=MOIS_CIBLE[0], day=1), # On prend le premier jour du mois de mai il y a 4 ans
                          annee_mois.replace(day=calendar.monthrange(annee_mois.year, annee_mois.month)[1]), # On prend le dernier jour du mois
                          annee_mois.year,
                          campagne_type,
                          output_path=dossier_chemin / f"onde_evolution-assec_{annee_mois.strftime('%Y')}_{campagne_type}.png")

    plot_evolution_ecoulements(df_complet,
                               campagne_type,
                               6,nb_mesures=385,
                               output_path=dossier_chemin / f"onde_evolution-ecoulement_{annee_mois.strftime('%Y-%m')}_{campagne_type}.png")
    logger.info("Données générées avec succès dans : " + str(dossier_chemin))


if __name__ == "__main__":
    plot_everything(OndeCampagneType.USUELLE, datetime(2026,6,1), GeographicScaleClip.REGION_ADMINISTRATIVE, "84")
    plot_everything(OndeCampagneType.COMPLEMENTAIRE, datetime(2026,6,1), GeographicScaleClip.REGION_ADMINISTRATIVE, "84")
    plot_everything(OndeCampagneType.ALL_CAMPAGNE, datetime(2026,6,1), GeographicScaleClip.REGION_ADMINISTRATIVE, "84")
