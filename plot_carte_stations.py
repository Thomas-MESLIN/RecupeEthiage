import pandas as pd
import geopandas as gpd
from pathlib import Path
import utils
import calcul_hydraulicite_mensuel

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
    df_stations = pd.read_csv(stations_path)

    # Filtre les stations pour avoir celle avec le bon code Sandre
    df_stations_sandre = df_stations[df_stations["code_sandre_reseau_station"].astype(str).str.contains(code_sandre)]

    # On filtre les stations ouvertes si une annee et un mois sont précisé
    if annee_mois is not None:
        df_stations_sandre_ouverte = df_stations_sandre[
            (annee_mois < df_stations_sandre["date_fermeture_station"].astype(str)) &
            (df_stations_sandre["date_ouverture_station"].astype(str) < annee_mois)
        ]
    else:
        df_stations_sandre_ouverte = df_stations_sandre

    # Conversion en GeoDataFrame
    gdf_final = gpd.GeoDataFrame(
        df_stations_sandre_ouverte,
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
