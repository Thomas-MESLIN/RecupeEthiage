from download_meteoFrance import MeteoFranceDataType
import download_meteoFrance as DMeteo
from datetime import datetime
from pathlib import Path
import calendar
import pandas as pd
import geopandas as gpd
import meteoFrance_aggregation_donnee as MeteoAgg

def plot_geojson_from_lambert2(output_path:Path, chemin_a_plot: Path|None = None,df_ready: pd.DataFrame|None = None):
    """
    Convertis le fichier pointé ou le dataframe fournis vers un fichier geojson dont les coordonnées sont au format EPSG:27572. (lambert2 étendu).
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

    gdf.to_file(output_path, driver="GeoJSON", mode="w")


def export_geojson_range(data_freq:MeteoFranceDataType, start_date:datetime, end_date:datetime, is_data_aggregated):
    """
    Enregistre un geojson contenant toutes les données entre start_date et end_date
    :param is_data_aggregated: Si a True, les données sont aggrégés, si a False, on retrouve les données individuelles.
    :param data_freq: Type de donnée à récupérer
    :param start_date: Date de début (inclus dans l'intervalle)
    :param end_date: Date de fin (inclus dans l'intervalle)
    :return: Rien
    """
    df_intervalle = DMeteo.get_data_in_range(data_freq, start_date, end_date)
    match data_freq:
        case MeteoFranceDataType.SIM2_QUOT if start_date.date() != end_date.date():
            if is_data_aggregated:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-SIM2-aggregated-{start_date:%Y%m%d}-{end_date:%Y%m%d}.geojson")
            else:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-SIM2-{start_date:%Y%m%d}-{end_date:%Y%m%d}.geojson")
        case MeteoFranceDataType.SIM2_QUOT:
            chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-SIM2-{start_date:%Y%m%d}.geojson")
        case MeteoFranceDataType.SIM2_MENS if start_date.strftime("%Y%m") != end_date.strftime("%Y%m"):
            if is_data_aggregated:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-SIM2-aggregated-{start_date:%Y%m}-{end_date:%Y%m}.geojson")
            else:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-SIM2-{start_date:%Y%m}-{end_date:%Y%m}.geojson")
        case MeteoFranceDataType.SIM2_MENS:
            chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-SIM2-{start_date:%Y%m}.geojson")
        case _:
            raise NotImplementedError

    if is_data_aggregated:
        df_intervalle = MeteoAgg.aggregate_range(data_freq, df_intervalle)

    plot_geojson_from_lambert2(chemin_sauvegarde, df_ready=df_intervalle)


def plot_month(data_freq:MeteoFranceDataType, month_date:datetime):
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

def plot_day(day_date:datetime):
    """
    Plot un unique jour de données.
    :param day_date: La date correspondant au jour choisi.
    :return: Rien
    """
    start_date = datetime(day_date.year, day_date.month, day_date.day)
    end_date = datetime(day_date.year, day_date.month, day_date.day)
    export_geojson_range(MeteoFranceDataType.SIM2_QUOT, start_date, end_date, False)

if __name__ == "__main__":
    print("Plotting !")

    # Donnée MENS non-aggrégé de 2020 à 2026.
    export_geojson_range(MeteoFranceDataType.SIM2_MENS, datetime(2020, 1, 1), datetime(2026, 5, 1), False)

    # Donnée MENS aggrégé de 2025 à 2026.
    export_geojson_range(MeteoFranceDataType.SIM2_MENS, datetime(2025, 1, 1), datetime(2025, 12, 31), False)

    # Données non-aggrégé sur 1 mois.
    plot_month(MeteoFranceDataType.SIM2_QUOT, datetime(2026,5,1))

    # Données aggrégé de base sur 1 mois.
    plot_month(MeteoFranceDataType.SIM2_MENS, datetime(2026,5,1))

    # Données aggrégés allant d'un jour à un autre.
    export_geojson_range(MeteoFranceDataType.SIM2_QUOT, datetime(2026,5,7), datetime(2026, 5,14), True)

    # Données pour 1 seul jour
    plot_day(datetime(2026,5,18))
