
import pandas as pd
import geopandas as gpd
from pathlib import Path
import utils
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import calcul_vcn3_frequence_retour_claude

def create_geojson_from_periode_de_retour(annee_mois:str, code_sandre:str, is_result_plotted:bool=False):
    """
    Suppose que le fichier a déjà été calculé.
    :param is_result_plotted: Génère les graphique station par station pour le calcul desp ériode de retour.
    :param code_sandre: Code Sandre à mettre en face des stations utilisées.
    :param annee_mois: AAAA-MM
    :return:
    """
    # ============================================================
    # 1. Chargement des données du vnc3
    # ============================================================
    calcul_vcn3_frequence_retour_claude.ensure_frequence_non_depassement_periode_retour_calcule(annee_mois, code_sandre, is_result_plotted)
    data_hydro_path = utils.get_path_periode_de_retour(code_sandre, annee_mois)

    df_hydro = pd.read_csv(data_hydro_path)

    # ============================================================
    # 2. Chargement des stations
    # ============================================================

    # On charge toute les stations active ce mois là.
    df_stations = utils.get_stations(code_sandre, annee_mois)

    # Conversion en GeoDataFrame
    gdf_stations = gpd.GeoDataFrame(
        df_stations,
        geometry=gpd.GeoSeries.from_wkt(df_stations["geometry"]),
        crs="EPSG:4326"
    )

    # ============================================================
    # 3. Jointure sur code_station
    # ============================================================

    gdf_final_avec_station = gdf_stations.merge(
        df_hydro,
        on="code_station",
        how="left"
    )

    # On charge toute les sites
    sites_path = utils.get_path_sites()
    # Le fichier contient une colonne WKT : POINT(...)
    df_sites = pd.DataFrame(pd.read_csv(sites_path))

    # ============================================================
    # 3. Jointure sur code_station
    # ============================================================

    gdf_final = gdf_final_avec_station.merge(
        df_sites,
        on="code_site",
        how="inner"
    )

    # ============================================================
    # 4. Nettoyage optionnel
    # ============================================================

    # Suppression des colonnes inutiles créées automatiquement
    colonnes_a_supprimer = [
        "Unnamed: 0"
    ]

    for col in colonnes_a_supprimer:
        if col in gdf_final.columns:
            gdf_final = gdf_final.drop(columns=col)


    # ============================================================
    # 5. Export GeoJSON
    # ============================================================

    output_geojson = Path(f"output/QGIS/VCN3_periode_de_retour/periode-de-retour-{code_sandre}-{annee_mois}.geojson")

    gdf_final.to_file(
        output_geojson,
        driver="GeoJSON"
    )

    print(f"GeoJSON créé : {output_geojson}")


# ---------------------------------------------------------------------------
# 5. Affichage console
# ---------------------------------------------------------------------------

def print_results(res: dict) -> None:
    print("=" * 65)
    print("  Loi : Log-Normale  |  Estimateur : L-moments  |  IC : PBOOT")
    print(f"  µ (log) = {res['mu']:.4f}   σ (log) = {res['sigma']:.4f}")
    print(f"  p0 (prob. débit nul) = {res['p0']:.3f}")
    print(f"  n total = {len(res['y'])}   n positifs = {len(res['z'])}")
    print("=" * 65)
    print(f"\n{'T (ans)':>10}  {'p non-dép.':>12}  {'VCN3 (m³/s)':>14}  {'IC bas':>10}  {'IC haut':>10}")
    print("-" * 65)
    q = res["quantiles"]
    for T, p, qv, ic_l, ic_h in zip(q["T"], q["p"], q["q"], q["IC_low"], q["IC_high"]):
        print(f"{T:>10.0f}  {p:>12.4f}  {qv:>14.4f}  {ic_l:>10.4f}  {ic_h:>10.4f}")
    print()


# ---------------------------------------------------------------------------
# 6. Tracé
# ---------------------------------------------------------------------------

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

    # -------------------------------------------------------------------
    # Graphique 3 : CDF — débit vs probabilité de non-dépassement
    # -------------------------------------------------------------------
    ax3 = axes[2]
    ax3.set_xlim(y_min, y_max)
    ax3.set_ylim(0, 1)

    ax3.plot(pcdf["x"], pcdf["cdf"], color="firebrick", linewidth=1.5,
             label="CDF Log-Normale (L-mom)")
    ax3.scatter(emp["y_sorted"], emp["freq"], color="steelblue", s=20,
                zorder=5, alpha=0.8, label="Fréquences empiriques (Hazen)")
    if res["p0"] > 0:
        ax3.axhline(res["p0"], color="gray", linestyle="--", linewidth=0.8,
                    label=f"p0 = {res['p0']:.2f}")
    ax3.set_xlabel("VCN3 (m³/s)", fontsize=11)
    ax3.set_ylabel("Probabilité de non-dépassement", fontsize=11)
    ax3.set_title("CDF empirique vs théorique")
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    # plt.show()
    print(f"Graphique sauvegardé : {output_path}")



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
    print(f"Graphique sauvegardé : {output_path}")

def plot_result_station(code_station: str, mois:str, result_station:dict, resultats_frequence_periode_retour:dict):
    resultats = resultats_frequence_periode_retour
    plot_results(resultats,
                 Path(f"output/VCN3/plot_stations/analyse-frequentielle-{code_station}-{mois:02}.png"),
                 title=f"VCN3 — Analyse fréquentielle - Station : {code_station}")
    vcn3_observation = result_station["debit_obs"]
    plot_period_from_flow(q_obs=vcn3_observation, res_station=result_station, res_estimation=resultats, code_station=code_station,
                          output_path=Path(f"output/VCN3/plot_stations/periode-de-retour-{code_station}-{mois:02}.png"))


if __name__ == "__main__":
    #create_geojson_from_hydraulicite("2026-04", "BSH001")
    #create_geojson_from_hydraulicite("2026-04", "BSH101")
    #create_geojson_from_hydraulicite("2026-02", "BSH001")
    #create_geojson_from_periode_de_retour("2026-04", "BSH001")
    #create_geojson_from_periode_de_retour("2026-04", "BSH001")
    #create_geojson_from_periode_de_retour("2026-05", "BSH001")
    create_geojson_from_periode_de_retour("2026-05", "BSH001")
    create_geojson_from_periode_de_retour("2026-04", "BSH001")
    create_geojson_from_periode_de_retour("2026-05", "custom")
    create_geojson_from_periode_de_retour("2026-04", "custom")
