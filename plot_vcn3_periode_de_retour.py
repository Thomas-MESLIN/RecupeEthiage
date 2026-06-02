
import pandas as pd
import geopandas as gpd
from pathlib import Path
import calcul_hydraulicite_mensuel

def create_geojson_from_periode_de_retour(annee_mois:str, code_sandre:str):
    """
    Suppose que le fichier a déjà été calculé.
    :param code_sandre: Code Sandre à mettre en face des stations utilisées.
    :param annee_mois: AAAA-MM
    :return:
    """
    # ============================================================
    # 1. Chargement des données du vnc3
    # ============================================================

    data_hydro_path = Path(f"output/VCN3/analyse_frequence_periode/analyse-frequence-{annee_mois}.csv")

    df_hydro = pd.read_csv(data_hydro_path)

    # ============================================================
    # 2. Chargement des stations
    # ============================================================

    # On charge toute les stations
    stations_path = Path("output/hubeau/downloaded_data/stations/stations.csv")

    # Le fichier contient une colonne WKT : POINT(...)
    df_stations = pd.read_csv(stations_path)

    # Filtre les stations pour avoir celle avec le bon code Sandre
    df_stations_sandre = df_stations[df_stations["code_sandre_reseau_station"].astype(str).str.contains(code_sandre)]

    # On filtre les stations
    df_stations_sandre_ouverte = df_stations_sandre[
        (annee_mois < df_stations_sandre["date_fermeture_station"].astype(str)) &
        (df_stations_sandre["date_ouverture_station"].astype(str) < annee_mois)
    ]

    # Conversion en GeoDataFrame
    gdf_stations = gpd.GeoDataFrame(
        df_stations_sandre_ouverte,
        geometry=gpd.GeoSeries.from_wkt(df_stations["geometry"]),
        crs="EPSG:4326"
    )

    # ============================================================
    # 3. Jointure sur code_station
    # ============================================================

    gdf_final = gdf_stations.merge(
        df_hydro,
        on="code_station",
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
        if col in gdf_final.columns:
            gdf_final = gdf_final.drop(columns=col)


    # ============================================================
    # 5. Export GeoJSON
    # ============================================================

    output_geojson = Path(f"output/VCN3/analyse_frequence_periode/periode-de-retour-{annee_mois}.geojson")

    gdf_final.to_file(
        output_geojson,
        driver="GeoJSON"
    )

    print(f"GeoJSON créé : {output_geojson}")

if __name__ == "__main__":
    #create_geojson_from_hydraulicite("2026-04", "BSH001")
    #create_geojson_from_hydraulicite("2026-04", "BSH101")
    #create_geojson_from_hydraulicite("2026-02", "BSH001")
    #create_geojson_from_vcn3("2025-07", "BSH001")
    create_geojson_from_periode_de_retour("2026-04", "BSH001")
