from download_meteoFrance import MeteoFranceDataType
import download_meteoFrance as dm
from datetime import datetime
from pathlib import Path
import calendar
import pandas as pd
import geopandas as gpd

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
            raise ValueError("Le chemin n'existe pas à plot n'existe pas.")
        res = pd.read_csv(chemin_a_plot)
    else:
        raise ValueError("Pas de données fournie.")

    # Les coordonnées sont ne Lambert2 étendue et en hm, on les convertis donc en m.
    gdf = gpd.GeoDataFrame(
        res, geometry=gpd.points_from_xy(res.LAMBX * 100, res.LAMBY * 100), crs="EPSG:27572"
    )

    gdf.to_file(output_path, driver="GeoJSON", mode="w")


def plot_any_date(data_freq:MeteoFranceDataType, start_date:datetime, end_date:datetime):
    """
    Enregistre un geojson contenant toutes les données entre start_date et end_date
    :param data_freq:
    :param start_date:
    :param end_date:
    :return: Rien
    """
    df_intervalle = dm.get_data_in_range(data_freq, start_date, end_date)
    match data_freq:
        case MeteoFranceDataType.SIM2_QUOT:
            if start_date.strftime("%Y%m%d") != end_date.strftime("%Y%m%d"):
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-SIM2-{start_date:%Y%m%d}-{end_date:%Y%m%d}.geojson")
            else:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-SIM2-{start_date:%Y%m%d}.geojson")
        case MeteoFranceDataType.SIM2_MENS:
            if start_date.strftime("%Y%m") != end_date.strftime("%Y%m"):
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-SIM2-{start_date:%Y%m}-{end_date:%Y%m}.geojson")
            else:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-SIM2-{start_date:%Y%m}.geojson")
        case _:
            raise NotImplementedError
    plot_geojson_from_lambert2(chemin_sauvegarde, df_ready=df_intervalle)


def plot_month(data_freq:MeteoFranceDataType, month_date:datetime):
    """
    Plot un mois entier de données.
    :param data_freq: Si le data_freq est sur MENS, prend le mois de la datetim, sinon prend tous les jours de l'années
    :param month_date: La date correspondant au mois choisi.
    :return: Rien
    """
    start_date = datetime(month_date.year, month_date.month, 1)
    end_date = datetime(month_date.year, month_date.month, calendar.monthrange(month_date.year, month_date.month)[1])
    plot_any_date(data_freq, start_date, end_date)

def create_map_from_geojson(chemin:Path, colonne_to_map:str):
    pass

if __name__ == "__main__":
    print("Plotting !")
    annee = 2026
    mois = 5

    # nombre_de_jour = calendar.monthrange(annee, mois)[1]
    # start_date = datetime(annee, mois, 1)
    # end_date = datetime(annee, mois, nombre_de_jour)

    # nombre_de_jour = calendar.monthrange(annee, mois - 1)[1]
    # start_date = datetime(annee, mois - 1, nombre_de_jour)
    # end_date = datetime(annee, mois, 1)
    #
    # plot_any_date(MeteoFranceDataType.SIM2_QUOT, start_date=start_date, end_date=end_date)
    #
    # plot_any_date(MeteoFranceDataType.SIM2_MENS, start_date=start_date, end_date=end_date)
    #
    #

    # for date in pd.date_range("2020-01-01", "2026-05-01", freq="MS"):
    #     print(date)
    #     plot_month(MeteoFranceDataType.SIM2_MENS, date)
    plot_any_date(MeteoFranceDataType.SIM2_MENS, datetime(2020,1,1), datetime(2026, 5,1))
    plot_any_date(MeteoFranceDataType.SIM2_QUOT, datetime(2026,5,1), datetime(2026, 5,31))
