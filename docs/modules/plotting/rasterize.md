---
layout: default
title: rasterize
description: "Documentation API du module rasterize - Rasterisation des GeoDataFrames"
nav_order: 4
parent: Module Plotting
grand_parent: Modules
---

# 🗺️ rasterize

**Documentation API complète**

> **Fichier** : `src/plotting/rasterize.py`
> **Module** : Rasterisation des données géospatiales
> **Auteur** : Thomas Meslin
> **Dernière mise à jour** : Juin 2026

---

## 📋 Table des Matières

- [🎯 Aperçu](#-aperçu)
- [📦 Dépendances](#-dépendances)
- [🔧 Fonctions](#-fonctions)
  - [rasterize_geojson](#rasterize_geojson)
  - [get_graphic_parameter](#get_graphic_parameter)
  - [get_departement_to_draw_from_region](#get_departement_to_draw_from_region)
  - [rasterize_geodataframe_geographiv_zone](#rasterize_geodataframe_geographiv_zone)
- [🎓 Tutoriel](#-tutoriel)
- [📊 Exemples Complets](#-exemples-complets)

---

## 🎯 Aperçu

Ce module permet de **rasteriser des GeoDataFrames** (conversion de points en image raster) pour créer des **cartes de chaleur** visualisant des indicateurs hydrologiques et météorologiques.

### Fonctionnalités principales

- ✅ **Interpolation spatiale** : Conversion de points discrets en surface continue
- ✅ **Masquage géographique** : Découpage selon des limites administratives
- ✅ **Palettes de couleurs** : Visualisation avec des couleurs adaptées à chaque indicateur
- ✅ **Export haute résolution** : Génération d'images PNG de qualité

### Cas d'utilisation

| Indicateur | Utilisation | Palette |
|------------|-------------|---------|
| **SSWI** | Standardized Soil Wetness Index | Turbo (inversée) |
| **Hydraulicité** | Niveau d'eau par rapport à la normale | Turbo (inversée) |
| Autre | Personnalisable | À définir |

---

## 📦 Dépendances

### Dépendances externes

```python
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
```

### Dépendances internes

```python
from model.enums import GeographicScaleClip
from src.config.paths import OUTPUT_DIR
from src.config.logging_config import setup_logger
from src.io.pynsee_departement import get_departements_from_regions
```

---

## 🔧 Fonctions

---

### `rasterize_geojson`

**Fonction principale : Rasterise un GeoDataFrame avec un masque géographique.**

#### 📌 Signature

```python
def rasterize_geojson(
    gdf_to_rasterize: gpd.GeoDataFrame,
    value_column_name: str,
    gdf_mask: gpd.GeoDataFrame,
    titre_graphique: str,
    color_palette: str,
    is_invert_palette: bool,
    intervalle_name: list[str],
    intervalle_marqueur: list[float],
    output_path: Path,
    geojson_to_draw: gpd.GeoDataFrame = None
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `gdf_to_rasterize` | `gpd.GeoDataFrame` | GeoDataFrame contenant les points à rasteriser | ✅ |
| `value_column_name` | `str` | Nom de la colonne contenant les valeurs à visualiser | ✅ |
| `gdf_mask` | `gpd.GeoDataFrame` | GeoDataFrame utilisé comme masque de découpe | ✅ |
| `titre_graphique` | `str` | Titre du graphique | ✅ |
| `color_palette` | `str` | Nom de la palette de couleurs matplotlib | ✅ |
| `is_invert_palette` | `bool` | Si True, inverse la palette | ✅ |
| `intervalle_name` | `list[str]` | Liste des noms pour les intervalles (barre de couleur) | ✅ |
| `intervalle_marqueur` | `list[float]` | Liste des valeurs de séparation entre intervalles | ✅ |
| `output_path` | `Path` | Chemin de sortie pour l'image PNG | ✅ |
| `geojson_to_draw` | `gpd.GeoDataFrame \| None` | GeoDataFrame supplémentaire à dessiner (contours) | `None` |

#### 📤 Retourne

`None` - L'image PNG est générée.

#### 📊 Comportement

**Étape 1 : Extraction des points**
```python
x = points.geometry.x.to_numpy()
y = points.geometry.y.to_numpy()
z = points[value_column_name].to_numpy()
```

**Étape 2 : Définition de la grille**
- Taille : `GRID_SIZE = 1500` (1500x1500 pixels)
- Étendue : Basée sur les limites des points (`total_bounds`)
- Résolution : `complex(GRID_SIZE)` pour une répartition uniforme

**Étape 3 : Interpolation**
- Méthode : `INTERPOLATION = "linear"`
- Utilise `scipy.interpolate.griddata()` pour interpoler les valeurs sur la grille

**Étape 4 : Transformation raster**
- Crée une transformation géoréférencée avec `from_bounds()`
- Écrit les données dans un dataset en mémoire

**Étape 5 : Masquage**
- Applique le masque géographique avec `rasterio.mask.mask()`
- Options : `crop=True, filled=True, nodata=np.nan`

**Étape 6 : Génération de l'image**
- Crée une figure matplotlib
- Applique la palette de couleurs (éventuellement inversée)
- Configure les intervalles avec `BoundaryNorm`
- Ajoute la barre de couleur avec les labels personnalisés
- Dessine la frontière du masque en noir
- Dessine éventuellement le GeoDataFrame supplémentaire

**Étape 7 : Export**
- Enregistre en PNG avec `dpi=300, transparent=True`
- Ferme la figure

#### ⚠️ Notes

- Le CRS doit être compatible entre les points et le masque
- Les valeurs `NaN` sont gérées par le masque
- La palette inversée permet d'avoir des couleurs adaptées (ex: bleu pour humide, rouge pour sec)

#### 📄 Fichiers générés

- `{output_path}.png` - Image PNG haute résolution (300 DPI)

#### 🎯 Exemple

```python
from pathlib import Path
import geopandas as gpd
from src.plotting.rasterize import rasterize_geojson

# Charger les données
points = gpd.read_file("output/QGIS/meteoFrance/MENS-SIM2-202606/bassin/MENS-SIM2-202606-B06.geojson").to_crs(2154)
mask = gpd.read_file("output/meteoFrance/downloaded_data/delimitation_qgis/BassinHydrographique_FXX.geojson").to_crs(2154)
mask = mask[mask["CdBH"] == "06"]

# Paramètres
palette = "turbo"
is_invert = True
intervalle_name = ["-1.25 - Extrêmement Sec", "-0.75", "-0.25", "0.25", "0.75", "1.25 - Extrêmement Humide", "Très Sec", "Modérément Sec", "Autour de la Normale", "Modérément Humide", "Très Humide"]
intervalle_marqueur = [-1.25, -0.75, -0.25, 0.25, 0.75, 1.25]

# Rasteriser
rasterize_geojson(
    gdf_to_rasterize=points,
    value_column_name="SSWI1",
    gdf_mask=mask,
    titre_graphique="SSWI1 du mois de Juin 2026 - Bassin Rhône-Méditerranée",
    color_palette=palette,
    is_invert_palette=is_invert,
    intervalle_name=intervalle_name,
    intervalle_marqueur=intervalle_marqueur,
    output_path=Path("output/test/sswi_juin_2026_bassin_06.png")
)
```

---

### `get_graphic_parameter`

**Récupère les paramètres graphiques pour un indicateur donné.**

#### 📌 Signature

```python
def get_graphic_parameter(unit_to_get_graphic: str) -> tuple[str, bool, list[str], list[float]] | None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `unit_to_get_graphic` | `str` | Nom de l'indicateur (ex: "SSWI1", "hydraulicite") | ✅ |

#### 📤 Retourne

`tuple[str, bool, list[str], list[float]] \| None` - Tuple contenant :
1. `palette_de_couleur` : Nom de la palette matplotlib
2. `is_palette_inverse` : Si True, la palette est inversée
3. `labels_colorBar` : Liste des labels pour la barre de couleur
4. `TickColorBar` : Liste des valeurs de séparation

Retourne `None` si l'indicateur n'est pas reconnu.

#### 📊 Paramètres par indicateur

**SSWI (tous types)** :
```python
(
    "turbo",
    True,  # Palette inversée
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
```

**Hydraulicité** :
```python
(
    "turbo",
    True,
    [
        "-0.25 - Très faible",
        "0.25",
        "0.75",
        "1.25",
        "1.75 - Très forte",
        "Faible",
        "Moyenne",
        "Forte",
    ],
    [-0.25, 0.25, 0.75, 1.25, 1.75]
)
```

#### 🎯 Exemple

```python
from src.plotting.rasterize import get_graphic_parameter

# Pour SSWI1
params = get_graphic_parameter("SSWI1")
if params:
    palette, is_invert, labels, ticks = params
    print(f"Palette: {palette}, Inversée: {is_invert}")
else:
    print("Indicateur non reconnu")
```

---

### `get_departement_to_draw_from_region`

**Récupère les départements d'une région pour les dessiner sur la carte.**

#### 📌 Signature

```python
def get_departement_to_draw_from_region(code_zone: str) -> gpd.GeoDataFrame
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `code_zone` | `str` | Code de la région | ✅ |

#### 📤 Retourne

`gpd.GeoDataFrame` - GeoDataFrame avec les départements de la région

#### 📊 Comportement

1. Charge le fichier des départements
2. Filtre pour ne garder que ceux de la région spécifiée
3. Convertit en Lambert 2 (EPSG:2154)

#### 📄 Fichiers utilisés

- `output/meteoFrance/downloaded_data/delimitation_qgis/departements-50m.geojson`

#### 🎯 Exemple

```python
from src.plotting.rasterize import get_departement_to_draw_from_region

# Récupérer les départements de la région 84 (Auvergne-Rhône-Alpes)
gdf_departements = get_departement_to_draw_from_region("84")
print(f"Nombre de départements : {len(gdf_departements)}")
```

---

### `rasterize_geodataframe_geographiv_zone`

**Fonction de haut niveau : Rasterise un GeoDataFrame pour une zone géographique spécifique.**

#### 📌 Signature

```python
def rasterize_geodataframe_geographiv_zone(
    geodataframe: gpd.GeoDataFrame,
    unit_to_rasterize: str,
    geographic_zone: GeographicScaleClip,
    code_zone: str,
    output_path: Path,
    titre_graphique: str,
    geojson_to_draw: gpd.GeoDataFrame = None
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `geodataframe` | `gpd.GeoDataFrame` | GeoDataFrame contenant les points à rasteriser | ✅ |
| `unit_to_rasterize` | `str` | Nom de la colonne à visualiser | ✅ |
| `geographic_zone` | `GeographicScaleClip` | Échelle géographique | ✅ |
| `code_zone` | `str` | Code de la zone | ✅ |
| `output_path` | `Path` | Chemin de sortie pour l'image | ✅ |
| `titre_graphique` | `str` | Titre du graphique | ✅ |
| `geojson_to_draw` | `gpd.GeoDataFrame \| None` | GeoDataFrame supplémentaire à dessiner | `None` |

#### 📤 Retourne

`None` - L'image PNG est générée.

#### 📊 Comportement

1. **Validation** : Vérifie que la colonne existe dans le GeoDataFrame
2. **Chargement du masque** : Selon l'échelle géographique :
   - **BASSIN** : `BassinHydrographique_FXX.geojson` (colonne `CdBH`)
   - **REGION_ADMINISTRATIVE / REGION_BASSIN** : `regions-100m.geojson` (colonne `code`) + charge les départements
   - **DEPARTEMENT_ADMINISTRATIF / DEPARTEMENT_BASSIN** : `departements-50m.geojson` (colonne `code`)
3. **Filtrage du masque** par le code de la zone
4. **Récupération des paramètres graphiques** : Appelle `get_graphic_parameter()`
5. **Appel de la rasterisation** : `rasterize_geojson()`

#### ⚠️ Notes

- Les GeoDataFrames doivent être dans le même CRS (recommandé : EPSG:2154)
- Le code de la zone doit exister dans le fichier de masque

#### 🎯 Exemple

```python
from pathlib import Path
import geopandas as gpd
from src.plotting.rasterize import rasterize_geodataframe_geographiv_zone
from src.model.enums import GeographicScaleClip

# Charger les données
points = gpd.read_file("output/QGIS/meteoFrance/MENS-SIM2-202606/region_administrative/MENS-SIM2-202606-R84.geojson").to_crs(2154)

# Rasteriser pour la région 84
rasterize_geodataframe_geographiv_zone(
    geodataframe=points,
    unit_to_rasterize="SSWI1",
    geographic_zone=GeographicScaleClip.REGION_ADMINISTRATIVE,
    code_zone="84",
    output_path=Path("output/test/sswi_juin_2026_region_84.png"),
    titre_graphique="SSWI1 au mois de Juin 2026 - Région Auvergne-Rhône-Alpes"
)
```

---

## 🎓 Tutoriel : Créer une Carte Rasterisée

### Étape 1 : Préparer les données

```python
import geopandas as gpd
from pathlib import Path

# Charger un GeoDataFrame avec des données SSWI
points = gpd.read_file(
    Path("output/QGIS/meteoFrance/MENS-SIM2-202606/bassin/MENS-SIM2-202606-B06.geojson")
).to_crs(2154)  # Lambert 93

# Vérifier que la colonne existe
print(f"Colonnes disponibles : {points.columns.tolist()}")
```

### Étape 2 : Charger le masque géographique

```python
from pathlib import Path
import geopandas as gpd

# Charger le masque du bassin 06
mask = gpd.read_file(
    Path("output/meteoFrance/downloaded_data/delimitation_qgis/BassinHydrographique_FXX.geojson")
).to_crs(2154)

# Filtrer pour le bassin 06 (Rhône-Méditerranée)
mask = mask[mask["CdBH"] == "06"]
```

### Étape 3 : Récupérer les paramètres graphiques

```python
from src.plotting.rasterize import get_graphic_parameter

# Pour l'indicateur SSWI1
params = get_graphic_parameter("SSWI1")
if params:
    palette, is_invert, labels, ticks = params
    print(f"✓ Paramètres trouvés pour SSWI1")
else:
    raise ValueError("Paramètres non trouvés pour SSWI1")
```

### Étape 4 : Générer la carte rasterisée

```python
from src.plotting.rasterize import rasterize_geojson

rasterize_geojson(
    gdf_to_rasterize=points,
    value_column_name="SSWI1",
    gdf_mask=mask,
    titre_graphique="SSWI1 - Juin 2026 - Bassin Rhône-Méditerranée",
    color_palette=palette,
    is_invert_palette=is_invert,
    intervalle_name=labels,
    intervalle_marqueur=ticks,
    output_path=Path("output/test/sswi_juin_2026_bassin_06.png")
)

print("✅ Carte rasterisée générée !")
```

### Étape 5 : Ajouter les contours des départements

```python
from src.plotting.rasterize import get_departement_to_draw_from_region

# Récupérer les départements de la région contenant le bassin 06
# Le bassin 06 (Rhône-Méditerranée) couvre principalement la région 84
departements = get_departement_to_draw_from_region("84")

# Rasteriser avec les contours
rasterize_geojson(
    gdf_to_rasterize=points,
    value_column_name="SSWI1",
    gdf_mask=mask,
    titre_graphique="SSWI1 - Juin 2026 - Bassin Rhône-Méditerranée avec départements",
    color_palette=palette,
    is_invert_palette=is_invert,
    intervalle_name=labels,
    intervalle_marqueur=ticks,
    output_path=Path("output/test/sswi_juin_2026_bassin_06_avec_departements.png"),
    geojson_to_draw=departements
)

print("✅ Carte avec contours générée !")
```

---

## 📊 Exemples Complets

### Exemple 1 : Rasterisation multi-indicateurs

```python
from pathlib import Path
import geopandas as gpd
from src.plotting.rasterize import rasterize_geojson, get_graphic_parameter

# Charger les données et le masque
points = gpd.read_file("output/QGIS/meteoFrance/MENS-SIM2-202606/bassin/MENS-SIM2-202606-B06.geojson").to_crs(2154)
mask = gpd.read_file("output/meteoFrance/downloaded_data/delimitation_qgis/BassinHydrographique_FXX.geojson").to_crs(2154)
mask = mask[mask["CdBH"] == "06"]

# Liste des indicateurs à rasteriser
indicateurs = ["SSWI1", "SPI1"]

for indicateur in indicateurs:
    print(f"Traitement de {indicateur}...")
    
    params = get_graphic_parameter(indicateur)
    if not params:
        print(f"⚠️ Paramètres non trouvés pour {indicateur}, passage...")
        continue
    
    palette, is_invert, labels, ticks = params
    
    rasterize_geojson(
        gdf_to_rasterize=points,
        value_column_name=indicateur,
        gdf_mask=mask,
        titre_graphique=f"{indicateur} - Juin 2026 - Bassin 06",
        color_palette=palette,
        is_invert_palette=is_invert,
        intervalle_name=labels,
        intervalle_marqueur=ticks,
        output_path=Path(f"output/test/{indicateur}_juin_2026_bassin_06.png")
    )
    
    print(f"✅ {indicateur} rasterisé")

print("✅ Tous les indicateurs rasterisés !")
```

### Exemple 2 : Rasterisation par zone géographique

```python
from pathlib import Path
import geopandas as gpd
from src.plotting.rasterize import rasterize_geodataframe_geographiv_zone
from src.model.enums import GeographicScaleClip

# Charger les données SIM2 pour toute la France
points = gpd.read_file("output/QGIS/meteoFrance/MENS-SIM2-202606/NATIONAL/MENS-SIM2-202606.geojson").to_crs(2154)

# Liste des zones à rasteriser
zones = [
    (GeographicScaleClip.BASSIN, "06", "Bassin Rhône-Méditerranée"),
    (GeographicScaleClip.BASSIN, "07", "Bassin Adour-Garonne"),
    (GeographicScaleClip.REGION_ADMINISTRATIVE, "84", "Région Auvergne-Rhône-Alpes"),
]

for echelle, code, nom in zones:
    print(f"Rasterisation pour {nom} ({echelle} - {code})...")
    
    try:
        rasterize_geodataframe_geographiv_zone(
            geodataframe=points,
            unit_to_rasterize="SSWI1",
            geographic_zone=echelle,
            code_zone=code,
            output_path=Path(f"output/test/sswi_juin_2026_{echelle}_{code}.png"),
            titre_graphique=f"SSWI1 - Juin 2026 - {nom}"
        )
        print(f"✅ {nom} rasterisé")
    except Exception as e:
        print(f"❌ Erreur pour {nom}: {e}")

print("✅ Rasterisation par zone terminée !")
```

### Exemple 3 : Rasterisation avec données hydrologiques

```python
from pathlib import Path
import geopandas as gpd
from src.plotting.rasterize import rasterize_geodataframe_geographiv_zone, get_graphic_parameter
from src.model.enums import GeographicScaleClip

# Charger les données d'hydraulicité
hydro_data = gpd.read_file(
    Path("output/QGIS/hydraulicite/hydraulicite-BSH001-2026-01.geojson")
).to_crs(2154)

# Vérifier que la colonne hydraulicite existe
if "hydraulicite" not in hydro_data.columns:
    print("❌ Colonne 'hydraulicite' non trouvée")
    # Essayer avec d'autres noms possibles
    for col in hydro_data.columns:
        if "hydraul" in col.lower():
            hydro_data = hydro_data.rename(columns={col: "hydraulicite"})
            break

# Récupérer les paramètres pour l'hydraulicité
params = get_graphic_parameter("hydraulicite")
if not params:
    print("❌ Paramètres non trouvés pour hydraulicite")
    # Définir des paramètres par défaut
    params = (
        "turbo",
        True,
        ["Faible", "Moyenne", "Forte", "Très forte"],
        [0.5, 1.0, 1.5, 2.0]
    )

palette, is_invert, labels, ticks = params

# Rasteriser
rasterize_geodataframe_geographiv_zone(
    geodataframe=hydro_data,
    unit_to_rasterize="hydraulicite",
    geographic_zone=GeographicScaleClip.BASSIN,
    code_zone="01",  # BSH001 correspond au bassin 01
    output_path=Path("output/test/hydraulicite_janvier_2026_bassin_01.png"),
    titre_graphique="Hydraulicité - Janvier 2026 - BSH001"
)

print("✅ Hydraulicité rasterisée !")
```

---

## 📚 Voir aussi

- [Module plotting](index.md) - Aperçu du module
- [plot_grandeur](plot_grandeur.md) - Données hydrologiques
- [plot_meteoFrance](plot_meteoFrance.md) - Données météorologiques
- [plot_onde](plot_onde.md) - Données ONDE
- [Concepts : SSWI](../../../concepts/spi-sswi.md)
- [Concepts : Hydraulicité](../../../concepts/hydraulicite.md)

---

## 🎯 Résumé des Fonctions

| Fonction | Description | Sortie |
|----------|-------------|--------|
| `rasterize_geojson` | **Fonction principale** - Rasterise un GeoDataFrame | `.png` |
| `get_graphic_parameter` | Récupère les paramètres pour un indicateur | `tuple` |
| `get_departement_to_draw_from_region` | Récupère les départements d'une région | `GeoDataFrame` |
| `rasterize_geodataframe_geographiv_zone` | Rasterise pour une zone géographique | `.png` |

---

## 🎨 Palettes de Couleurs par Défaut

### SSWI (Standardized Soil Wetness Index)

| Valeur | Couleur | Signification |
|--------|---------|---------------|
| <-1.25 | Dark Red | Extrêmement sec |
| -1.25 à -0.75 | Dark Orange | Très sec |
| -0.75 à -0.25 | Yellow | Modérément sec |
| -0.25 à 0.25 | Lime | Autour de la normale |
| 0.25 à 0.75 | Turquoise | Modérément humide |
| 0.75 à 1.25 | Royal Blue | Très humide |
| >1.25 | Midnight Blue | Extrêmement humide |

### Hydraulicité

| Valeur | Couleur | Signification |
|--------|---------|---------------|
| <-0.25 | Dark Red | Très faible |
| -0.25 à 0.25 | Red | Faible |
| 0.25 à 0.75 | Orange | Moyenne |
| 0.75 à 1.25 | Yellow | Forte |
| 1.25 à 1.75 | Light Green | Très forte |

---

## ⚙️ Paramètres Techniques

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| `GRID_SIZE` | 1500 | Taille de la grille d'interpolation |
| `INTERPOLATION` | "linear" | Méthode d'interpolation |
| `ENABLE_CLIP` | True | Active le masquage géographique |
| DPI | 300 | Résolution des images générées |
| CRS recommandé | EPSG:2154 | Lambert 93 (pour la France) |

---

*Documentation générée automatiquement à partir du code source | Dernière mise à jour : {{ "now" | date: "%d %B %Y" }}*



