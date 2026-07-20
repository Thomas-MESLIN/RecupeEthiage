
import pandas as pd
import geopandas as gpd
from pathlib import Path
import src.utils.utils as utils
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import src.processing.calcul_frequence_periode_de_retour as f_T
import src.processing.station as station
import src.io.download_Hubeau as download_Hubeau
import src.processing.calcul_hydraulicite as calcul_hydraulicite
import logging
from src.plotting.rasterize import rasterize_geodataframe_geographiv_zone
from src.model.enums import GeographicScaleClip
from src.config.logging_config import setup_logger
from src.config.paths import OUTPUT_DIR

# Initialiser le logger
logger = setup_logger(name="plot_grandeur")


def create_geojson_from_path(chemin_donees_csv:Path, output_path: Path, annee_mois:str, code_sandre:str):
    """
    Créer un geojson et le sauvegarde à partir d'un csv.
    Suppose que le fichier a déjà été calculé.
    :param output_path: Chemin vers lequel le fichier sera écrit.
    :param chemin_donees_csv: Un chemin vers des données contenant des stations.
    :param is_result_plotted: Génère les graphique station par station pour le calcul desp ériode de retour.
    :param code_sandre: Code Sandre à mettre en face des stations utilisées.
    :param annee_mois: AAAA-MM
    :return:
    """
    df_hydro = pd.read_csv(chemin_donees_csv)
    if "code_site" in df_hydro.columns:
        df_hydro.drop(columns=["code_site"], inplace=True)
    # On charge toute les stations active ce mois là.
    df_stations = station.get_stations(code_sandre, annee_mois)

    # Conversion en GeoDataFrame
    gdf_stations = gpd.GeoDataFrame(
        df_stations,
        geometry=gpd.GeoSeries.from_wkt(df_stations["geometry"]),
        crs="EPSG:4326"
    )

    gdf_final_avec_station = gdf_stations.merge(
        df_hydro,
        on="code_station",
        how="left"
    )

    # On charge toute les sites
    download_Hubeau.ensure_sites_downloaded()
    sites_path = utils.get_path_sites()
    df_sites = pd.DataFrame(pd.read_csv(sites_path))

    gdf_final = gdf_final_avec_station.merge(
        df_sites,
        on="code_site",
        how="inner"
    )

    # Suppression des colonnes inutiles créées automatiquement
    colonnes_a_supprimer = [
        "Unnamed: 0"
    ]

    for col in colonnes_a_supprimer:
        if col in gdf_final.columns:
            gdf_final = gdf_final.drop(columns=col)

    output_geojson = output_path

    gdf_final.to_file(
        output_geojson,
        driver="GeoJSON"
    )

    logging.info(f"GeoJSON créé : {output_geojson}")

def create_geojson_from_stations(code_sandre:str|None=None, annee_mois:str|None=None):
    """
    Suppose que le fichier a déjà été calculé.
    :param annee_mois: AAAA-MM
    :param code_sandre: Un code Sandre
    :return:
    """
    # Le fichier contient une colonne WKT : POINT(...)
    df_stations = station.get_stations(code_sandre, annee_mois)

    # Conversion en GeoDataFrame
    gdf_final = gpd.GeoDataFrame(
        df_stations,
        geometry=gpd.GeoSeries.from_wkt(df_stations["geometry"]),
        crs="EPSG:4326"
    )

    # Suppression des colonnes inutiles créées automatiquement
    colonnes_a_supprimer = [
        "Unnamed: 0"
    ]

    for col in colonnes_a_supprimer:
        if col in gdf_final.columns:
            gdf_final = gdf_final.drop(columns=col)

    if annee_mois is not None:
        if code_sandre is not None:
            output_geojson = OUTPUT_DIR / "QGIS" / "stations" / f"stations-ouverte-{code_sandre}-{annee_mois}.geojson"
        else:
            output_geojson = OUTPUT_DIR / "QGIS" / "stations" / f"stations-ouverte-{annee_mois}.geojson"
    else:
        if code_sandre is not None:
            output_geojson = OUTPUT_DIR / "QGIS" / "stations" / f"stations-{code_sandre}.geojson"
        else:
            output_geojson = OUTPUT_DIR / "QGIS" / "stations" / "stations.geojson"

    gdf_final.to_file(
        output_geojson,
        driver="GeoJSON"
    )

    gdf_final.to_csv(
        output_geojson.with_suffix(".csv"),
        sep=';',
        index=False,
    )

    logging.info(f"GeoJSON créé : {output_geojson}")

