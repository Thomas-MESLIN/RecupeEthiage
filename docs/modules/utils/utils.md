---
layout: default
title: utils.py
description: "Documentation API des fonctions utilitaires principales"
nav_order: 1
parent: Module Utils
grand_parent: Modules
---

# 🔧 utils.py

**Fonctions utilitaires principales pour la gestion des chemins et des données**

Ce module centralise toutes les fonctions utilitaires liées à la gestion des chemins de fichiers, des métadonnées et des constantes utilisées dans l'application. Il permet d'éviter la duplication de code et de garantir la cohérence des chemins dans tout le projet.

---

## 🎯 Fonctionnalités Principales

- **Gestion des chemins** : Centralisation de tous les chemins de fichiers utilisés dans l'application
- **Constantes globales** : Définition des constantes comme les grandeurs disponibles
- **Fonctions de paths** : Génération dynamique des chemins en fonction des paramètres
- **Gestion des métadonnées** : Récupération des chemins vers les fichiers de stations et sites

---

## 📋 Constantes Disponibles

### `GRANDEUR`

Dictionnaire des grandeurs hydrologiques disponibles.

```python
GRANDEUR = {
    "QmM",      # Débit Moyen Mensuel
    "QmnJ",     # Débit Moyen Journalier
}
```

**Exemple**
```python
from src.utils.utils import GRANDEUR

# Vérifier si une grandeur est disponible
if "QmM" in GRANDEUR:
    print("QmM est une grandeur valide")

# Parcourir toutes les grandeurs disponibles
for grandeur in GRANDEUR:
    print(f"Grandeur disponible : {grandeur}")
```

---

## 📁 Fonctions de Chemins

### Chemins Hub'Eau

#### `get_path_historique_raw_csv(grandeur: str) -> Path`

Retourne le chemin vers le fichier CSV brut contenant les données historiques pour une grandeur donnée.

**Paramètres**
- `grandeur` : La grandeur pour laquelle récupérer le chemin (ex: "QmM", "QmnJ")

**Retourne**
- `Path` : Chemin vers le fichier CSV historique

**Exemple**
```python
from src.utils.utils import get_path_historique_raw_csv

# Chemin vers les données historiques QmM
qmm_historique = get_path_historique_raw_csv("QmM")
print(qmm_historique)
# Output: output/hubeau/downloaded_data/observations_elaboree/observations-QmM-AURA-1991-2020.csv
```

#### `get_path_mensuel_raw_csv(annee_mois: str, grandeur: str) -> Path`

Retourne le chemin vers le fichier CSV brut contenant les données mensuelles pour une grandeur et une période données.

**Paramètres**
- `annee_mois` : Année et mois au format AAAA-MM (ex: "2026-06")
- `grandeur` : La grandeur pour laquelle récupérer le chemin

**Retourne**
- `Path` : Chemin vers le fichier CSV mensuel

**Exemple**
```python
from src.utils.utils import get_path_mensuel_raw_csv

# Chemin vers les données mensuelles QmM de juin 2026
qmm_mensuel = get_path_mensuel_raw_csv("2026-06", "QmM")
print(qmm_mensuel)
# Output: output/hubeau/downloaded_data/observations_elaboree/observations-QmM-AURA-2026-06.csv
```

#### `get_path_clean_csv(code_sandre: str, annee_mois: str, grandeur: str) -> Path`

Retourne le chemin vers le fichier CSV nettoyé.

**Paramètres**
- `code_sandre` : Code Sandre du réseau (ex: "BSH001", "custom")
- `annee_mois` : Année et mois au format AAAA-MM
- `grandeur` : La grandeur concernée

**Retourne**
- `Path` : Chemin vers le fichier CSV nettoyé

**Exemple**
```python
from src.utils.utils import get_path_clean_csv

# Chemin vers les données nettoyées QmM pour BSH001 en juin 2026
clean_path = get_path_clean_csv("BSH001", "2026-06", "QmM")
print(clean_path)
# Output: output/hubeau/cleaned_data/clean-QmM-BSH001-2026-06.csv
```

### Chemins QmM Moyen

#### `get_path_qmm_moyen_historique(code_sandre: str) -> Path`

Retourne le chemin vers le fichier CSV contenant les moyennes historiques QmM (1991-2020).

**Paramètres**
- `code_sandre` : Code Sandre du réseau

**Retourne**
- `Path` : Chemin vers le fichier des moyennes historiques

