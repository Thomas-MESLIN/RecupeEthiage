---
layout: default
title: Module Plotting
description: "Documentation complète du module de visualisation et cartographie"
nav_order: 1
parent: Modules
has_children: true
---

# 📊 Module Plotting

**Documentation API complète du module de visualisation**

Ce module est le cœur de la génération de cartes et graphiques de l'application. Il permet de visualiser les données hydrologiques, météorologiques et ONDE sous différentes formes.

---

## 🗂️ Structure du Module

```
src/plotting/
├── __init__.py
├── plot_grandeur.py          # ⭐ Grandeurs hydrologiques (hydraulicité, VCN3)
├── plot_meteoFrance.py       # ⭐ Données MétéoFrance (SPI, SSWI, précipitations)
├── plot_onde.py              # ⭐ Données ONDE (écoulements, assecs)
├── rasterize.py              # ⭐ Rasterisation des GeoDataFrames
└── plot_res_validation_clean.py # Validation des données
```

---

## 🎯 Aperçu des Fonctionnalités

| Fichier | Domaine | Types de Sortie | Utilisation Principale |
|--------|---------|----------------|----------------------|
| [plot_grandeur](plot_grandeur.md) | Hydrologie | GeoJSON, PNG | Cartes d'hydraulicité, VCN3, périodes de retour |
| [plot_meteoFrance](plot_meteoFrance.md) | Météorologie | GeoJSON, PNG | Cartes SPI, SSWI, précipitations par zone |
| [plot_onde](plot_onde.md) | ONDE | PNG | Graphiques d'évolution des écoulements et assecs |
| [rasterize](rasterize.md) | Cartographie | PNG | Cartes de chaleur rasterisées |
| [plot_res_validation_clean](plot_res_validation_clean.md) | Validation | PNG | Comparaison de sources de données |

---

## 📋 Fonctionnalités par Type de Données

### 💧 Hydrologie (plot_grandeur)

- **Création de GeoJSON** à partir de données de stations
- **Calcul et visualisation** de l'hydraulicité
- **Analyse fréquentielle** du VCN3
- **Graphiques de périodes de retour** par station
- **Génération de cartes** compatibles QGIS

### 🌦️ Météorologie (plot_meteoFrance)

- **Export multi-échelles** (bassin, région, département)
- **Graphiques temporels** (SPI, SSWI, précipitations, ETP)
- **Agrégation de données** sur des périodes
- **Découpage géographique** automatique
- **Création de barres chronologiques** avec seuils de référence

### 🌊 ONDE (plot_onde)

- **Suivi des assecs** par mois et par année
- **Répartition des écoulements** (visible, faible, non-visible, assec)
- **Comparaison inter-annuelle**
- **Moyennes mobiles** et tendances

### 🗺️ Rasterisation (rasterize)

- **Interpolation spatiale** de points en raster
- **Masquage géographique** par zone
- **Palettes de couleurs** personnalisables
- **Export en PNG haute résolution**

---

## 🔧 Prérequis et Dépendances

### Dépendances Python

```python
# Dépendances directes du module plotting
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from pathlib import Path
from scipy.interpolate import griddata
from rasterio.transform import from_bounds
from rasterio.mask import mask
from rasterio.plot import plotting_extent
from rasterio.io import MemoryFile
```

### Modules Internes Utilisés

```python
from src.config.paths import OUTPUT_DIR
from src.config.logging_config import setup_logger
from src.config.styles import COULEUR_MOYENNE, ANNEE_COULEURS
from src.model.enums import GeographicScaleClip, OndeCampagneType, MeteoFranceDataType
from src.processing.station import get_stations
from src.processing.calcul_frequence_periode_de_retour import ensure_frequence_non_depassement_periode_retour_calcule
from src.processing.calcul_hydraulicite import calcul_hydraulicite_mensuel
from src.io.download_Hubeau import ensure_sites_downloaded
from src.io.download_meteoFrance import get_data_in_range, get_geographic_list, download_and_extract
from src.io.pynsee_departement import get_departements_from_regions
```

---

## 📁 Structure des Fichiers de Sortie

### Arbre des Dossiers de Sortie

```
output/
├── QGIS/                                    # Cartes GeoJSON
│   ├── hydraulicite/                        # Cartes d'hydraulicité
│   │   └── hydraulicite-{code_sandre}-{annee_mois}.geojson
│   ├── vcn3/                                # Cartes de VCN3
│   │   └── frequence_periode_de_retour/    # Périodes de retour
│   │       └── periode-de-retour-{code_sandre}-{annee_mois}.geojson
│   ├── meteo/                               # Cartes météo
│   │   └── meteoFrance/                    # Données MétéoFrance
│   │       ├── {type}-{dates}/             # Par type et période
│   │       │   ├── {type}-{dates}.geojson   # Données GeoJSON
│   │       │   └── plots/                  # Graphiques
│   │       │       └── {echelle}/{code}/   # Par zone géographique
│   │       │           └── {indicateur}.png # Graphiques par indicateur
│   └── onde/                               # Cartes ONDE
│       └── BSH_{annee_mois}/              # Par mois
│           └── {echelle}{code}/            # Par zone
│               ├── onde_evolution-assec_{annee}_{type}.png
│               └── onde_evolution-ecoulement_{annee_mois}_{type}.png
├── VCN3/                                    # Graphiques VCN3
│   ├── plot_stations/                       # Graphiques par station
│   │   ├── analyse-frequentielle-{station}-{mois}.png
│   │   └── periode-de-retour-{station}-{mois}.png
│   └── analyse_frequence_periode/          # Données d'analyse
│       └── periode-de-retour-{code_sandre}-{annee_mois}.csv
└── test/                                    # Tests et exemples
    └── output_rasterise_test.png            # Exemples de rasterisation
```