def create_geojson_from_sites(code_sandre:str|None=None):
    """
    Suppose que le fichier a déjà été calculé.
    :param annee_mois: AAAA-MM
    :param code_sandre: Un code Sandre
    :return:
    """
    df_stations = station.get_stations(code_sandre, None)

    # Conversion en GeoDataFrame
    gdf_final = gpd.GeoDataFrame(
        df_stations,
        geometry=gpd.GeoSeries.from_wkt(df_stations["geometry"]),
        crs="EPSG:4326"
    )

    # On charge toute les stations
    download_Hubeau.ensure_sites_downloaded()
    sites_path = utils.get_path_sites()
    df_sites = pd.DataFrame(pd.read_csv(sites_path))

    gdf_complet_sites_code_sandre = df_sites.merge(
        gdf_final,
        on="code_site",
        how="left"
    )

    # Suppression des colonnes inutiles créées automatiquement
    colonnes_a_supprimer = [
        "Unnamed: 0"
    ]

    for col in colonnes_a_supprimer:
        if col in gdf_complet_sites_code_sandre.columns:
            gdf_complet_sites_code_sandre = gdf_complet_sites_code_sandre.drop(columns=col)

    if code_sandre is not None:
        output_geojson = OUTPUT_DIR / "QGIS" / "sites" / f"sites-{code_sandre}.geojson"
    else:
        output_geojson = OUTPUT_DIR / "QGIS" / "sites" / "sites.geojson"

    gdf_final.to_file(
        output_geojson,
        driver="GeoJSON"
    )

    logging.info(f"GeoJSON créé : {output_geojson}")

def print_results(res: dict) -> None:
    logger.info("=" * 65)
    logger.info("  Loi : Log-Normale  |  Estimateur : L-moments  |  IC : PBOOT")
    logger.info(f"  µ (log) = {res['mu']:.4f}   σ (log) = {res['sigma']:.4f}")
    logger.info(f"  p0 (prob. débit nul) = {res['p0']:.3f}")
    logger.info(f"  n total = {len(res['y'])}   n positifs = {len(res['z'])}")
    logger.info("=" * 65)
    logger.info(f"\n{'T (ans)':>10}  {'p non-dép.':>12}  {'VCN3 (m³/s)':>14}  {'IC bas':>10}  {'IC haut':>10}")
    logger.info("-" * 65)
    q = res["quantiles"]
    for T, p, qv, ic_l, ic_h in zip(q["T"], q["p"], q["q"], q["IC_low"], q["IC_high"]):
        logger.info(f"{T:>10.0f}  {p:>12.4f}  {qv:>14.4f}  {ic_l:>10.4f}  {ic_h:>10.4f}")
    logger.info("")