**Exemple**
```python
from src.utils.utils import get_path_qmm_moyen_historique

# Chemin vers les moyennes historiques QmM pour BSH001
moyennes_path = get_path_qmm_moyen_historique("BSH001")
print(moyennes_path)
# Output: output/QmM_moyen/QmM_moyennes_BSH001_1991_2020.csv
```

### Chemins Hydraulicité

#### `get_path_hydraulicite(code_sandre: str, annee_mois: str) -> Path`

Retourne le chemin vers le fichier CSV contenant les résultats d'hydraulicité.

**Paramètres**
- `code_sandre` : Code Sandre du réseau
- `annee_mois` : Année et mois au format AAAA-MM

**Retourne**
- `Path` : Chemin vers le fichier d'hydraulicité

**Exemple**
```python
from src.utils.utils import get_path_hydraulicite

# Chemin vers l'hydraulicité pour BSH001 en juin 2026
hydraulicite_path = get_path_hydraulicite("BSH001", "2026-06")
print(hydraulicite_path)
# Output: output/hydraulicite/hydraulicite-BSH001-2026-06.csv
```

### Chemins VCN3

#### `get_path_vcn3_moyenne_historique(code_sandre: str) -> Path`

Retourne le chemin vers le fichier CSV contenant les moyennes historiques VCN3.

**Paramètres**
- `code_sandre` : Code Sandre du réseau

**Retourne**
- `Path` : Chemin vers les moyennes VCN3 historiques

**Exemple**
```python
from src.utils.utils import get_path_vcn3_moyenne_historique

vcn3_moyen = get_path_vcn3_moyenne_historique("BSH001")
print(vcn3_moyen)
# Output: output/VCN3/moyenne_historique/VCN3-moyenne-BSH001-1991-2020.csv
```

#### `get_path_vcn3_mensuel(code_sandre: str, annee_mois: str) -> Path`

Retourne le chemin vers le fichier CSV contenant les VCN3 mensuels.

**Paramètres**
- `code_sandre` : Code Sandre du réseau
- `annee_mois` : Année et mois au format AAAA-MM

**Retourne**
- `Path` : Chemin vers le fichier VCN3 mensuel

**Exemple**
```python
from src.utils.utils import get_path_vcn3_mensuel

vcn3_mensuel = get_path_vcn3_mensuel("BSH001", "2026-06")
print(vcn3_mensuel)
# Output: output/VCN3/mensuel/VCN3-BSH001-2026-06.csv
```

#### `get_path_vcn3_station(code_station: str) -> Path`

Retourne le chemin vers le fichier CSV contenant les VCN3 pour une station spécifique.

**Paramètres**
- `code_station` : Code de la station

**Retourne**
- `Path` : Chemin vers le fichier VCN3 de la station

**Exemple**
```python
from src.utils.utils import get_path_vcn3_station

vcn3_station = get_path_vcn3_station("H000001")
print(vcn3_station)
# Output: output/VCN3/stations/VCN3-station-H000001.csv
```

#### `get_path_periode_de_retour(code_sandre: str, annee_mois: str) -> Path`

Retourne le chemin vers le fichier CSV contenant les périodes de retour.

**Paramètres**
- `code_sandre` : Code Sandre du réseau
- `annee_mois` : Année et mois au format AAAA-MM

**Retourne**
- `Path` : Chemin vers le fichier des périodes de retour

**Exemple**
```python
from src.utils.utils import get_path_periode_de_retour

periode_path = get_path_periode_de_retour("BSH001", "2026-06")
print(periode_path)
# Output: output/VCN3/analyse_frequence_periode/periode-de-retour-BSH001-2026-06.csv
```

### Chemins Stations et Sites

#### `get_path_stations() -> Path`

Retourne le chemin vers le fichier CSV contenant les métadonnées des stations Hub'Eau.

**Retourne**
- `Path` : Chemin vers le fichier des stations

**Exemple**
```python
from src.utils.utils import get_path_stations

stations_path = get_path_stations()
print(stations_path)
# Output: output/hubeau/downloaded_data/stations/stations.csv
```

#### `get_path_sites() -> Path`

Retourne le chemin vers le fichier CSV contenant les métadonnées des sites Hub'Eau.

**Retourne**
- `Path` : Chemin vers le fichier des sites

**Exemple**
```python
from src.utils.utils import get_path_sites

sites_path = get_path_sites()
print(sites_path)
# Output: output/hubeau/downloaded_data/sites/sites.csv
```

