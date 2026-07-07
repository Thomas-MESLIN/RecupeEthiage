import calendar
from datetime import datetime
import download_Hubeau
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from utils import OndeGeographicZone, OndeCampagneType

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

COULEUR_MOYENNE = "#000000"  # noir

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

def configure_matplotlib():
    plt.rcParams.update({
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "--",
    })

def plot_evolution_assecs(df: pd.DataFrame, date_depart:datetime, date_fin:datetime, annee_actuelle:int, campagne_type:OndeCampagneType, output_path:Path=None):
    df = df.copy()

    # On filtre la plage sélectionnée.
    df = df[df["date_observation"].between(date_depart, date_fin)]

    # uniquement mai -> septembre
    df = df[df["mois"].between(MOIS_CIBLE[0], MOIS_CIBLE[-1])]

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
            print()
            print(f"ERREUR, LA COULEUR DE L'ANNEE '{annee}' N'A PAS ETE REMPLIE.")
            print("Veuillez l'ajouter à la variable 'ANNEE_COULEURS' dans le script plot_onde.py")
            print()
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

    ax.grid(alpha=0.3)

    ax.legend(
        ncol=1,
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
    )
    ax.set_title(f"Nombres d'assecs lors des campagnes ONDE {get_titre_from_campagne_type(campagne_type)} de {date_depart.year} à {date_fin.year}")
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

    if output_path is not None:
        plt.savefig(output_path)

    plt.close()

def save_df_onde(df_to_save:pd.DataFrame, csv_path:Path,geojson_path:Path):
    """
    Sauvegarde le dataframe sous forme de GeoJSON et de csv dans les chemins indiqués
    :param df_to_save: Le DataFrame à sauvegarder
    :param csv_path: Le chemin pour le csv
    :param geojson_path: Le chemin pour le geojson
    :return: Rien
    """
    df_to_save.to_csv(csv_path, index=False)
    gpd.GeoDataFrame(df_to_save, geometry=df_to_save["geometry"]).to_file(geojson_path, driver="GeoJSON", index=False)

