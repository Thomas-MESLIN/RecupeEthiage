---
layout: default
title: Format de Sortie
description: "Description des formats de sortie générés par l'application"
nav_order: 2
parent: Données
grand_parent: ""
---

# 📤 Format de Sortie

**Formats et structure des fichiers générés**

---

## 🗂️ Arborescence de Sortie

```
output/
├── QGIS/                    # Cartes géographiques
│   ├── hydraulicite/        # Cartes d'hydraulicité (GeoJSON)
│   ├── vcn3/                # Cartes de VCN3 (GeoJSON)
│   ├── meteo/               # Cartes météo (GeoJSON)
│   └── onde/                # Cartes ONDE (GeoJSON)
│
├── hubeau/                  # Données hydrologiques
│   ├── downloaded_data/     # Données brutes téléchargées
│   │   ├── observations_elaboree/  # CSV : QmM, QmnJ
│   │   ├── stations/        # CSV : Métadonnées
│   │   └── sites/           # CSV : Sites
│   └── cleaned_data/        # CSV : Données nettoyées
│
├── meteoFrance/             # Données météorologiques
│   ├── downloaded_data/     # CSV : Données brutes
│   └── processed_data/      # CSV : Données traitées
│
├── VCN3/                    # Analyses VCN3
│   ├── analyse_frequentielle/  # Graphiques par station
│   └── plot_stations/       # Graphiques détaillés
│
├── ressource/               # Ressources
│   └── site_station_custom/  # Listes personnalisées
│
├── logs/                    # Journaux d'exécution
└── res-validation/          # Validation des données
    └── diff_hydro_hubeau_clean.csv
```

---

## 📄 Formats de Fichiers

### GeoJSON

**Format principal pour les cartes**

- **Extension** : `.geojson`
- **Utilisation** : QGIS, Google Earth, applications web
- **Structure** :
  - Propriétés : métadonnées et indicateurs
  - Géométrie : points, lignes ou polygones
- **Encodage** : UTF-8

### CSV

**Format pour les données tabulaires**

- **Extension** : `.csv`
- **Séparateur** : virgule (`,`) ou point-virgule (`;`) selon la source
- **Encodage** : UTF-8
- **Utilisation** : Analyse avec pandas, Excel, etc.

### PNG

**Format pour les graphiques**

- **Extension** : `.png`
- **Résolution** : Adaptée à la visualisation
- **Utilisation** : Rapports, présentations

---

## 🎯 Nomenclature des Fichiers

### Hydraulicité

- **Pattern** : `hydraulicite-{code_sandre}-{annee_mois}.geojson`
- **Exemple** : `hydraulicite-BSH001-2026-06.geojson`

### VCN3 / Période de Retour

- **Pattern** : `periode-de-retour-{code_sandre}-{annee_mois}.geojson`
- **Exemple** : `periode-de-retour-BSH001-2026-06.geojson`

### MétéoFrance

- **Pattern** : `meteo-{type}-{echelle}-{date}.geojson`
- **Exemple** : `meteo-SPI-BASSIN-2026-06.geojson`

### ONDE

- **Pattern** : `onde-{type}-{code}-{date}.geojson`
- **Exemple** : `onde-USUELLE-06-2026-06.geojson`

---

## 📊 Structure des GeoJSON

### Propriétés courantes

| Propriété | Type | Description |
|-----------|------|-------------|
| `code_sandre` | string | Code du réseau Sandre |
| `annee_mois` | string | Période au format AAAA-MM |
| `hydraulicite` | number | Valeur de l'hydraulicité |
| `percée_retour` | number | Période de retour en jours |
| `spi` | number | Indice SPI |
| `sswi` | number | Indice SSWI |

---

## 🔗 Liens

- [Module Plotting](../modules/plotting/index.md) - Génération des cartes
- [Module IO](../modules/io/index.md) - Récupération des données
- [Module Processing](../modules/processing/index.md) - Traitement des données
