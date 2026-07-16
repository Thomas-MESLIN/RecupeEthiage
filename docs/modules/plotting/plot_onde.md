---
layout: default
title: plot_onde
description: "Documentation API du module plot_onde - Visualisation des données ONDE"
nav_order: 3
parent: Module Plotting
grand_parent: Modules
---

# 🌊 plot_onde

**Documentation API complète**

> **Fichier** : `src/plotting/plot_onde.py`
> **Module** : Visualisation des données ONDE (Observatoire National des Établissements)
> **Auteur** : Thomas Meslin
> **Dernière mise à jour** : Juin 2026

---

## 📋 Table des Matières

- [🎯 Aperçu](#-aperçu)
- [📦 Dépendances](#-dépendances)
- [🔧 Fonctions](#-fonctions)
  - [configure_matplotlib](#configure_matplotlib)
  - [save_and_close_plot](#save_and_close_plot)
  - [plot_evolution_assecs](#plot_evolution_assecs)
  - [plot_evolution_ecoulements](#plot_evolution_ecoulements)
  - [plot_everything](#plot_everything)
  - [get_titre_from_campagne_type](#get_titre_from_campagne_type)
- [🎓 Tutoriel](#-tutoriel)
- [📊 Exemples Complets](#-exemples-complets)

---

## 🎯 Aperçu

Ce module gère la **visualisation des données ONDE**, qui sont des observations de l'écoulement des cours d'eau en France. Il permet de :

- ✅ **Analyser l'évolution des assecs** (zones sans eau) sur plusieurs années
- ✅ **Visualiser la répartition des écoulements** par type (visible, faible, non-visible, assec)
- ✅ **Comparer les campagnes** (usuelles vs complémentaires)
- ✅ **Générer des graphiques par zone géographique**

### Domaines couverts

| Domaine | Description | Fonctions associées |
|---------|-------------|---------------------|
| **Assecs** | Évolution du nombre d'assecs par mois et année | `plot_evolution_assecs` |
| **Écoulements** | Répartition des types d'écoulement | `plot_evolution_ecoulements` |
| **Export complet** | Génération de tous les graphiques pour une zone | `plot_everything` |
| **Configuration** | Configuration des styles matplotlib | `configure_matplotlib` |

---

## 📦 Dépendances

### Dépendances externes

```python
import calendar
from datetime import datetime
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
```

### Dépendances internes

```python
from src.model.enums import GeographicScaleClip, OndeCampagneType
import src.processing.process_onde as process_onde
from src.config.styles import COULEUR_MOYENNE, ANNEE_COULEURS
from src.config.logging_config import setup_logger
from src.config.paths import OUTPUT_DIR
```

---

## 🔧 Fonctions

---

### `configure_matplotlib`

**Configure les paramètres par défaut de matplotlib pour les graphiques ONDE.**

#### 📌 Signature

```python
def configure_matplotlib() -> None
```

#### 📝 Paramètres

Aucun

#### 📤 Retourne

`None` - Configure matplotlib globalement.

#### 📊 Comportement

Définit les paramètres suivants :

```python
plt.rcParams.update({
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
})
```

#### ⚠️ Notes

- Ces paramètres s'appliquent à tous les graphiques générés après l'appel
- Réduit les bordures pour un rendu plus propre
- Ajoute une grille discrète

#### 🎯 Exemple

```python
from src.plotting.plot_onde import configure_matplotlib

# Configurer matplotlib avant de générer des graphiques
configure_matplotlib()

# Les graphiques suivants utiliseront ces paramètres
```

---

### `save_and_close_plot`

**Enregistre et ferme le graphique actuel.**

#### 📌 Signature

```python
def save_and_close_plot(output_path: Path | None) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `output_path` | `Path \| None` | Chemin pour enregistrer le graphique | ✅ |

#### 📤 Retourne

`None` - Le graphique est enregistré et fermé.

#### 📊 Comportement

1. Si `output_path` est fourni, enregistre le graphique avec `plt.savefig()`
2. Ferme le graphique avec `plt.close()`
3. Affiche un message de journalisation

#### ⚠️ Notes

- Le format par défaut est PNG
- Le DPI par défaut dépend de la configuration matplotlib

#### 🎯 Exemple

```python
from pathlib import Path
from src.plotting.plot_onde import save_and_close_plot
import matplotlib.pyplot as plt

plt.figure()
plt.plot([1, 2, 3], [4, 5, 6])

save_and_close_plot(Path("output/onde/test.png"))
```

---

### `plot_evolution_assecs`

**Génère un graphique de l'évolution du nombre d'assecs par mois et par année.**

#### 📌 Signature

```python
def plot_evolution_assecs(
    df: pd.DataFrame,
    date_depart: datetime,
    date_fin: datetime,
    annee_actuelle: int,
    campagne_type: OndeCampagneType,
    output_path: Path = None
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `df` | `pd.DataFrame` | DataFrame contenant les données ONDE | ✅ |
| `date_depart` | `datetime` | Date de début de la période d'analyse | ✅ |
| `date_fin` | `datetime` | Date de fin de la période d'analyse | ✅ |
| `annee_actuelle` | `int` | Année à mettre en évidence dans le graphique | ✅ |
| `campagne_type` | `OndeCampagneType` | Type de campagne (USUELLE, COMPLEMENTAIRE, ALL_CAMPAGNE) | ✅ |
| `output_path` | `Path \| None` | Chemin pour enregistrer le graphique | `None` |

#### 📤 Retourne

`None` - Le graphique est généré et éventuellement enregistré.

#### 📊 Comportement

1. **Filtrage des données** :
   - Filtre par la plage de dates
   - Garde uniquement les mois de mai à septembre (`MOIS_CIBLE = [5, 6, 7, 8, 9]`)
   - Filtre pour ne garder que les assecs (`libelle_ecoulement == "Assec"`)

2. **Agrégation** :
   - Compte le nombre d'assecs par année et par mois
   - Crée une table avec les années en lignes et les mois en colonnes

3. **Calcul de la moyenne** :
   - Calcule la moyenne sur toutes les années pour chaque mois

4. **Création du graphique** :
   - Trace une ligne par année
   - L'année actuelle est mise en évidence (épaisseur de ligne doublée)
   - La moyenne est tracée juste en dessous de l'année actuelle
   - Chaque année a une couleur distincte (depuis `ANNEE_COULEURS`)

5. **Style** :
   - Taille de la figure : 9x5 pouces
   - Noms des mois sur l'axe X
   - Légende à droite du graphique
   - Titre descriptif

#### 📄 Fichiers générés

- `{output_path}.png` (si `output_path` est fourni)

#### 🎯 Exemple

```python
from datetime import datetime
from pathlib import Path
from src.plotting.plot_onde import plot_evolution_assecs
from src.model.enums import OndeCampagneType
import pandas as pd

# Charger les données ONDE
df = pd.read_csv("output/hubeau/downloaded_data/onde/observation_onde_B06_20240501_20260630.csv")

plot_evolution_assecs(
    df=df,
    date_depart=datetime(2020, 5, 1),
    date_fin=datetime(2026, 9, 30),
    annee_actuelle=2026,
    campagne_type=OndeCampagneType.ALL_CAMPAGNE,
    output_path=Path("output/onde/BSH_2026-06/B/06/onde_evolution-assec_2026_A.png")
)
```

---

### `plot_evolution_ecoulements`

**Génère un graphique empilé de la répartition des écoulements par année.**

#### 📌 Signature

```python
def plot_evolution_ecoulements(
    df: pd.DataFrame,
    campagne_type: OndeCampagneType,
    mois_souhaite: int,
    nb_mesures: int | None = None,
    output_path: Path = None
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `df` | `pd.DataFrame` | DataFrame contenant les données ONDE | ✅ |
| `campagne_type` | `OndeCampagneType` | Type de campagne | ✅ |
| `mois_souhaite` | `int` | Mois à analyser (5-9) | ✅ |
| `nb_mesures` | `int \| None` | Nombre total de stations/mesures. Si None, calculé à partir du code_station | `None` |
| `output_path` | `Path \| None` | Chemin pour enregistrer le graphique | `None` |

#### 📤 Retourne

`None` - Le graphique est généré et éventuellement enregistré.

#### 📊 Comportement

1. **Filtrage des données** :
   - Garde uniquement le mois souhaité

2. **Comptage par type d'écoulement** :
   Pour chaque année et chaque code d'écoulement :
   - `1, 1a` : Écoulement visible acceptable
   - `1f` : Écoulement visible faible
   - `2` : Écoulement non visible
   - `3` : Assec

3. **Calcul des pourcentages** :
   - Convertit les comptes en pourcentages du total
   - Arrondit à 1 décimale

4. **Création du graphique empilé** :
   - Un bar par année
   - Chaque bar est divisée en segments colorés selon le type d'écoulement
   - Les couleurs sont définies dans `COULEURS`
   - Les pourcentages sont affichés dans chaque segment

5. **Ordre des catégories** (de bas en haut) :
   - Pas de données (gris)
   - Écoulement visible acceptable (bleu)
   - Écoulement visible faible (bleu clair)
   - Écoulement non visible (orange)
   - Assec (rouge)

#### 🎨 Palette de couleurs

```python
COULEURS = {
    "Pas de données": "#D9D9D9",
    "Ecoulement visible acceptable": "#1f77b4",
    "Ecoulement visible faible": "#5dade2",
    "Ecoulement non visible": "#f39c12",
    "Assec": "#d62728",
}
```

#### 📄 Fichiers générés

- `{output_path}.png` (si `output_path` est fourni)

#### 🎯 Exemple

```python
from pathlib import Path
from src.plotting.plot_onde import plot_evolution_ecoulements
from src.model.enums import OndeCampagneType
import pandas as pd

# Charger les données ONDE
df = pd.read_csv("output/hubeau/downloaded_data/onde/observation_onde_B06_20240501_20260630.csv")

plot_evolution_ecoulements(
    df=df,
    campagne_type=OndeCampagneType.ALL_CAMPAGNE,
    mois_souhaite=6,  # Juin
    nb_mesures=385,   # Nombre de stations dans le bassin 06
    output_path=Path("output/onde/BSH_2026-06/B/06/onde_evolution-ecoulement_2026-06_A.png")
)
```

---

### `get_titre_from_campagne_type`

**Retourne le titre descriptif pour un type de campagne ONDE.**

#### 📌 Signature

```python
def get_titre_from_campagne_type(campagne_type: OndeCampagneType) -> str
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `campagne_type` | `OndeCampagneType` | Type de campagne | ✅ |

#### 📤 Retourne

`str` - Titre descriptif

#### 📊 Correspondances

| Type | Titre |
|------|-------|
| `OndeCampagneType.COMPLEMENTAIRE` | `"Complémentaire"` |
| `OndeCampagneType.USUELLE` | `"Usuelle"` |
| `OndeCampagneType.ALL_CAMPAGNE` | `"Usuelle et Complémentaire"` |

#### 🎯 Exemple

```python
from src.plotting.plot_onde import get_titre_from_campagne_type
from src.model.enums import OndeCampagneType

titre = get_titre_from_campagne_type(OndeCampagneType.ALL_CAMPAGNE)
print(titre)  # "Usuelle et Complémentaire"
```

---

### `plot_everything`

**Génère tous les graphiques ONDE pour une configuration donnée.**

#### 📌 Signature

```python
def plot_everything(
    campagne_type: OndeCampagneType,
    annee_mois: datetime,
    geographic_scale: GeographicScaleClip,
    zone_code: str
) -> None
```

#### 📝 Paramètres

| Paramètre | Type | Description | Obligatoire |
|-----------|------|-------------|-------------|
| `campagne_type` | `OndeCampagneType` | Type de campagne ONDE | ✅ |
| `annee_mois` | `datetime` | Date de référence (année et mois) | ✅ |
| `geographic_scale` | `GeographicScaleClip` | Échelle géographique | ✅ |
| `zone_code` | `str` | Code de la zone géographique | ✅ |

#### 📤 Retourne

`None` - Les graphiques sont générés et enregistrés.

#### 📊 Comportement

1. **Validation** : Vérifie que `zone_code` n'est pas `None`
2. **Création du dossier** :
   ```
   output/onde/BSH_{annee_mois.strftime('%Y-%m')}/{geographic_scale[0]}{zone_code}/
   ```
3. **Chargement des données** : Appelle `process_onde.load_and_prepare_onde_data()`
4. **Génération des graphiques** :
   - **Évolution des assecs** : `plot_evolution_assecs()` avec une période de 4 ans
   - **Évolution des écoulements** : `plot_evolution_ecoulements()` pour le mois 6 (juin)

5. **Période d'analyse** :
   - Pour les assecs : du 1er mai il y a 4 ans au dernier jour du mois spécifié
   - Pour les écoulements : uniquement le mois spécifié

#### 📄 Fichiers générés

- `{dossier}/onde_evolution-assec_{annee}_{campagne_type}.png`
- `{dossier}/onde_evolution-ecoulement_{annee_mois.strftime('%Y-%m')}_{campagne_type}.png`

#### 🎯 Exemple

```python
from datetime import datetime
from src.plotting.plot_onde import plot_everything
from src.model.enums import OndeCampagneType, GeographicScaleClip

# Générer tous les graphiques pour la région 84 (Auvergne-Rhône-Alpes)
# Campagne usuelle, juin 2026
plot_everything(
    campagne_type=OndeCampagneType.USUELLE,
    annee_mois=datetime(2026, 6, 1),
    geographic_scale=GeographicScaleClip.REGION_ADMINISTRATIVE,
    zone_code="84"
)

# Résultat :
# - output/onde/BSH_2026-06/R84/onde_evolution-assec_2026_U.png
# - output/onde/BSH_2026-06/R84/onde_evolution-ecoulement_2026-06_U.png
```

---

## 🎓 Tutoriel : Analyser les Données ONDE

### Étape 1 : Importer les modules

```python
from datetime import datetime
from src.plotting.plot_onde import plot_everything
from src.model.enums import OndeCampagneType, GeographicScaleClip
```

### Étape 2 : Générer une analyse complète pour un bassin

```python
# Analyser les données ONDE pour le bassin Rhône-Méditerranée (06)
# Campagne : Toutes (usuelles + complémentaires)
# Mois : Juin 2026

plot_everything(
    campagne_type=OndeCampagneType.ALL_CAMPAGNE,
    annee_mois=datetime(2026, 6, 1),
    geographic_scale=GeographicScaleClip.BASSIN,
    zone_code="06"
)
```

**Résultats :**
```
output/onde/BSH_2026-06/B06/
├── onde_evolution-assec_2026_A.png
└── onde_evolution-ecoulement_2026-06_A.png
```

### Étape 3 : Analyser plusieurs zones

```python
# Liste des bassins à analyser
bassins = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]

for bassin in bassins:
    print(f"Analyse du bassin {bassin}...")
    plot_everything(
        campagne_type=OndeCampagneType.ALL_CAMPAGNE,
        annee_mois=datetime(2026, 6, 1),
        geographic_scale=GeographicScaleClip.BASSIN,
        zone_code=bassin
    )

print("✅ Analyse de tous les bassins terminée !")
```

### Étape 4 : Comparer les types de campagne

```python
from src.model.enums import OndeCampagneType

# Pour le bassin 06, comparer les trois types de campagne
for campagne in [OndeCampagneType.USUELLE, OndeCampagneType.COMPLEMENTAIRE, OndeCampagneType.ALL_CAMPAGNE]:
    print(f"Analyse campagne {campagne}...")
    plot_everything(
        campagne_type=campagne,
        annee_mois=datetime(2026, 6, 1),
        geographic_scale=GeographicScaleClip.BASSIN,
        zone_code="06"
    )

print("✅ Comparaison des campagnes terminée !")
```

---

## 📊 Exemples Complets

### Exemple 1 : Analyse mensuelle pour plusieurs mois

```python
from datetime import datetime
from src.plotting.plot_onde import plot_everything
from src.model.enums import OndeCampagneType, GeographicScaleClip
import calendar

# Analyser chaque mois de mai à septembre 2026
for mois in range(5, 10):  # 5=mai, 6=juin, 7=juillet, 8=août, 9=septembre
    # Créer une date pour le 1er du mois
    annee_mois = datetime(2026, mois, 1)
    
    # Nom du mois
    nom_mois = calendar.month_name[mois]
    print(f"Analyse du mois de {nom_mois} 2026...")
    
    plot_everything(
        campagne_type=OndeCampagneType.ALL_CAMPAGNE,
        annee_mois=annee_mois,
        geographic_scale=GeographicScaleClip.BASSIN,
        zone_code="06"
    )

print("✅ Analyse mensuelle terminée !")
```

### Exemple 2 : Analyse multi-échelles pour une zone

```python
from datetime import datetime
from src.plotting.plot_onde import plot_everything
from src.model.enums import OndeCampagneType, GeographicScaleClip

# Zone : Région Auvergne-Rhône-Alpes (84)
annee_mois = datetime(2026, 6, 1)

# Analyser à différentes échelles
echelles = [
    GeographicScaleClip.REGION_ADMINISTRATIVE,
    GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF,
]

for echelle in echelles:
    print(f"Analyse à l'échelle {echelle}...")
    plot_everything(
        campagne_type=OndeCampagneType.ALL_CAMPAGNE,
        annee_mois=annee_mois,
        geographic_scale=echelle,
        zone_code="84"
    )

print("✅ Analyse multi-échelles terminée !")
```

### Exemple 3 : Analyse historique sur plusieurs années

```python
from datetime import datetime
from src.plotting.plot_onde import plot_everything
from src.model.enums import OndeCampagneType, GeographicScaleClip

# Analyser juin pour chaque année de 2020 à 2026
for annee in range(2020, 2027):
    print(f"Analyse de juin {annee}...")
    plot_everything(
        campagne_type=OndeCampagneType.ALL_CAMPAGNE,
        annee_mois=datetime(annee, 6, 1),
        geographic_scale=GeographicScaleClip.BASSIN,
        zone_code="06"
    )

print("✅ Analyse historique terminée !")
```

### Exemple 4 : Graphique personnalisé des assecs

```python
from datetime import datetime
from pathlib import Path
from src.plotting.plot_onde import plot_evolution_assecs
from src.model.enums import OndeCampagneType
import src.processing.process_onde as process_onde

# Charger les données pour le bassin 06
df = process_onde.load_and_prepare_onde_data(
    OndeCampagneType.ALL_CAMPAGNE,
    datetime(2026, 6, 1),
    GeographicScaleClip.BASSIN,
    "06"
)

# Générer le graphique des assecs
plot_evolution_assecs(
    df=df,
    date_depart=datetime(2022, 5, 1),  # Depuis mai 2022
    date_fin=datetime(2026, 9, 30),   # Jusqu'à septembre 2026
    annee_actuelle=2026,
    campagne_type=OndeCampagneType.ALL_CAMPAGNE,
    output_path=Path("output/onde/custom/assecs_2022-2026.png")
)

print("✅ Graphique personnalisé des assecs généré !")
```

---

## 📚 Voir aussi

- [Module plotting](index.md) - Aperçu du module
- [plot_grandeur](plot_grandeur.md) - Données hydrologiques
- [plot_meteoFrance](plot_meteoFrance.md) - Données météorologiques
- [rasterize](rasterize.md) - Rasterisation
- [Concepts : ONDE](../../../concepts/onde.md)
- [Utilisation CLI](../../../usage/cli.md)

---

## 🎯 Résumé des Fonctions

| Fonction | Description | Sortie |
|----------|-------------|--------|
| `configure_matplotlib` | Configure les styles matplotlib | Aucune |
| `save_and_close_plot` | Enregistre et ferme le graphique | `.png` |
| `plot_evolution_assecs` | Graphique de l'évolution des assecs | `.png` |
| `plot_evolution_ecoulements` | Graphique empilé des écoulements | `.png` |
| `get_titre_from_campagne_type` | Retourne le titre d'une campagne | `str` |
| `plot_everything` | **Fonction principale** - Génère tous les graphiques | `.png` × 2 |

---

## 📊 Légende des Codes d'Écoulement

| Code | Libellé | Description |
|------|---------|-------------|
| 1 | Écoulement visible acceptable | Écoulement normal |
| 1a | Écoulement visible acceptable | Variante de 1 |
| 1f | Écoulement visible faible | Débit réduit mais visible |
| 2 | Écoulement non visible | Eau présente mais non visible en surface |
| 3 | Assec | Pas d'eau |

---

## 🎨 Palette de Couleurs

| Catégorie | Couleur |
|----------|---------|
| Pas de données | `#D9D9D9` (gris) |
| Écoulement visible acceptable | `#1f77b4` (bleu) |
| Écoulement visible faible | `#5dade2` (bleu clair) |
| Écoulement non visible | `#f39c12` (orange) |
| Assec | `#d62728` (rouge) |
| Moyenne | `#000000` (noir) |

---

*Documentation générée automatiquement à partir du code source | Dernière mise à jour : {{ "now" | date: "%d %B %Y" }}*
