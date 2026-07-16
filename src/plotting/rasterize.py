import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path
from rasterio.transform import from_bounds
from rasterio.mask import mask
from rasterio.plot import plotting_extent
from rasterio.io import MemoryFile
from scipy.interpolate import griddata
from src.model.enums import GeographicScaleClip
from src.config.paths import OUTPUT_DIR
from src.config.logging_config import setup_logger
from src.io.pynsee_departement import get_departements_from_regions

# Initialiser le logger
logger = setup_logger(name="rasterize")


def rasterize_geojson(gdf_to_rasterize:gpd.GeoDataFrame, value_column_name:str, gdf_mask:gpd.GeoDataFrame, titre_graphique:str,
                      color_palette:str, is_invert_palette:bool, intervalle_name:list[str], intervalle_marqueur:list[float],
                      output_path:Path, geojson_to_draw:gpd.GeoDataFrame=None):
    """
    Créer un raster du geodataframe passé en paramètre. Les systèmes de coordonnées entre le masque et le geodataframe doivent être identiques.
    """
    GRID_SIZE = 1500

    INTERPOLATION = "linear"

    ENABLE_CLIP = True

    points = gdf_to_rasterize

    # =========================
    # POINTS
    # =========================

    x = points.geometry.x.to_numpy()
    y = points.geometry.y.to_numpy()
    z = points[value_column_name].to_numpy()

    # =========================
    # GRID
    # =========================

    xmin, ymin, xmax, ymax = gdf_mask.total_bounds

    # IMPORTANT :
    # ymax -> ymin pour respecter la convention raster

    grid_y, grid_x = np.mgrid[
        ymax:ymin:complex(GRID_SIZE),
        xmin:xmax:complex(GRID_SIZE)
    ]

    # =========================
    # INTERPOLATION
    # =========================

    grid_z = griddata(
        points=(x, y),
        values=z,
        xi=(grid_x, grid_y),
        method=INTERPOLATION
    )

    # On complète les trous avec NEAREST
    grid_nearest = griddata(
        (x, y),
        z,
        (grid_x, grid_y),
        method="nearest"
    )

    grid_z[np.isnan(grid_z)] = grid_nearest[np.isnan(grid_z)]

    # =========================
    # TRANSFORM
    # =========================

    transform = from_bounds(
        xmin,
        ymin,
        xmax,
        ymax,
        GRID_SIZE,
        GRID_SIZE
    )

    # =========================
    # CLIP
    # =========================

    if ENABLE_CLIP:

        with MemoryFile() as memfile:

            with memfile.open(
                driver="GTiff",
                height=GRID_SIZE,
                width=GRID_SIZE,
                count=1,
                dtype=grid_z.dtype,
                crs=points.crs,
                transform=transform,
            ) as dataset:

                dataset.write(grid_z, 1)

                clipped, clipped_transform = mask(
                    dataset,
                    gdf_mask.geometry,
                    crop=True,
                    filled=True,
                    nodata=np.nan
                )

        data = clipped[0]

        extent = plotting_extent(data, clipped_transform)

    else:

        data = grid_z

        extent = (
            xmin,
            xmax,
            ymin,
            ymax
        )

    # =========================
    # EXPORT PNG
    # =========================

    fig, ax = plt.subplots(figsize=(10, 10))

    ax.set_title(titre_graphique)
    if is_invert_palette:
        cmap = mpl.colormaps[color_palette].reversed()
    else:
        cmap = mpl.colormaps[color_palette]

    bounds = intervalle_marqueur
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend="both")

    img = ax.imshow(
        data,
        origin="upper",
        extent=extent,
        cmap=cmap,
        norm=norm,
    )

    # ColorBar.

    ticks = bounds + [(bounds[i] + bounds[i+1]) / 2 for i in range(len(bounds)-1)]

    cbar = fig.colorbar(img, ax=ax, label=value_column_name, extend="both", shrink=0.7)

    cbar.set_ticks(ticks)

    cbar.set_ticklabels(intervalle_name)

    cbar.ax.yaxis.set_label_coords(-1,0.5)

    # Bordure autour du graphique.
    gdf_mask.boundary.plot(
        ax=ax,
        color="black",
        linewidth=1
    )

    if geojson_to_draw is not None:
        geojson_to_draw.boundary.plot(
            ax=ax,
            color="black",
            linewidth=0.5
        )

    ax.axis("off")
    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
        transparent=True,
    )


    logger.info(f"PNG généré : {output_path}")


