---
layout: default
title: clean.py
description: "Documentation API du module de nettoyage des données"
nav_order: 1
parent: Module Processing
grand_parent: Modules
---

# 🧹 clean.py

**Nettoyage et préparation des données hydrologiques**

Ce module gère le nettoyage, le filtrage et la préparation des données brutes provenant principalement de l'API Hub'Eau. Il assure que les données sont dans un format cohérent et prêt pour l'analyse.

---

## 🎯 Fonctionnalités Principales

- **Nettoyage des données Hub'Eau** : Extraction par date, code Sandre, suppression des doublons
- **Gestion historique** : Traitement des séries temporelles de 1991 à 2020
- **Validation** : Vérification de l'intégrité et de la fraîcheur des données
- **Cache** : Optimisation des performances avec mise en cache
- **Synchronisation** : Vérification que les données nettoyées sont à jour par rapport aux sources

---

## 📋 Fonctions Disponibles

### `get_grandeur_historique_df(grandeur: str) -> pd.DataFrame`

Récupère et met en cache le DataFrame correspondant à une grandeur sur la période historique 1991-2020.

**Paramètres**
- `grandeur` : Une grandeur à télécharger (ex: "QmM", "QmnJ")

**Retourne**
- `pd.DataFrame` : DataFrame contenant toutes les données historiques pour la grandeur spécifiée

**Exemple**
```python
from src.processing.clean import get_grandeur_historique_df

# Récupérer toutes les données QmM historiques
df_qmm = get_grandeur_historique_df("QmM")
print(f"Nombre d'enregistrements : {len(df_qmm)}")

# Récupérer toutes les données QmnJ historiques  
df_qmnj = get_grandeur_historique_df("QmnJ")
```

**Détails**
- Utilise un cache pour éviter de recharger les données plusieurs fois
- Si le fichier unique historique n'existe pas, concatène tous les fichiers mensuels
- Utilise `download_Hubeau.ensure_grandeur_historique_downloaded()` pour s'assurer que les données sont téléchargées

---

### `clean_hubeau_data(date_a_filtrer: str, code_sandre: str, path_file_to_clean=Path(""), grandeur_a_filtrer="", fichier_station_hubeau=str) -> pd.DataFrame`

Nettoie les données Hub'Eau pour une date, un code Sandre et une grandeur spécifiques.

**Paramètres**
- `date_a_filtrer` : La date qui servira de filtre au format YYYY-MM
- `code_sandre` : Le code Sandre correspondant à la liste de stations à extraire
- `path_file_to_clean` : Chemin vers le fichier CSV à nettoyer (optionnel)
- `grandeur_a_filtrer` : Une grandeur à filtrer, utile uniquement pour les données historiques
- `fichier_station_hubeau` : Le nom du fichier des stations à utiliser

**Retourne**
- `pd.DataFrame` : DataFrame nettoyé contenant uniquement les données pertinentes

**Exemple**
```python
from src.processing.clean import clean_hubeau_data

# Nettoyer les données pour juin 2026 et code Sandre BSH001
df_clean = clean_hubeau_data(
    date_a_filtrer="2026-06",
    code_sandre="BSH001",
    grandeur_a_filtrer="QmM"
)
print(f"Données nettoyées : {len(df_clean)} enregistrements")
```

**Processus de nettoyage**
1. Chargement des données depuis le fichier spécifié ou téléchargement
2. Filtrage pour garder uniquement les enregistrements du mois spécifié
3. Récupération des stations correspondant au code Sandre
4. Filtrage pour garder uniquement les stations du code Sandre
5. Suppression des doublons sur (code_station, date_obs_elab)

---

### `clean_single_month(annee_mois: str, code_sandre: str, grandeur: str)`

Nettoie un fichier contenant un seul mois de données. Télécharge les données si nécessaire.

**Paramètres**
- `annee_mois` : Année et mois au format AAAA-MM
- `code_sandre` : Code Sandre à extraire
- `grandeur` : La grandeur à récupérer (ex: "QmM", "QmnJ")

**Exemple**
```python
from src.processing.clean import clean_single_month

# Nettoyer les données QmM pour juin 2026
clean_single_month(
    annee_mois="2026-06",
    code_sandre="BSH001", 
    grandeur="QmM"
)
```

**Détails**
- Utilise `download_Hubeau.ensure_grandeur_mensuel_downloaded()` pour s'assurer que les données sont téléchargées
- Sauvegarde le résultat dans `output/hubeau/cleaned_data/clean-{grandeur}-{code_sandre}-{annee_mois}.csv`

---

### `clean_historic_data(code_sandre: str, grandeur: str)`

Nettoie les données historiques de 1991 à 2020.

**Paramètres**
- `code_sandre` : Filtre les données avec les stations associées à code_sandre
- `grandeur` : Filtre la grandeur souhaitée

**Exemple**
```python
from src.processing.clean import clean_historic_data

# Nettoyer toutes les données historiques QmM pour BSH001
clean_historic_data(
    code_sandre="BSH001",
    grandeur="QmM"
)
```

**Détails**
- Traite chaque mois de 1991 à 2020 (ou 1990-12 à 2020 pour QmnJ)
- Utilise tqdm pour afficher une barre de progression
- Sauvegarde chaque mois nettoyé individuellement

---

### `ensure_single_month_cleaned(annee_mois: str, code_reseau_sandre: str, grandeur: str)`

S'assure que les données du mois sont à jour et qu'elles ont été nettoyées et synchronisées avec les données brutes.

