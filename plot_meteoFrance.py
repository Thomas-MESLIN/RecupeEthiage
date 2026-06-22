from download_meteoFrance import MeteoFranceDataType
import download_meteoFrance as DMeteo
from datetime import datetime
from pathlib import Path
import calendar
import pandas as pd
import geopandas as gpd
import meteoFrance_aggregation_donnee as MeteoAgg
from functools import cache

def plot_geojson_from_lambert2(output_path:Path, chemin_a_plot: Path|None = None,df_ready: pd.DataFrame|None = None, clip_mask: gpd.GeoDataFrame|None = None):
    """
    Convertis le fichier pointé ou le dataframe fournis vers un fichier geojson dont les coordonnées sont au format EPSG:27572. (lambert2 étendu).
    :param clip_mask: Le masque servant à délimiter
    :param output_path: Endroit où le fichier va être sauvegardé.
    :param df_ready: Prend en paramètre un dataframe déjà lu, si il est fourni, alors le chemin à plot est ignoré.
    :param chemin_a_plot: Le chemin vers le fichier csv à convertir en geojson.
    :return: Rien
    """
    if df_ready is not None:
        res = df_ready
    elif chemin_a_plot is not None:
        if not chemin_a_plot.exists():
            raise ValueError("Le chemin à plot n'existe pas.")
        res = pd.read_csv(chemin_a_plot)
    else:
        raise ValueError("Pas de données fournie.")

    # Les coordonnées sont ne Lambert2 étendue et en hm, on les convertis donc en m.
    gdf = gpd.GeoDataFrame(
        res, geometry=gpd.points_from_xy(res.LAMBX * 100, res.LAMBY * 100), crs="EPSG:27572"
    )

    if clip_mask is not None:
        # On récupère la geometry correspondant à l'unique élément du df du masque et on compare les distances à celle-ci.
        gdf_geom = gdf[gdf.geometry.distance(clip_mask.geometry.iloc[0]) < 7000]
    else:
        gdf_geom = gdf

    gdf_geom.to_file(output_path, driver="GeoJSON", mode="w")

def get_chemin_sauvegarde(data_freq:MeteoFranceDataType, start_date:datetime, end_date:datetime, is_data_aggregated:bool) -> Path:
    match data_freq:
        case MeteoFranceDataType.SIM2_QUOT if start_date.date() != end_date.date():
            if is_data_aggregated:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-SIM2-aggregated-{start_date:%Y%m%d}-{end_date:%Y%m%d}/QUOT-SIM2-aggregated-{start_date:%Y%m%d}-{end_date:%Y%m%d}.geojson")
            else:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-SIM2-{start_date:%Y%m%d}-{end_date:%Y%m%d}/QUOT-SIM2-{start_date:%Y%m%d}-{end_date:%Y%m%d}.geojson")
        case MeteoFranceDataType.SIM2_QUOT:
            chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-SIM2-{start_date:%Y%m%d}/QUOT-SIM2-{start_date:%Y%m%d}.geojson")
        case MeteoFranceDataType.SIM2_MENS if start_date.strftime("%Y%m") != end_date.strftime("%Y%m"):
            if is_data_aggregated:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-SIM2-aggregated-{start_date:%Y%m}-{end_date:%Y%m}/MENS-SIM2-aggregated-{start_date:%Y%m}-{end_date:%Y%m}.geojson")
            else:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-SIM2-{start_date:%Y%m}-{end_date:%Y%m}/MENS-SIM2-{start_date:%Y%m}-{end_date:%Y%m}.geojson")
        case MeteoFranceDataType.SIM2_MENS:
            chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-SIM2-{start_date:%Y%m}/MENS-SIM2-{start_date:%Y%m}.geojson")
        case _:
            raise NotImplementedError
    return chemin_sauvegarde

def get_chemin_sauvegarde_departement(chemin_sauvegarde_original:Path, code_departement:str)->Path:
    nouveau_chemin = chemin_sauvegarde_original
    nouveau_chemin = nouveau_chemin.with_stem(f"{chemin_sauvegarde_original.stem}-D{code_departement}")
    nouveau_chemin = nouveau_chemin.parent / "departement" / nouveau_chemin.name
    return nouveau_chemin

def export_to_every_departement(df:pd.DataFrame, chemin_save_original:Path):
    print("Export de tous les département en cours...")
    for code in DMeteo.departement_list:
        gdf_departement = get_departement(code)
        chemin_save = get_chemin_sauvegarde_departement(chemin_save_original,code)
        chemin_save.parent.mkdir(exist_ok=True)
        plot_geojson_from_lambert2(chemin_save, df_ready=df, clip_mask=gdf_departement)
    print("Export de tous les département terminés")

