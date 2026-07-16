---
layout: default
title: plot_meteoFrance
description: "Documentation API du module plot_meteoFrance - Visualisation des données météorologiques"
nav_order: 2
parent: Module Plotting
grand_parent: Modules
---

# 🌦️ plot_meteoFrance

**Documentation API complète**

> **Fichier** : `src/plotting/plot_meteoFrance.py`
> **Module** : Visualisation des données météorologiques
> **Auteur** : Thomas Meslin
> **Dernière mise à jour** : Juin 2026

---

## 📋 Table des Matières

- [🎯 Aperçu](#-aperçu)
- [📦 Dépendances](#-dépendances)
- [🔧 Fonctions](#-fonctions)
  - [to_lambert2_geodataframe](#to_lambert2_geodataframe)
  - [clip_with_distance](#clip_with_distance)
  - [plot_geojson_from_lambert2](#plot_geojson_from_lambert2)
  - [get_chemin_sauvegarde](#get_chemin_sauvegarde)
  - [get_chemin_sauvegarde_geographie](#get_chemin_sauvegarde_geographie)
  - [export_to_every_geographic_element](#export_to_every_geographic_element)
  - [create_all_plot_for_unique_scale](#create_all_plot_for_unique_scale)
  - [df_range_processed](#df_range_processed)
  - [export_all_format_geojson_range](#export_all_format_geojson_range)
  - [export_geojson_month](#export_geojson_month)
  - [export_geojson_day](#export_geojson_day)
  - [get_all_geographic_geodf](#get_all_geographic_geodf)
  - [get_geographic_element](#get_geographic_element)
  - [get_bassin_versant](#get_bassin_versant)
  - [plot_bar_dataframe](#plot_bar_dataframe)
- [🎓 Tutoriel](#-tutoriel)
- [📊 Exemples Complets](#-exemples-complets)

---

## 🎯 Aperçu

Ce module gère la **visualisation et l'export des données météorologiques** provenants de MétéoFrance. Il permet de :

- ✅ **Exporter des données** au format GeoJSON pour différentes échelles géographiques
- ✅ **Générer des graphiques temporels** pour divers indicateurs (SPI, SSWI, précipitations, etc.)
- ✅ **Découper géographiquement** les données par bassin, région ou département
- ✅ **Agréger des données** sur des périodes spécifiques
- ✅ **Créer des visualisations** avec des palettes de couleurs personnalisées

### Domaines couverts

| Domaine | Description | Types de données |
|---------|-------------|-----------------|
| **Données SIM2** | Données interpolées sur grille 8x8km | QUOT, MENS |
| **Données brutes** | Données de stations météorologiques | QUOT, MENS |
| **Export multi-échelles** | Découpage par zone géographique | Bassin, Région, Département |
| **Graphiques temporels** | Visualisation chronologique | SPI, SSWI, PE, RR, ETP |
| **Agrégation** | Sommation sur des périodes | Par date, par position |

---

## 📦 Dépendances

### Dépendances externes

```python
from tqdm import tqdm
from datetime import datetime
from pathlib import Path
import calendar
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from functools import cache
```

### Dépendances internes

```python
from src.model.enums import GeographicScaleClip, MeteoFranceDataType
import src.io.download_meteoFrance as DMeteo
from src.processing.meteoFrance_aggregation_donnee import GroupByMethod, aggregate_range
from src.config.logging_config import setup_logger
from src.config.paths import OUTPUT_DIR
```

---

## 🔧 Fonctions

---

### `to_lambert2_geodataframe`

**Convertit un DataFrame en GeoDataFrame avec projection Lambert 2.**

#### 📌 Signature

```python
def to_lambert2_geodataframe(
    data_freq: MeteoFranceDataType,
    df_to_convert: pd.DataFrame
) -> gpd.GeoDataFrame
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `data_freq` | `MeteoFranceDataType` | Type de données (SIM2_QUOT, SIM2_MENS, QUOT, MENS) | ✅ |
| `df_to_convert` | `pd.DataFrame` | DataFrame à convertir | ✅ |

#### 📤 Retourne

`gpd.GeoDataFrame` - GeoDataFrame avec géométrie en Lambert 2 (EPSG:27572)

#### 📊 Comportement

Selon le type de données :
- **SIM2_QUOT / SIM2_MENS** : Utilise les colonnes `LAMBX` et `LAMBY` (multipliées par 100)
- **QUOT / MENS** : Utilise les colonnes `LON` et `LAT` (converties en Lambert 2)

#### ⚠️ Notes

- Le DataFrame doit contenir les colonnes appropriées selon le type
- Le CRS est toujours **EPSG:27572** (Lambert 2 étendu)

#### 🎯 Exemple

```python
import pandas as pd
from src.plotting.plot_meteoFrance import to_lambert2_geodataframe
from src.model.enums import MeteoFranceDataType

# Exemple avec données SIM2
df_sim2 = pd.DataFrame({
    'LAMBX': [123456, 123457],
    'LAMBY': [678901, 678902],
    'SSWI1': [0.5, -0.3]
})

gdf = to_lambert2_geodataframe(
    MeteoFranceDataType.SIM2_MENS,
    df_sim2
)
print(gdf.crs)  # EPSG:27572
```

---

### `clip_with_distance`

**Découpe un GeoDataFrame en utilisant une distance de masquage.**

#### 📌 Signature

```python
def clip_with_distance(
    gdf_to_clip: gpd.GeoDataFrame,
    clip_mask: gpd.GeoDataFrame
) -> gpd.GeoDataFrame
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `gdf_to_clip` | `gpd.GeoDataFrame` | GeoDataFrame à découper | ✅ |
| `clip_mask` | `gpd.GeoDataFrame` | Masque de découpe | ✅ |

#### 📤 Retourne

`gpd.GeoDataFrame` - GeoDataFrame découpé

#### 📊 Comportement

1. Vérifie que le masque ne contient pas plusieurs géométries (affiche un avertissement si c'est le cas)
2. Retourne les entités du GeoDataFrame d'origine dont la distance au masque est inférieure à **7000 mètres**

#### ⚠️ Notes

- La distance de 7000m permet de prendre une marge autour des contours
- Les deux GeoDataFrames doivent être dans le même CRS

#### 🎯 Exemple

```python
import geopandas as gpd
from src.plotting.plot_meteoFrance import clip_with_distance

# Charger un GeoDataFrame et un masque
gdf_donnees = gpd.read_file("donnees.geojson").to_crs("EPSG:27572")
gdf_masque = gpd.read_file("masque.geojson").to_crs("EPSG:27572")

# Découper
resultat = clip_with_distance(gdf_donnees, gdf_masque)
```

---

### `plot_geojson_from_lambert2`

**Enregistre un GeoDataFrame sous forme de GeoJSON et CSV.**

#### 📌 Signature

```python
def plot_geojson_from_lambert2(
    output_path: Path,
    gdf_ready: gpd.GeoDataFrame
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `output_path` | `Path` | Chemin de base pour les fichiers de sortie | ✅ |
| `gdf_ready` | `gpd.GeoDataFrame` | GeoDataFrame à exporter | ✅ |

#### 📤 Retourne

`None` - Les fichiers sont enregistrés.

#### 📊 Comportement

1. Si le GeoDataFrame est vide, affiche un avertissement et ne fait rien
2. Sinon, exporte en :
   - `{output_path}.geojson` - Fichier GeoJSON
   - `{output_path}.csv` - Fichier CSV

#### ⚠️ Notes

- Le mode d'écriture (`mode="w"`) écrase les fichiers existants

#### 🎯 Exemple

```python
from pathlib import Path
import geopandas as gpd
from src.plotting.plot_meteoFrance import plot_geojson_from_lambert2

gdf = gpd.GeoDataFrame(...)
plot_geojson_from_lambert2(
    Path("output/meteo/test"),
    gdf
)
# Crée : output/meteo/test.geojson et output/meteo/test.csv
```

---

### `get_chemin_sauvegarde`

**Retourne le chemin de sauvegarde pour un type de données et une période.**

#### 📌 Signature

```python
def get_chemin_sauvegarde(
    data_freq: MeteoFranceDataType,
    start_date: datetime,
    end_date: datetime,
    is_data_aggregated: bool
) -> Path
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `data_freq` | `MeteoFranceDataType` | Type de données | ✅ |
| `start_date` | `datetime` | Date de début | ✅ |
| `end_date` | `datetime` | Date de fin | ✅ |
| `is_data_aggregated` | `bool` | Si les données sont agrégées | ✅ |

#### 📤 Retourne

`Path` - Chemin complet pour le fichier de sortie

#### 📊 Comportement

Génère un chemin selon le type de données et la période :

- **SIM2_QUOT** : `QGIS/meteoFrance/QUOT-SIM2[-aggregated]-{dates}/{fichier}.geojson`
- **SIM2_MENS** : `QGIS/meteoFrance/MENS-SIM2[-aggregated]-{dates}/{fichier}.geojson`
- **QUOT** : `QGIS/meteoFrance/QUOT[-aggregated]-{dates}/{fichier}.geojson`
- **MENS** : `QGIS/meteoFrance/MENS[-aggregated]-{dates}/{fichier}.geojson`

#### 🎯 Exemple

```python
from datetime import datetime
from src.plotting.plot_meteoFrance import get_chemin_sauvegarde
from src.model.enums import MeteoFranceDataType

chemin = get_chemin_sauvegarde(
    MeteoFranceDataType.SIM2_MENS,
    datetime(2026, 1, 1),
    datetime(2026, 1, 31),
    False
)
# Retourne : output/QGIS/meteoFrance/MENS-SIM2-202601-202601/MENS-SIM2-202601-202601.geojson
```

---

### `get_chemin_sauvegarde_geographie`

**Retourne le chemin de sauvegarde pour une zone géographique spécifique.**

#### 📌 Signature

```python
def get_chemin_sauvegarde_geographie(
    geographic_scale: GeographicScaleClip,
    chemin_sauvegarde_original: Path,
    code_geographique: str | None = ""
) -> Path
```

#### 📝 Paramètres

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `geographic_scale` | `GeographicScaleClip` | Échelle géographique | ✅ |
| `chemin_sauvegarde_original` | `Path` | Chemin de base | ✅ |
| `code_geographique` | `str \| None` | Code de la zone | `""` |

#### 📤 Retourne

`Path` - Chemin avec suffixe géographique

#### 📊 Comportement

Ajoute un suffixe au nom du fichier selon l'échelle :

| Échelle | Suffix | Dossier |
|--------|--------|---------|
| BASSIN | `-B{code}` | `bassin/` |
| DEPARTEMENT_BASSIN | `-Db{code}` | `departement_bassin/` |
| DEPARTEMENT_ADMINISTRATIF | `-D{code}` | `departement_administratif/` |
| REGION_BASSIN | `-Rb{code}` | `region_bassin/` |
| REGION_ADMINISTRATIVE | `-R{code}` | `region_administrative/` |
| NATIONAL | (aucun) | (aucun) |

#### 🎯 Exemple

```python
from src.plotting.plot_meteoFrance import get_chemin_sauvegarde_geographie
from src.model.enums import GeographicScaleClip

chemin_base = Path("output/QGIS/meteoFrance/MENS-SIM2-202601/MENS-SIM2-202601.geojson")

# Pour le bassin 06
chemin_bassin = get_chemin_sauvegarde_geographie(
    GeographicScaleClip.BASSIN,
    chemin_base,
    "06"
)
# Retourne : output/QGIS/meteoFrance/MENS-SIM2-202601/bassin/MENS-SIM2-202601-B06.geojson
```

---

### `export_to_every_geographic_element`

**Exporte les données pour toutes les zones géographiques d'une échelle donnée.**

#### 📌 Signature

```python
def export_to_every_geographic_element(
    data_freq: MeteoFranceDataType,
    geographic_scale: GeographicScaleClip,
    df: pd.DataFrame,
    chemin_save_original: Path,
    is_data_aggregated: bool
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `data_freq` | `MeteoFranceDataType` | Type de données | ✅ |
| `geographic_scale` | `GeographicScaleClip` | Échelle géographique | ✅ |
| `df` | `pd.DataFrame` | DataFrame contenant les données | ✅ |
| `chemin_save_original` | `Path` | Chemin de base pour la sauvegarde | ✅ |
| `is_data_aggregated` | `bool` | Si les données sont agrégées | ✅ |

#### 📤 Retourne

`None` - Les fichiers sont exportés pour chaque zone.

#### 📊 Comportement

1. Récupère la liste des zones géographiques pour l'échelle
2. Convertit le DataFrame en GeoDataFrame
3. Pour chaque zone :
   - Découpe le GeoDataFrame avec le masque de la zone
   - Découpe éventuellement avec le masque du bassin (si nécessaire)
   - Si des données restent, exporte en GeoJSON
   - Si les données ne sont pas agrégées, génère aussi des graphiques
4. Utilise `tqdm` pour afficher une barre de progression

#### 📄 Fichiers générés

- `{chemin}/bassin/{zone}/*.geojson` (selon l'échelle)
- `{chemin}/bassin/{zone}/plots/*.png` (si pas d'agrégation)

#### 🎯 Exemple

```python
import pandas as pd
from pathlib import Path
from src.plotting.plot_meteoFrance import export_to_every_geographic_element
from src.model.enums import GeographicScaleClip, MeteoFranceDataType

df = pd.read_csv("donnees_meteo.csv")
chemin_base = Path("output/QGIS/meteoFrance/test")

export_to_every_geographic_element(
    MeteoFranceDataType.SIM2_MENS,
    GeographicScaleClip.BASSIN,
    df,
    chemin_base,
    False
)
```

---

### `create_all_plot_for_unique_scale`

**Crée tous les graphiques pour une échelle géographique unique.**

#### 📌 Signature

```python
def create_all_plot_for_unique_scale(
    df_aggregated: pd.DataFrame,
    nom_echelle: str,
    start_date: datetime,
    end_date: datetime,
    chemin_de_base: Path
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `df_aggregated` | `pd.DataFrame` | DataFrame avec les données agrégées | ✅ |
| `nom_echelle` | `str` | Nom de l'échelle pour le titre | ✅ |
| `start_date` | `datetime` | Date de début | ✅ |
| `end_date` | `datetime` | Date de fin | ✅ |
| `chemin_de_base` | `Path` | Dossier de base pour les graphiques | ✅ |

#### 📤 Retourne

`None` - Les graphiques sont enregistrés dans le dossier.

#### 📊 Comportement

1. Crée le dossier de sortie
2. Pour chaque indicateur présent dans le DataFrame, crée un graphique :
   - **SSWI_10J** : Graphique avec palette de couleurs par niveau de sécheresse
   - **PE** : Pluie efficace
   - **PRELIQ** : Cumul des précipitations liquides
   - **EVAP** : Cumul de l'évapotranspiration
   - **ETP** : Cumul de l'évapotranspiration potentielle
   - **RR** : Cumul de pluie
   - **SPI1** : Indice de précipitation standardisé

#### ⚠️ Notes

- Utilise `plot_bar_dataframe()` pour chaque indicateur
- Le titre suit le format : `[Indicateur] : [nom_echelle] [start_date] [end_date]`

#### 🎯 Exemple

```python
from datetime import datetime
from pathlib import Path
import pandas as pd
from src.plotting.plot_meteoFrance import create_all_plot_for_unique_scale

df = pd.DataFrame({
    'DATE_DATETIME': pd.date_range('2026-01-01', '2026-01-31'),
    'SSWI_10J': [0.5, -0.3, 0.1, ...],
    'RR': [10, 15, 5, ...]
})

create_all_plot_for_unique_scale(
    df,
    "Bassin 06",
    datetime(2026, 1, 1),
    datetime(2026, 1, 31),
    Path("output/test/plots")
)
# Crée : output/test/plots/SSWI_10J.png et output/test/plots/RR.png
```

---

### `df_range_processed`

**Retourne un DataFrame avec toutes les données entre deux dates.**

#### 📌 Signature

```python
def df_range_processed(
    data_freq: MeteoFranceDataType,
    start_date: datetime,
    end_date: datetime,
    is_data_aggregated: bool = True,
    has_index_update: bool = True,
    is_data_update_allowed: bool = True
) -> pd.DataFrame
```

#### 📝 Paramètres

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `data_freq` | `MeteoFranceDataType` | Type de données | ✅ |
| `start_date` | `datetime` | Date de début | ✅ |
| `end_date` | `datetime` | Date de fin | ✅ |
| `is_data_aggregated` | `bool` | Si les données doivent être agrégées | `True` |
| `has_index_update` | `bool` | Autorise la mise à jour de l'index | `True` |
| `is_data_update_allowed` | `bool` | Autorise la mise à jour des données | `True` |

#### 📤 Retourne

`pd.DataFrame` - DataFrame contenant les données de la période

#### 📊 Comportement

1. Récupère les données dans la plage de dates
2. Si `is_data_aggregated=True`, aggrège les données
3. Retourne le DataFrame ou un DataFrame vide si aucune donnée

#### 🎯 Exemple

```python
from datetime import datetime
from src.plotting.plot_meteoFrance import df_range_processed
from src.model.enums import MeteoFranceDataType

df = df_range_processed(
    MeteoFranceDataType.SIM2_QUOT,
    datetime(2026, 1, 1),
    datetime(2026, 1, 31),
    is_data_aggregated=False
)
```

---

### `export_all_format_geojson_range`

**Fonction principale : Exporte des GeoJSON pour toutes les échelles géographiques.**

#### 📌 Signature

```python
def export_all_format_geojson_range(
    geo_scale: GeographicScaleClip,
    data_freq: MeteoFranceDataType,
    start_date: datetime,
    end_date: datetime,
    is_data_aggregated: bool,
    has_index_update: bool = True,
    is_data_update_allowed: bool = True
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `geo_scale` | `GeographicScaleClip` | Échelle géographique de base | ✅ |
| `data_freq` | `MeteoFranceDataType` | Type de données | ✅ |
| `start_date` | `datetime` | Date de début | ✅ |
| `end_date` | `datetime` | Date de fin | ✅ |
| `is_data_aggregated` | `bool` | Si les données sont agrégées | ✅ |
| `has_index_update` | `bool` | Autorise la mise à jour de l'index | `True` |
| `is_data_update_allowed` | `bool` | Autorise la mise à jour des données | `True` |

#### 📤 Retourne

`None` - Les fichiers GeoJSON et graphiques sont générés.

#### 📊 Comportement

1. Si `is_data_update_allowed=False`, force `has_index_update=False`
2. Récupère les données pour la période
3. Détermine le chemin de sauvegarde
4. Appelle `export_to_every_geographic_element()` pour exporter les données

#### 📄 Fichiers générés

- Plusieurs GeoJSON par zone géographique
- Plusieurs PNG de graphiques (si pas d'agrégation)

#### 🎯 Exemple

```python
from datetime import datetime
from src.plotting.plot_meteoFrance import export_all_format_geojson_range
from src.model.enums import GeographicScaleClip, MeteoFranceDataType

export_all_format_geojson_range(
    GeographicScaleClip.BASSIN,
    MeteoFranceDataType.SIM2_MENS,
    datetime(2026, 1, 1),
    datetime(2026, 1, 31),
    is_data_aggregated=False,
    has_index_update=True,
    is_data_update_allowed=True
)
```

---

### `export_geojson_month`

**Exporte un mois entier de données météo.**

#### 📌 Signature

```python
def export_geojson_month(
    data_freq: MeteoFranceDataType,
    month_date: datetime
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `data_freq` | `MeteoFranceDataType` | Type de données | ✅ |
| `month_date` | `datetime` | Date représentant le mois | ✅ |

#### 📤 Retourne

`None` - Les fichiers sont générés.

#### 📊 Comportement

1. Calcule les dates de début et fin du mois
2. Appelle `export_all_format_geojson_range()` avec `is_data_aggregated=False`

#### 🎯 Exemple

```python
from datetime import datetime
from src.plotting.plot_meteoFrance import export_geojson_month
from src.model.enums import MeteoFranceDataType

export_geojson_month(
    MeteoFranceDataType.SIM2_QUOT,
    datetime(2026, 1, 15)  # N'importe quel jour du mois
)
# Exporte tous les jours de janvier 2026
```

---

### `export_geojson_day`

**Exporte un seul jour de données météo.**

#### 📌 Signature

```python
def export_geojson_day(
    data_freq: MeteoFranceDataType,
    day_date: datetime
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `data_freq` | `MeteoFranceDataType` | Type de données | ✅ |
| `day_date` | `datetime` | Date du jour à exporter | ✅ |

#### 📤 Retourne

`None` - Les fichiers sont générés.

#### 📊 Comportement

1. Utilise la même date pour start_date et end_date
2. Appelle `export_all_format_geojson_range()` avec `is_data_aggregated=False`

#### 🎯 Exemple

```python
from datetime import datetime
from src.plotting.plot_meteoFrance import export_geojson_day
from src.model.enums import MeteoFranceDataType

export_geojson_day(
    MeteoFranceDataType.QUOT,
    datetime(2026, 1, 15)
)
# Exporte les données du 15 janvier 2026
```

---

### `get_all_geographic_geodf`

**Récupère le GeoDataFrame pour toutes les zones géographiques d'une échelle.**

#### 📌 Signature

```python
@cache
def get_all_geographic_geodf(
    geographic_scale: GeographicScaleClip
) -> gpd.GeoDataFrame
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `geographic_scale` | `GeographicScaleClip` | Échelle géographique | ✅ |

#### 📤 Retourne

`gpd.GeoDataFrame` - GeoDataFrame avec toutes les zones

#### 📊 Comportement

1. Détermine le fichier correspondant selon l'échelle
2. Si le fichier n'existe pas, le télécharge
3. Retourne le GeoDataFrame en Lambert 2 (EPSG:27572)

#### 📄 Fichiers utilisés

| Échelle | Fichier |
|--------|--------|
| REGION_BASSIN / REGION_ADMINISTRATIVE | `regions-100m.geojson` |
| DEPARTEMENT_BASSIN / DEPARTEMENT_ADMINISTRATIF | `departements-50m.geojson` |
| BASSIN | `BassinHydrographique_FXX.geojson` |

#### 🎯 Exemple

```python
from src.plotting.plot_meteoFrance import get_all_geographic_geodf
from src.model.enums import GeographicScaleClip

gdf_regions = get_all_geographic_geodf(GeographicScaleClip.REGION_ADMINISTRATIVE)
print(f"Nombre de régions : {len(gdf_regions)}")
```

---

### `get_geographic_element`

**Récupère une zone géographique spécifique.**

#### 📌 Signature

```python
def get_geographic_element(
    geographic_scale: GeographicScaleClip,
    code: str
) -> gpd.GeoDataFrame
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `geographic_scale` | `GeographicScaleClip` | Échelle géographique | ✅ |
| `code` | `str` | Code de la zone | ✅ |

#### 📤 Retourne

`gpd.GeoDataFrame` - GeoDataFrame avec la zone correspondante

#### 📊 Comportement

1. Récupère toutes les zones de l'échelle
2. Filtre par la colonne appropriée (CdBH, code) selon l'échelle
3. Retourne le GeoDataFrame filtré

#### 🎯 Exemple

```python
from src.plotting.plot_meteoFrance import get_geographic_element
from src.model.enums import GeographicScaleClip

# Récupérer le bassin 06
gdf_bassin_06 = get_geographic_element(
    GeographicScaleClip.BASSIN,
    "06"
)

# Récupérer la région 84
gdf_region_84 = get_geographic_element(
    GeographicScaleClip.REGION_ADMINISTRATIVE,
    "84"
)
```

---

### `get_bassin_versant`

**Récupère un bassin versant spécifique.**

#### 📌 Signature

```python
def get_bassin_versant(code: str) -> gpd.GeoDataFrame
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `code` | `str` | Code du bassin | ✅ |

#### 📤 Retourne

`gpd.GeoDataFrame` - GeoDataFrame du bassin

#### 📊 Comportement

1. Récupère toutes les zones de l'échelle BASSIN
2. Filtre par la colonne `CdBH`
3. Retourne le GeoDataFrame du bassin

#### 🎯 Exemple

```python
from src.plotting.plot_meteoFrance import get_bassin_versant

gdf_bassin = get_bassin_versant("06")  # Rhône-Méditerranée
```

---

### `plot_bar_dataframe`

**Génère un graphique en barres à partir d'une Series.**

#### 📌 Signature

```python
def plot_bar_dataframe(
    series_to_plot: pd.Series,
    series_date: pd.Series,
    normale_value: float = None,
    plot_title: str = "",
    reference_lines: dict[str, tuple[float, float, str]] = None,
    output_path: Path = None
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `series_to_plot` | `pd.Series` | Série de valeurs à afficher | ✅ |
| `series_date` | `pd.Series` | Série de dates correspondantes | ✅ |
| `normale_value` | `float \| None` | Valeur de référence (ligne rouge) | `None` |
| `plot_title` | `str` | Titre du graphique | `""` |
| `reference_lines` | `dict \| None` | Lignes de référence horizontales | `None` |
| `output_path` | `Path \| None` | Chemin pour enregistrer le graphique | `None` |

#### 📤 Retourne

`None` - Le graphique est affiché ou enregistré.

#### 📊 Comportement

1. Crée une figure matplotlib
2. Si `reference_lines` est fourni, ajoute des zones colorées horizontales
3. Ajoute les barres pour la série
4. Si `normale_value` est fourni, ajoute une ligne rouge pointillée
5. Configure le titre et les labels
6. Enregistre le graphique si `output_path` est fourni

#### 🎨 Paramètre `reference_lines`

```python
reference_lines = {
    "Extrêmement humide": (1.75, max_value, "midnightblue"),
    "Très humide": (1.28, 1.75, "royalblue"),
    "Modérément humide": (0.84, 1.28, "turquoise"),
    "Autour de la Normale": (-0.84, 0.84, "lime"),
    "Modérément sec": (-1.28, -0.84, "yellow"),
    "Très sec": (-1.75, -1.28, "darkorange"),
    "Extrêmement sec": (min_value, -1.75, "darkred"),
}
```

#### 🎯 Exemple

```python
import pandas as pd
from pathlib import Path
from src.plotting.plot_meteoFrance import plot_bar_dataframe
import matplotlib.pyplot as plt

# Données d'exemple
dates = pd.date_range('2026-01-01', '2026-01-31')
values = [0.5, -0.3, 0.1, 0.8, -0.5, ...]  # 31 valeurs

plot_bar_dataframe(
    series_to_plot=pd.Series(values, name="SSWI_10J"),
    series_date=pd.Series(dates, name="Date"),
    normale_value=0,
    plot_title="Standardized Soil Wetness Index - Janvier 2026",
    reference_lines={
        "Très humide": (1.28, 1.75, "royalblue"),
        "Autour de la Normale": (-0.84, 0.84, "lime"),
        "Très sec": (-1.75, -1.28, "darkorange"),
    },
    output_path=Path("output/plots/sswi_janvier.png")
)
```

---

## 🎓 Tutoriel : Créer une Carte Météorologique Complète

### Étape 1 : Importer les modules

```python
from datetime import datetime
from src.plotting.plot_meteoFrance import export_all_format_geojson_range
from src.model.enums import GeographicScaleClip, MeteoFranceDataType
```

### Étape 2 : Exporter les données SIM2 mensuelles

```python
# Exporter les données SIM2 mensuelles pour janvier 2026
# Découpées par bassin, avec graphiques
start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 1, 31)

export_all_format_geojson_range(
    geo_scale=GeographicScaleClip.BASSIN,
    data_freq=MeteoFranceDataType.SIM2_MENS,
    start_date=start_date,
    end_date=end_date,
    is_data_aggregated=False,  # Génère des graphiques par bassin
    has_index_update=True,
    is_data_update_allowed=True
)
```

**Résultats :**
- `output/QGIS/meteoFrance/MENS-SIM2-202601-202601/`
  - `bassin/MENS-SIM2-202601-202601-B{code}.geojson` (pour chaque bassin)
  - `bassin/MENS-SIM2-202601-202601-B{code}/plots/`
    - `SSWI_10J.png`, `SPI1.png`, etc.

### Étape 3 : Exporter les données agrégées

```python
# Exporter les données agrégées sur toute la période (sans graphiques)
export_all_format_geojson_range(
    geo_scale=GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF,
    data_freq=MeteoFranceDataType.SIM2_QUOT,
    start_date=datetime(2026, 6, 1),
    end_date=datetime(2026, 6, 30),
    is_data_aggregated=True,  # Données agrégées, pas de graphiques
    has_index_update=False,
    is_data_update_allowed=False
)
```

**Résultats :**
- `output/QGIS/meteoFrance/QUOT-SIM2-aggregated-20260601-20260630/`
  - `departement_administratif/QUOT-SIM2-aggregated-20260601-20260630-D{code}.geojson`

### Étape 4 : Exporter un jour spécifique

```python
# Exporter les données du 15 juin 2026
export_geojson_day(
    data_freq=MeteoFranceDataType.QUOT,
    day_date=datetime(2026, 6, 15)
)
```

---

## 📊 Exemples Complets

### Exemple 1 : Génération mensuelle pour tous les bassins

```python
from datetime import datetime
from src.plotting.plot_meteoFrance import export_all_format_geojson_range
from src.model.enums import GeographicScaleClip, MeteoFranceDataType

# Générer pour chaque mois de 2025
for mois in range(1, 13):
    start_date = datetime(2025, mois, 1)
    end_date = datetime(2025, mois, 1)
    
    # Le dernier jour du mois sera calculé automatiquement
    # si start_date et end_date sont le même jour
    
    print(f"Traitement du mois {mois:02d}/2025...")
    
    export_all_format_geojson_range(
        geo_scale=GeographicScaleClip.BASSIN,
        data_freq=MeteoFranceDataType.SIM2_MENS,
        start_date=start_date,
        end_date=end_date,
        is_data_aggregated=False
    )

print("✅ Toutes les données mensuelles générées !")
```

### Exemple 2 : Génération quotidienne pour une semaine

```python
from datetime import datetime, timedelta
from src.plotting.plot_meteoFrance import export_geojson_day
from src.model.enums import MeteoFranceDataType

# Générer pour chaque jour d'une semaine
start_date = datetime(2026, 6, 10)
for i in range(7):
    current_date = start_date + timedelta(days=i)
    print(f"Traitement du {current_date.strftime('%Y-%m-%d')}...")
    
    export_geojson_day(
        data_freq=MeteoFranceDataType.SIM2_QUOT,
        day_date=current_date
    )

print("✅ Données quotidiennes générées !")
```

### Exemple 3 : Génération agrégée pour une analyse globale

```python
from datetime import datetime
from src.plotting.plot_meteoFrance import export_all_format_geojson_range
from src.model.enums import GeographicScaleClip, MeteoFranceDataType

# Générer des données agrégées pour l'année hydrologique 2025-2026
# (de septembre 2025 à août 2026)

export_all_format_geojson_range(
    geo_scale=GeographicScaleClip.NATIONAL,
    data_freq=MeteoFranceDataType.SIM2_MENS,
    start_date=datetime(2025, 9, 1),
    end_date=datetime(2026, 8, 31),
    is_data_aggregated=True,  # Agrégé sur toute la période
    has_index_update=True,
    is_data_update_allowed=True
)

print("✅ Données annuelles agrégées générées !")
```

### Exemple 4 : Création d'un graphique personnalisé

```python
import pandas as pd
from pathlib import Path
from src.plotting.plot_meteoFrance import plot_bar_dataframe

# Données pour le graphique
dates = pd.date_range('2026-01-01', '2026-01-31', freq='D')
sswi_values = [-0.5, -0.3, 0.1, 0.4, 0.2, -0.1, -0.3, 0.0, 0.5, 0.8,
               0.6, 0.4, 0.2, -0.1, -0.4, -0.6, -0.5, -0.3, 0.0, 0.2,
               0.4, 0.6, 0.8, 1.0, 0.8, 0.5, 0.3, 0.1, -0.1, -0.2, -0.3]

# Créer le graphique
plot_bar_dataframe(
    series_to_plot=pd.Series(sswi_values, name="SSWI_10J"),
    series_date=pd.Series(dates, name="Date"),
    normale_value=0,
    plot_title="SSWI 10 jours - Janvier 2026 - Bassin Rhône-Méditerranée",
    reference_lines={
        "Extrêmement humide": (1.75, 2.0, "midnightblue"),
        "Très humide": (1.28, 1.75, "royalblue"),
        "Modérément humide": (0.84, 1.28, "turquoise"),
        "Autour de la Normale": (-0.84, 0.84, "lime"),
        "Modérément sec": (-1.28, -0.84, "yellow"),
        "Très sec": (-1.75, -1.28, "darkorange"),
        "Extrêmement sec": (-2.0, -1.75, "darkred"),
    },
    output_path=Path("output/plots/sswi_janvier_2026_bassin_06.png")
)

print("✅ Graphique SSWI généré !")
```

---

## 📚 Voir aussi

- [Module plotting](index.md) - Aperçu du module
- [plot_grandeur](plot_grandeur.md) - Données hydrologiques
- [plot_onde](plot_onde.md) - Données ONDE
- [rasterize](rasterize.md) - Rasterisation
- [Concepts : SPI et SSWI](../../../concepts/spi-sswi.md)
- [Utilisation CLI](../../../usage/cli.md)

---

## 🎯 Résumé des Fonctions

| Fonction | Description | Sortie |
|----------|-------------|--------|
| `to_lambert2_geodataframe` | Convertit DataFrame en GeoDataFrame Lambert 2 | `GeoDataFrame` |
| `clip_with_distance` | Découpe un GeoDataFrame avec un masque | `GeoDataFrame` |
| `plot_geojson_from_lambert2` | Exporte GeoDataFrame en GeoJSON + CSV | `.geojson`, `.csv` |
| `get_chemin_sauvegarde` | Génère le chemin de sauvegarde | `Path` |
| `get_chemin_sauvegarde_geographie` | Génère le chemin avec suffixe géographique | `Path` |
| `export_to_every_geographic_element` | Exporte pour toutes les zones d'une échelle | `.geojson` (+ `.png`) |
| `create_all_plot_for_unique_scale` | Crée tous les graphiques pour une zone | `.png` × N |
| `df_range_processed` | Récupère les données pour une période | `DataFrame` |
| `export_all_format_geojson_range` | **Fonction principale** - Exporte pour toutes les échelles | `.geojson` (+ `.png`) |
| `export_geojson_month` | Exporte un mois complet | `.geojson` (+ `.png`) |
| `export_geojson_day` | Exporte un jour spécifique | `.geojson` (+ `.png`) |
| `get_all_geographic_geodf` | Récupère toutes les zones géographiques | `GeoDataFrame` |
| `get_geographic_element` | Récupère une zone spécifique | `GeoDataFrame` |
| `get_bassin_versant` | Récupère un bassin versant | `GeoDataFrame` |
| `plot_bar_dataframe` | Génère un graphique en barres | `.png` |

---

*Documentation générée automatiquement à partir du code source | Dernière mise à jour : {{ "now" | date: "%d %B %Y" }}*
