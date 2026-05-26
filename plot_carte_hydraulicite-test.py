import pandas as pd
import geopandas as gpd
from pathlib import Path

# ============================================================
# 1. Chargement des données d'hydraulicité
# ============================================================

data_hydro_path = Path("output/hydraulicite/hydraulicite-BSH001-2020-01.csv")

df_hydro = pd.read_csv(data_hydro_path)

print(df_hydro.head())


# ============================================================
# 2. Chargement des stations
# ============================================================

stations_path = Path("output/stations.csv")

# Le fichier contient une colonne WKT : POINT(...)
df_stations = pd.read_csv(stations_path)

# Conversion en GeoDataFrame
gdf_stations = gpd.GeoDataFrame(
    df_stations,
    geometry=gpd.GeoSeries.from_wkt(df_stations["geometry"]),
    crs="EPSG:4326"
)

print(gdf_stations.head())


# ============================================================
# 3. Jointure sur code_station
# ============================================================

gdf_final = gdf_stations.merge(
    df_hydro,
    on="code_station",
    how="inner"
)

print(gdf_final.head())


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

output_geojson = Path("output/hydraulicite/hydraulicite.geojson")

gdf_final.to_file(
    output_geojson,
    driver="GeoJSON"
)

print(f"GeoJSON créé : {output_geojson}")