def get_chemin_sauvegarde_region(chemin_sauvegarde_original:Path, code_region:str):
    nouveau_chemin = chemin_sauvegarde_original
    nouveau_chemin = nouveau_chemin.with_stem(f"{chemin_sauvegarde_original.stem}-R{code_region}")
    nouveau_chemin = nouveau_chemin.parent / "region_administrative" / nouveau_chemin.name
    return nouveau_chemin

def export_to_every_region(df:pd.DataFrame, chemin_save_original:Path):
    print("Export de toutes les régions en cours...")
    for code in DMeteo.region_list_metropole:
        gdf_region = get_region(code)
        chemin_save = get_chemin_sauvegarde_region(chemin_save_original, code)
        chemin_save.parent.mkdir(exist_ok=True)
        plot_geojson_from_lambert2(chemin_save, df_ready=df, clip_mask=gdf_region)
    print("Export de toutes les régions terminées")

def get_chemin_sauvegarde_bassin(chemin_sauvegarde_original:Path, code_bassin:str):
    nouveau_chemin = chemin_sauvegarde_original
    nouveau_chemin = nouveau_chemin.with_stem(f"{chemin_sauvegarde_original.stem}-B{code_bassin}")
    nouveau_chemin = nouveau_chemin.parent / "bassin" / nouveau_chemin.name
    return nouveau_chemin

def export_to_every_bassin(df:pd.DataFrame, chemin_save_original:Path):
    print("Export de tous les bassins en cours...")
    for code in DMeteo.code_bassin_versant_list:
        gdf_bassin = get_bassin_versant(code)
        chemin_save = get_chemin_sauvegarde_bassin(chemin_save_original, code)
        chemin_save.parent.mkdir(exist_ok=True)
        plot_geojson_from_lambert2(chemin_save, df_ready=df, clip_mask=gdf_bassin)
    print("Export de toutes les bassins terminées")

def export_geojson_range(data_freq:MeteoFranceDataType, start_date:datetime, end_date:datetime, is_data_aggregated:bool):
    """
    Enregistre un geojson contenant toutes les données entre start_date et end_date
    :param is_data_aggregated: Si a True, les données sont aggrégés, si a False, on retrouve les données individuelles.
    :param data_freq: Type de donnée à récupérer
    :param start_date: Date de début (inclus dans l'intervalle)
    :param end_date: Date de fin (inclus dans l'intervalle)
    :return: Rien
    """
    df_intervalle = DMeteo.get_data_in_range(data_freq, start_date, end_date)
    if df_intervalle.empty:
        print(f"L'intervalle de données ({start_date} - {end_date}) est vide. Abandon.")
        return

    if is_data_aggregated:
        df_intervalle = MeteoAgg.aggregate_range(data_freq, df_intervalle)

    chemin_sauvegarde = get_chemin_sauvegarde(data_freq, start_date, end_date, is_data_aggregated)
    chemin_sauvegarde.parent.mkdir(exist_ok=True)
    # On export ele geojson qui a toute les données de la France.
    plot_geojson_from_lambert2(chemin_sauvegarde, df_ready=df_intervalle)

    export_to_every_bassin(df_intervalle, chemin_sauvegarde)
    export_to_every_region(df_intervalle, chemin_sauvegarde)
    export_to_every_departement(df_intervalle, chemin_sauvegarde)


def export_geojson_month(data_freq:MeteoFranceDataType, month_date:datetime):
    """
    Plot un mois entier de données, les données ne sont pas aggrégés.
    Si vous souhaitez les données QUOT aggrégé sur le mois, utilisez les données MENS directement.
    :param data_freq: Si le data_freq est sur MENS, prend le mois de la datetime, sinon prend tous les jours de l'années
    :param month_date: La date correspondant au mois choisi.
    :return: Rien
    """
    start_date = datetime(month_date.year, month_date.month, 1)
    end_date = datetime(month_date.year, month_date.month, calendar.monthrange(month_date.year, month_date.month)[1])
    export_geojson_range(data_freq, start_date, end_date, False)

def export_geojson_day(day_date:datetime):
    """
    Plot un unique jour de données.
    :param day_date: La date correspondant au jour choisi.
    :return: Rien
    """
    start_date = datetime(day_date.year, day_date.month, day_date.day)
    end_date = datetime(day_date.year, day_date.month, day_date.day)
    export_geojson_range(MeteoFranceDataType.SIM2_QUOT, start_date, end_date, False)