def get_graphic_parameter(unit_to_get_graphic: str) -> tuple[str, bool, list[str], list[float]]|None:
    """
    Récupère les paramètre pour cette unité souhaité
    :param unit_to_get_graphic: L'unité dont il faut récupérer les paramètre.
    :return: Renvoie un triplet (palette_de_couleur, is_palette_inverse labels_colorBar, TickColorBar)
    """
    if "SSWI" in unit_to_get_graphic:
        return (
            "turbo",
            True,
            [
                "-1.25 - Extrêmement Sec",
                "-0.75",
                "-0.25",
                "0.25",
                "0.75",
                "1.25 - Extrêmement Humide",
                "Très Sec",
                "Modérément Sec",
                "Autour de la Normale",
                "Modérément Humide",
                "Très Humide",
            ],
            [-1.25, -0.75, -0.25, 0.25, 0.75, 1.25]
        )
    elif "hydraulicite" in unit_to_get_graphic:
        ## TODO mettre les bonnes couleur
        return (
            "turbo",
            True,
            [
                "0.25 - Très faible",
                "0.75",
                "1.25",
                "1.75 - Très forte",
                "Faible",
                "Moyenne",
                "Forte",
            ],
            [0.25, 0.75, 1.25, 1.75]
        )
    else:
        return None

def get_departement_to_draw_from_region(code_zone: str) -> gpd.GeoDataFrame:
    DEPARTEMENT = OUTPUT_DIR / "meteoFrance/downloaded_data/delimitation_qgis/departements-50m.geojson"
    geo_departement_mask = gpd.read_file(DEPARTEMENT).to_crs(2154)
    geo_departement_mask = geo_departement_mask[
        geo_departement_mask["code"].isin(get_departements_from_regions(code_zone))]
    return geo_departement_mask

def rasterize_geodataframe_geographiv_zone(
    geodataframe: gpd.GeoDataFrame,
    unit_to_rasterize: str,
    geographic_zone: GeographicScaleClip,
    code_zone: str,
    output_path: Path,
    titre_graphique:str
) -> None:
    """
    Rasterise un GeoDataFrame pour une zone géographique spécifique et une unité de mesure donnée.

    Supprime les entrées n'ayant pas de données pour supprimer les trous sur la carte.
    Args:
        geodataframe (gpd.GeoDataFrame): Le GeoDataFrame contenant les points à rasteriser.
        unit_to_rasterize (str): Le nom de l'unité à rasteriser (ex: "SSWI1", "hydraulicite").
        geographic_zone (GeographicScaleClip): L'échelle géographique (ex: bassin, région, département).
        code_zone (str): Le code identifiant la zone (ex: "06" pour un bassin, "84" pour une région).
        output_path (Path): Chemin de sortie pour l'image générée.
        titre_graphique (str): Le titre du graphique.
        geojson_to_draw (gpd.GeoDataFrame, optional): GeoDataFrame supplémentaire à dessiner sur la carte (ex: limites de départements).
    """
    logger.info(f"Rasterisation commencée pour {unit_to_rasterize} dans la zone {code_zone} ({geographic_zone}).")

    # Vérifier que le GeoDataFrame contient la colonne de valeur
    if unit_to_rasterize not in geodataframe.columns:
        logger.error(f"La colonne {unit_to_rasterize} n'existe pas dans le GeoDataFrame.")
        raise ValueError(f"La colonne {unit_to_rasterize} n'existe pas dans le GeoDataFrame.")

    geodataframe = geodataframe.dropna(subset=[unit_to_rasterize])

    # Charger le masque en fonction de l'échelle géographique
    mask_file_path = Path()
    mask_column_name = None
    geojson_to_draw = None
    match geographic_zone:
        case GeographicScaleClip.BASSIN:
            mask_file_path = OUTPUT_DIR / "meteoFrance/downloaded_data/delimitation_qgis/BassinHydrographique_FXX.geojson"
            mask_column_name = "CdBH"
        case GeographicScaleClip.REGION_ADMINISTRATIVE | GeographicScaleClip.REGION_BASSIN:
            mask_file_path = OUTPUT_DIR / "meteoFrance/downloaded_data/delimitation_qgis/regions-100m.geojson"
            mask_column_name = "code"
            geojson_to_draw = get_departement_to_draw_from_region(code_zone)
        case GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF | GeographicScaleClip.DEPARTEMENT_BASSIN:
            mask_file_path = OUTPUT_DIR / "meteoFrance/downloaded_data/delimitation_qgis/departements-50m.geojson"
            mask_column_name = "code"
        case _:
            logger.error(f"Échelle géographique non prise en charge : {geographic_zone}")
            raise ValueError(f"Échelle géographique non prise en charge : {geographic_zone}")

    # Charger le masque et filtrer selon le code de la zone
    geo_mask = gpd.read_file(mask_file_path).to_crs(2154)
    geo_mask = geo_mask[geo_mask[mask_column_name] == code_zone]

    if geo_mask.empty:
        logger.error(f"Aucune zone trouvée avec le code {code_zone} dans {mask_file_path}.")
        raise ValueError(f"Aucune zone trouvée avec le code {code_zone} dans {mask_file_path}.")

    # Récupérer les paramètres graphiques pour l'unité
    graphic_params = get_graphic_parameter(unit_to_rasterize)
    if graphic_params is None:
        logger.error(f"Aucun paramètre graphique défini pour l'unité {unit_to_rasterize}.")
        raise ValueError(f"Aucun paramètre graphique défini pour l'unité {unit_to_rasterize}.")

    palette, is_palette_inverse, intervalle_name, tick_pos = graphic_params

    # Appeler la fonction de rasterisation
    rasterize_geojson(
        gdf_to_rasterize=geodataframe,
        value_column_name=unit_to_rasterize,
        gdf_mask=geo_mask,
        titre_graphique=titre_graphique,
        color_palette=palette,
        is_invert_palette=is_palette_inverse,
        intervalle_name=intervalle_name,
        intervalle_marqueur=tick_pos,
        output_path=output_path,
        geojson_to_draw=geojson_to_draw,
    )

    logger.info(f"Rasterisation terminée pour {unit_to_rasterize} dans la zone {code_zone} ({geographic_zone}).")