def get_df_complet_campagne_usuelle(onde_campagne_type:OndeCampagneType, annee_mois:datetime, geographic_scale:OndeGeographicZone, zone_code:str) -> pd.DataFrame:
    """
    Récupère les données des campagnes et des observations depuis 2012 jusqu'à today()
    :return:
    """
    dossier_csv = Path(f"output/onde/BSH_{annee_mois.strftime('%Y-%m')}/csv")
    dossier_csv.mkdir(parents=True, exist_ok=True)
    output_path_campagne_all_csv: Path = dossier_csv / Path(f"observations_et_campagnes_all_{annee_mois.strftime('%Y-%m')}.csv")
    output_path_campagne_usuelles_csv: Path = dossier_csv / Path(f"observations_et_campagnes_usuelles_{annee_mois.strftime('%Y-%m')}.csv")
    output_path_campagne_complementaire_csv: Path = dossier_csv / Path(f"observations_et_campagnes_complementaires_{annee_mois.strftime('%Y-%m')}.csv")

    output_path_campagne_no_duplicated_csv: Path = dossier_csv / Path(
        f"observations_et_campagnes_latest_{geographic_scale}{zone_code}_{onde_campagne_type}_{annee_mois.strftime('%Y-%m')}.csv")

    dossier_geojson = Path(f"output/onde/BSH_{annee_mois.strftime('%Y-%m')}/geojson")
    dossier_geojson.mkdir(parents=True, exist_ok=True)
    output_path_campagne_all_geojson: Path = dossier_geojson / Path(f"observations_et_campagnes_all_{annee_mois.strftime('%Y-%m')}.geojson")
    output_path_campagne_usuelles_geojson: Path = dossier_geojson / Path(f"observations_et_campagnes_usuelles_{annee_mois.strftime('%Y-%m')}.geojson")
    output_path_campagne_complementaire_geojson: Path = dossier_geojson / Path(f"observations_et_campagnes_complementaires_{annee_mois.strftime('%Y-%m')}.geojson")

    output_path_campagne_no_duplicated_geojson: Path = dossier_geojson / Path(
        f"observations_et_campagnes_latest_{annee_mois.strftime('%Y-%m')}_{onde_campagne_type}_{geographic_scale}{zone_code}.geojson")

    df_observations = download_Hubeau.get_df_observations_geographic_zone(
        datetime(2012,1,1),
        datetime.today(),
        geographic_scale,
        zone_code,
    )
    df_observations["code_campagne"] = df_observations["code_campagne"].astype("int64")
    df_campagnes = download_Hubeau.get_df_all_campagne()
    # On ne garde quie les colonnes utiles et on enlève les doublons. Les campgnes osnt enregistré pour chaque déparemetns.
    # On a besoin uniquement des modalités, donc on ne garde qu'un seul code.
    df_campagne_reduit = df_campagnes[["code_campagne","date_campagne","nombre_modalite_ecoulement",
                                       "code_type_campagne", "libelle_type_campagne", "code_reseau",
                                       "libelle_reseau", "uri_reseau"]].drop_duplicates(subset="code_campagne", ignore_index=True)
    df_join_campagne = df_observations.merge(df_campagne_reduit, on="code_campagne", how="left")
    save_df_onde(df_join_campagne, output_path_campagne_all_csv, output_path_campagne_all_geojson)

    # On filtre avec que les campagnes usuelles
    df_join_campagne_usuelle = df_join_campagne[df_join_campagne["code_type_campagne"] == 1]
    save_df_onde(df_join_campagne_usuelle, output_path_campagne_usuelles_csv, output_path_campagne_usuelles_geojson)

    # On sauvegarde aussi les campagnes complémentaires
    df_join_campagne_complementaire = df_join_campagne[df_join_campagne["code_type_campagne"] == 2]
    save_df_onde(df_join_campagne_complementaire, output_path_campagne_complementaire_csv, output_path_campagne_complementaire_geojson)

    match onde_campagne_type:
        case OndeCampagneType.COMPLEMENTAIRE:
            df_campagne = df_join_campagne_complementaire
        case OndeCampagneType.USUELLE:
            df_campagne = df_join_campagne_usuelle
        case OndeCampagneType.ALL_CAMPAGNE:
            df_campagne = df_join_campagne
        case _:
            raise NotImplementedError(f"Type de Campagne non implémenté : {onde_campagne_type}")

    # Mise en formes des dates.
    df_campagne["date_observation"] = pd.to_datetime(df_campagne["date_observation"])
    df_campagne["annee"] = df_campagne["date_observation"].dt.year
    df_campagne["mois"] = df_campagne["date_observation"].dt.month

    # On supprime les duplicatas et on garde le plus récent :
    df_campagne_trie = df_campagne.sort_values(by="date_observation", ascending=False)
    df_campagne_derniere_donne_chaque_station = df_campagne_trie.drop_duplicates(subset=["geometry","annee","mois"], keep="first")
    save_df_onde(df_campagne_derniere_donne_chaque_station, output_path_campagne_no_duplicated_csv, output_path_campagne_no_duplicated_geojson)

    return df_campagne_derniere_donne_chaque_station

def plot_everything(campagne_type:OndeCampagneType, annee_mois:datetime, geographic_scale:OndeGeographicZone, zone_code:str):
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
    dossier_chemin = Path(f"output/onde/BSH_{annee_mois.strftime('%Y-%m')}")
    dossier_chemin.mkdir(parents=True, exist_ok=True)
    df_complet = get_df_complet_campagne_usuelle(campagne_type, annee_mois, geographic_scale, zone_code)
    # On prend l'extrait depuis 4 ans.
    plot_evolution_assecs(df_complet,
                          annee_mois.replace(year=annee_mois.year-4, month=MOIS_CIBLE[0], day=1), # On prend le premier jour du mois de mai il y a 4 ans
                          annee_mois.replace(day=calendar.monthrange(annee_mois.year, annee_mois.month)[1]), # On prend le dernier jour du mois
                          annee_mois.year,
                          campagne_type,
                          output_path=dossier_chemin / f"onde_evolution-assec_{annee_mois.strftime('%Y')}_{campagne_type}_{geographic_scale}{zone_code}.png")

    plot_evolution_ecoulements(df_complet,
                               campagne_type,
                               6,nb_mesures=385,
                               output_path=dossier_chemin / f"onde_evolution-ecoulement_{annee_mois.strftime('%Y-%m')}_{campagne_type}_{geographic_scale}{zone_code}.png")


if __name__ == "__main__":
    plot_everything(OndeCampagneType.USUELLE, datetime(2026,6,1), OndeGeographicZone.REGION, "84")
    plot_everything(OndeCampagneType.COMPLEMENTAIRE, datetime(2026,6,1), OndeGeographicZone.REGION, "84")
    plot_everything(OndeCampagneType.ALL_CAMPAGNE, datetime(2026,6,1), OndeGeographicZone.REGION, "84")
