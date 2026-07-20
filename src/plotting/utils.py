from src.model.enums import GeographicScaleClip,MeteoFranceDataType
from src.config.paths import OUTPUT_DIR,DATA_DIR
from pathlib import Path
import pandas as pd
import geopandas as gpd
import src.io.download_meteoFrance as DMeteo
from functools import cache

@cache
def get_all_geographic_geodf(geographic_scale:GeographicScaleClip):
    match geographic_scale:
        case GeographicScaleClip.REGION_BASSIN | GeographicScaleClip.REGION_ADMINISTRATIVE:
            chemin_archive = OUTPUT_DIR / "meteoFrance" / "downloaded_data" / "delimitation_qgis_archive" / "regions-100m.geojson.gz"
            chemin = OUTPUT_DIR / "meteoFrance" / "downloaded_data" / "delimitation_qgis" / "regions-100m.geojson"
            id_data_gouv = "aa76860a-51af-4744-a593-4c19af2570b8"
        case GeographicScaleClip.DEPARTEMENT_BASSIN | GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF:
            chemin_archive = OUTPUT_DIR / "meteoFrance" / "downloaded_data" / "delimitation_qgis_archive" / "departements-50m.geojson.gz"
            chemin = OUTPUT_DIR / "meteoFrance" / "downloaded_data" / "delimitation_qgis" / "departements-50m.geojson"
            id_data_gouv = "93a2ba8f-e30f-4916-a73b-0c4d87247ace"
        case GeographicScaleClip.BASSIN:
            chemin_archive = OUTPUT_DIR / "meteoFrance" / "downloaded_data" / "delimitation_qgis_archive" / "bassin-hydrographique.geojson.zip"
            chemin = OUTPUT_DIR / "meteoFrance" / "downloaded_data" / "delimitation_qgis" / "BassinHydrographique_FXX.geojson"
            id_data_gouv = "b0761a88-b59f-466f-a3cc-b97f237fd732"
        case GeographicScaleClip.ECOREGION_HYDROLOGIQUE:
            chemin_archive = OUTPUT_DIR / "meteoFrance" / "downloaded_data" / "delimitation_qgis_archive" / "Climato_hydro_region.geojson.zip"
            chemin = OUTPUT_DIR / "meteoFrance" / "downloaded_data" / "delimitation_qgis" / "Climato_hydro_region.geojson"
            id_data_gouv = "bf4e654b-9aa9-49fd-b745-12219953268b"
        case _:
            raise NotImplementedError

    if not chemin.exists():
        DMeteo.download_and_extract(id_data_gouv, chemin_archive, chemin)
    df_tout_departement = gpd.read_file(chemin).to_crs(crs="EPSG:27572")
    return df_tout_departement


def get_geographic_list(geographic_scale: GeographicScaleClip):
    match geographic_scale:
        case GeographicScaleClip.NATIONAL:
            return []
        case GeographicScaleClip.BASSIN:
            file_to_read = DATA_DIR / Path("liste_bassin.csv")
        case GeographicScaleClip.REGION_BASSIN | GeographicScaleClip.REGION_ADMINISTRATIVE:
            file_to_read = DATA_DIR / Path("liste_region.csv")
        case GeographicScaleClip.DEPARTEMENT_BASSIN | GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF:
            file_to_read = DATA_DIR / Path("liste_departement.csv")
        case GeographicScaleClip.ECOREGION_HYDROLOGIQUE:
            file_to_read = DATA_DIR / Path("liste_eco_hydro.csv")
        case _:
            raise NotImplementedError

    if file_to_read.exists():
        df_liste = pd.read_csv(file_to_read, dtype={"code":str})
        liste = df_liste[df_liste.columns[0]].to_list()
    else:
        raise FileNotFoundError(f"Le fichier {file_to_read} n'existe pas !")

    return liste


def get_geographic_element(geographic_scale:GeographicScaleClip, code:str):
    df = get_all_geographic_geodf(geographic_scale)
    match geographic_scale:
        case GeographicScaleClip.BASSIN:
            nom_colonne = "CdBH"
        case GeographicScaleClip.DEPARTEMENT_BASSIN | GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF:
            nom_colonne = "code"
        case GeographicScaleClip.REGION_BASSIN | GeographicScaleClip.REGION_ADMINISTRATIVE:
            nom_colonne = "code"
        case GeographicScaleClip.ECOREGION_HYDROLOGIQUE:
            nom_colonne = "code"
        case _:
            raise NotImplementedError

    df_departement = df[df[nom_colonne] == code]
    return df_departement

def get_bassin_versant(code:str) -> gpd.GeoDataFrame:
    df = get_all_geographic_geodf(GeographicScaleClip.BASSIN)
    df_bassin = df[df["CdBH"] == code]
    return df_bassin