if __name__ == "__main__":
    POINTS_FILE = OUTPUT_DIR / "QGIS/meteoFrance/MENS-SIM2-202606/bassin/MENS-SIM2-202606-B06.geojson"

    VALUE_FIELD = "SSWI1"

    OUTPUT_PNG = OUTPUT_DIR / "test/output_rasterise_test.png"

    MASK_FILE = OUTPUT_DIR / "meteoFrance/downloaded_data/delimitation_qgis/BassinHydrographique_FXX.geojson"

    point_dataframe = gpd.read_file(POINTS_FILE).to_crs(2154)
    geo_mask = gpd.read_file(MASK_FILE).to_crs(2154)
    geo_mask = geo_mask[geo_mask["CdBH"] == "06"]

    palette, is_palette_inverse, intervalle_name, tick_pos = get_graphic_parameter("SSWI1")

    rasterize_geojson(point_dataframe, "SSWI1", geo_mask, "SSWI1 du mois de Juin 2026",
                      palette, is_palette_inverse, intervalle_name, tick_pos, OUTPUT_PNG)

    # AUTRE ECHELLE

    POINTS_FILE = OUTPUT_DIR / "QGIS/meteoFrance/MENS-SIM2-202606/region_administrative/MENS-SIM2-202606-R84.geojson"

    VALUE_FIELD = "SSWI1"

    OUTPUT_PNG = OUTPUT_DIR / "test/output_rasterise_test_REGION.png"

    point_dataframe = gpd.read_file(POINTS_FILE).to_crs(2154)

    DEPARTEMENT = OUTPUT_DIR / "meteoFrance/downloaded_data/delimitation_qgis/departements-50m.geojson"
    geo_departement_mask = gpd.read_file(DEPARTEMENT).to_crs(2154)
    geo_departement_mask = geo_departement_mask[
        geo_departement_mask["code"].isin(["03", "01", "74", "63", "42", "69", "73", "38", "26", "07", "43", "15"])]

    palette, is_palette_inverse,  intervalle_name, tick_pos = get_graphic_parameter("SSWI1")

    rasterize_geojson(point_dataframe, "SSWI1", geo_mask, "SSWI1 du mois de Juin 2026 en Auvergne-Rhône-Alpes",
                      palette, is_palette_inverse, intervalle_name, tick_pos, OUTPUT_PNG, geo_departement_mask)

    # AUTRE TEST ENCORE


    POINTS_FILE = OUTPUT_DIR / "QGIS/meteoFrance/QUOT-SIM2-20260601/region_administrative/QUOT-SIM2-20260601-R27.geojson"

    OUTPUT_PNG = OUTPUT_DIR / "test/output_rasterise_test_REGION_test_QUOT.png"

    point_dataframe = gpd.read_file(POINTS_FILE).to_crs(2154)

    rasterize_geodataframe_geographiv_zone(
        point_dataframe,
        "SSWI_10J",
        GeographicScaleClip.REGION_ADMINISTRATIVE,
        "27",
        OUTPUT_DIR / "test/test_region_administrative_fonction.png",
        "SSWI_10J au 1er du mois de juin 2026 de la région 27."
    )

