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

from src.config.paths import OUTPUT_DIR


def rasterize_geojson(series_to_rasterize:gpd.GeoDataFrame, value_column_name:str, gdf_mask:gpd.GeoDataFrame, titre_graphique:str,
                      color_palette:str, is_invert_palette:bool, intervalle_name:list[str], intervalle_marqueur:list[float],
                      output_path:Path, geojson_to_draw:gpd.GeoDataFrame=None):
    """
    Les données doivent être en .to_crs(2154)
    :param series_to_rasterize:
    :param gdf_mask:
    :param titre_graphique:
    :param color_palette:
    :param is_invert_palette:
    :param intervalle_name:
    :param intervalle_marqueur:
    :return:
    """
    GRID_SIZE = 1500

    INTERPOLATION = "linear"

    ENABLE_CLIP = True

    points = series_to_rasterize

    # =========================
    # POINTS
    # =========================

    x = points.geometry.x.to_numpy()
    y = points.geometry.y.to_numpy()
    z = points[value_column_name].to_numpy()

    # =========================
    # GRID
    # =========================

    xmin, ymin, xmax, ymax = points.total_bounds

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

    cbar = fig.colorbar(img, ax=ax, label=VALUE_FIELD, extend="both", shrink=0.7)

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


    print(f"PNG généré : {output_path}")


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
    else:
        return None

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

    MASK_FILE = OUTPUT_DIR / "meteoFrance/downloaded_data/delimitation_qgis/regions-100m.geojson"

    point_dataframe = gpd.read_file(POINTS_FILE).to_crs(2154)
    geo_mask = gpd.read_file(MASK_FILE).to_crs(2154)
    geo_mask = geo_mask[geo_mask["code"] == "84"]

    DEPARTEMENT = OUTPUT_DIR / "meteoFrance/downloaded_data/delimitation_qgis/departements-50m.geojson"
    geo_departement_mask = gpd.read_file(DEPARTEMENT).to_crs(2154)
    geo_departement_mask = geo_departement_mask[
        geo_departement_mask["code"].isin(["03", "01", "74", "63", "42", "69", "73", "38", "26", "07", "43", "15"])]

    palette, is_palette_inverse,  intervalle_name, tick_pos = get_graphic_parameter("SSWI1")

    rasterize_geojson(point_dataframe, "SSWI1", geo_mask, "SSWI1 du mois de Juin 2026 en Auvergne-Rhône-Alpes",
                      palette, is_palette_inverse, intervalle_name, tick_pos, OUTPUT_PNG, geo_departement_mask)

