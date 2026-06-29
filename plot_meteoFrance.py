from tqdm import tqdm
import download_meteoFrance
from download_meteoFrance import MeteoFranceDataType, GeographicScaleClip
import download_meteoFrance as DMeteo
from datetime import datetime
from pathlib import Path
import calendar
import pandas as pd
import geopandas as gpd
import meteoFrance_aggregation_donnee as MeteoAgg
from meteoFrance_aggregation_donnee import GroupByMethod
from functools import cache
import matplotlib.pyplot as plt

def to_lambert2_geodataframe(data_freq:MeteoFranceDataType, df_to_convert:pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Convertis le DataFrame en GeoDataFrame, doit avoir les colonne LAMBX et LAMBY et être en coordonnées EPSG:27572
    :param df_to_convert: Le DataFrame a convertir ne GeoDataFrame.
    :return: Le GeoDataFrame convertis.
    """
    match data_freq:
        case MeteoFranceDataType.SIM2_QUOT | MeteoFranceDataType.SIM2_MENS:
            return gpd.GeoDataFrame(df_to_convert,
                                    geometry=gpd.points_from_xy(df_to_convert.LAMBX * 100, df_to_convert.LAMBY * 100),
                                    crs="EPSG:27572")
        case MeteoFranceDataType.QUOT | MeteoFranceDataType.MENS:
            return gpd.GeoDataFrame(df_to_convert,
                                    geometry=gpd.points_from_xy(df_to_convert.LON, df_to_convert.LAT),
                                    crs="EPSG:4326").to_crs("EPSG:27572")

def clip_with_distance(gdf_to_clip : gpd.GeoDataFrame, clip_mask:gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Clip le geoDataFrame avec le clip_mask en utilisant une distance pour prendre les contours.
    :param gdf_to_clip: Le GeoDataFrame a découper.
    :param clip_mask: Le Masque de découpage
    :return: Un GeoDataFrame Découpé.
    """
    if len(clip_mask) > 1:
        print("Auscour ascour clip_mask a plusieurs géométrie.........")
    return gdf_to_clip[gdf_to_clip.geometry.distance(clip_mask.geometry.iloc[0]) < 7000]

def plot_geojson_from_lambert2(output_path:Path, gdf_ready: gpd.GeoDataFrame):
    """
    Enregistre le Dataframe sous forme de Geojson dans l'output_path.
    Si le gdf_ready est vide, ne fais rien.
    :param output_path: Endroit où le fichier va être sauvegardé.
    :param gdf_ready: Le DataFrame à plot.
    :return: Rien
    """
    print("Saving...")
    if not gdf_ready.empty:
        gdf_ready.to_file(output_path, driver="GeoJSON", mode="w")
    else:
        print("gdf empty ! " + output_path)

def get_chemin_sauvegarde(data_freq:MeteoFranceDataType, start_date:datetime, end_date:datetime, is_data_aggregated:bool) -> Path:
    match data_freq:
        # SIM2_QUOT
        case MeteoFranceDataType.SIM2_QUOT if start_date.date() != end_date.date():
            if is_data_aggregated:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-SIM2-aggregated-{start_date:%Y%m%d}-{end_date:%Y%m%d}/QUOT-SIM2-aggregated-{start_date:%Y%m%d}-{end_date:%Y%m%d}.geojson")
            else:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-SIM2-{start_date:%Y%m%d}-{end_date:%Y%m%d}/QUOT-SIM2-{start_date:%Y%m%d}-{end_date:%Y%m%d}.geojson")
        case MeteoFranceDataType.SIM2_QUOT:
            chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-SIM2-{start_date:%Y%m%d}/QUOT-SIM2-{start_date:%Y%m%d}.geojson")
        # SIM2_MENS
        case MeteoFranceDataType.SIM2_MENS if start_date.strftime("%Y%m") != end_date.strftime("%Y%m"):
            if is_data_aggregated:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-SIM2-aggregated-{start_date:%Y%m}-{end_date:%Y%m}/MENS-SIM2-aggregated-{start_date:%Y%m}-{end_date:%Y%m}.geojson")
            else:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-SIM2-{start_date:%Y%m}-{end_date:%Y%m}/MENS-SIM2-{start_date:%Y%m}-{end_date:%Y%m}.geojson")
        case MeteoFranceDataType.SIM2_MENS:
            chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-SIM2-{start_date:%Y%m}/MENS-SIM2-{start_date:%Y%m}.geojson")
        # QUOT
        case MeteoFranceDataType.QUOT if start_date.strftime("%Y%m%d") != end_date.strftime("%Y%m%d"):
            if is_data_aggregated:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-aggregated-{start_date:%Y%m%d}-{end_date:%Y%m%d}/QUOT-aggregated-{start_date:%Y%m%d}-{end_date:%Y%m%d}.geojson")
            else:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-{start_date:%Y%m%d}-{end_date:%Y%m%d}/QUOT-{start_date:%Y%m%d}-{end_date:%Y%m%d}.geojson")
        case MeteoFranceDataType.QUOT:
            chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/QUOT-{start_date:%Y%m%d}/QUOT-{start_date:%Y%m%d}.geojson")
        # MENS
        case MeteoFranceDataType.MENS if start_date.strftime("%Y%m") != end_date.strftime("%Y%m"):
            if is_data_aggregated:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-aggregated-{start_date:%Y%m}-{end_date:%Y%m}/MENS-aggregated-{start_date:%Y%m}-{end_date:%Y%m}.geojson")
            else:
                chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-{start_date:%Y%m}-{end_date:%Y%m}/MENS-{start_date:%Y%m}-{end_date:%Y%m}.geojson")
        case MeteoFranceDataType.MENS:
            chemin_sauvegarde = Path(f"output/QGIS/meteoFrance/MENS-{start_date:%Y%m}/MENS-{start_date:%Y%m}.geojson")
        case _:
            raise NotImplementedError
    return chemin_sauvegarde

def get_chemin_sauvegarde_geographie(geographic_scale:GeographicScaleClip, chemin_sauvegarde_original:Path, code_geographique:str|None="")->Path:
    """
    Renvoie le chemin de sauvegarde pour chaque niveau geographique en se basant sur le dossier de sauvegarde actuel.
    :param geographic_scale: Le niveau géographique souhaité
    :param chemin_sauvegarde_original: Le chemin de sauvegarde de l'enregistrement
    :param code_geographique: Le code de département/région/bassin
    :return:
    """
    nouveau_chemin = chemin_sauvegarde_original
    match geographic_scale:
        case GeographicScaleClip.BASSIN:
            suffix_letter = "B"
            dossier = "bassin"
        case GeographicScaleClip.DEPARTEMENT_BASSIN:
            suffix_letter = "Db"
            dossier = "departement_bassin"
        case GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF:
            suffix_letter = "D"
            dossier = "departement_administratif"
        case GeographicScaleClip.REGION_BASSIN:
            suffix_letter = "Rb"
            dossier = "region_bassin"
        case GeographicScaleClip.REGION_ADMINISTRATIVE:
            suffix_letter = "R"
            dossier = "region_administrative"
        case GeographicScaleClip.NATIONAL:
            suffix_letter = ""
            dossier = ""
    nouveau_chemin = nouveau_chemin.with_stem(f"{chemin_sauvegarde_original.stem}-{suffix_letter}{code_geographique}")
    nouveau_chemin = nouveau_chemin.parent / dossier / nouveau_chemin.name
    return nouveau_chemin

def export_to_every_geographic_element(data_freq: MeteoFranceDataType, geographic_scale:GeographicScaleClip, df:pd.DataFrame, chemin_save_original:Path, is_data_aggregated:bool):
    """
    Export en géojson le df à toute les échelles.

    Génère des plots si associés à chaque zone géographique, si les données ne sont pas aggrégé.
    :param is_data_aggregated: Si les données sont aggrégé, ne génère pas les plots.
    :param data_freq:
    :param geographic_scale:
    :param df:
    :param chemin_save_original:
    :return:
    """
    print(f"Export de tous les region géographique en cours : {geographic_scale}...")
    # Conversion des coordonnées du dataframe
    print("Conversion des coordonnées")
    gdf = to_lambert2_geodataframe(data_freq, df)
    chemin_save_plot = chemin_save_original.parent / "plots"
    # De manière générale, sauf nationale et bassin le masque doit être redécoupé.
    is_bassin_clip_required = True
    match geographic_scale:
        case GeographicScaleClip.NATIONAL:
            plot_geojson_from_lambert2(chemin_save_original, gdf)
            return
        case GeographicScaleClip.BASSIN | GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF | GeographicScaleClip.REGION_ADMINISTRATIVE:
            is_bassin_clip_required = False
        case GeographicScaleClip.DEPARTEMENT_BASSIN | GeographicScaleClip.REGION_BASSIN:
            is_bassin_clip_required = True

    element_list = DMeteo.get_geographic_list(geographic_scale)
    if "DATE_DATETIME" in gdf.columns:
        start_date = gdf["DATE_DATETIME"].min()
        end_date = gdf["DATE_DATETIME"].max()
    elif "DATE_DATETIME_min" in gdf.columns and "DATE_DATETIME_max":
        start_date = gdf["DATE_DATETIME_min"].min()
        end_date = gdf["DATE_DATETIME_max"].max()
    else:
        raise ValueError("Date de début et de fin non trouvée")

    chemin_zone_geographique = chemin_save_plot / geographic_scale
    print("Récupération Mask bassin versant")
    # Récupération du bassin versant (on prend le premier bassin versant de la liste des bassin versant.
    code_bassin_decoupe = download_meteoFrance.get_geographic_list(GeographicScaleClip.BASSIN)[0]
    gdf_bassin_mask = get_bassin_versant(code_bassin_decoupe)
    for code in tqdm(element_list):
        print(f"code : {code}")
        print("Récupération Mask")
        gdf_geographie_mask = get_geographic_element(geographic_scale, code)

        # On procède au clipping du gdf d'origine.
        print("Clipping GeoDataFrame with geographic mask.")
        gdf_first_clip = clip_with_distance(gdf, gdf_geographie_mask)

        # Si on doit prendre l'échelle bassin, on découpe les données restantes avec le masque du bassin.
        print("Clipping GeoDataFrame with Bassin mask.")
        if is_bassin_clip_required:
            gdf_second_clip = clip_with_distance(gdf_first_clip, gdf_bassin_mask)
        else:
            gdf_second_clip = gdf_first_clip

        if len(gdf_second_clip) == 0:
            print("Les données se sont fait supprimé par la découpe sur bassin et la géographie !")
            print("Passage à l'élément suivant !")
            continue

        # On récupère le chemin de sauvegarde.
        chemin_save = get_chemin_sauvegarde_geographie(geographic_scale, chemin_save_original,code)
        chemin_save.parent.mkdir(exist_ok=True)

        # On plot le résultat
        print("Sauvegarde gdf")
        plot_geojson_from_lambert2(chemin_save, gdf_second_clip)

        # On crée les plots matplotlib associé à cette zone gégraphique.
        if not is_data_aggregated:
            print("Créations des plots pour la zone géographique.")
            gdf_aggrege_by_datetime = MeteoAgg.aggregate_range(data_freq ,gdf_second_clip, GroupByMethod.BY_DATE)
            #Créer le dossier de cahque zone geographiique et faire a l'interieur un dossier par code.
            chemin_code = chemin_zone_geographique / code
            chemin_code.mkdir(parents=True, exist_ok=True)
            nom_echelle = f"{geographic_scale}-{code}"
            create_all_plot_for_unique_scale(gdf_aggrege_by_datetime, nom_echelle, start_date,end_date, chemin_code)

    print(f"Export de tous les {geographic_scale} terminés.")

def create_all_plot_for_unique_scale(df_aggregated:pd.DataFrame, nom_echelle:str, start_date:datetime, end_date:datetime, chemin_de_base:Path):
    """
    Créer tous les plots avec ce Dataframe en entrée, les sauvegarde dans le dossier pointé par le chemin_de_base.

    Le titre des plots est au format '[Description de l'unité] : [nom_echelle] [start_date] [end_date]'.
    :param df_aggregated:
    :param nom_echelle: Chaine de caractère indiquant le nom de cette échelle.
    :param start_date:
    :param end_date:
    :param chemin_de_base:
    :return:
    """
    # On crée le dossier où tout est sauvegardé.
    chemin_de_base.mkdir(exist_ok=True)

    dataframe_trie_par_date = df_aggregated.sort_values(by=["DATE_DATETIME"])
    dataframe_date = dataframe_trie_par_date["DATE_DATETIME"]
    # SSWI_10J
    if "SSWI_10J" in dataframe_trie_par_date.columns:
        max_value = max(2, dataframe_trie_par_date["SSWI_10J"].max()) + 0.2
        min_value = min(-2, dataframe_trie_par_date["SSWI_10J"].min()) - 0.2
        plot_bar_dataframe(dataframe_trie_par_date["SSWI_10J"],
                           dataframe_date,
                           normale_value=0,
                           plot_title=f"Standardized Soil Wetness Index : {nom_echelle} {start_date:%Y%m%d} {end_date:%Y%m%d}",
                           output_path=chemin_de_base / "SSWI_10J.png",
                           reference_lines={
                               "Extrêmement humide": (1.75, max_value, "midnightblue"),
                               "Très humide": (1.28, 1.75, "royalblue"),
                               "Modérément humide": (0.84, 1.28, "turquoise"),
                               "Autour de la Normale": (-0.84, 0.84, "lime"),
                               "Modérément sec": (-1.28, -0.84, "yellow"),
                               "Très sec": (-1.75, -1.28, "darkorange"),
                               "Extrêmement sec": (min_value, -1.75, "darkred"),
                           })

    if "PE" in dataframe_trie_par_date.columns:
        plot_bar_dataframe(dataframe_trie_par_date["PE"],
                           dataframe_date,
                           plot_title=f"Pluie Efficace : {nom_echelle} {start_date:%Y%m%d} {end_date:%Y%m%d}",
                           output_path=chemin_de_base / "PE.png")

    if "PRELIQ" in dataframe_trie_par_date.columns:
        plot_bar_dataframe(dataframe_trie_par_date["PRELIQ"],
                           dataframe_date,
                           plot_title=f"Cumul des précipitation liquide quotidiennes (mm) : {nom_echelle} {start_date:%Y%m%d} {end_date:%Y%m%d}",
                           output_path=chemin_de_base / "PRELIQ.png")

    if "EVAP" in dataframe_trie_par_date.columns:
        plot_bar_dataframe(dataframe_trie_par_date["EVAP"],
                           dataframe_date,
                           plot_title=f"Cumul de l'évapotranspiration quotidienne (mm) : {nom_echelle} {start_date:%Y%m%d} {end_date:%Y%m%d}",
                           output_path=chemin_de_base / "EVAP.png")

    if "ETP" in dataframe_trie_par_date.columns:
        plot_bar_dataframe(dataframe_trie_par_date["ETP"],
                           dataframe_date,
                           plot_title=f"Cumul de l'évapotranspiration potentielle quotidienne (mm) : {nom_echelle} {start_date:%Y%m%d} {end_date:%Y%m%d}",
                           output_path=chemin_de_base / "ETP.png")

    if "RR" in dataframe_trie_par_date.columns:
        plot_bar_dataframe(dataframe_trie_par_date["RR"],
                           dataframe_date,
                           plot_title=f"Cumul de pluie : {nom_echelle} {start_date:%Y%m%d} {end_date:%Y%m%d}",
                           output_path=chemin_de_base / "RR.png")

    if "SPI1" in dataframe_trie_par_date.columns:
        max_value = max(2, dataframe_trie_par_date["SPI1"].max()) + 0.2
        min_value = min(-2, dataframe_trie_par_date["SPI1"].min()) - 0.2
        plot_bar_dataframe(dataframe_trie_par_date["SPI1"],
                           dataframe_date,
                           normale_value=0,
                           plot_title=f"Cumul de pluie : {nom_echelle} {start_date:%Y%m%d} {end_date:%Y%m%d}",
                           output_path=chemin_de_base / "SPI1.png",
                           reference_lines={
                               "Extrêmement humide": (2.0, max_value, "midnightblue"),
                               "Modérément humide": (1.0, 2.0, "turquoise"),
                               "Autour de la Normale": (-1.0, 1.0, "lime"),
                               "Modérément sec": (-2.0, -1.0, "yellow"),
                               "Extrêmement sec": (min_value, -2, "darkred"),
                           }
                           )

def export_all_format_geojson_range(data_freq:MeteoFranceDataType, start_date:datetime, end_date:datetime, is_data_aggregated:bool,
                                    has_index_update:bool=True, is_data_update_allowed:bool=True) -> None:
    """
    Enregistre des geojson contenant toutes les données entre start_date et end_date.
    Créer des découpages à l'échelle départementale, régionale et bassin.

    De plus, si les données ne sont pas aggrégé, produit des plots pour chaque métrique surveillé.
    :param is_data_aggregated: Si a True, les données sont aggrégés, si a False, on retrouve les données individuelles.
    :param data_freq: Type de donnée à récupérer
    :param start_date: Date de début (inclus dans l'intervalle)
    :param end_date: Date de fin (inclus dans l'intervalle)
    :param has_index_update: Défini si l'index fichiers -> id_datagouv est mis à jour. Peut-être long pour les fichiers données non-analysé.
    :param is_data_update_allowed: Si à faux, aucune mis à jour n'est fait, ni sur les fichiers à télécharger, ni sur les index.
    :return: Rien
    """
    if not is_data_update_allowed:
        has_index_update = False

    df_intervalle = DMeteo.get_data_in_range(data_freq, start_date, end_date, has_index_update, is_data_update_allowed)
    if df_intervalle.empty:
        print(f"L'intervalle de données ({start_date} - {end_date}) est vide. Abandon.")
        return

    if is_data_aggregated:
        df_intervalle = MeteoAgg.aggregate_range(data_freq, df_intervalle, GroupByMethod.BY_POSITION)

    chemin_sauvegarde = get_chemin_sauvegarde(data_freq, start_date, end_date, is_data_aggregated)
    chemin_sauvegarde.parent.mkdir(exist_ok=True)

    export_to_every_geographic_element(data_freq, GeographicScaleClip.DEPARTEMENT_BASSIN, df_intervalle, chemin_sauvegarde, is_data_aggregated)
    export_to_every_geographic_element(data_freq, GeographicScaleClip.NATIONAL, df_intervalle, chemin_sauvegarde, is_data_aggregated)
    export_to_every_geographic_element(data_freq, GeographicScaleClip.BASSIN, df_intervalle, chemin_sauvegarde, is_data_aggregated)
    export_to_every_geographic_element(data_freq, GeographicScaleClip.REGION_BASSIN, df_intervalle, chemin_sauvegarde, is_data_aggregated)


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
    export_all_format_geojson_range(data_freq, start_date, end_date, False)

def export_geojson_day(data_freq:MeteoFranceDataType, day_date:datetime):
    """
    Plot un unique jour de données.
    :param data_freq:
    :param day_date: La date correspondant au jour choisi.
    :return: Rien
    """
    start_date = datetime(day_date.year, day_date.month, day_date.day)
    end_date = datetime(day_date.year, day_date.month, day_date.day)
    export_all_format_geojson_range(data_freq, start_date, end_date, False)

@cache
def get_all_geographic_geodf(geographic_scale:GeographicScaleClip):
    match geographic_scale:
        case GeographicScaleClip.REGION_BASSIN | GeographicScaleClip.REGION_ADMINISTRATIVE:
            chemin_archive = Path(
                "output/meteoFrance/downloaded_data/delimitation_qgis_archive/regions-100m.geojson.gz")
            chemin = Path("output/meteoFrance/downloaded_data/delimitation_qgis/regions-100m.geojson")
            id_data_gouv = "aa76860a-51af-4744-a593-4c19af2570b8"
        case GeographicScaleClip.DEPARTEMENT_BASSIN | GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF:
            chemin_archive = Path(
                "output/meteoFrance/downloaded_data/delimitation_qgis_archive/departements-50m.geojson.gz")
            chemin = Path("output/meteoFrance/downloaded_data/delimitation_qgis/departements-50m.geojson")
            id_data_gouv = "93a2ba8f-e30f-4916-a73b-0c4d87247ace"
        case GeographicScaleClip.BASSIN:
            chemin_archive = Path(
                "output/meteoFrance/downloaded_data/delimitation_qgis_archive/bassin-hydrographique.geojson.zip")
            chemin = Path("output/meteoFrance/downloaded_data/delimitation_qgis/BassinHydrographique_FXX.geojson")
            id_data_gouv = "b0761a88-b59f-466f-a3cc-b97f237fd732"
        case _:
            raise NotImplementedError

    if not chemin.exists():
        DMeteo.download_and_extract(id_data_gouv, chemin_archive, chemin)
    df_tout_departement = gpd.read_file(chemin).to_crs(crs="EPSG:27572")
    return df_tout_departement

def get_geographic_element(geographic_scale:GeographicScaleClip, code:str):
    df = get_all_geographic_geodf(geographic_scale)
    match geographic_scale:
        case GeographicScaleClip.BASSIN:
            nom_colonne = "CdBH"
        case GeographicScaleClip.DEPARTEMENT_BASSIN | GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF:
            nom_colonne = "code"
        case GeographicScaleClip.REGION_BASSIN | GeographicScaleClip.REGION_ADMINISTRATIVE:
            nom_colonne = "code"
        case _:
            raise NotImplementedError

    df_departement = df[df[nom_colonne] == code]
    return df_departement

def get_bassin_versant(code:str):
    df = get_all_geographic_geodf(GeographicScaleClip.BASSIN)
    df_bassin = df[df["CdBH"] == code]
    return df_bassin

def plot_bar_dataframe(
    series_to_plot: pd.Series,
    series_date: pd.Series,
    normale_value: float = None,
    plot_title: str = "",
    reference_lines: dict[str, tuple[float,float,str]] = None,
    output_path: Path = None
):
    """
    Affiche une serie de données sous forme de barres,
    avec en abscisse la date et en ordonnée les valeurs de la série.
    Compare les valeurs à la normale_value.

    Enregistre le plot dans output_path.
    :param series_to_plot:La série de valeurs à afficher
    :param series_date:La série de datetime correspondant aux valeurs
    :param normale_value: La valeur normale pour cette série.
    :param plot_title:Le titre du plot
    :param reference_lines: Un ensemble de ligne horizontale traversant le graphique
    :param output_path: Chemin vers lequel le plot est enregistré.
    :return: Rien
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Zone horizontale de référence.
    if reference_lines is not None:
        for key_label in reference_lines.keys():
            start_range, end_range, color = reference_lines[key_label]
            ax.axhspan(
                ymin=start_range,
                ymax=end_range,
                alpha=0.3,
                color=color,
                linestyle="--",
                linewidth=1,
                label=f"{key_label} [{start_range:.2f}:{end_range:.2f}]"
            )

    # Barres de la série
    ax.bar(
        series_date.values,
        series_to_plot.values,
        label=series_to_plot.name or "Valeurs"
    )

    # Ligne de normale
    if normale_value is not None:
        ax.axhline(
            y=normale_value,
            color="red",
            linestyle="--",
            linewidth=2,
            label=f"Normale 1991-2020 : {normale_value:.2f}"
        )

    ax.set_title(plot_title)
    ax.set_xlabel(series_date.name or "")
    ax.set_ylabel(series_to_plot.name or "Valeur")
    ax.legend()

    plt.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=300)
    plt.close(fig)



if __name__ == "__main__":
    print("Plotting !")

    # Donnée MENS aggrégé de 2025 à 2026.
    # export_geojson_range(MeteoFranceDataType.SIM2_MENS, datetime(2025, 1, 1), datetime(2025, 12, 31), False)
    # Cumul depuis le dernier bulletin 10 juin et nombre de jour où la temptérature est au-dessus de la normale.
    #today = datetime.today()
    #export_geojson_range(MeteoFranceDataType.SIM2_QUOT, datetime(2026, 6, 10), today, True)

    # SWI du 14 juin
    # export_geojson_day(datetime(2026,6,14))

    # # Données pour 1 seul jour
    # plot_day(datetime(2026,5,18))
    #
    # # Données non-aggrégé sur 1 mois.
    #export_geojson_month(MeteoFranceDataType.SIM2_QUOT, datetime(2026, 5, 1))
    #export_geojson_day(MeteoFranceDataType.QUOT, datetime(2026, 6, 1))
    # export_geojson_month(MeteoFranceDataType.MENS, datetime(2026, 5, 1))

    # # Données aggrégé de base sur 1 mois.
    # plot_month(MeteoFranceDataType.SIM2_MENS, datetime(2026,5,1))
    #
    # # Données aggrégés allant d'un jour à un autre.
    # export_geojson_range(MeteoFranceDataType.SIM2_QUOT, datetime(2026,5,7), datetime(2026, 5,14), True)
    #
    # # Donnée MENS non-aggrégé de 2020 à 2026.
    # export_geojson_range(MeteoFranceDataType.SIM2_MENS, datetime(2020, 1, 1), datetime(2026, 5, 1), False)

    # CUMUL des quantités d'eau depuis le début de l'année hydrologique.
    today = datetime.today()
    # export_all_format_geojson_range(MeteoFranceDataType.SIM2_MENS, datetime(2025, 9, 1), today, False)
    # export_all_format_geojson_range(MeteoFranceDataType.MENS, datetime(2025, 9, 1), today, False)

    # Evlution du 10 au 24 juin.
    #export_all_format_geojson_range(MeteoFranceDataType.SIM2_QUOT, datetime(2026, 6, 10), today, False)

    # export_all_format_geojson_range(MeteoFranceDataType.SIM2_QUOT, datetime(2026, 6, 10), today, True)

    #export_all_format_geojson_range(MeteoFranceDataType.QUOT, datetime(2026, 6, 10), today, True)
    #export_all_format_geojson_range(MeteoFranceDataType.QUOT, datetime(2026, 6, 10), today, False)
    export_all_format_geojson_range(MeteoFranceDataType.SIM2_QUOT, datetime(2026, 6, 10), today, True)
    export_all_format_geojson_range(MeteoFranceDataType.SIM2_QUOT, datetime(2026, 6, 10), today, False)