def plot_results(res: dict, output_path: str|Path, title: str = "Analyse fréquentielle VCN3",
                 ) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(title + "\n[Log-Normale — L-moments — Bootstrap paramétrique]",
                 fontsize=12, fontweight="bold")

    emp = res["empirical"]
    quant = res["quantiles"]
    pcdf = res["pcdf"]

    # Bornes X (période de retour)
    T_min_data = min(emp["T"].min(), 1.0)
    T_max_data = emp["T"].max() * 1.05

    # Borne Y : basée sur les données observées + marge de 20%
    # On ignore volontairement les valeurs théoriques aux bords de la loi
    # qui divergent et écrasent l'échelle des graphiques.
    y_max = emp["y_sorted"].max() * 1.2
    y_min = 0.0

    # -------------------------------------------------------------------
    # Graphique 1 : Période de retour T (ans) vs débit
    # -------------------------------------------------------------------
    ax1 = axes[0]
    ax1.set_xlim(T_min_data, T_max_data)
    ax1.set_ylim(y_min, y_max)

    mask1 = np.isfinite(pcdf["T"]) & (pcdf["T"] >= T_min_data) & (pcdf["T"] <= T_max_data)
    ax1.fill_between(pcdf["T"][mask1],
                     pcdf["IC_low"][mask1], pcdf["IC_high"][mask1],
                     color="firebrick", alpha=0.15, label="IC 95% (PBOOT)")
    ax1.plot(pcdf["T"][mask1], pcdf["x"][mask1], color="firebrick",
             linewidth=1.5, label="Loi Log-Normale (L-mom)")
    ax1.scatter(emp["T"], emp["y_sorted"], color="steelblue", s=20, zorder=5,
                alpha=0.8, label="Observations")
    ax1.set_xscale("log")
    ax1.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax1.set_xlabel("Période de retour T (ans)", fontsize=11)
    ax1.set_ylabel("VCN3 (m³/s)", fontsize=11)
    ax1.set_title("Période de retour vs débit")
    ax1.legend(fontsize=9)
    ax1.grid(True, which="both", alpha=0.3)

    # -------------------------------------------------------------------
    # Graphique 2 : Fréquence de non-dépassement vs débit
    # -------------------------------------------------------------------
    ax2 = axes[1]
    ax2.set_xlim(0, 1)
    ax2.set_ylim(y_min, y_max)

    ax2.fill_between(pcdf["cdf"],
                     pcdf["IC_low"], pcdf["IC_high"],
                     color="firebrick", alpha=0.15, label="IC 95% (PBOOT)")
    ax2.plot(pcdf["cdf"], pcdf["x"], color="firebrick",
             linewidth=1.5, label="Loi Log-Normale (L-mom)")
    ax2.scatter(emp["freq"], emp["y_sorted"], color="steelblue", s=20, zorder=5,
                alpha=0.8, label="Observations")
    ax2.set_xlabel("Fréquence de non-dépassement", fontsize=11)
    ax2.set_ylabel("VCN3 (m³/s)", fontsize=11)
    ax2.set_title("Fréquence vs débit")
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    # plt.show()
    logger.info(f"Graphique sauvegardé : {output_path}")

