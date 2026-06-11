import pandas as pd
import geopandas as gpd
from pathlib import Path
import utils
import hydraulicite

def create_geojson_from_sites(code_sandre:str|None=None):
    """
    Suppose que le fichier a déjà été calculé.
    :param annee_mois: AAAA-MM
    :param code_sandre: Un code Sandre
    :return:
    """

    # On charge toute les stations
    stations_path = utils.get_path_stations()

    # Le fichier contient une colonne WKT : POINT(...)
    df_stations = pd.read_csv(stations_path)

    if code_sandre is not None:
        # Filtre les stations pour avoir celle avec le bon code Sandre
        df_stations_sandre = df_stations[df_stations["code_sandre_reseau_station"].astype(str).str.contains(code_sandre)]
    else:
        df_stations_sandre = df_stations

    # Conversion en GeoDataFrame
    gdf_final = gpd.GeoDataFrame(
        df_stations_sandre,
        geometry=gpd.GeoSeries.from_wkt(df_stations["geometry"]),
        crs="EPSG:4326"
    )

    # On charge toute les stations
    sites_path = utils.get_path_sites()
    df_sites = pd.DataFrame(pd.read_csv(sites_path))

    gdf_complet_sites_code_sandre = df_sites.merge(
        gdf_final,
        on="code_site",
        how="left"
    )

    # ============================================================
    # 4. Nettoyage optionnel
    # ============================================================

    # Suppression des colonnes inutiles créées automatiquement
    colonnes_a_supprimer = [
        "Unnamed: 0"
    ]

    for col in colonnes_a_supprimer:
        if col in gdf_complet_sites_code_sandre.columns:
            gdf_complet_sites_code_sandre = gdf_complet_sites_code_sandre.drop(columns=col)


    # ============================================================
    # 5. Export GeoJSON
    # ============================================================
    if code_sandre is not None:
        output_geojson = Path(f"output/QGIS/sites/sites-{code_sandre}.geojson")
    else:
        output_geojson = Path(f"output/QGIS/sites/sites.geojson")

    gdf_final.to_file(
        output_geojson,
        driver="GeoJSON"
    )

    print(f"GeoJSON créé : {output_geojson}")

if __name__ == "__main__":
    create_geojson_from_sites(code_sandre="BSH001")
    create_geojson_from_sites()