---

## 🎓 Tutorial : Créer une Visualisation Complète

### Étape 1 : Préparer les données

```python
from src.plotting.plot_grandeur import create_geojson_from_hydraulicite

# Générer une carte d'hydraulicité
create_geojson_from_hydraulicite(
    annee_mois="2026-01",
    code_sandre="BSH001"
)
```

### Étape 2 : Générer des graphiques VCN3

```python
from src.plotting.plot_grandeur import create_geojson_from_periode_de_retour

# Avec graphiques individuels par station
create_geojson_from_periode_de_retour(
    annee_mois="2026-01",
    code_sandre="BSH001",
    is_result_plotted=True
)
```

### Étape 3 : Créer des visualisations météo

```python
from src.plotting.plot_meteoFrance import export_all_format_geojson_range
from src.model.enums import GeographicScaleClip, MeteoFranceDataType
from datetime import datetime

export_all_format_geojson_range(
    geo_scale=GeographicScaleClip.BASSIN,
    data_freq=MeteoFranceDataType.SIM2_MENS,
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31),
    is_data_aggregated=False
)
```

### Étape 4 : Visualiser les données ONDE

```python
from src.plotting.plot_onde import plot_everything
from src.model.enums import OndeCampagneType, GeographicScaleClip
from datetime import datetime

plot_everything(
    campagne_type=OndeCampagneType.ALL_CAMPAGNE,
    annee_mois=datetime(2026, 6, 1),
    geographic_scale=GeographicScaleClip.REGION_ADMINISTRATIVE,
    zone_code="84"
)
```

### Étape 5 : Rasteriser une carte

```python
from src.plotting.rasterize import rasterize_geodataframe_geographiv_zone
from src.model.enums import GeographicScaleClip
import geopandas as gpd

# Charger vos données
gdf = gpd.read_file("output/QGIS/meteoFrance/MENS-SIM2-202606/bassin/MENS-SIM2-202606-B06.geojson")

# Rasteriser
rasterize_geodataframe_geographiv_zone(
    geodataframe=gdf,
    unit_to_rasterize="SSWI1",
    geographic_zone=GeographicScaleClip.BASSIN,
    code_zone="06",
    output_path="output/test/raster_test.png",
    titre_graphique="SSWI1 - Juin 2026 - Bassin 06"
)
```

---

## 📚 Documentation par Fichier

| Fichier | Description | [Lien](link) |
|--------|-------------|------|
| **plot_grandeur.py** | Visualisation des grandeurs hydrologiques (hydraulicité, VCN3, périodes de retour) | [Voir →](plot_grandeur.md) |
| **plot_meteoFrance.py** | Visualisation des données météorologiques (SPI, SSWI, précipitations) | [Voir →](plot_meteoFrance.md) |
| **plot_onde.py** | Visualisation des données ONDE (écoulements, assecs) | [Voir →](plot_onde.md) |
| **rasterize.py** | Rasterisation des GeoDataFrames pour créer des cartes de chaleur | [Voir →](rasterize.md) |
| **plot_res_validation_clean.py** | Validation et comparaison des sources de données | [Voir →](plot_res_validation_clean.md) |

---

## 🎯 Bonnes Pratiques

### 1. Gestion des Chemins

Toujours utiliser les fonctions de `src/config/paths.py` :

```python
from src.config.paths import OUTPUT_DIR

# ✅ Bon
output_path = OUTPUT_DIR / "QGIS" / "hydraulicite" / "ma_carte.geojson"

# ❌ À éviter
output_path = Path("output/QGIS/hydraulicite/ma_carte.geojson")
```

### 2. Journalisation

Utiliser le logger configuré pour chaque module :

```python
from src.config.logging_config import setup_logger

logger = setup_logger(name="mon_module")
logger.info("Début du traitement...")
```

### 3. Gestion des Erreurs

Vérifier l'existence des colonnes avant de les utiliser :

```python
if "colonne" in df.columns:
    df["colonne"].mean()
```

### 4. Création des Dossiers

Toujours créer les dossiers parents avant d'écrire :

```python
output_path = OUTPUT_DIR / "nouveau" / "dossier" / "fichier.geojson"
output_path.parent.mkdir(parents=True, exist_ok=True)
```

---

## 🔗 Liens Utiles

- [Documentation plot_grandeur](plot_grandeur.md)
- [Documentation plot_meteoFrance](plot_meteoFrance.md)
- [Documentation plot_onde](plot_onde.md)
- [Documentation rasterize](rasterize.md)
- [Concepts Clés](../../concepts/index.md)
- [Utilisation CLI](../../usage/cli.md)

---

*Dernière mise à jour : {{ "now" | date: "%d %B %Y" }}*



