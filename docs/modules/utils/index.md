---
layout: default
title: Module Utils
description: "Documentation complète du module utilitaire"
nav_order: 6
parent: Modules
has_children: true
---

# 🛠️ Module Utils

**Documentation API complète du module utilitaire**

Ce module fournit des fonctions utilitaires essentielles pour le bon fonctionnement de l'application. Il comprend la gestion des chemins, des fichiers, du proxy réseau et d'autres fonctionnalités transverses.

---

## 🗂️ Structure du Module

```
src/utils/
├── __init__.py
├── utils.py              # Fonctions utilitaires principales (chemins, gestion des données)
├── utils_file.py         # Gestion des fichiers et vérification des dates
└── utils_proxy.py        # Configuration et test du proxy réseau
```

---

## 🎯 Aperçu des Fonctionnalités

| Fichier | Domaine | Fonctionnalités Principales | Utilisation |
|--------|---------|----------------------------|-------------|
| [utils.py](utils.md) | Chemins et Données | Gestion des chemins de fichiers, récupération des métadonnées | Partout dans l'application |
| [utils_file.py](utils_file.md) | Fichiers | Vérification de l'âge des fichiers, gestion des mises à jour | Vérification de la fraîcheur des données |
| [utils_proxy.py](utils_proxy.md) | Réseau | Configuration automatique du proxy, test de connexion | Accès internet |

---

## 📋 Fonctionnalités par Catégorie

### 📁 Gestion des Chemins (utils.py)

Centralisation de tous les chemins de fichiers utilisés dans l'application.

- **Chemins Hub'Eau** : Données brutes, nettoyées, stations, sites
- **Chemins VCN3** : Moyennes historiques, données mensuelles, analyses
- **Chemins Hydraulicité** : Résultats des calculs d'hydraulicité
- **Chemins MétéoFrance** : Données météo, correspondances géographiques
- **Chemins ONDE** : Campagnes, observations, stations

### 🔄 Gestion des Fichiers (utils_file.py)

Vérification et gestion de la fraîcheur des données.

- **Vérification d'âge** : Déterminer si un fichier est trop vieux
- **Comparaison de dates** : Vérifier que les résultats sont à jour par rapport aux sources
- **Promptes utilisateur** : Interface pour la mise à jour des fichiers
- **Cache des réponses** : Éviter de redemander à l'utilisateur

### 🌐 Gestion du Proxy (utils_proxy.py)

Configuration automatique du proxy pour l'accès internet.

- **Test de connexion** : Vérifier si la connexion internet fonctionne
- **Configuration automatique** : Déterminer si le proxy est nécessaire
- **Gestion des erreurs** : Messages clairs en cas de problème de connexion
- **Cache** : Exécuter le test une seule fois par session

---

## 🔧 Prérequis et Dépendances

### Dépendances Python

```python
# Dépendances directes du module utils
import os
import requests
from pathlib import Path
from datetime import datetime, timedelta
from functools import cache
from dotenv import load_dotenv
```

### Modules Internes Utilisés

```python
from src.config.paths import OUTPUT_DIR
from src.config.logging_config import setup_logger
```

---

## 📁 Structure des Chemins Gérés

### Arbre des Chemins

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
├── QmM_moyen/                             # Moyennes historiques QmM
│   └── QmM_moyennes_{code_sandre}_1991_2020.csv
├── hydraulicite/                          # Résultats d'hydraulicité
│   └── hydraulicite-{code_sandre}-{annee_mois}.csv
├── VCN3/
│   ├── moyenne_historique/                # VCN3 historiques
│   │   └── VCN3-moyenne-{code_sandre}-1991-2020.csv
│   ├── mensuel/                            # VCN3 mensuels
│   │   └── VCN3-{code_sandre}-{annee_mois}.csv
│   ├── stations/                           # VCN3 par station
│   │   └── VCN3-station-{code_station}.csv
│   └── analyse_frequence_periode/          # Périodes de retour
│       └── periode-de-retour-{code_sandre}-{annee_mois}.csv
└── meteoFrance/
    ├── departement_id_datagouv/           # Correspondances départements
    │   └── MENS_departement_id_datagouv_historique.csv
    └── downloaded_data/                    # Données MétéoFrance brutes
        └── ...
```

---

## 🎓 Tutorial : Utilisation des Fonctions Utilitaires

### Étape 1 : Récupérer les chemins des fichiers

```python
from src.utils.utils import (
    get_path_historique_raw_csv,
    get_path_mensuel_raw_csv,
    get_path_clean_csv,
    get_path_qmm_moyen_historique
)

# Chemins vers les données brutes
historique_qmm = get_path_historique_raw_csv("QmM")
mensuel_qmm = get_path_mensuel_raw_csv("2026-06", "QmM")

# Chemins vers les données nettoyées
clean_qmm = get_path_clean_csv("BSH001", "2026-06", "QmM")

# Chemins vers les moyennes
qmm_moyen = get_path_qmm_moyen_historique("BSH001")
```

### Étape 2 : Vérifier la fraîcheur des données

```python
import src.utils.utils_file as utils_file
from src.utils.utils import get_paths_source_mensuel

# Vérifier si un fichier doit être mis à jour
chemin_source = get_paths_source_mensuel("QmM", "2026-06")
chemin_resultat = get_path_clean_csv("BSH001", "2026-06", "QmM")

if not utils_file.is_res_updated_with_source(chemin_source, chemin_resultat):
    print("Les données doivent être mises à jour")
else:
    print("Les données sont à jour")
```

### Étape 3 : Configurer le proxy

```python
from src.utils.utils_proxy import set_up_working_proxy

# Configurer automatiquement le proxy (à appeler au démarrage)
set_up_working_proxy()
```

---

## 📚 Documentation par Fichier

| Fichier | Description | [Lien](link) |
|--------|-------------|------|
| **utils.py** | Fonctions utilitaires principales pour la gestion des chemins et données | [Voir →](utils.md) |
| **utils_file.py** | Gestion des fichiers, vérification de fraîcheur et prompts utilisateur | [Voir →](utils_file.md) |
| **utils_proxy.py** | Configuration et test du proxy réseau pour l'accès internet | [Voir →](utils_proxy.md) |

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

### 2. Vérifier la fraîcheur avant de recalculer

```python
import src.utils.utils_file as utils_file
from src.utils.utils import get_paths_source_mensuel

# Toujours vérifier si le recalcul est nécessaire
chemin_source = get_paths_source_mensuel("QmM", "2026-06")
chemin_resultat = get_path_clean_csv("BSH001", "2026-06", "QmM")

if not utils_file.is_res_updated_with_source(chemin_source, chemin_resultat):
    # Recalculer les données
    recalculer_donnees()
```

### 3. Configurer le proxy une seule fois

```python
from src.utils.utils_proxy import set_up_working_proxy

# Appeler au démarrage de l'application
set_up_working_proxy()  # Exécuté une seule fois grâce au cache

# Les appels suivants utilisent le cache, pas de test supplémentaire
set_up_working_proxy()
```

---

## 🔗 Liens Utiles

- [Documentation utils.py](utils.md)
- [Documentation utils_file.py](utils_file.md)
- [Documentation utils_proxy.py](utils_proxy.md)
- [Module Processing](../processing/index.md)
- [Module IO](../io/index.md)
- [Concepts Clés](../../concepts/index.md)
- [Utilisation CLI](../../usage/cli.md)

---

*Dernière mise à jour : {{ "now" | date: "%d %B %Y" }}*


