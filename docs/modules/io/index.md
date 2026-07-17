---
layout: default
title: Module IO
description: "Documentation du module d'entrée/sortie - Récupération des données"
nav_order: 1
parent: Modules
has_children: true
---

# 📥 Module IO

**Documentation du module de récupération des données**

Le module `io` gère **toute la récupération des données** depuis les différentes sources : Hub'Eau, MétéoFrance, et les correspondances géographiques.

---

## 🗂️ Structure du Module

```
src/io/
├── __init__.py
├── download_Hubeau.py     # Téléchargement depuis Hub'Eau
├── download_meteoFrance.py # Téléchargement depuis MétéoFrance
└── pynsee_departement.py    # Correspondance régions-départements
```

---

## 📋 Modules par Fichier

### 🌊 [download_Hubeau.py](download_Hubeau.md)

**Gère la récupération des données hydrologiques depuis l'API Hub'Eau.**

Fonctionnalités principales :
- Téléchargement des observations hydrologiques (QmM, QmnJ)
- Récupération de la liste des stations
- Récupération de la liste des sites
- Vérification et mise à jour des données
- Cache local des données téléchargées

**Sources de données** :
- API Hub'Eau (https://hubeau.eaufrance.fr/)
- Observations élaborees (débits moyens mensuels)
- Stations hydrométriques
- Sites hydrologiques

**Utilisation typique** :
```python
from src.io.download_Hubeau import ensure_station_downloaded, ensure_sites_downloaded
from src.model.enums import GeographicScaleClip

# S'assurer que les stations sont à jour
ensure_station_downloaded()
ensure_sites_downloaded()

# Télécharger les données Onde.
download_hubeau_onde_stations_geographic_zone(GeographicScaleClip.REGION_ADMINISTRATIVE,"84")
```

### 🌦️ [download_meteoFrance.py](download_meteoFrance.md)

**Gère la récupération des données météorologiques depuis les API MétéoFrance.**

Fonctionnalités principales :
- Téléchargement des données SIM2 (grille 8x8km)
- Téléchargement des données brutes (stations)
- Téléchargement des données historiques
- Téléchargement des limites géographiques (bassins, régions, départements)
- Mise à jour des index de correspondance
- Cache local avec gestion des archives

**Types de données** :
- **SIM2_QUOT** : Données quotidiennes interpolées
- **SIM2_MENS** : Données mensuelles interpolées
- **QUOT** : Données quotidiennes brutes
- **MENS** : Données mensuelles brutes

**Utilisation typique** :
```python
from src.io.download_meteoFrance import get_data_in_range, get_geographic_list
from src.model.enums import MeteoFranceDataType, GeographicScaleClip
from datetime import datetime

# Récupérer des données pour une période
df = get_data_in_range(
    MeteoFranceDataType.SIM2_MENS,
    datetime(2026, 1, 1),
    datetime(2026, 1, 31),
    has_index_update=True,
    is_data_update_allowed=True
)

# Récupérer la liste des bassins
bassins = get_geographic_list(GeographicScaleClip.BASSIN)
```

### 🗺️ [pynsee_departement.py](pynsee_departement.md)

**Gère la correspondance entre régions et départements** en utilisant l'API Pynsee (INSEE).

Fonctionnalités principales :
- Récupération des départements d'une région
- Correspondance entre codes région et codes département
- Utilisation du cache pour éviter les appels répétés

**Utilisation typique** :
```python
from src.io.pynsee_departement import get_departements_from_regions

# Récupérer les départements de la région 84 (Auvergne-Rhône-Alpes)
departements = get_departements_from_regions("84")
print(departements)  # ['01', '03', '07', '15', '26', '38', '42', '43', '63', '69', '73', '74']
```

---

## 🎯 Diagramme des Flux de Données

![Diagramme de flux de données io, on voit les différentes API allant chacune vers sont module puis vers output.](img\flux_de_donnee_io.png)

---

## 📊 Exemple d'Utilisation Complète

```python
from src.io.download_Hubeau import ensure_station_downloaded
from src.io.download_meteoFrance import get_data_in_range, download_and_extract
from src.io.pynsee_departement import get_departements_from_regions
from src.model.enums import MeteoFranceDataType, GeographicScaleClip
from datetime import datetime

# 1. Télécharger les stations Hub'Eau
print("Téléchargement des stations...")
ensure_station_downloaded()

# 2. Télécharger les données météo pour un mois
print("Téléchargement des données météo...")
df_meteo = get_data_in_range(
    MeteoFranceDataType.SIM2_MENS,
    datetime(2026, 1, 1),
    datetime(2026, 1, 31)
)

# 3. Télécharger un fichier géographique
print("Téléchargement des limites géographiques...")
download_and_extract(
    id_data_gouv="b0761a88-b59f-466f-a3cc-b97f237fd732",
    chemin_archive="output/meteoFrance/downloaded_data/delimitation_qgis_archive/bassin-hydrographique.geojson.zip",
    chemin_final="output/meteoFrance/downloaded_data/delimitation_qgis/BassinHydrographique_FXX.geojson"
)

# 4. Récupérer les départements d'une région
departements_84 = get_departements_from_regions("84")
print(f"Départements de la région 84 : {departements_84}")

print("✅ Toutes les données téléchargées !")
```

---

## 🔗 Les modules plus en détails

- [download_Hubeau.py](download_Hubeau.md)
- [download_meteoFrance.py](download_meteoFrance.md)
- [pynsee_departement.py](pynsee_departement.md)

---

[Retour au départ](index.md)