#### `get_path_liste_site_station_custom() -> Path`

Retourne le chemin vers le fichier CSV contenant la liste personnalisée des sites et stations.

**Retourne**
- `Path` : Chemin vers le fichier personnalisé

**Exemple**
```python
from src.utils.utils import get_path_liste_site_station_custom

custom_path = get_path_liste_site_station_custom()
print(custom_path)
# Output: output/site_station_custom/liste_site_et_station_custom.csv
```

### Chemins MétéoFrance

#### `get_path_meteofrance_correspondance_departement_id_datagouv_mens_historique() -> Path`

Retourne le chemin vers le fichier CSV de correspondance entre départements et identifiants DataGouv.

**Retourne**
- `Path` : Chemin vers le fichier de correspondance

**Exemple**
```python
from src.utils.utils import get_path_meteofrance_correspondance_departement_id_datagouv_mens_historique

correspondance_path = get_path_meteofrance_correspondance_departement_id_datagouv_mens_historique()
print(correspondance_path)
# Output: output/meteoFrance/departement_id_datagouv/MENS_departement_id_datagouv_historique.csv
```

### Chemins ONDE

#### `get_path_campagne_onde() -> Path`

Retourne le chemin vers le fichier CSV contenant toutes les campagnes ONDE.

**Retourne**
- `Path` : Chemin vers le fichier des campagnes ONDE

**Exemple**
```python
from src.utils.utils import get_path_campagne_onde

campagne_path = get_path_campagne_onde()
print(campagne_path)
# Output: output/hubeau/downloaded_data/onde/campagnes_onde.csv
```

#### `get_path_observation_onde(date_debut: datetime, date_fin: datetime, onde_zone: GeographicScaleClip, code_associe: str) -> Path`

Retourne le chemin vers le fichier CSV contenant les observations ONDE pour une période et une zone géographique.

**Paramètres**
- `date_debut` : Date de début des observations
- `date_fin` : Date de fin des observations
- `onde_zone` : Zone géographique (utiliser `GeographicScaleClip`)
- `code_associe` : Code associé à la zone géographique

**Retourne**
- `Path` : Chemin vers le fichier des observations ONDE

**Exemple**
```python
from src.utils.utils import get_path_observation_onde
from src.model.enums import GeographicScaleClip
from datetime import datetime

observation_path = get_path_observation_onde(
    date_debut=datetime(2026, 6, 1),
    date_fin=datetime(2026, 6, 30),
    onde_zone=GeographicScaleClip.BASSIN,
    code_associe="06"
)
print(observation_path)
# Output: output/hubeau/downloaded_data/onde/observation_onde_B06_20260601_20260630.csv
```

#### `get_path_stations_onde(onde_zone: GeographicScaleClip, code_associe: str) -> Path`

Retourne le chemin vers le fichier CSV contenant les stations ONDE pour une zone géographique.

**Paramètres**
- `onde_zone` : Zone géographique (utiliser `GeographicScaleClip`)
- `code_associe` : Code associé à la zone géographique

**Retourne**
- `Path` : Chemin vers le fichier des stations ONDE

**Exemple**
```python
from src.utils.utils import get_path_stations_onde
from src.model.enums import GeographicScaleClip

stations_onde_path = get_path_stations_onde(
    onde_zone=GeographicScaleClip.BASSIN,
    code_associe="06"
)
print(stations_onde_path)
# Output: output/hubeau/downloaded_data/onde/stations_onde_B06.csv
```

---

## 🔄 Fonctions de Sources

### `is_date_historique(annee_mois: str) -> bool`

Vérifie si une date correspond à la période historique (1990-12 à 2020-12).

**Paramètres**
- `annee_mois` : Date au format AAAA-MM

**Retourne**
- `bool` : True si la date est dans la période historique, False sinon

**Exemple**
```python
from src.utils.utils import is_date_historique

print(is_date_historique("2020-12"))  # True
print(is_date_historique("2021-01"))  # False
print(is_date_historique("1990-12"))  # True
```

### `get_paths_source_historique(grandeur: str) -> list[Path]`

Retourne la liste des chemins vers les fichiers sources nécessaires pour une grandeur historique.

**Paramètres**
- `grandeur` : La grandeur concernée

**Retourne**
- `list[Path]` : Liste des chemins sources

