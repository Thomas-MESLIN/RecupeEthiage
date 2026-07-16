---
layout: default
title: utils_file.py
description: "Documentation API de la gestion des fichiers et vérification de fraîcheur"
nav_order: 2
parent: Module Utils
grand_parent: Modules
---

# 📁 utils_file.py

**Gestion des fichiers et vérification de fraîcheur des données**

Ce module fournit des fonctions pour vérifier l'âge des fichiers, comparer les dates de modification et déterminer si les données doivent être mises à jour. Il est essentiel pour maintenir la cohérence entre les données sources et les résultats calculés.

---

## 🎯 Fonctionnalités Principales

- **Vérification d'âge** : Déterminer si un fichier est trop vieux pour être utilisé
- **Comparaison de dates** : Vérifier que les résultats sont à jour par rapport aux sources
- **Promptes utilisateur** : Interface interactive pour la mise à jour des fichiers
- **Cache des réponses** : Éviter de redemander à l'utilisateur pour les mêmes questions

---

## 📋 Fonctions Disponibles

### `is_path_valid_age(chemin: Path) -> bool`

Vérifie si un fichier est assez récent (moins d'un an).

**Paramètres**
- `chemin` : Un chemin sous forme de Path pointant vers un fichier

**Retourne**
- `bool` : True si le fichier est récent (< 1 an), False sinon

**Lève**
- `FileNotFoundError` : Si le fichier n'existe pas

**Exemple**
```python
from pathlib import Path
from src.utils.utils_file import is_path_valid_age

# Vérifier si un fichier est récent
fichier_recent = Path("output/clean-QmM-BSH001-2026-06.csv")
fichier_vieux = Path("output/clean-QmM-BSH001-2023-06.csv")

try:
    print(f"Fichier récent valide : {is_path_valid_age(fichier_recent)}")
    print(f"Fichier vieux valide : {is_path_valid_age(fichier_vieux)}")
except FileNotFoundError as e:
    print(f"Fichier introuvable : {e}")
```

**Détails**
- Un fichier est considéré comme récent s'il a été modifié il y a moins de 360 jours
- La date de référence est la date actuelle au moment de l'appel
- Si le fichier n'existe pas, lève une exception `FileNotFoundError`

---

### `prompt_renew_old_data(chemin: Path) -> bool`

Demande à l'utilisateur s'il souhaite renouveler un fichier qui est trop vieux.

**Paramètres**
- `chemin` : Un chemin sous forme de Path pointant vers un fichier à potentiellement renouveler

**Retourne**
- `bool` : True si l'utilisateur accepte de renouveler le fichier, False sinon

**Exemple**
```python
from pathlib import Path
from src.utils.utils_file import prompt_renew_old_data

# Demander à l'utilisateur de renouveler un fichier
fichier_vieux = Path("output/clean-QmM-BSH001-2023-06.csv")

if prompt_renew_old_data(fichier_vieux):
    print("L'utilisateur souhaite renouveler le fichier")
else:
    print("L'utilisateur ne souhaite pas renouveler le fichier")
```

**Détails**
- Si la réponse "renouveler tous" a déjà été donnée, retourne True sans poser la question
- Si la réponse "ne rien renouveler" a déjà été donnée, retourne False sans poser la question
- Propose trois options à l'utilisateur :
  - 0 : Ne rien renouveler
  - 1 : Renouveler uniquement ce fichier
  - 2 : Renouveler tous les fichiers trop vieux
- Met en cache la réponse pour éviter de redemander

**Exemple de dialogue**
```
Le fichier : clean-QmM-BSH001-2023-06.csv est vieux de plus d'un an, souhaitez vous : 
Ne rien renouveler ? (0)
renouveler uniquement ce fichier ? (1)
renouveler tous les fichiers trop vieux ? (2)
Entrez votre réponse (0,1 ou 2) -> 
```

---

### `is_file_need_download(chemin: Path) -> bool`

Vérifie si un fichier doit être téléchargé (n'existe pas ou est trop vieux).

**Paramètres**
- `chemin` : Le chemin du fichier à vérifier

**Retourne**
- `bool` : True si le fichier doit être téléchargé, False sinon

**Exemple**
```python
from pathlib import Path
from src.utils.utils_file import is_file_need_download

# Vérifier si un fichier doit être téléchargé
fichier_existant = Path("output/clean-QmM-BSH001-2026-06.csv")
fichier_manquant = Path("output/clean-QmM-BSH001-2026-07.csv")

print(f"Fichier existant à télécharger : {is_file_need_download(fichier_existant)}")
print(f"Fichier manquant à télécharger : {is_file_need_download(fichier_manquant)}")
```

**Détails**
- Retourne True si :
  - Le fichier n'existe pas, OU
  - Le fichier existe mais est trop vieux (> 1 an), ET l'utilisateur accepte de le renouveler
- Utilise `is_path_valid_age()` pour vérifier l'âge
- Utilise `prompt_renew_old_data()` pour demander à l'utilisateur
- Affiche des informations de journalisation sur le processus

---

### `is_res_updated_with_source(chemin_source_list: list[Path], chemin_resultat: Path) -> bool`

Compare la date de modification du fichier de résultat et des fichiers sources. Vérifie que le fichier de résultat est plus récent que tous les fichiers sources.

**Paramètres**
- `chemin_source_list` : Une liste de fichiers qui servent à construire le résultat
- `chemin_resultat` : Le fichier résultat basé sur les fichiers sources

**Retourne**
- `bool` : True si le fichier résultat est plus récent que tous les fichiers sources, False sinon

**Exemple**
```python
from pathlib import Path
from src.utils.utils_file import is_res_updated_with_source
from src.utils.utils import get_paths_source_mensuel, get_path_clean_csv

# Vérifier si les données nettoyées sont à jour par rapport aux sources
sources = get_paths_source_mensuel("QmM", "2026-06")
resultat = get_path_clean_csv("BSH001", "2026-06", "QmM")

if is_res_updated_with_source(sources, resultat):
    print("Les données nettoyées sont à jour")
else:
    print("Les données nettoyées doivent être mises à jour")
```

**Détails**
- Si le fichier résultat n'existe pas, retourne False
- Si un fichier source n'existe pas, retourne False
- Compare la date de modification de chaque fichier source avec celle du fichier résultat
- Retourne False si un fichier source est plus récent que le fichier résultat
- Retourne True uniquement si le fichier résultat est plus récent que tous les fichiers sources

---

## 🔧 Exemple Complet : Vérification et Mise à Jour

### Vérifier et mettre à jour les données si nécessaire

```python
from pathlib import Path
from src.utils.utils_file import is_res_updated_with_source, is_file_need_download
from src.utils.utils import get_paths_source_mensuel, get_path_clean_csv
from src.io.download_Hubeau import ensure_grandeur_mensuel_downloaded
from src.processing.clean import clean_single_month

# Configuration
code_sandre = "BSH001"
annee_mois = "2026-06"
grandeur = "QmM"

# 1. Vérifier que les sources existent et sont fraîches
print("Vérification des sources...")
sources = get_paths_source_mensuel(grandeur, annee_mois)
for source in sources:
    if is_file_need_download(source):
        print(f"Source à télécharger : {source.name}")
        # Télécharger la source si nécessaire
        if "observations" in str(source):
            ensure_grandeur_mensuel_downloaded(annee_mois, grandeur)

# 2. Vérifier que le résultat est à jour
resultat = get_path_clean_csv(code_sandre, annee_mois, grandeur)
if not is_res_updated_with_source(sources, resultat):
    print("Les données doivent être mises à jour...")
    clean_single_month(annee_mois, code_sandre, grandeur)
    print("Mise à jour terminée !")
else:
    print("Les données sont déjà à jour.")
```

---

## 🎯 Bonnes Pratiques

### 1. Toujours vérifier avant de recalculer

```python
from src.utils.utils_file import is_res_updated_with_source
from src.utils.utils import get_paths_source_mensuel, get_path_clean_csv

# ✅ Bon - Vérification systématique
sources = get_paths_source_mensuel("QmM", "2026-06")
resultat = get_path_clean_csv("BSH001", "2026-06", "QmM")

if not is_res_updated_with_source(sources, resultat):
    recalculer_donnees()
```

### 2. Gérer les exceptions pour les fichiers manquants

```python
from src.utils.utils_file import is_path_valid_age
from pathlib import Path

# ✅ Bon - Gestion des exceptions
fichier = Path("output/clean-QmM-BSH001-2026-06.csv")
try:
    if is_path_valid_age(fichier):
        print("Fichier récent")
    else:
        print("Fichier trop vieux")
except FileNotFoundError:
    print("Fichier introuvable, doit être téléchargé")
```

### 3. Utiliser le cache des réponses utilisateur

```python
from src.utils.utils_file import prompt_renew_old_data

# ✅ Bon - Le cache évite de redemander à l'utilisateur
# Premier appel : demande à l'utilisateur
reponse1 = prompt_renew_old_data(Path("fichier1.csv"))

# Si l'utilisateur a choisi "renouveler tout", les appels suivants retournent True
reponse2 = prompt_renew_old_data(Path("fichier2.csv"))  # Pas de question, retourne True
reponse3 = prompt_renew_old_data(Path("fichier3.csv"))  # Pas de question, retourne True
```

### 4. Vérification complète avant traitement

```python
from src.utils.utils_file import is_res_updated_with_source, is_file_need_download
from src.utils.utils import get_paths_source_mensuel, get_path_clean_csv

def ensure_data_updated(code_sandre, annee_mois, grandeur):
    """S'assure que les données sont à jour avant de les utiliser."""
    # Vérifier les sources
    sources = get_paths_source_mensuel(grandeur, annee_mois)
    for source in sources:
        if is_file_need_download(source):
            return False  # Il manque des sources
    
    # Vérifier le résultat
    resultat = get_path_clean_csv(code_sandre, annee_mois, grandeur)
    return is_res_updated_with_source(sources, resultat)

# Utilisation
if ensure_data_updated("BSH001", "2026-06", "QmM"):
    print("Données prêtes à être utilisées")
else:
    print("Données doivent être mises à jour")
```

---

## 🔍 Dépannage

### Problème : Les fichiers sont toujours considérés comme trop vieux

**Cause possible** : Problème avec la détection de l'âge des fichiers

**Solution** : Vérifier manuellement la date de modification
```python
from pathlib import Path
import os
from datetime import datetime, timedelta

fichier = Path("output/clean-QmM-BSH001-2026-06.csv")
if fichier.exists():
    mtime = fichier.stat().st_mtime
    mod_date = datetime.fromtimestamp(mtime)
    current_date = datetime.now()
    age = current_date - mod_date
    print(f"Âge du fichier : {age.days} jours")
```

### Problème : La comparaison des sources ne fonctionne pas

**Cause possible** : Les fichiers sources n'existent pas ou le chemin est incorrect

**Solution** : Vérifier chaque fichier source individuellement
```python
from src.utils.utils import get_paths_source_mensuel

sources = get_paths_source_mensuel("QmM", "2026-06")
for source in sources:
    print(f"Source : {source}")
    print(f"  Existe : {source.exists()}")
    if source.exists():
        print(f"  Date modif : {source.stat().st_mtime}")
```

### Problème : Le prompt ne s'affiche pas

**Cause possible** : Le cache des réponses a déjà été défini

**Solution** : Réinitialiser le cache ou utiliser une nouvelle session
```python
# Forcer la réinitialisation du cache
from src.utils import utils_file
utils_file._cache_prompt = {}  # Réinitialiser le cache

# Maintenant le prompt s'affichera
from src.utils.utils_file import prompt_renew_old_data
prompt_renew_old_data(Path("fichier.csv"))
```

---

## 📚 Liens Utiles

- [Documentation du Module Utils](index.md)
- [Documentation utils.py](utils.md)
- [Documentation utils_proxy.py](utils_proxy.md)
- [Module Processing](../../processing/index.md)
- [Concepts Clés](../../../concepts/index.md)

---

*Dernière mise à jour : {{ "now" | date: "%d %B %Y" }}*