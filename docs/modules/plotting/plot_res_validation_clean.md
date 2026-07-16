---
layout: default
title: plot_res_validation_clean
description: "Documentation API du module plot_res_validation_clean - Validation des données"
nav_order: 5
parent: Module Plotting
grand_parent: Modules
---

# 🔍 plot_res_validation_clean

**Documentation API complète**

> **Fichier** : `src/plotting/plot_res_validation_clean.py`
> **Module** : Validation et comparaison des sources de données
> **Auteur** : Thomas Meslin
> **Dernière mise à jour** : Juin 2026

---

## 📋 Table des Matières

- [🎯 Aperçu](#-aperçu)
- [📦 Dépendances](#-dépendances)
- [🔧 Fonctions](#-fonctions)
  - [Fonctions principales (sans signature explicite)](#fonctions-principales-sans-signature-explicite)
- [🎓 Tutoriel](#-tutoriel)
- [📊 Exemples Complets](#-exemples-complets)

---

## 🎯 Aperçu

Ce module est dédié à la **validation et comparaison des données** entre différentes sources, notamment entre **Hub'Eau** et **Hydroportail**. Il permet de :

- ✅ **Comparer les stations** disponibles dans chaque source
- ✅ **Visualiser les différences** de couverture temporelle
- ✅ **Identifier les écarts** entre les deux bases de données

### Contexte

L'outil peut récupérer des données hydrologiques depuis deux sources principales :
1. **Hub'Eau** : API officielle du ministère
2. **Hydroportail** : Autre source de données

Ce module permet de vérifier la cohérence entre ces deux sources.

---

## 📦 Dépendances

### Dépendances externes

```python
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
```

### Dépendances internes

```python
from src.config.paths import OUTPUT_DIR
```

---

## 🔧 Fonctions

---

### Fonctions principales (sans signature explicite)

Le fichier `plot_res_validation_clean.py` ne définit pas de fonctions avec des signatures formelles, mais contient un **script d'analyse** qui se lance directement. Voici les composants principaux :

#### 1. Chargement des données

```python
# Exemple : chargement du CSV de validation
df = pd.read_csv(OUTPUT_DIR / "res-validation" / "diff_hydro_hubeau_clean.csv")

# Conversion de la colonne date
df["annee_mois"] = pd.to_datetime(df["annee_mois"], format="%Y-%m")
```

**Fichier source attendu** :
- `output/res-validation/diff_hydro_hubeau_clean.csv`

**Colonnes attendues** :
- `annee_mois` : Date au format AAAA-MM
- `code_sandre` : Code du réseau SANDRE
- `station_uniquement_hubeau` : Nombre de stations uniquement dans Hub'Eau
- `total_station_hubeau` : Nombre total de stations dans Hub'Eau
- `station_uniquement_hydroportail` : Nombre de stations uniquement dans Hydroportail
- `total_station_hydroportail` : Nombre total de stations dans Hydroportail

#### 2. Fonction `do_plot_hubeau_hydroportail`

**Génère des graphiques comparant Hub'Eau et Hydroportail.**

##### 📌 Signature implicite

```python
def do_plot_hubeau_hydroportail(
    col_hubeau: str,
    col_hydroportail: str,
    titre: str
) -> None
```

##### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `col_hubeau` | `str` | Nom de la colonne Hub'Eau | ✅ |
| `col_hydroportail` | `str` | Nom de la colonne Hydroportail | ✅ |
| `titre` | `str` | Titre du graphique | ✅ |

##### 📤 Retourne

`None` - Les graphiques sont affichés (pas enregistrés).

##### 📊 Comportement

1. **Groupement par code SANDRE** :
   ```python
   for code, group in df.groupby("code_sandre"):
   ```

2. **Tri par date** :
   ```python
   group = group.sort_values("annee_mois")
   ```

3. **Création du graphique** :
   - Une figure par code SANDRE
   - Taille : 12x5 pouces
   - Deux courbes : une pour Hub'Eau, une pour Hydroportail
   - Ligne pointillée avec marqueurs
   - Titre personnalisé avec le code
   - Labels des axes
   - Grille activée

4. **Ajustement de l'axe Y** :
   ```python
   xmin, xmax, ymin, ymax = plt.axis()
   plt.axis((xmin, xmax, 0, ymax))  # Force Y à commencer à 0
   ```

##### 🎯 Exemple d'utilisation interne

```python
# Dans le fichier, appelé directement :
do_plot_hubeau_hydroportail(
    "station_uniquement_hubeau",
    "station_uniquement_hydroportail",
    "Stations uniquement dans Hubeau ou hydroportail, contenant de la donnée, par mois, de la liste "
)

do_plot_hubeau_hydroportail(
    "total_station_hubeau",
    "total_station_hydroportail",
    "Nombre total de station dans Hubeau ou hydroportail, contenant de la donnée, par mois, de la liste "
)
```

---

#### 3. Graphiques individuels par colonne

**Boucle principale du script** :

```python
# Colonnes numériques à tracer
colonnes_a_plot = [
    "station_uniquement_hubeau",
    "total_station_hubeau",
    "station_uniquement_hydroportail",
    "total_station_hydroportail",
]

# Un graphique par colonne
for col in colonnes_a_plot:
    plt.figure(figsize=(12, 5))
    
    # Si plusieurs code_sandre, on trace une courbe par code
    for code, group in df.groupby("code_sandre"):
        group = group.sort_values("annee_mois")
        
        label = code if code != "" else "GLOBAL"
        
        plt.plot(
            group["annee_mois"],
            group[col],
            marker="o",
            label=label
        )
    
    plt.title(col)
    plt.xlabel("Date")
    plt.ylabel(col)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    xmin, xmax, ymin, ymax = plt.axis()
    plt.axis((xmin, xmax, 0, ymax))
    plt.show()
```

**Comportement** :
- Une courbe par code SANDRE
- Chaque code a une couleur distincte
- Légende avec les codes
- Axe Y forcé à commencer à 0
- Affichage immédiat avec `plt.show()`

---

## 📊 Structure des Données

### Fichier source

**Chemin** : `output/res-validation/diff_hydro_hubeau_clean.csv`

**Format** : CSV avec les colonnes :

| Colonne | Type | Description |
|---------|------|-------------|
| `annee_mois` | datetime | Date (AAAA-MM) |
| `code_sandre` | str | Code du réseau SANDRE |
| `station_uniquement_hubeau` | int | Stations uniquement dans Hub'Eau |
| `total_station_hubeau` | int | Total des stations dans Hub'Eau |
| `station_uniquement_hydroportail` | int | Stations uniquement dans Hydroportail |
| `total_station_hydroportail` | int | Total des stations dans Hydroportail |

---

## 🎓 Tutoriel : Valider les Données

### Étape 1 : Préparer les données de validation

Avant d'utiliser ce module, vous devez générer le fichier de comparaison :

```python
# Ce fichier devrait être généré par un script de traitement
# Exemple de structure attendue :

import pandas as pd
from pathlib import Path

# Créer un DataFrame de test
data = {
    "annee_mois": ["2025-01", "2025-02", "2025-03", "2025-04"] * 2,
    "code_sandre": ["BSH001"] * 4 + ["BSH002"] * 4,
    "station_uniquement_hubeau": [10, 12, 8, 15, 5, 7, 6, 8],
    "total_station_hubeau": [50, 52, 48, 55, 45, 47, 46, 48],
    "station_uniquement_hydroportail": [5, 3, 8, 2, 10, 8, 9, 11],
    "total_station_hydroportail": [45, 43, 48, 42, 50, 48, 49, 51],
}

df_validation = pd.DataFrame(data)

# Sauvegarder au bon endroit
output_dir = Path("output/res-validation")
output_dir.mkdir(parents=True, exist_ok=True)
df_validation.to_csv(output_dir / "diff_hydro_hubeau_clean.csv", index=False)

print("✅ Fichier de validation créé !")
```

### Étape 2 : Exécuter la validation

```python
# Exécuter le script de validation
# Le script se lance automatiquement lors de l'import
import src.plotting.plot_res_validation_clean as validation

# Ou exécuter directement :
# python -c "import src.plotting.plot_res_validation_clean"
```

**Résultat** :
- Plusieurs fenêtres de graphiques s'affichent
- Chaque graphique montre l'évolution des indicateurs pour chaque code SANDRE

### Étape 3 : Analyser les résultats

Les graphiques générés permettent de :

1. **Identifier les écarts** : Comparer les nombres de stations entre les deux sources
2. **Vérifier la couverture temporelle** : Voir si une source a plus de données pour certaines périodes
3. **Détecter les incohérences** : Repérer les différences importantes entre Hub'Eau et Hydroportail

---

## 📊 Exemples Complets

### Exemple 1 : Comparaison simple

```python
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from src.config.paths import OUTPUT_DIR

# Charger les données
df = pd.read_csv(OUTPUT_DIR / "res-validation" / "diff_hydro_hubeau_clean.csv")
df["annee_mois"] = pd.to_datetime(df["annee_mois"], format="%Y-%m")

# Comparaison pour un code SANDRE spécifique
code = "BSH001"
group = df[df["code_sandre"] == code].sort_values("annee_mois")

plt.figure(figsize=(12, 6))

plt.plot(
    group["annee_mois"],
    group["total_station_hubeau"],
    marker="o",
    label="Hub'Eau",
    linewidth=2
)

plt.plot(
    group["annee_mois"],
    group["total_station_hydroportail"],
    marker="s",
    label="Hydroportail",
    linewidth=2
)

plt.title(f"Comparaison Hub'Eau vs Hydroportail - {code}")
plt.xlabel("Date")
plt.ylabel("Nombre de stations")
plt.grid(True)
plt.legend()
plt.tight_layout()

xmin, xmax, ymin, ymax = plt.axis()
plt.axis((xmin, xmax, 0, ymax))

plt.savefig(OUTPUT_DIR / "res-validation" / "comparaison_hubeau_hydroportail.png")
plt.close()

print("✅ Graphique de comparaison généré !")
```

### Exemple 2 : Analyse des différences

```python
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from src.config.paths import OUTPUT_DIR

# Charger les données
df = pd.read_csv(OUTPUT_DIR / "res-validation" / "diff_hydro_hubeau_clean.csv")
df["annee_mois"] = pd.to_datetime(df["annee_mois"], format="%Y-%m")

# Calculer les différences
df["diff_uniquement"] = df["station_uniquement_hubeau"] - df["station_uniquement_hydroportail"]
df["diff_total"] = df["total_station_hubeau"] - df["total_station_hydroportail"]

# Graphique des différences
plt.figure(figsize=(12, 6))

for code, group in df.groupby("code_sandre"):
    group = group.sort_values("annee_mois")
    label = code if code != "" else "GLOBAL"
    
    plt.plot(
        group["annee_mois"],
        group["diff_total"],
        marker="o",
        label=f"{label} (Hub'Eau - Hydroportail)"
    )

plt.title("Différence du nombre total de stations entre Hub'Eau et Hydroportail")
plt.xlabel("Date")
plt.ylabel("Différence (Hub'Eau - Hydroportail)")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.axhline(0, color='gray', linestyle='--', linewidth=1, label="Égalité")
plt.legend()

plt.savefig(OUTPUT_DIR / "res-validation" / "difference_hubeau_hydroportail.png")
plt.close()

print("✅ Graphique des différences généré !")
```

### Exemple 3 : Statistiques récapitulatives

```python
import pandas as pd
from pathlib import Path
from src.config.paths import OUTPUT_DIR

# Charger les données
df = pd.read_csv(OUTPUT_DIR / "res-validation" / "diff_hydro_hubeau_clean.csv")

# Statistiques globales
total_hubeau = df["total_station_hubeau"].sum()
total_hydroportail = df["total_station_hydroportail"].sum()
uniquement_hubeau = df["station_uniquement_hubeau"].sum()
uniquement_hydroportail = df["station_uniquement_hydroportail"].sum()

print("=" * 60)
print("STATISTIQUES DE VALIDATION")
print("=" * 60)
print(f"Total stations Hub'Eau : {total_hubeau}")
print(f"Total stations Hydroportail : {total_hydroportail}")
print(f"Stations uniquement Hub'Eau : {uniquement_hubeau}")
print(f"Stations uniquement Hydroportail : {uniquement_hydroportail}")
print(f"Écart total : {total_hubeau - total_hydroportail}")
print("=" * 60)

# Statistiques par code SANDRE
print("\nSTATISTIQUES PAR CODE SANDRE :")
for code, group in df.groupby("code_sandre"):
    if code == "":
        label = "GLOBAL"
    else:
        label = code
    
    print(f"\n{label}:")
    print(f"  - Hub'Eau : {group['total_station_hubeau'].sum()}")
    print(f"  - Hydroportail : {group['total_station_hydroportail'].sum()}")
    print(f"  - Différence : {group['total_station_hubeau'].sum() - group['total_station_hydroportail'].sum()}")
```

---

## 📚 Voir aussi

- [Module plotting](index.md) - Aperçu du module
- [plot_grandeur](plot_grandeur.md) - Données hydrologiques
- [plot_meteoFrance](plot_meteoFrance.md) - Données météorologiques
- [plot_onde](plot_onde.md) - Données ONDE
- [Concepts : Données hydrologiques](../../../concepts/index.md)

---

## 🎯 Résumé des Capacités

| Fonctionnalité | Description | Sortie |
|---------------|-------------|--------|
| Comparaison par colonne | Trace l'évolution d'une colonne pour chaque code | Graphique |
| Comparaison Hub'Eau vs Hydroportail | Compare deux colonnes entre les deux sources | Graphique |
| Analyse des différences | Calcule et visualise les écarts | Graphique |
| Statistiques | Génère des statistiques récapitulatives | Console |

---

## ⚠️ Limitations

1. **Pas de signature formelle** : Les fonctions ne sont pas définies avec des signatures claires
2. **Affichage seulement** : Les graphiques sont affichés, pas enregistrés automatiquement
3. **Dépendance au fichier** : Nécessite un fichier CSV spécifique au bon format
4. **Pas de flexibilité** : Les colonnes et chemins sont codés en dur

---

## 💡 Améliorations Possibles

Pour améliorer ce module, vous pourriez :

1. **Ajouter des signatures formelles** : Définir des fonctions avec des paramètres clairs
2. **Ajouter l'enregistrement automatique** : Sauvegarder les graphiques dans le dossier de sortie
3. **Rendre configurable** : Permettre de spécifier le fichier source et les colonnes
4. **Ajouter des tests** : Vérifier la validité des données avant de tracer

---

*Documentation générée automatiquement à partir du code source | Dernière mise à jour : {{ "now" | date: "%d %B %Y" }}*