**Exemple**
```python
from src.utils.utils import get_paths_source_historique

# Sources pour QmM historique
sources_qmm = get_paths_source_historique("QmM")
for source in sources_qmm:
    print(source)
```

**Détails**
- Pour QmnJ : Retourne tous les fichiers mensuels de 1990-12 à 2020-12
- Pour QmM : Retourne le fichier historique unique
- Inclut toujours les fichiers des stations et sites

### `get_paths_source_mensuel(grandeur: str, annee_mois: str) -> list[Path]`

Retourne la liste des chemins vers les fichiers sources nécessaires pour une grandeur mensuelle.

**Paramètres**
- `grandeur` : La grandeur concernée
- `annee_mois` : Année et mois au format AAAA-MM

**Retourne**
- `list[Path]` : Liste des chemins sources

**Exemple**
```python
from src.utils.utils import get_paths_source_mensuel

# Sources pour QmM de juin 2026
sources_mensuel = get_paths_source_mensuel("QmM", "2026-06")
for source in sources_mensuel:
    print(source)
```

### `get_path_sources(code_sandre: str, grandeur: str, annee_mois: str) -> list[Path]`

Retourne la liste complète des chemins sources pour un code Sandre, une grandeur et une date donnés.

**Paramètres**
- `code_sandre` : Code Sandre du réseau
- `grandeur` : La grandeur concernée
- `annee_mois` : Année et mois au format AAAA-MM

**Retourne**
- `list[Path]` : Liste complète des chemins sources

**Exemple**
```python
from src.utils.utils import get_path_sources

# Toutes les sources pour BSH001, QmM, juin 2026
all_sources = get_path_sources("BSH001", "QmM", "2026-06")
for source in all_sources:
    print(source)
```

---

## 🔧 Exemple Complet : Utilisation des Fonctions de Chemins

### Récupérer tous les chemins nécessaires pour une analyse

```python
from src.utils.utils import (
    get_path_clean_csv,
    get_path_qmm_moyen_historique,
    get_path_hydraulicite,
    get_path_vcn3_mensuel,
    get_path_periode_de_retour
)

# Configuration
code_sandre = "BSH001"
annee_mois = "2026-06"

# Chemins pour l'analyse
chemins = {
    "donnees_nettoyees_qmm": get_path_clean_csv(code_sandre, annee_mois, "QmM"),
    "donnees_nettoyees_qmnj": get_path_clean_csv(code_sandre, annee_mois, "QmnJ"),
    "moyennes_qmm": get_path_qmm_moyen_historique(code_sandre),
    "hydraulicite": get_path_hydraulicite(code_sandre, annee_mois),
    "vcn3_mensuel": get_path_vcn3_mensuel(code_sandre, annee_mois),
    "periode_retour": get_path_periode_de_retour(code_sandre, annee_mois),
}

print("Chemins pour l'analyse :")
for nom, chemin in chemins.items():
    print(f"{nom}: {chemin}")
```

---

## 🎯 Bonnes Pratiques

### 1. Toujours utiliser les fonctions de chemins

```python
from src.utils.utils import get_path_clean_csv

# ✅ Bon - Utilisation de la fonction dédiée
output_path = get_path_clean_csv("BSH001", "2026-06", "QmM")

# ❌ À éviter - Chemin codé en dur
output_path = Path("output/hubeau/cleaned_data/clean-QmM-BSH001-2026-06.csv")
```

### 2. Vérifier l'existence des fichiers

```python
from src.utils.utils import get_path_clean_csv

chemin = get_path_clean_csv("BSH001", "2026-06", "QmM")
if chemin.exists():
    print(f"Fichier existe : {chemin}")
else:
    print(f"Fichier manquant : {chemin}")
```

### 3. Utiliser les constantes pour les grandeurs

```python
from src.utils.utils import GRANDEUR

# ✅ Bon - Utilisation de la constante
for grandeur in GRANDEUR:
    process_grandeur(grandeur)

# ❌ À éviter - Grandeurs codées en dur
for grandeur in ["QmM", "QmnJ"]:
    process_grandeur(grandeur)
```

---

## 🔗 Liens Utiles

- [Documentation du Module Utils](index.md)
- [Documentation utils_file.py](utils_file.md)
- [Documentation utils_proxy.py](utils_proxy.md)
- [Module Processing](../../processing/index.md)
- [Module IO](../../io/index.md)
- [Concepts Clés](../../../concepts/index.md)

---

*Dernière mise à jour : {{ "now" | date: "%d %B %Y" }}*