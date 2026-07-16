---
layout: default
title: Module Processing
description: "Documentation complète du module de traitement des données"
nav_order: 4
parent: Modules
has_children: true
---

# 🔄 Module Processing

**Documentation API complète du module de traitement des données hydrologiques et météorologiques**

Ce module est le cœur du traitement et de l'analyse des données. Il permet de nettoyer, transformer et calculer les indicateurs hydrologiques et météorologiques à partir des données brutes.

---

## 🗂️ Structure du Module

```
src/processing/
├── __init__.py
├── bricolage_normale.py          # Calcul des normales climatiques
├── calcul_frequence_periode_de_retour.py  # Calcul des périodes de retour (VCN3)
├── calcul_hydraulicite.py        # Calcul de l'hydraulicité
├── calcul_vcn3.py               # Calcul du Volume Current Non-dépassé sur 3 mois
├── clean.py                      # Nettoyage et préparation des données
├── meteoFrance_aggregation_donnee.py  # Agrégation des données MétéoFrance
├── process_onde.py               # Traitement des données ONDE
└── station.py                    # Gestion des stations de mesure
```

---

## 🎯 Aperçu des Fonctionnalités

| Fichier | Domaine | Fonctionnalités Principales | Types de Données |
|--------|---------|----------------------------|------------------|
| [clean](clean.md) | Nettoyage | Filtrage, déduplication, extraction par station | QmM, QmnJ |
| [calcul_hydraulicite](calcul_hydraulicite.md) | Hydraulicité | Calcul des rapports à la normale | QmM |
| [calcul_vcn3](calcul_vcn3.md) | VCN3 | Calcul des volumes minimum sur 3 mois | QmnJ |
| [calcul_frequence_periode_de_retour](calcul_frequence_periode_de_retour.md) | Statistiques | Analyse fréquentielle, périodes de retour | VCN3 |
| [bricolage_normale](bricolage_normale.md) | Climatologie | Calcul des normales climatiques | MétéoFrance |
| [meteoFrance_aggregation_donnee](meteoFrance_aggregation_donnee.md) | Météorologie | Agrégation spatiale et temporelle | MétéoFrance |
| [process_onde](process_onde.md) | ONDE | Traitement des campagnes d'observation | ONDE |
| [station](station.md) | Stations | Gestion des métadonnées des stations | Toutes |

---

## 📋 Fonctionnalités par Type de Données

### 💧 Nettoyage des Données (clean.py)

Ce module gère le nettoyage et la préparation des données brutes provenant de différentes sources.

- **Nettoyage des données Hub'Eau** : Extraction par date, code Sandre, suppression des doublons
- **Gestion historique** : Traitement des séries temporelles de 1991 à 2020
- **Validation** : Vérification de l'intégrité et de la fraîcheur des données
- **Cache** : Optimisation des performances avec mise en cache

### 📊 Calcul de l'Hydraulicité (calcul_hydraulicite.py)

L'hydraulicité mesure le rapport entre le débit observé et le débit moyen historique pour la même période.

- **Calcul mensuel** : Rapport des débits moyens mensuels
- **Calcul historique** : Moyennes sur la période 1991-2020
- **Visualisation** : Export en GeoJSON pour cartographie
- **Agrégation** : Par station, par mois, par année

### 🔬 Analyse VCN3 (calcul_vcn3.py)

Le VCN3 (Volume Current Non-dépassé sur 3 mois) est un indicateur clé de la sécheresse hydrologique.

- **Calcul des moyennes mobiles** sur 3 mois
- **Détection des minimums** : Identification des VCN3 les plus bas
- **Analyse historique** : Comparaison avec les séries historiques
- **Statistiques** : Fréquence, période de retour

### 📈 Analyse Fréquentielle (calcul_frequence_periode_de_retour.py)

Calcul des périodes de retour pour les événements hydrologiques extrêmes.

- **Ajustement statistique** : Loi Log-Normale avec estimation par L-moments
- **Bootstrap paramétrique** : Estimation des intervalles de confiance
- **Périodes de retour** : Calcul des T ans (2, 5, 10, 20, 50, 100 ans)
- **Visualisation** : Courbes de fréquence de non-dépassement

