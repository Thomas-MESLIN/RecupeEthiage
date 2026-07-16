---
layout: default
title: Référence API
description: "Référence complète des fonctions par module"
nav_order: 6
parent: ""
---

# 📚 Référence API

**Liste complète des fonctions disponibles par module**

---

## 📦 Modules et Fonctions

### 📊 Module Plotting

| Fichier | Fonction | Description |
|---------|----------|-------------|
| plot_grandeur.py | `create_geojson_from_hydraulicite` | Crée carte GeoJSON d'hydraulicité |
| plot_grandeur.py | `create_geojson_from_periode_de_retour` | Crée carte GeoJSON de périodes de retour |
| plot_meteoFrance.py | `export_all_format_geojson_range` | Exporte données météo en GeoJSON |
| plot_meteoFrance.py | `plot_timeline` | Graphique temporel des indicateurs |
| plot_onde.py | `plot_everything` | Visualise données ONDE |
| rasterize.py | `rasterize_geodataframe_geographiv_zone` | Rasterise GeoDataFrame |

### 🔄 Module Processing

| Fichier | Fonction | Description |
|---------|----------|-------------|
| clean.py | `ensure_historic_cleaned` | Nettoie données historiques |
| clean.py | `ensure_single_month_cleaned` | Nettoie données mensuelles |
| calcul_hydraulicite.py | `calcul_hydraulicite_mensuel` | Calcule hydraulicité mensuelle |
| calcul_vcn3.py | `ensure_calcul_vcn3_calcule` | Calcule VCN3 |
| calcul_frequence_periode_de_retour.py | `vcn3_frequence_retour` | Analyse fréquentielle VCN3 |
| calcul_frequence_periode_de_retour.py | `get_period_from_flow` | Période de retour d'un débit |

### 📥 Module IO

| Fichier | Fonction | Description |
|---------|----------|-------------|
| download_Hubeau.py | `ensure_grandeur_mensuel_downloaded` | Télécharge données mensuelles |
| download_Hubeau.py | `ensure_grandeur_historique_downloaded` | Télécharge données historiques |
| download_meteoFrance.py | `download_and_extract` | Télécharge données MétéoFrance |
| pynsee_departement.py | `get_departements_from_regions` | Convertit régions en départements |

### 🛠️ Module Utils

| Fichier | Fonction | Description |
|---------|----------|-------------|
| utils.py | `get_path_*` | Chemins vers les fichiers |
| utils_file.py | `is_res_updated_with_source` | Vérifie fraîcheur des données |
| utils_proxy.py | `set_up_working_proxy` | Configure proxy réseau |

---

## 🔍 Index par Type de Donnée

### Hydrologie
- **Récupération** : `ensure_grandeur_mensuel_downloaded`, `ensure_grandeur_historique_downloaded`
- **Nettoyage** : `ensure_historic_cleaned`, `ensure_single_month_cleaned`
- **Calcul** : `calcul_hydraulicite_mensuel`, `ensure_calcul_vcn3_calcule`
- **Visualisation** : `create_geojson_from_hydraulicite`

### Météorologie
- **Récupération** : `download_and_extract`
- **Calcul** : `vcn3_frequence_retour`
- **Visualisation** : `export_all_format_geojson_range`, `plot_timeline`

### ONDE
- **Récupération** : Via download_Hubeau.py
- **Visualisation** : `plot_everything`

---

## 🎯 Fonctions par Cas d'Usage

### ⚡ Analyse Complète Hydrologique
```python
# 1. Télécharger
from src.io.download_Hubeau import ensure_grandeur_mensuel_downloaded
ensure_grandeur_mensuel_downloaded("2026-06", "QmM")

# 2. Nettoyer
from src.processing.clean import ensure_single_month_cleaned
ensure_single_month_cleaned("2026-06", "BSH001", "QmM")

# 3. Calculer
from src.processing.calcul_hydraulicite import calcul_hydraulicite_mensuel
calcul_hydraulicite_mensuel("2026-06", "BSH001")

# 4. Visualiser
from src.plotting.plot_grandeur import create_geojson_from_hydraulicite
create_geojson_from_hydraulicite("2026-06", "BSH001")
```

### ⚡ Analyse VCN3 et Périodes de Retour
```python
# 1-2. Télécharger et nettoyer QmnJ (similaire à QmM)

# 3. Calculer VCN3
from src.processing.calcul_vcn3 import ensure_calcul_vcn3_calcule
ensure_calcul_vcn3_calcule("2026-06", "BSH001")

# 4. Calculer périodes de retour
from src.processing.calcul_frequence_periode_de_retour import ensure_frequence_non_depassement_periode_retour_calcule
ensure_frequence_non_depassement_periode_retour_calcule("2026-06", "BSH001")

# 5. Visualiser
from src.plotting.plot_grandeur import create_geojson_from_periode_de_retour
create_geojson_from_periode_de_retour("2026-06", "BSH001")
```

---

## 📖 Voir aussi

- [Module Plotting](../modules/plotting/index.md)
- [Module Processing](../modules/processing/index.md)
- [Module IO](../modules/io/index.md)
- [Module Utils](../modules/utils/index.md)