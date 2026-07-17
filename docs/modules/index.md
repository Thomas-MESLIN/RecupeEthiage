---
layout: default
title: Modules
description: "Documentation des modules de l'application"
nav_order: 4
has_children: true
---

# 🔧 Modules

L'application est organisée en plusieurs modules fonctionnels, chacun ayant un rôle spécifique dans le processus de récupération, traitement et visualisation des données.

---

## 🗂️ Arborescence des Modules

```
src/
├── cli/              # Interface en ligne de commande
│   ├── main_cli.py         # Gestion du mode CLI
│   ├── main_interactive.py # Gestion du mode interactif
│   └── utils.py            # Fonctions utilitaires pour le CLI
│
├── config/           # Configuration de l'application
│   ├── paths.py            # Chemins des fichiers
│   ├── styles.py           # Styles et couleurs
│   ├── logging_config.py   # Configuration du logging
│   └── init_project.py     # Initialisation des dossiers
│
├── io/               # Entrées/Sorties - Récupération des données
│   ├── download_Hubeau.py     # Téléchargement depuis Hub'Eau
│   ├── download_meteoFrance.py # Téléchargement depuis MétéoFrance
│   └── pynsee_departement.py    # Correspondance régions-départements
│
├── model/            # Modèles de données
│   └── enums.py            # Énumérations (OndeCampagneType, MeteoFranceDataType, etc.)
│
├── plotting/         # Visualisation
│   ├── plot_grandeur.py         # Visualisation des grandeurs hydrologiques
│   ├── plot_meteoFrance.py     # Visualisation des données MétéoFrance
│   ├── plot_onde.py            # Visualisation des données ONDE
│   ├── rasterize.py            # Rasterisation des GeoDataFrames
│   └── plot_res_validation_clean.py # Validation des données
│
├── processing/        # Traitement des données
│   ├── calcul_frequence_periode_de_retour.py # Calcul des périodes de retour
│   ├── calcul_hydraulicite.py             # Calcul de l'hydraulicité
│   ├── calcul_vcn3.py                     # Calcul du VCN3
│   ├── meteoFrance_aggregation_donnee.py  # Agrégation des données météo
│   ├── process_onde.py                    # Traitement des données ONDE
│   ├── station.py                         # Gestion des stations
│   └── clean.py                           # Nettoyage des données
│
└── utils/             # Fonctions utilitaires
    ├── utils.py            # Fonctions utilitaires générales
    ├── utils_file.py       # Gestion des fichiers
    └── utils_proxy.py      # Gestion du proxy
```

---

## 🎯 Modules par Catégorie

### 📊 **[plotting](plotting/index.md)** - Visualisation et Cartographie

**Module principal documenté en détail** - Gère toute la génération de graphiques et de cartes GeoJSON.

| Fichier | Description | Fonctions Clés |
|--------|-------------|----------------|
| [plot_grandeur](plotting/plot_grandeur.md) | Grandeurs hydrologiques (hydraulicité, VCN3) | `create_geojson_from_hydraulicite`, `create_geojson_from_periode_de_retour`, `plot_results`, `plot_period_from_flow` |
| [plot_meteoFrance](plotting/plot_meteoFrance.md) | Données météorologiques | `export_all_format_geojson_range`, `plot_bar_dataframe`, `to_lambert2_geodataframe` |
| [plot_onde](plotting/plot_onde.md) | Données ONDE | `plot_evolution_assecs`, `plot_evolution_ecoulements`, `plot_everything` |
| [rasterize](plotting/rasterize.md) | Rasterisation | `rasterize_geojson`, `rasterize_geodataframe_geographiv_zone` |
| [styles](plotting/styles.md) | Styles et couleurs | `COULEUR_MOYENNE`, `ANNEE_COULEURS` |

### 📥 **[io](io/index.md)** - Entrées/Sorties

Gère la récupération des données depuis différentes sources.

### ⚙️ **[processing](processing/index.md)** - Traitement

Effectue les calculs et transformations sur les données brutes.

### ⚙️ **[config](config/index.md)** - Configuration

Centralise tous les paramètres de configuration de l'application.

### 🎮 **[cli](cli/index.md)** - Interface Utilisateur

Gère l'interaction avec l'utilisateur (mode CLI et interactif).

### 🧰 **[utils](utils/index.md)** - Utilitaires

Fonctions utilitaires utilisées par tous les autres modules.

### 📊 **[model](model/index.md)** - Modèles

Définitions des types de données et énumérations.

---

## Module de visualisation : plotting

Le module **`plotting`** est le cœur de la visualisation de votre application. Il permet de :

- **Générer des cartes GeoJSON** pour QGIS et autres logiciels SIG
- **Créer des graphiques statistiques** (histogrammes, courbes, diagrammes)
- **Visualiser des indicateurs** (hydraulicité, VCN3, SPI, SSWI)
- **Rasteriser des données** pour créer des cartes de chaleur
- **Exporter des données par zone géographique** (bassin, région, département)

**📖 [Documentation complète du module plotting →](plotting/index.md)**

---

## 📚 Navigation

- [plotting](plotting/index.md)
- [config](config/index.md)
- [io](io/index.md)
- [processing](processing/index.md)
- [cli](cli/index.md)
- [model](model/index.md)
- [utils](utils/index.md)