### 🌦️ Traitement MétéoFrance (bricolage_normale.py, meteoFrance_aggregation_donnee.py)

Traitement et agrégation des données météorologiques.

- **Calcul des normales** : Moyennes climatiques sur périodes de référence
- **Agrégation spatiale** : Par bassin, région, département
- **Agrégation temporelle** : Par jour, mois, saison
- **Comparaison** : Rapports aux normales

### 🌊 Traitement ONDE (process_onde.py)

Traitement des données de l'Observatoire National des Établissements.

- **Analyse des campagnes** : Suivi des écoulements et assecs
- **Agrégation** : Par zone géographique et période
- **Calcul d'indicateurs** : Pourcentage d'écoulement visible, faible, non-visible, assec
- **Tendances** : Évolution temporelle et spatiale

### 📍 Gestion des Stations (station.py)

Gestion des métadonnées des stations de mesure.

- **Récupération** : depuis Hub'Eau et fichiers locaux
- **Filtrage** : Par code Sandre, date, type
- **Validation** : Vérification de la cohérence des données
- **Export** : Formats CSV, GeoJSON

---

## 🔧 Prérequis et Dépendances

### Dépendances Python

```python
# Dépendances directes du module processing
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from functools import cache
from pathlib import Path
from tqdm import tqdm
import scipy.stats as stats
from lmoments3 import distr as lm_distr
```

### Modules Internes Utilisés

```python
from src.config.paths import OUTPUT_DIR
from src.config.logging_config import setup_logger
from src.model.enums import GeographicScaleClip, MeteoFranceDataType
from src.io.download_Hubeau import ensure_grandeur_mensuel_downloaded
from src.io.download_meteoFrance import get_data_in_range, get_geographic_list
import src.utils.utils as utils
import src.utils.utils_file as utils_file
import src.plotting.plot_grandeur as plot_grandeur
```

---

## 📁 Structure des Fichiers de Sortie

### Arbre des Dossiers de Sortie

```
output/
├── hubeau/
│   ├── downloaded_data/
│   │   ├── observations_elaboree/          # Données brutes Hub'Eau
│   │   │   ├── observations-QmM-AURA-1991-2020.csv
│   │   │   └── observations-QmnJ-AURA-AAAA-MM.csv
│   │   ├── sites/                          # Métadonnées des sites
│   │   │   └── sites.csv
│   │   └── stations/                       # Métadonnées des stations
│   │       └── stations.csv
│   └── cleaned_data/                       # Données nettoyées
│       └── clean-{grandeur}-{code_sandre}-{annee_mois}.csv
├── QmM_moyen/                             # Moyennes historiques
│   └── QmM_moyennes_{code_sandre}_1991_2020.csv
├── hydraulicite/                          # Résultats d'hydraulicité
│   └── hydraulicite-{code_sandre}-{annee_mois}.csv
└── VCN3/
    ├── moyenne_historique/                # VCN3 historiques
    │   └── VCN3-moyenne-{code_sandre}-1991-2020.csv
    ├── mensuel/                            # VCN3 mensuels
    │   └── VCN3-{code_sandre}-{annee_mois}.csv
    ├── stations/                           # VCN3 par station
    │   └── VCN3-station-{code_station}.csv
    └── analyse_frequence_periode/          # Périodes de retour
        └── periode-de-retour-{code_sandre}-{annee_mois}.csv
```

---

## 🎓 Tutorial : Effectuer une Analyse Complète

### Étape 1 : Nettoyer les données brutes

```python
from src.processing.clean import ensure_single_month_cleaned

# Nettoyer les données d'un mois spécifique
ensure_single_month_cleaned(
    annee_mois="2026-06",
    code_reseau_sandre="BSH001", 
    grandeur="QmM"
)
```

### Étape 2 : Calculer l'hydraulicité

```python
from src.processing.calcul_hydraulicite import calcul_hydraulicite_mensuel

# Calculer l'hydraulicité pour un mois donné
calcul_hydraulicite_mensuel(
    annee_mois="2026-06",
    code_sandre="BSH001"
)
```

### Étape 3 : Calculer les VCN3