@cache
def get_all_region_geodf():
    chemin_archive = Path("output/meteoFrance/downloaded_data/delimitation_qgis_archive/regions-100m.geojson.gz")
    chemin = Path("output/meteoFrance/downloaded_data/delimitation_qgis/regions-100m.geojson")
    id_data_gouv = "aa76860a-51af-4744-a593-4c19af2570b8"
    if not chemin.exists():
        DMeteo.download_and_extract(id_data_gouv, chemin_archive, chemin)
    df_toute_region = gpd.read_file(chemin).to_crs(crs="EPSG:27572")
    df_metropole = df_toute_region[df_toute_region["code"].isin(DMeteo.region_list_metropole)].copy()
    return df_metropole

@cache
def get_all_departement_geodf():
    chemin_archive = Path("output/meteoFrance/downloaded_data/delimitation_qgis_archive/departements-50m.geojson.gz")
    chemin = Path("output/meteoFrance/downloaded_data/delimitation_qgis/departements-50m.geojson")
    id_data_gouv = "93a2ba8f-e30f-4916-a73b-0c4d87247ace"
    if not chemin.exists():
        DMeteo.download_and_extract(id_data_gouv, chemin_archive, chemin)
    df_tout_departement = gpd.read_file(chemin).to_crs(crs="EPSG:27572")
    df_departement_aura = df_tout_departement[df_tout_departement["code"].isin(DMeteo.departement_list)].copy()
    return df_departement_aura

@cache
def get_all_bassin_versant():
    chemin_archive = Path("output/meteoFrance/downloaded_data/delimitation_qgis_archive/bassin-hydrographique.geojson.zip")
    chemin = Path("output/meteoFrance/downloaded_data/delimitation_qgis/BassinHydrographique_FXX.geojson")
    id_data_gouv = "b0761a88-b59f-466f-a3cc-b97f237fd732"
    if not chemin.exists():
        DMeteo.download_and_extract(id_data_gouv, chemin_archive, chemin)
    df_tout_bassin = gpd.read_file(chemin).to_crs(crs="EPSG:27572")
    return df_tout_bassin

def get_departement(code:str):
    df = get_all_departement_geodf()
    df_departement = df[df["code"] == code]
    return df_departement

def get_region(code:str):
    df = get_all_region_geodf()
    df_region = df[df["code"] == code]
    return df_region

def get_bassin_versant(code:str):
    df = get_all_bassin_versant()
    df_bassin = df[df["CdBH"] == code]
    return df_bassin

def clip_by_region(code:str):
    pass

if __name__ == "__main__":
    print("Plotting !")

    # gdf_region = get_all_region_geodf()
    # print(gdf_region)
    # region = get_region("93")
    # print(region)
    # gdf_departement = get_all_departement_geodf()
    # print(gdf_departement)
    # departement = get_departement("71")
    # print(departement)
    # SWI d'aujourd'hui
    export_geojson_day(datetime(2026,6,17))

    # Donnée MENS aggrégé de 2025 à 2026.
    # export_geojson_range(MeteoFranceDataType.SIM2_MENS, datetime(2025, 1, 1), datetime(2025, 12, 31), False)
    # Cumul depuis le dernier bulletin 10 juin et nombre de jour où la temptérature est au-dessus de la normale.
    today = datetime.today()
    export_geojson_range(MeteoFranceDataType.SIM2_QUOT, datetime(2026, 6, 10), today, True)

    # SWI du 10 juin
    export_geojson_day(datetime(2026,6,10))




    #
    # # Données pour 1 seul jour
    # plot_day(datetime(2026,5,18))
    #
    # # Données non-aggrégé sur 1 mois.
    # plot_month(MeteoFranceDataType.SIM2_QUOT, datetime(2026,5,1))
    #
    # # Données aggrégé de base sur 1 mois.
    # plot_month(MeteoFranceDataType.SIM2_MENS, datetime(2026,5,1))
    #
    # # Données aggrégés allant d'un jour à un autre.
    # export_geojson_range(MeteoFranceDataType.SIM2_QUOT, datetime(2026,5,7), datetime(2026, 5,14), True)
    #
    # # Donnée MENS non-aggrégé de 2020 à 2026.
    # export_geojson_range(MeteoFranceDataType.SIM2_MENS, datetime(2020, 1, 1), datetime(2026, 5, 1), False)