**Paramètres**
- `annee_mois` : AAAA-MM
- `code_reseau_sandre` : Code du réseau Sandre qui est nettoyé
- `grandeur` : La grandeur à nettoyer

**Exemple**
```python
from src.processing.clean import ensure_single_month_cleaned

# S'assurer que les données de juin 2026 sont nettoyées et à jour
ensure_single_month_cleaned(
    annee_mois="2026-06",
    code_reseau_sandre="BSH001",
    grandeur="QmM"
)
```

**Détails**
- Vérifie que le fichier nettoyé existe et est plus récent que les sources
- Si ce n'est pas le cas, lance `clean_single_month()`
- Utilise `utils_file.is_res_updated_with_source()` pour la vérification

---

### `ensure_historic_cleaned(code_reseau_sandre: str, grandeur: str)`

S'assure que les données historiques sont à jour et qu'elles ont été nettoyées et synchronisées avec les données brutes.

**Paramètres**
- `code_reseau_sandre` : Code du réseau Sandre qui est nettoyé
- `grandeur` : La grandeur à nettoyer

**Exemple**
```python
from src.processing.clean import ensure_historic_cleaned

# S'assurer que toutes les données historiques QmM sont nettoyées et à jour
ensure_historic_cleaned(
    code_reseau_sandre="BSH001",
    grandeur="QmM"
)
```

**Détails**
- Utilise `@cache` pour optimiser les performances
- Vérifie chaque mois individuellement
- Lance `clean_historic_data()` si nécessaire

---

## 🔧 Exemple Complet : Nettoyage de Données

### Nettoyer et préparer les données pour une analyse complète

```python
from src.processing.clean import ensure_single_month_cleaned, ensure_historic_cleaned
from src.model.enums import GeographicScaleClip

# 1. S'assurer que les données historiques sont nettoyées
print("Nettoyage des données historiques...")
ensure_historic_cleaned("BSH001", "QmM")

# 2. Nettoyer les données du mois actuel
print("Nettoyage des données du mois actuel...")
ensure_single_month_cleaned("2026-06", "BSH001", "QmM")

# 3. Nettoyer également les données QmnJ pour les analyses VCN3
ensure_historic_cleaned("BSH001", "QmnJ")
ensure_single_month_cleaned("2026-06", "BSH001", "QmnJ")

print("Nettoyage terminé !")
```

---

## 📁 Fichiers de Sortie

Les fonctions de nettoyage génèrent les fichiers suivants :

```
output/
└── hubeau/
    └── cleaned_data/
        ├── clean-QmM-BSH001-1991-01.csv          # Données nettoyées QmM
        ├── clean-QmM-BSH001-1991-02.csv
        ├── ...
        ├── clean-QmM-BSH001-2026-06.csv
        ├── clean-QmnJ-BSH001-1990-12.csv         # Données nettoyées QmnJ
        ├── clean-QmnJ-BSH001-1991-01.csv
        └── ...
```

---

## 🎯 Bonnes Pratiques

### 1. Toujours vérifier avant de nettoyer

```python
import src.utils.utils_file as utils_file
from src.utils.utils import get_paths_source_mensuel

# Vérifier si le nettoyage est nécessaire
chemin_source = get_paths_source_mensuel("QmM", "2026-06")
chemin_resultat = utils.get_path_clean_csv("BSH001", "2026-06", "QmM")

if not utils_file.is_res_updated_with_source(chemin_source, chemin_resultat):
    # Nettoyage nécessaire
    ensure_single_month_cleaned("2026-06", "BSH001", "QmM")
```

### 2. Utiliser le cache pour les données historiques

```python
# Le cache évite de recharger les données plusieurs fois
from src.processing.clean import get_grandeur_historique_df

# Première appel : charge les données
df1 = get_grandeur_historique_df("QmM")

# Deuxième appel : utilise le cache, plus rapide
df2 = get_grandeur_historique_df("QmM")

# df1 et df2 sont la même référence en mémoire
```

### 3. Nettoyage par lots

```python
from src.processing.clean import ensure_historic_cleaned
from tqdm import tqdm

# Nettoyer plusieurs codes Sandre
codes_sandre = ["BSH001", "BSH002", "custom"]
grandeurs = ["QmM", "QmnJ"]

for code in codes_sandre:
    for grandeur in grandeurs:
        print(f"Nettoyage {grandeur} pour {code}...")
        ensure_historic_cleaned(code, grandeur)
```

---

## 🔍 Dépannage

### Problème : Les données ne sont pas nettoyées

**Cause possible** : Les données sources n'existent pas

**Solution** : Vérifier que les données brutes existent
```python
from src.utils.utils import get_path_mensuel_raw_csv

chemin = get_path_mensuel_raw_csv("2026-06", "QmM")
print(f"Fichier existe : {chemin.exists()}")
```

### Problème : Doublons dans les données

**Cause possible** : Problème lors du filtrage

**Solution** : Vérifier la fonction `clean_hubeau_data`
```python
# Vérifier les doublons dans le résultat
df = clean_hubeau_data("2026-06", "BSH001", grandeur_a_filtrer="QmM")
doublons = df.duplicated(subset=["code_station", "date_obs_elab"])
print(f"Nombre de doublons : {doublons.sum()}")
```

---

## 📚 Liens Utiles

- [Documentation du Module Processing](index.md)
- [Module IO](../io/index.md) - Pour le téléchargement des données
- [Module Plotting](../plotting/index.md) - Pour la visualisation
- [Concepts Clés](../../concepts/index.md)
- [Utilisation CLI](../../usage/cli.md)

---

*Dernière mise à jour : {{ "now" | date: "%d %B %Y" }}*


