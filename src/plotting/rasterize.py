import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt

from rasterio.transform import from_bounds
from rasterio.mask import mask
from rasterio.plot import plotting_extent
from rasterio.io import MemoryFile

from scipy.interpolate import griddata

from src.config.paths import OUTPUT_DIR

# =========================
# CONFIG
# =========================

POINTS_FILE = OUTPUT_DIR / "QGIS/meteoFrance/QUOT-SIM2-aggregated-20260601-20260630/bassin/QUOT-SIM2-aggregated-20260601-20260630-B06.geojson"

VALUE_FIELD = "SSWI_10J"

OUTPUT_PNG = OUTPUT_DIR / "test/output_rasterise_test.png"

DEPT_FILE = OUTPUT_DIR / "meteoFrance/downloaded_data/delimitation_qgis/BassinHydrographique_FXX.geojson"

GRID_SIZE = 1000

INTERPOLATION = "linear"

ENABLE_CLIP = True

# =========================
# LOAD DATA
# =========================

points = gpd.read_file(POINTS_FILE).to_crs(2154)

dept = gpd.read_file(DEPT_FILE)
dept = dept[dept["CdBH"] == "06"].to_crs(2154)

# =========================
# POINTS
# =========================

x = points.geometry.x.to_numpy()
y = points.geometry.y.to_numpy()
z = points[VALUE_FIELD].to_numpy()

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
                dept.geometry,
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

img = ax.imshow(
    data,
    origin="upper",
    extent=extent,
    cmap="viridis"
)

fig.colorbar(img, label=VALUE_FIELD)

dept.boundary.plot(
    ax=ax,
    color="black",
    linewidth=1
)

ax.axis("off")

plt.tight_layout()

plt.savefig(
    OUTPUT_PNG,
    dpi=300,
    transparent=True,
)

print(f"PNG généré : {OUTPUT_PNG}")