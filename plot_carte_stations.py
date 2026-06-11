import pandas as pd
import geopandas as gpd
from pathlib import Path
import utils
import hydraulicite

def create_geojson_from_stations(code_sandre:str, annee_mois:str|None=None):
    """
    Suppose que le fichier a déjà été calculé.
    :param annee_mois: AAAA-MM
    :param code_sandre: Un code Sandre
    :return:
    """

    # On charge toute les stations
    stations_path = Path("output/hubeau/downloaded_data/stations/stations.csv")

    # Le fichier contient une colonne WKT : POINT(...)
    df_stations = utils.get_stations(code_sandre, annee_mois)

        # Conversion en GeoDataFrame
    gdf_final = gpd.GeoDataFrame(
        df_stations,
        geometry=gpd.GeoSeries.from_wkt(df_stations["geometry"]),
        crs="EPSG:4326"
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
    if annee_mois is not None:
        output_geojson = Path(f"output/QGIS/stations/stations-ouverte-{code_sandre}-{annee_mois}.geojson")
    else:
        output_geojson = Path(f"output/QGIS/stations/stations-{code_sandre}.geojson")

    gdf_final.to_file(
        output_geojson,
        driver="GeoJSON"
    )

    print(f"GeoJSON créé : {output_geojson}")

if __name__ == "__main__":
    create_geojson_from_stations("BSH001", annee_mois="2026-04")
    create_geojson_from_stations("BSH001")
    create_geojson_from_stations("custom")
