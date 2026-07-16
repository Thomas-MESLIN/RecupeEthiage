---
layout: page
title: Module Config
description: "Documentation du module de configuration de l'application"
---

# ⚙️ Module Config

**Documentation des modules de configuration**

Le module `config` centralise toute la configuration de l'application, permettant une **gestion centralisée** des paramètres utilisés par les différents modules.

---

## 🗂️ Structure du Module

```
src/config/
├── __init__.py
├── paths.py            # Chemins des fichiers
├── styles.py           # Styles et couleurs (documenté séparément)
├── logging_config.py   # Configuration du logging
└── init_project.py     # Initialisation des dossiers
```

---

## 📋 Modules par Fichier

### 📁 [paths.py](paths.md)

**Gère tous les chemins de fichiers et dossiers de l'application.**

| Variable | Type | Description | Valeur |
|----------|------|-------------|--------|
| `ROOT_DIR` | `Path` | Racine du projet | `Path(__file__).resolve().parents[2]` |
| `OUTPUT_DIR` | `Path` | Dossier de sortie | `ROOT_DIR / "output"` |
| `DATA_DIR` | `Path` | Dossier des données | `ROOT_DIR / "data"` |
| `SRC_DIR` | `Path` | Dossier source | `ROOT_DIR / "src"` |

**Utilisation** :
```python
from src.config.paths import OUTPUT_DIR, DATA_DIR

# Accéder au dossier de sortie
output_path = OUTPUT_DIR / "QGIS" / "mon_fichier.geojson"

# Accéder au dossier des données
data_path = DATA_DIR / "mes_donnees.csv"
```

### 🎨 [styles.py](../plotting/styles.md)

**Centralise les styles et couleurs** (documentation détaillée disponible).

### 📝 [logging_config.py](logging_config.md)

**Configure la journalisation (logging) de l'application.**

Fournit la fonction `setup_logger()` pour créer des loggers avec :
- Handler console (niveau INFO)
- Handler fichier (niveau DEBUG)
- Handler erreurs (niveau ERROR)
- Rotation automatique des logs (10 Mo max, 5 backups)

**Utilisation** :
```python
from src.config.logging_config import setup_logger

logger = setup_logger(name="mon_module")
logger.info("Message d'information")
logger.error("Message d'erreur")
```

### 🚀 [init_project.py](init_project.md)

**Initialise l'arborescence complète des dossiers** nécessaire au fonctionnement de l'application.

Crée les dossiers :
- `output/` - Dossier principal de sortie
- `output/hubeau/` et `output/hydroportail/` - Données brutes
- `output/QGIS/` - Cartes générées
- `output/meteoFrance/` - Données météorologiques
- `output/onde/` - Données ONDE
- `output/VCN3/` - Analyses VCN3
- `output/site_station_custom/` - Listes personnalisées
- `output/logs/` - Journaux d'exécution

**Utilisation** :
```python
# Initialiser tous les dossiers avant la première utilisation
from src.config.init_project import *
```

---

## 🎯 Bonnes Pratiques

### 1. Toujours utiliser les chemins centralisés

```python
# ✅ Bon
from src.config.paths import OUTPUT_DIR
output_path = OUTPUT_DIR / "QGIS" / "ma_carte.geojson"

# ❌ À éviter
output_path = Path("output/QGIS/ma_carte.geojson")
```

### 2. Configurer le logger pour chaque module

```python
# ✅ Bon - Un logger par module
logger = setup_logger(name="plot_grandeur")
logger.info("Début du traitement...")

# ❌ À éviter - Utiliser print()
print("Début du traitement...")
```

### 3. Initialiser les dossiers au démarrage

```python
# Dans main.py ou au point d'entrée de l'application
from src.config.init_project import *
```

---

## 📊 Arbre des Dossiers Créés par init_project

```
output/
├── hubeau/
│   ├── cleaned_data/
│   ├── downloaded_data/
│   │   ├── observations_elaboree/
│   │   ├── sites/
│   │   ├── stations/
│   │   └── onde/
│   └── QmM_moyen/
├── hydroportail/
│   └── (même structure que hubeau)
├── QGIS/
│   ├── stations/
│   ├── sites/
│   ├── hydraulicite/
│   ├── vcn3/
│   │   ├── stations/
│   │   ├── plot_stations/
│   │   ├── analyse_frequence_periode/
│   │   └── mensuel/
│   ├── meteo/
│   │   └── meteoFrance/
│   └── onde/
│       └── HISTORIC_DATA/
├── meteoFrance/
│   ├── departement_id_datagouv/
│   └── downloaded_data/
│       ├── mens_historique/
│       ├── mens_historique_archive/
│       ├── mens_sim2/
│       ├── mens_sim2_archive/
│       ├── mens/
│       ├── mens_archive/
│       ├── quot/
│       ├── quot_archive/
│       ├── quot_sim2/
│       ├── quot_sim2_archive/
│       ├── delimitation_qgis/
│       └── delimitation_qgis_archive/
├── VCN3/
│   ├── stations/
│   ├── plot_stations/
│   └── analyse_frequence_periode/
├── site_station_custom/
├── onde/
│   └── HISTORIC_DATA/
└── logs/
```

---

## 🔗 Navigation

- [paths.py](paths.md) - Chemins des fichiers
- [logging_config.py](logging_config.md) - Configuration du logging
- [init_project.py](init_project.md) - Initialisation des dossiers
- [styles.py](../plotting/styles.md) - Styles et couleurs

---

[Retour aux modules](index.md)
