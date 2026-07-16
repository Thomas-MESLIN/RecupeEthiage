---
layout: default
title: plot_grandeur
description: "Documentation API du module plot_grandeur - Visualisation des grandeurs hydrologiques"
nav_order: 1
parent: Module Plotting
grand_parent: Modules
---

# 📈 plot_grandeur

**Documentation API complète**

> **Fichier** : `src/plotting/plot_grandeur.py`
> **Module** : Visualisation des grandeurs hydrologiques
> **Auteur** : Thomas Meslin
> **Dernière mise à jour** : Juin 2026

---

## 📋 Table des Matières

- [🎯 Aperçu](#-aperçu)
- [📦 Dépendances](#-dépendances)
- [🔧 Fonctions](#-fonctions)
  - [create_geojson_from_path](#create_geojson_from_path)
  - [create_geojson_from_stations](#create_geojson_from_stations)
  - [create_geojson_from_sites](#create_geojson_from_sites)
  - [print_results](#print_results)
  - [plot_results](#plot_results)
  - [plot_period_from_flow](#plot_period_from_flow)
  - [plot_result_station](#plot_result_station)
  - [create_geojson_from_periode_de_retour](#create_geojson_from_periode_de_retour)
  - [create_geojson_from_hydraulicite](#create_geojson_from_hydraulicite)
- [🎓 Tutoriel](#-tutoriel)
- [📊 Exemples Complets](#-exemples-complets)

---

## 🎯 Aperçu

Ce module gère la **création de cartes GeoJSON** et de **graphiques** pour les données hydrologiques, notamment :

- ✅ **Hydraulicité** : Mesure du niveau d'eau par rapport à la normale
- ✅ **VCN3** : Volume Current Non-dépassé sur 3 mois (indice d'étiage)
- ✅ **Périodes de retour** : Analyse fréquentielle des débits minimaux
- ✅ **Graphiques par station** : Visualisation détaillée pour chaque station

### Domaines couverts

| Domaine | Description | Fonctions associées |
|---------|-------------|---------------------|
| **Hydraulicité** | Calcul et cartographie de l'hydraulicité mensuelle | `create_geojson_from_hydraulicite` |
| **VCN3** | Calcul et analyse des volumes d'étiage | `create_geojson_from_periode_de_retour` |
| **Stations** | Gestion et visualisation des stations de mesure | `create_geojson_from_stations` |
| **Sites** | Gestion et visualisation des sites hydrologiques | `create_geojson_from_sites` |
| **Graphiques** | Génération de graphiques statistiques | `plot_results`, `plot_period_from_flow` |

---

## 📦 Dépendances

### Dépendances externes

```python
import pandas as pd
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
```

### Dépendances internes

```python
import src.utils.utils as utils
import src.processing.calcul_frequence_periode_de_retour as f_T
import src.processing.station as station
import src.io.download_Hubeau as download_Hubeau
import src.processing.calcul_hydraulicite as calcul_hydraulicite
import logging
from src.config.logging_config import setup_logger
from src.config.paths import OUTPUT_DIR
```

---

## 🔧 Fonctions

---

### `create_geojson_from_path`

**Crée un GeoJSON à partir d'un fichier CSV de données hydrologiques.**

#### 📌 Signature

```python
def create_geojson_from_path(
    chemin_donees_csv: Path,
    output_path: Path,
    annee_mois: str,
    code_sandre: str
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `chemin_donees_csv` | `Path` | Chemin vers le fichier CSV contenant les données hydrologiques | ✅ |
| `output_path` | `Path` | Chemin de sortie pour le fichier GeoJSON | ✅ |
| `annee_mois` | `str` | Date au format `AAAA-MM` (ex: `2026-01`) | ✅ |
| `code_sandre` | `str` | Code du réseau SANDRE (ex: `BSH001`) | ✅ |

#### 📤 Retourne

`None` - Le fichier GeoJSON est enregistré à l'emplacement spécifié.

#### 📊 Comportement

1. Charge le CSV des données hydrologiques
2. Récupère les stations actives pour le mois et le code SANDRE spécifiés
3. Fusionne les données avec les informations des stations
4. Charge les informations des sites
5. Fusionne avec les sites
6. Exporte le résultat au format GeoJSON

#### ⚠️ Notes

- Supprime automatiquement la colonne `Unnamed: 0` si présente
- Utilise le système de coordonnées **EPSG:4326** (WGS84)
- Nécessite que le fichier CSV contienne une colonne `code_station`

#### 📄 Fichiers générés

- `{output_path}.geojson` - Fichier GeoJSON

#### 🎯 Exemple

```python
from pathlib import Path
from src.plotting.plot_grandeur import create_geojson_from_path

create_geojson_from_path(
    chemin_donees_csv=Path("output/hydraulicite/hydraulicite-BSH001-2026-01.csv"),
    output_path=Path("output/QGIS/hydraulicite/hydraulicite-BSH001-2026-01.geojson"),
    annee_mois="2026-01",
    code_sandre="BSH001"
)
```

---

### `create_geojson_from_stations`

**Crée un GeoJSON des stations hydrologiques.**

#### 📌 Signature

```python
def create_geojson_from_stations(
    code_sandre: str | None = None,
    annee_mois: str | None = None
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `code_sandre` | `str \| None` | Code du réseau SANDRE. Utilisez `None` pour toutes les stations | `None` |
| `annee_mois` | `str \| None` | Date au format `AAAA-MM` pour filtrer les stations actives | `None` |

#### 📤 Retourne

`None` - Les fichiers GeoJSON et CSV sont enregistrés.

#### 📊 Comportement

1. Récupère les stations correspondant au code SANDRE (ou toutes si `None`)
2. Filtre les stations actives si `annee_mois` est spécifié
3. Convertit en GeoDataFrame avec géométrie WKT
4. Exporte en GeoJSON et CSV

#### 📄 Fichiers générés

- `output/QGIS/stations/stations-ouverte-{code_sandre}-{annee_mois}.geojson`
- `output/QGIS/stations/stations-ouverte-{code_sandre}-{annee_mois}.csv`
- `output/QGIS/stations/stations-{code_sandre}.geojson` (si pas de mois)
- `output/QGIS/stations/stations.geojson` (si tout est `None`)

#### 🎯 Exemple

```python
from src.plotting.plot_grandeur import create_geojson_from_stations

# Toutes les stations du réseau BSH001 actives en janvier 2026
create_geojson_from_stations("BSH001", "2026-01")

# Toutes les stations (tous réseaux, toutes périodes)
create_geojson_from_stations()

# Stations du réseau custom
create_geojson_from_stations("custom", "2026-01")
```

---

### `create_geojson_from_sites`

**Crée un GeoJSON des sites hydrologiques.**

#### 📌 Signature

```python
def create_geojson_from_sites(code_sandre: str | None = None) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `code_sandre` | `str \| None` | Code du réseau SANDRE. Utilisez `None` pour tous les sites | `None` |

#### 📤 Retourne

`None` - Le fichier GeoJSON est enregistré.

#### 📊 Comportement

1. Récupère les stations correspondant au code SANDRE
2. Récupère tous les sites
3. Fusionne les données pour associer chaque site à ses stations
4. Exporte en GeoJSON

#### 📄 Fichiers générés

- `output/QGIS/sites/sites-{code_sandre}.geojson`
- `output/QGIS/sites/sites.geojson` (si `code_sandre` est `None`)

#### 🎯 Exemple

```python
from src.plotting.plot_grandeur import create_geojson_from_sites

# Sites du réseau BSH001
create_geojson_from_sites("BSH001")

# Tous les sites
create_geojson_from_sites()
```

---

### `print_results`

**Affiche les résultats d'analyse fréquentielle dans la console.**

#### 📌 Signature

```python
def print_results(res: dict) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `res` | `dict` | Dictionnaire contenant les résultats d'analyse fréquentielle | ✅ |

#### 📤 Retourne

`None` - Affiche les résultats dans la console.

#### 📊 Structure du dictionnaire `res`

```python
{
    'mu': float,           # Moyenne (log)
    'sigma': float,        # Écart-type (log)
    'p0': float,           # Probabilité de débit nul
    'y': list,             # Séries de données
    'z': list,             # Séries sans zéros
    'quantiles': DataFrame, # Tableau des quantiles
    'empirical': DataFrame, # Données empiriques
    'pcdf': DataFrame      # Fonction de répartition cumulative
}
```

#### 📄 Affichage

Affiche un tableau formaté avec :
- Loi : Log-Normale
- Estimateur : L-moments
- IC : PBOOT
- Paramètres µ et σ
- Période de retour (T), fréquence de non-dépassement (p), VCN3, intervalles de confiance

#### 🎯 Exemple

```python
from src.plotting.plot_grandeur import print_results

resultats = {
    'mu': 2.5,
    'sigma': 0.5,
    'p0': 0.05,
    'y': [1.2, 1.5, 1.8, 2.1],
    'z': [1.2, 1.5, 1.8, 2.1],
    'quantiles': ...,
    'empirical': ...,
    'pcdf': ...
}

print_results(resultats)
```

**Sortie console :**
```
=================================================================
  Loi : Log-Normale  |  Estimateur : L-moments  |  IC : PBOOT
  µ (log) = 2.5000   σ (log) = 0.5000
  p0 (prob. débit nul) = 0.050
  n total = 4   n positifs = 4
=================================================================

     T (ans)    p non-dép.    VCN3 (m³/s)    IC bas     IC haut
-----------------------------------------------------------------
         1        0.5000         1.5000      1.2000      1.8000
        10        0.9000         0.8000      0.7000      0.9000
       100        0.9900         0.5000      0.4000      0.6000
```

---

### `plot_results`

**Génère trois graphiques d'analyse fréquentielle VCN3.**

#### 📌 Signature

```python
def plot_results(
    res: dict,
    output_path: str | Path,
    title: str = "Analyse fréquentielle VCN3"
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `res` | `dict` | Dictionnaire des résultats d'analyse fréquentielle | ✅ |
| `output_path` | `str \| Path` | Chemin de sortie pour l'image PNG | ✅ |
| `title` | `str` | Titre du graphique | `"Analyse fréquentielle VCN3"` |

#### 📤 Retourne

`None` - Trois graphiques sont enregistrés dans un seul fichier PNG.

#### 📊 Comportement

Crée une figure avec **3 sous-graphiques** :

1. **Période de retour T (ans) vs débit**
   - Axe X : Période de retour (échelle logarithmique)
   - Axe Y : VCN3 (m³/s)
   - Affiche : Loi Log-Normale, IC 95% (PBOOT), Observations

2. **Fréquence de non-dépassement vs débit**
   - Axe X : Fréquence de non-dépassement (0 à 1)
   - Axe Y : VCN3 (m³/s)
   - Affiche : Loi Log-Normale, IC 95% (PBOOT), Observations

3. **Vide** (réservé pour extensions futures)

#### 📄 Fichiers générés

- `{output_path}.png` - Image PNG haute résolution (150 DPI)

#### 🎯 Exemple

```python
from pathlib import Path
from src.plotting.plot_grandeur import plot_results
from src.processing.calcul_frequence_periode_de_retour import vcn3_frequence_retour
import numpy as np

# Calculer les résultats d'analyse
donnees = np.array([1.5, 2.0, 1.8, 2.2, 1.7, 1.9, 2.1, 1.6])
resultats = vcn3_frequence_retour(donnees)

# Générer le graphique
plot_results(
    res=resultats,
    output_path=Path("output/VCN3/analyse-frequentielle-test.png"),
    title="Analyse fréquentielle VCN3 - Station Test"
)
```

---

### `plot_period_from_flow`

**Trace la courbe T vs débit avec un débit observé mis en évidence.**

#### 📌 Signature

```python
def plot_period_from_flow(
    q_obs: float,
    res_station: dict,
    res_estimation: dict,
    code_station: str,
    output_path: str | Path
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `q_obs` | `float` | Débit observé (m³/s) | ✅ |
| `res_station` | `dict` | Résultats pour la station (doit contenir : `Periode_de_retour`, `debit_obs`, `frequence_non_depassement`, etc.) | ✅ |
| `res_estimation` | `dict` | Résultats d'estimation fréquentielle | ✅ |
| `code_station` | `str` | Code de la station | ✅ |
| `output_path` | `str \| Path` | Chemin de sortie pour l'image PNG | ✅ |

#### 📤 Retourne

`None` - Un graphique est enregistré.

#### 📊 Comportement

Crée un graphique montrant :
- La loi Log-Normale ajustée
- Les intervalles de confiance 95%
- Les observations
- Le débit observé (`q_obs`) avec :
  - Une ligne horizontale à `q_obs`
  - Une ligne verticale à la période de retour correspondante
  - Un point d'intersection marqué
  - Une bande verticale pour l'intervalle de confiance sur T

#### 📄 Fichiers générés

- `{output_path}.png` - Image PNG haute résolution (150 DPI)

#### 🎯 Exemple

```python
from pathlib import Path
from src.plotting.plot_grandeur import plot_period_from_flow

# Données d'exemple
q_observé = 1.5  # m³/s
résultats_station = {
    'debit_obs': 1.5,
    'Periode_de_retour': 10.0,
    'frequence_non_depassement': 0.90,
    'Periode_de_retour_interval_confiance_bas': 8.0,
    'Periode_de_retour_interval_confiance_haut': 12.0
}
résultats_estimation = {
    'pcdf': {...},  # Résultats de l'estimation
    'empirical': {...}
}

plot_period_from_flow(
    q_obs=q_observé,
    res_station=résultats_station,
    res_estimation=résultats_estimation,
    code_station="H1234567",
    output_path=Path("output/VCN3/periode-de-retour-H1234567-01.png")
)
```

---

### `plot_result_station`

**Génère les graphiques pour une station spécifique.**

#### 📌 Signature

```python
def plot_result_station(
    code_station: str,
    mois: str,
    result_station: dict,
    resultats_frequence_periode_retour: dict
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `code_station` | `str` | Code de la station | ✅ |
| `mois` | `str` | Mois au format `MM` (ex: `"01"`) | ✅ |
| `result_station` | `dict` | Résultats pour la station | ✅ |
| `resultats_frequence_periode_retour` | `dict` | Résultats d'analyse fréquentielle | ✅ |

#### 📤 Retourne

`None` - Deux graphiques sont générés.

#### 📊 Comportement

Appelle :
1. `plot_results()` - Analyse fréquentielle complète
2. `plot_period_from_flow()` - Période de retour pour le débit observé

#### 📄 Fichiers générés

- `output/VCN3/plot_stations/analyse-frequentielle-{code_station}-{mois}.png`
- `output/VCN3/plot_stations/periode-de-retour-{code_station}-{mois}.png`

#### 🎯 Exemple

```python
from src.plotting.plot_grandeur import plot_result_station

plot_result_station(
    code_station="H1234567",
    mois="01",
    result_station={
        'debit_obs': 1.5,
        'Periode_de_retour': 10.0,
        'frequence_non_depassement': 0.90,
        'Periode_de_retour_interval_confiance_bas': 8.0,
        'Periode_de_retour_interval_confiance_haut': 12.0
    },
    resultats_frequence_periode_retour=résultats_analysis
)
```

---

### `create_geojson_from_periode_de_retour`

**Crée un GeoJSON des périodes de retour VCN3.**

#### 📌 Signature

```python
def create_geojson_from_periode_de_retour(
    annee_mois: str,
    code_sandre: str,
    is_result_plotted: bool = False
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `annee_mois` | `str` | Date au format `AAAA-MM` | ✅ |
| `code_sandre` | `str` | Code du réseau SANDRE | ✅ |
| `is_result_plotted` | `bool` | Si `True`, génère les graphiques par station | `False` |

#### 📤 Retourne

`None` - Les fichiers GeoJSON et éventuellement les graphiques sont générés.

#### 📊 Comportement

1. Vérifie que les périodes de retour sont déjà calculées
2. Si non, appelle `f_T.ensure_frequence_non_depassement_periode_retour_calcule()`
3. Charge le fichier CSV des périodes de retour
4. Appelle `create_geojson_from_path()` pour générer le GeoJSON
5. Si `is_result_plotted=True`, génère aussi les graphiques par station via `plot_result_station()`

#### 📄 Fichiers générés

- `output/QGIS/frequence_periode_de_retour/periode-de-retour-{code_sandre}-{annee_mois}.geojson`
- `output/VCN3/plot_stations/*.png` (si `is_result_plotted=True`)

#### 🎯 Exemple

```python
from src.plotting.plot_grandeur import create_geojson_from_periode_de_retour

# Sans graphiques
create_geojson_from_periode_de_retour("2026-01", "BSH001")

# Avec graphiques par station
create_geojson_from_periode_de_retour("2026-01", "BSH001", is_result_plotted=True)
```

---

### `create_geojson_from_hydraulicite`

**Exporte un GeoJSON de l'hydraulicité du mois spécifié.**

#### 📌 Signature

```python
def create_geojson_from_hydraulicite(annee_mois: str, code_sandre: str) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `annee_mois` | `str` | Date au format `AAAA-MM` | ✅ |
| `code_sandre` | `str` | Code du réseau SANDRE | ✅ |

#### 📤 Retourne

`None` - Le fichier GeoJSON est généré.

#### 📊 Comportement

1. Vérifie que l'hydraulicité est calculée pour le mois et le réseau
2. Si non, appelle `calcul_hydraulicite.calcul_hydraulicite_mensuel()`
3. Charge le fichier CSV de l'hydraulicité
4. Appelle `create_geojson_from_path()` pour générer le GeoJSON

#### 📄 Fichiers générés

- `output/QGIS/hydraulicite/hydraulicite-{code_sandre}-{annee_mois}.geojson`

#### 🎯 Exemple

```python
from src.plotting.plot_grandeur import create_geojson_from_hydraulicite

create_geojson_from_hydraulicite("2026-01", "BSH001")
```

---

## 🎓 Tutoriel : Générer une Analyse Complète VCN3

### Étape 1 : Préparer l'environnement

```python
# Importer les modules nécessaires
from src.plotting.plot_grandeur import (
    create_geojson_from_hydraulicite,
    create_geojson_from_periode_de_retour,
    create_geojson_from_stations,
    create_geojson_from_sites
)
```

### Étape 2 : Générer les données de base

```python
# Code SANDRE et mois d'intérêt
code_sandre = "BSH001"
annee_mois = "2026-01"

# Générer les stations et sites
create_geojson_from_stations(code_sandre, annee_mois)
create_geojson_from_sites(code_sandre)
```

### Étape 3 : Générer la carte d'hydraulicité

```python
create_geojson_from_hydraulicite(annee_mois, code_sandre)
```

**Résultat** : `output/QGIS/hydraulicite/hydraulicite-BSH001-2026-01.geojson`

### Étape 4 : Générer la carte VCN3 avec graphiques

```python
create_geojson_from_periode_de_retour(
    annee_mois,
    code_sandre,
    is_result_plotted=True  # Génère les graphiques par station
)
```

**Résultats** :
- `output/QGIS/frequence_periode_de_retour/periode-de-retour-BSH001-2026-01.geojson`
- `output/VCN3/plot_stations/analyse-frequentielle-{station}-01.png` (pour chaque station)
- `output/VCN3/plot_stations/periode-de-retour-{station}-01.png` (pour chaque station)

### Étape 5 : Visualiser dans QGIS

1. Ouvrez QGIS
2. Importez les fichiers GeoJSON générés
3. Stylez les couches selon vos besoins
4. Visualisez les résultats

---

## 📊 Exemples Complets

### Exemple 1 : Génération complète pour un mois

```python
from src.plotting.plot_grandeur import (
    create_geojson_from_hydraulicite,
    create_geojson_from_periode_de_retour,
    create_geojson_from_stations,
    create_geojson_from_sites
)

# Paramètres
code = "BSH001"
mois = "2026-01"

# 1. Générer les fichiers de base
print("Génération des stations et sites...")
create_geojson_from_stations(code, mois)
create_geojson_from_sites(code)

# 2. Générer l'hydraulicité
print("Génération de l'hydraulicité...")
create_geojson_from_hydraulicite(mois, code)

# 3. Générer le VCN3 avec graphiques
print("Génération du VCN3 avec graphiques...")
create_geojson_from_periode_de_retour(mois, code, is_result_plotted=True)

print("✅ Toutes les cartes générées avec succès !")
```

### Exemple 2 : Traitement par lots pour plusieurs mois

```python
from src.plotting.plot_grandeur import (
    create_geojson_from_hydraulicite,
    create_geojson_from_periode_de_retour
)
import pandas as pd

# Liste des mois à traiter
mois_list = [
    "2025-07", "2025-08", "2025-09",
    "2025-10", "2025-11", "2025-12",
    "2026-01", "2026-02", "2026-03"
]

code_sandre = "BSH001"

for mois in mois_list:
    print(f"Traitement du mois {mois}...")
    
    # Générer l'hydraulicité
    try:
        create_geojson_from_hydraulicite(mois, code_sandre)
        print(f"  ✓ Hydraulicité {mois} générée")
    except Exception as e:
        print(f"  ✗ Erreur hydraulicité {mois}: {e}")
    
    # Générer le VCN3 (sans graphiques pour gagner du temps)
    try:
        create_geojson_from_periode_de_retour(mois, code_sandre, is_result_plotted=False)
        print(f"  ✓ VCN3 {mois} généré")
    except Exception as e:
        print(f"  ✗ Erreur VCN3 {mois}: {e}")

print("✅ Traitement par lots terminé !")
```

### Exemple 3 : Utilisation avec des données personnalisées

```python
from src.plotting.plot_grandeur import (
    create_geojson_from_path,
    create_geojson_from_stations
)
from pathlib import Path
import pandas as pd

# Utiliser un réseau custom
code_sandre = "custom"
annee_mois = "2026-01"

# 1. Générer les stations custom
create_geojson_from_stations(code_sandre, annee_mois)

# 2. Si vous avez vos propres données dans un CSV
chemin_csv = Path("mes_donnees/hydraulicite-custom-2026-01.csv")
output_geojson = Path("output/QGIS/hydraulicite/hydraulicite-custom-2026-01.geojson")

# Générer le GeoJSON
create_geojson_from_path(
    chemin_donees_csv=chemin_csv,
    output_path=output_geojson,
    annee_mois=annee_mois,
    code_sandre=code_sandre
)
```

---

## 📚 Voir aussi

- [Module plotting](index.md) - Aperçu du module
- [plot_meteoFrance](plot_meteoFrance.md) - Données météorologiques
- [plot_onde](plot_onde.md) - Données ONDE
- [rasterize](rasterize.md) - Rasterisation
- [Concepts : Hydraulicité](../../../concepts/hydraulicite.md)
- [Concepts : VCN3](../../../concepts/vcn3.md)

---

## 🎯 Résumé des Fonctions

| Fonction | Description | Sortie |
|----------|-------------|--------|
| `create_geojson_from_path` | Crée GeoJSON à partir de CSV | `.geojson` |
| `create_geojson_from_stations` | Crée GeoJSON des stations | `.geojson`, `.csv` |
| `create_geojson_from_sites` | Crée GeoJSON des sites | `.geojson` |
| `print_results` | Affiche les résultats dans la console | Console |
| `plot_results` | Génère 3 graphiques d'analyse | `.png` |
| `plot_period_from_flow` | Génère graphique T vs débit | `.png` |
| `plot_result_station` | Génère graphiques pour une station | `.png` × 2 |
| `create_geojson_from_periode_de_retour` | Crée GeoJSON VCN3 + graphiques optionnels | `.geojson` (+ `.png`) |
| `create_geojson_from_hydraulicite` | Crée GeoJSON d'hydraulicité | `.geojson` |

---

*Documentation générée automatiquement à partir du code source | Dernière mise à jour : {{ "now" | date: "%d %B %Y" }}*