def plot_period_from_flow(q_obs: float, res_station:dict, res_estimation: dict, code_station: str,
                          output_path: str|Path) -> None:
    """Trace la courbe T vs débit avec le débit q_obs mis en évidence."""
    r = res_station
    r["T"] = r["Periode_de_retour"]
    r["q"] = r["debit_obs"]
    r["p"] = r["frequence_non_depassement"]
    r["IC_low"] = r["Periode_de_retour_interval_confiance_bas"]
    r["IC_high"] = r["Periode_de_retour_interval_confiance_haut"]
    res = res_estimation
    pcdf = res["pcdf"]
    emp = res["empirical"]
    T_min = min(emp["T"].min(), 1.0)
    T_max = emp["T"].max() * 1.05
    mask = np.isfinite(pcdf["T"]) & (pcdf["T"] >= T_min) & (pcdf["T"] <= T_max)

    # Borne Y : basée sur les données observées + marge 20%, même logique que plot_results
    y_max = emp["y_sorted"].max() * 1.2
    y_min = 0.0

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(T_min, T_max)
    ax.set_ylim(y_min, y_max)

    ax.fill_between(pcdf["T"][mask], pcdf["IC_low"][mask], pcdf["IC_high"][mask],
                    color="firebrick", alpha=0.15, label="IC 95% (PBOOT)")
    ax.plot(pcdf["T"][mask], pcdf["x"][mask], color="firebrick",
            linewidth=1.5, label="Loi Log-Normale (L-mom)")
    ax.scatter(emp["T"], emp["y_sorted"], color="steelblue", s=20, zorder=5,
               alpha=0.8, label="Observations")

    # Lignes de lecture
    ax.axhline(q_obs, color="darkorange", linestyle="--", linewidth=1.2)
    ax.axvline(r["T"], color="darkorange", linestyle="--", linewidth=1.2)
    ax.plot(r["T"], q_obs, "o", color="darkorange", markersize=9, zorder=10,
            label=f"q = {q_obs:.2f} m³/s → T = {r['T']:.1f} ans")

    # Zone IC sur T (bande verticale)
    ax.axvspan(r["IC_low"], r["IC_high"], color="darkorange", alpha=0.10,
               label=f"IC T : [{r['IC_low']:.1f} – {r['IC_high']:.1f}] ans")

    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.set_xlabel("Période de retour T (ans)", fontsize=11)
    ax.set_ylabel("VCN3 (m³/s)", fontsize=11)
    ax.set_title(f"Période de retour pour q = {q_obs:.4f} m³/s - Station {code_station}", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, which="both", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    # plt.show()
    plt.close()
    logger.info(f"Graphique sauvegardé : {output_path}")

def plot_result_station(code_station: str, mois:str, result_station:dict, resultats_frequence_periode_retour:dict):
    resultats = resultats_frequence_periode_retour
    plot_results(resultats,
                 OUTPUT_DIR / "VCN3" / "plot_stations" / f"analyse-frequentielle-{code_station}-{mois:02}.png",
                 title=f"VCN3 — Analyse fréquentielle - Station : {code_station}")
    vcn3_observation = result_station["debit_obs"]
    plot_period_from_flow(q_obs=vcn3_observation, res_station=result_station, res_estimation=resultats, code_station=code_station,
                          output_path=OUTPUT_DIR / "VCN3" / "plot_stations" / f"periode-de-retour-{code_station}-{mois:02}.png")


def create_geojson_from_periode_de_retour(annee_mois:str, code_sandre:str, is_result_plotted:bool=False):
    chemin_periode_de_retour = utils.get_path_periode_de_retour(code_sandre, annee_mois)
    f_T.ensure_frequence_non_depassement_periode_retour_calcule(annee_mois, code_sandre, is_result_plotted)

    output_path = OUTPUT_DIR / "QGIS" / "frequence_periode_de_retour" / f"periode-de-retour-{code_sandre}-{annee_mois}.geojson"

    create_geojson_from_path(chemin_periode_de_retour, output_path, annee_mois, code_sandre)

    generate_raster_from_periode_de_retour_geojson(output_path, output_path.with_stem(output_path.stem+"_frequence_non_depassement").with_suffix(".png"), "frequence_non_depassement",GeographicScaleClip.BASSIN,"06",f"Fréquence de non dépassemment de {annee_mois} de la liste {code_sandre}.")

    generate_raster_from_periode_de_retour_geojson(output_path, output_path.with_stem(output_path.stem+"_periode_de_non_retour").with_suffix(".png"), "Periode_de_retour",GeographicScaleClip.BASSIN,"06",f"Période de retour de {annee_mois} de la liste {code_sandre}.")


def generate_raster_from_hydraulicite_geojson(geojson_path: Path, output_path: Path, value_column: str,
                                              geographic_scale: GeographicScaleClip, code_zone: str, titre: str,
                                              no_interpolation: bool = False):
    """
    Génère un raster à partir d'un fichier GeoJSON d'hydraulicité existant.

    :param geojson_path: Chemin vers le fichier GeoJSON à rasteriser
    :param output_path: Chemin de sortie pour l'image raster
    :param value_column: Nom de la colonne contenant les valeurs à rasteriser (ex: hydraulicite)
    :param geographic_scale: L'échelle géographique
    :param code_zone: Le code de la zone géographique
    :param titre: Titre du graphique raster
    :param no_interpolation: Si True, crée une carte de points sans interpolation (défaut: False)
    :return: Rien
    """
    try:
        # Charger le GeoJSON
        gdf = gpd.read_file(geojson_path).to_crs(2154)

        if value_column not in gdf.columns:
            logger.error(f"La colonne '{value_column}' n'existe pas dans le GeoDataFrame")
            raise ValueError(f"Colonne {value_column} introuvable dans {geojson_path}")

        # Générer le raster
        rasterize_geodataframe_geographiv_zone(
            gdf,
            value_column,
            geographic_scale,
            code_zone,
            output_path,
            titre,
            no_interpolation
        )
        logger.info(f"Raster hydraulicité généré : {output_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la génération du raster hydraulicité : {e}")
        raise


def generate_raster_from_periode_de_retour_geojson(geojson_path: Path, output_path: Path, value_column: str,
                                              geographic_scale: GeographicScaleClip, code_zone: str, titre: str,
                                              no_interpolation: bool = False):
    """
    Génère un raster à partir d'un fichier GeoJSON de période de retour existant

    :param geojson_path: Chemin vers le fichier GeoJSON à rasteriser
    :param output_path: Chemin de sortie pour l'image raster
    :param value_column: Nom de la colonne contenant les valeurs à rasteriser (ex: hydraulicite)
    :param geographic_scale: L'échelle géographique
    :param code_zone: Le code de la zone géographique
    :param titre: Titre du graphique raster
    :param no_interpolation: Si True, crée une carte de points sans interpolation (défaut: False)
    :return: Rien
    """
    try:
        # Charger le GeoJSON
        gdf = gpd.read_file(geojson_path).to_crs(2154)

        if value_column not in gdf.columns:
            logger.error(f"La colonne '{value_column}' n'existe pas dans le GeoDataFrame")
            raise ValueError(f"Colonne {value_column} introuvable dans {geojson_path}")

        # On borne les valeurs.
        gdf["Periode_de_retour"] = gdf["Periode_de_retour"].clip(lower=0, upper=10)

        # Générer le raster
        rasterize_geodataframe_geographiv_zone(
            gdf,
            value_column,
            geographic_scale,
            code_zone,
            output_path,
            titre,
            no_interpolation
        )
        logger.info(f"Raster periode de retour généré : {output_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la génération du raster periode de retour : {e}")
        raise


def create_geojson_from_hydraulicite(annee_mois:str, code_sandre:str):
    """
    Exporte un geojson de l'hydraulicite du mois AAAA-MM des stations correspondant au code_sandre.
    :param annee_mois:
    :param code_sandre:
    :return:
    """
    chemin_hydraulicite = utils.get_path_hydraulicite(code_sandre, annee_mois)
    calcul_hydraulicite.calcul_hydraulicite_mensuel(annee_mois, code_sandre)

    output_path = OUTPUT_DIR / "QGIS" / "hydraulicite" / f"hydraulicite-{code_sandre}-{annee_mois}.geojson"

    create_geojson_from_path(chemin_hydraulicite, output_path, annee_mois, code_sandre)

    generate_raster_from_hydraulicite_geojson(output_path, output_path.with_suffix(".png"), "hydraulicite",
                                              GeographicScaleClip.BASSIN, "06",
                                              f"Hydraulicité de {annee_mois} pour les stations de la liste {code_sandre}")


if __name__ == "__main__":
    #create_geojson_from_hydraulicite("2026-04", "BSH001")
    #create_geojson_from_hydraulicite("2026-04", "BSH101")
    #create_geojson_from_hydraulicite("2026-02", "BSH001")
    #create_geojson_from_periode_de_retour("2026-04", "BSH001")
    #create_geojson_from_periode_de_retour("2026-04", "BSH001")
    #create_geojson_from_periode_de_retour("2026-05", "BSH001")
    # create_geojson_from_periode_de_retour("2026-06", "BSH101")
    # create_geojson_from_hydraulicite("2026-06", "BSH101")
    # create_geojson_from_hydraulicite("2026-05", "custom")
    # create_geojson_from_periode_de_retour("2026-05", "BSH001")
    # create_geojson_from_periode_de_retour("2026-04", "BSH001")
    # create_geojson_from_periode_de_retour("2026-05", "custom")
    # create_geojson_from_periode_de_retour("2026-04", "BSH001")
    # create_geojson_from_periode_de_retour("2026-04", "custom")
    # create_geojson_from_stations(None, None)
    # create_geojson_from_sites(None)

    create_geojson_from_periode_de_retour("2026-05", "custom",is_result_plotted=True)
    # for date in pd.date_range("2025-09-01", "2026-06-30", freq="MS"):
    #      annee_mois = date.strftime("%Y-%m")
    #      create_geojson_from_periode_de_retour(annee_mois, "custom")