```python
from src.processing.calcul_vcn3 import ensure_calcul_vcn3_calcule

# S'assurer que les VCN3 sont calculés
ensure_calcul_vcn3_calcule(
    annee_mois="2026-06", 
    code_sandre="BSH001"
)
```

### Étape 4 : Analyser les périodes de retour

```python
from src.processing.calcul_frequence_periode_de_retour import ensure_frequence_non_depassement_periode_retour_calcule

# Calculer les périodes de retour pour un mois
ensure_frequence_non_depassement_periode_retour_calcule(
    annee_mois="2026-06",
    code_sandre="BSH001",
    is_result_plotted=True
)
```

### Étape 5 : Traiter les données MétéoFrance

```python
from src.processing.meteoFrance_aggregation_donnee import aggregate_range
from src.model.enums import GeographicScaleClip, MeteoFranceDataType
from datetime import datetime

# Agrégation des données météo
aggregate_range(
    geo_scale=GeographicScaleClip.BASSIN,
    data_freq=MeteoFranceDataType.SIM2_MENS,
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31),
    is_data_aggregated=False
)
```

---

## 📚 Documentation par Fichier

| Fichier | Description | [Lien](link) |
|--------|-------------|------|
| **clean.py** | Nettoyage et préparation des données Hub'Eau | [Voir →](clean.md) |
| **calcul_hydraulicite.py** | Calcul de l'hydraulicité | [Voir →](calcul_hydraulicite.md) |
| **calcul_vcn3.py** | Calcul du VCN3 | [Voir →](calcul_vcn3.md) |
| **calcul_frequence_periode_de_retour.py** | Analyse fréquentielle et périodes de retour | [Voir →](calcul_frequence_periode_de_retour.md) |
| **bricolage_normale.py** | Calcul des normales climatiques | [Voir →](bricolage_normale.md) |
| **meteoFrance_aggregation_donnee.py** | Agrégation des données MétéoFrance | [Voir →](meteoFrance_aggregation_donnee.md) |
| **process_onde.py** | Traitement des données ONDE | [Voir →](process_onde.md) |
| **station.py** | Gestion des stations de mesure | [Voir →](station.md) |

---

## 🎯 Bonnes Pratiques

### 1. Gestion des Chemins

Toujours utiliser les fonctions de `src/config/paths.py` et `src/utils/utils.py` :

```python
from src.utils.utils import get_path_clean_csv, get_path_qmm_moyen_historique

# ✅ Bon
output_path = get_path_clean_csv("BSH001", "2026-06", "QmM")

# ❌ À éviter
output_path = Path("output/hubeau/cleaned_data/clean-QmM-BSH001-2026-06.csv")
```

### 2. Journalisation

Utiliser le logger configuré pour chaque module :

```python
from src.config.logging_config import setup_logger

logger = setup_logger(name="mon_module")
logger.info("Début du traitement...")
logger.debug(f"Traitement de {len(df)} enregistrements")
```

### 3. Gestion des Erreurs

Vérifier l'existence des données avant de les utiliser :

```python
import src.utils.utils_file as utils_file

if not utils_file.is_res_updated_with_source(source_paths, result_path):
    # Recalculer les données
    calculate_data()
```

### 4. Cache

Utiliser le décorateur `@cache` pour les fonctions coûteuses :

```python
from functools import cache

@cache
def get_expensive_data():
    # Calcul coûteux
    return expensive_calculation()
```

### 5. Barres de Progression

Utiliser tqdm pour les traitements longs :

```python
from tqdm import tqdm

with tqdm(total=100, desc="Traitement en cours") as pbar:
    for item in items:
        process(item)
        pbar.update(1)
```

---

## 🔗 Liens Utiles

- [Documentation clean.py](clean.md)
- [Documentation calcul_hydraulicite.py](calcul_hydraulicite.md)
- [Documentation calcul_vcn3.py](calcul_vcn3.md)
- [Documentation calcul_frequence_periode_de_retour.py](calcul_frequence_periode_de_retour.md)
- [Concepts Clés](../../concepts/index.md)
- [Utilisation CLI](../../usage/cli.md)
- [Module IO](../io/index.md)
- [Module Plotting](../plotting/index.md)

---

*Dernière mise à jour : {{ "now" | date: "%d %B %Y" }}*


