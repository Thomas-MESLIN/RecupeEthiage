---
layout: default
title: Styles et Couleurs
description: "Documentation des styles et palettes de couleurs utilisés dans le module plotting"
nav_order: 6
parent: Module Plotting
grand_parent: Modules
---

# 🎨 Styles et Couleurs

**Documentation complète des paramètres de style**

> **Fichier** : `src/config/styles.py`
> **Module** : Configuration des styles visuels
> **Auteur** : Thomas Meslin
> **Dernière mise à jour** : Juin 2026

---

## 📋 Table des Matières

- [🎯 Aperçu](#-aperçu)
- [📦 Contenu du fichier](#-contenu-du-fichier)
- [🔧 Variables de Style](#-variables-de-style)
  - [COULEUR_MOYENNE](#couleur_moyenne)
  - [ANNEE_COULEURS](#annee_couleurs)
- [🎨 Utilisation des Styles](#-utilisation-des-styles)
- [📊 Palettes de Couleurs par Module](#-palettes-de-couleurs-par-module)
- [💡 Bonnes Pratiques](#-bonnes-pratiques)

---

## 🎯 Aperçu

Le fichier `styles.py` centralise **toutes les constantes de style** utilisées dans l'application, notamment :

- ✅ **Couleurs des lignes de moyenne** pour les graphiques
- ✅ **Palettes de couleurs par année** pour différencier les années dans les graphiques temporels
- ✅ **Cohérence visuelle** à travers tous les modules

Ce fichier permet de **maintenir une apparence uniforme** et de **faciliter les modifications** de style.

---

## 📦 Contenu du fichier

```python
# src/config/styles.py

## Couleur de la ligne MOYENNE
COULEUR_MOYENNE = "#000000"  # noir

## Couleur associé à chaque année pour différencier facilement les années dans les graphiques
ANNEE_COULEURS : dict[int, str] = {
    2012: "#1f77b4",
    2013: "#ff7f0e",
    2014: "#2ca02c",
    2015: "#d62728",
    2016: "#9467bd",
    2017: "#8c564b",
    2018: "#e377c2",
    2019: "#7f7f7f",
    2020: "#bcbd22",
    2021: "#17becf",
    2022: "#1b9e77",
    2023: "#d95f02",
    2024: "#7570b3",
    2025: "#e3298a",
    2026: "#ee0000",  # On met du rouge pour l'année actuelle !
}
```

---

## 🔧 Variables de Style

---

### `COULEUR_MOYENNE`

**Couleur utilisée pour tracer les lignes de moyenne dans les graphiques.**

#### 📌 Définition

```python
COULEUR_MOYENNE = "#000000"  # noir
```

#### 📝 Type

`str` - Code couleur hexadécimal

#### 📊 Utilisation

Utilisée dans les graphiques ONDE pour tracer la ligne de moyenne des assecs :

```python
# Dans plot_onde.py
if annee == annee_actuelle:
    # ...
    ax.plot(
        moyenne.index,
        moyenne.values,
        color=COULEUR_MOYENNE,  # ← Utilisation ici
        linewidth=lw,
        marker="o",
        markersize=ms,
        label="Moyenne",
    )
```

#### 🎨 Alternative

Pour une meilleure visibilité, vous pourriez utiliser :
- `#333333` (gris foncé)
- `#555555` (gris moyen)
- `#800000` (rouge foncé)

---

### `ANNEE_COULEURS`

**Dictionnaire associant chaque année à une couleur pour les graphiques.**

#### 📌 Définition

```python
ANNEE_COULEURS : dict[int, str] = {
    2012: "#1f77b4",
    2013: "#ff7f0e",
    2014: "#2ca02c",
    2015: "#d62728",
    2016: "#9467bd",
    2017: "#8c564b",
    2018: "#e377c2",
    2019: "#7f7f7f",
    2020: "#bcbd22",
    2021: "#17becf",
    2022: "#1b9e77",
    2023: "#d95f02",
    2024: "#7570b3",
    2025: "#e3298a",
    2026: "#ee0000",
}
```

#### 📝 Type

`dict[int, str]` - Dictionnaire année → code couleur hexadécimal

#### 📊 Utilisation

Utilisée dans les graphiques ONDE pour différencier les années :

```python
# Dans plot_onde.py
for annee in sorted(data.index):
    # ...
    if annee not in ANNEE_COULEURS:
        logger.error(f"ERREUR, LA COULEUR DE L'ANNEE '{annee}' N'A PAS ETE REMPLIE.")
        raise ValueError(f"Aucune couleur définie pour l'année {annee}")
    
    ax.plot(
        data.columns,
        data.loc[annee],
        color=ANNEE_COULEURS[annee],  # ← Utilisation ici
        linewidth=lw,
        marker="o",
        markersize=ms,
        label=str(annee),
    )
```

#### 🎨 Palette utilisée

Cette palette utilise les **couleurs par défaut de matplotlib** (liste de base) :

| Année | Couleur | Code Hex | Nom matplotlib |
|-------|---------|----------|----------------|
| 2012 | 🔵 | `#1f77b4` | bleu 1 |
| 2013 | 🟠 | `#ff7f0e` | orange 1 |
| 2014 | 🟢 | `#2ca02c` | vert 1 |
| 2015 | 🔴 | `#d62728` | rouge 1 |
| 2016 | 🟣 | `#9467bd` | violet 1 |
| 2017 | 🟤 | `#8c564b` | marron 1 |
| 2018 | 🟪 | `#e377c2` | rose 1 |
| 2019 | ⚫ | `#7f7f7f` | gris 1 |
| 2020 | 🟡 | `#bcbd22` | jaune olive |
| 2021 | 🔵 | `#17becf` | bleu 2 |
| 2022 | 🟢 | `#1b9e77` | vert 2 |
| 2023 | 🟤 | `#d95f02` | marron 2 |
| 2024 | 🟣 | `#7570b3` | violet 2 |
| 2025 | 🟪 | `#e3298a` | rose 2 |
| 2026 | 🔴 | `#ee0000` | **rouge** (année actuelle) |

#### ⚠️ Notes

- **2026 est en rouge** (`#ee0000`) pour être facilement identifiable comme l'année en cours
- Les couleurs sont **distinctes et contrastées** pour une bonne lisibilité
- La palette suit un **cycle de couleurs** pour faciliter la distinction

---

## 🎨 Utilisation des Styles

### Dans le module `plotting`

#### 1. **plot_onde.py**

```python
# Import des styles
from src.config.styles import COULEUR_MOYENNE, ANNEE_COULEURS

# Utilisation pour la moyenne
ax.plot(moyenne.index, moyenne.values, color=COULEUR_MOYENNE, ...)

# Utilisation pour les années
ax.plot(data.columns, data.loc[annee], color=ANNEE_COULEURS[annee], ...)
```

#### 2. **Autres modules**

Les autres modules de plotting peuvent importer et utiliser ces constantes :

```python
from src.config.styles import ANNEE_COULEURS

# Pour un graphique temporel
for year, color in ANNEE_COULEURS.items():
    if year in my_data.index:
        plt.plot(my_data.index, my_data.loc[year], color=color, label=str(year))
```

---

## 📊 Palettes de Couleurs par Module

Chaque module utilise des palettes spécifiques :

### 🌊 Module `plot_onde`

| Élément | Couleur | Code | Utilisation |
|---------|---------|------|-------------|
| **Moyenne** | Noir | `#000000` | Ligne de moyenne des assecs |
| **2012-2025** | Divers | Voir `ANNEE_COULEURS` | Courbes par année |
| **Pas de données** | Gris clair | `#D9D9D9` | Zone sans données |
| **Écoulement visible acceptable** | Bleu | `#1f77b4` | Segment de bar |
| **Écoulement visible faible** | Bleu clair | `#5dade2` | Segment de bar |
| **Écoulement non visible** | Orange | `#f39c12` | Segment de bar |
| **Assec** | Rouge | `#d62728` | Segment de bar |

### 🌦️ Module `plot_meteoFrance`

| Indicateur | Palette | Inversée | Intervalles |
|------------|---------|----------|-------------|
| **SSWI** | turbo | Oui | [-1.25, -0.75, -0.25, 0.25, 0.75, 1.25] |
| **SPI** | turbo | Oui | [-2.0, -1.0, -0.5, 0.5, 1.0, 2.0] |
| **Précipitations** | Par défaut | Non | Auto |

### 💧 Module `plot_grandeur`

| Élément | Couleur | Style | Utilisation |
|---------|---------|-------|-------------|
| **Loi Log-Normale** | Rouge feu | Ligne pleine | Courbe théorique |
| **IC 95%** | Rouge feu | Zone ombrée (alpha=0.15) | Intervalle de confiance |
| **Observations** | Bleu acier | Points | Données empiriques |
| **Débit observé** | Orange foncé | Ligne pointillée | Valeur spécifique |
| **IC sur T** | Orange foncé | Zone ombrée (alpha=0.10) | Intervalle de période de retour |

### 🗺️ Module `rasterize`

| Indicateur | Palette | Inversée | Intervalles |
|------------|---------|----------|-------------|
| **SSWI** | turbo | Oui | [-1.25, -0.75, -0.25, 0.25, 0.75, 1.25] |
| **Hydraulicité** | turbo | Oui | [-0.25, 0.25, 0.75, 1.25, 1.75] |

---

## 💡 Bonnes Pratiques

### 1. **Ajouter une nouvelle année**

Si vous travaillez avec des données pour une nouvelle année (ex: 2027), ajoutez-la au dictionnaire :

```python
ANNEE_COULEURS[2027] = "#aaaaaa"  # Gris clair
```

**Recommandation** : Utilisez une couleur qui n'est pas déjà utilisée et qui reste dans la gamme de couleurs distinguables.

### 2. **Personnaliser les couleurs**

Pour adapter les couleurs à votre charte graphique :

```python
# Remplacer une couleur existante
ANNEE_COULEURS[2026] = "#ff0000"  # Rouge pur

# Ou définir une palette complètement différente
ANNEE_COULEURS = {
    2020: "#0066cc",
    2021: "#0099cc",
    2022: "#00cc99",
    2023: "#00cc66",
    2024: "#33cc33",
    2025: "#66cc00",
    2026: "#99cc00",
}
```

### 3. **Utiliser des palettes matplotlib**

Pour les graphiques continus, vous pouvez utiliser les palettes intégrées de matplotlib :

```python
# Palettes séquentielles (de clair à foncé)
"Greys", "Purples", "Blues", "Greens", "Oranges", "Reds"
"YlOrBr", "YlOrRd", "OrRd", "PuRd", "RdPu", "BuPu"
"GnBu", "PuBu", "YlGnBu", "PuBuGn", "BuGn", "YlGn"

# Palettes divergentes (avec point central)
"PiYG", "PRGn", "BrBG", "PuOr", "RdGy", "RdBu"
"RdYlBu", "RdYlGn", "Spectral", "coolwarm", "bwr", "seismic"

# Palettes qualitatives (couleurs distinctes)
"Pastel1", "Pastel2", "Set1", "Set2", "Set3"
"tab10", "tab20", "tab20b", "tab20c"
```

### 4. **Tester l'accessibilité**

Vérifiez que vos combinaisons de couleurs sont accessibles :

```python
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Vérifier le contraste
colors = list(ANNEE_COULEURS.values())
for i, c1 in enumerate(colors):
    for j, c2 in enumerate(colors[i+1:], i+1):
        # Calculer la différence de luminance (simplifiée)
        # Plus la valeur est élevée, meilleur est le contraste
        luminance_diff = abs(
            (0.299 * int(c1[1:3], 16) + 0.587 * int(c1[3:5], 16) + 0.114 * int(c1[5:7], 16)) -
            (0.299 * int(c2[1:3], 16) + 0.587 * int(c2[3:5], 16) + 0.114 * int(c2[5:7], 16))
        )
        if luminance_diff < 50:
            print(f"Faible contraste entre {c1} et {c2}")
```

---

## 🎯 Conseils pour l'Extension

### Ajouter une nouvelle constante de style

1. **Choisir un nom explicite** :
   ```python
   COULEUR_ECARTS = "#ff0000"
   COULEUR_MEDIANE = "#0000ff"
   ```

2. **Documenter dans le fichier** :
   ```python
   # Couleur utilisée pour mettre en évidence les écarts
   COULEUR_ECARTS = "#ff0000"
   ```

3. **Utiliser de manière cohérente** : Importer et utiliser la constante dans tous les modules concernés.

---

## 📚 Voir aussi

- [Module plotting](index.md) - Aperçu du module
- [plot_onde](plot_onde.md) - Utilisation des couleurs par année
- [rasterize](rasterize.md) - Palettes de couleurs pour les indicateurs
- [Documentation matplotlib sur les couleurs](https://matplotlib.org/stable/tutorials/colors/colormaps.html)

---

## 🎨 Visualisation des Couleurs

Voici un aperçu des couleurs définies dans `ANNEE_COULEURS` :

| Année | Couleur | Aperçu |
|-------|---------|--------|
| 2012 | `#1f77b4` | ![#1f77b4](https://via.placeholder.com/30/1f77b4/000000?text=+) |
| 2013 | `#ff7f0e` | ![#ff7f0e](https://via.placeholder.com/30/ff7f0e/000000?text=+) |
| 2014 | `#2ca02c` | ![#2ca02c](https://via.placeholder.com/30/2ca02c/000000?text=+) |
| 2015 | `#d62728` | ![#d62728](https://via.placeholder.com/30/d62728/000000?text=+) |
| 2016 | `#9467bd` | ![#9467bd](https://via.placeholder.com/30/9467bd/000000?text=+) |
| 2017 | `#8c564b` | ![#8c564b](https://via.placeholder.com/30/8c564b/000000?text=+) |
| 2018 | `#e377c2` | ![#e377c2](https://via.placeholder.com/30/e377c2/000000?text=+) |
| 2019 | `#7f7f7f` | ![#7f7f7f](https://via.placeholder.com/30/7f7f7f/000000?text=+) |
| 2020 | `#bcbd22` | ![#bcbd22](https://via.placeholder.com/30/bcbd22/000000?text=+) |
| 2021 | `#17becf` | ![#17becf](https://via.placeholder.com/30/17becf/000000?text=+) |
| 2022 | `#1b9e77` | ![#1b9e77](https://via.placeholder.com/30/1b9e77/000000?text=+) |
| 2023 | `#d95f02` | ![#d95f02](https://via.placeholder.com/30/d95f02/000000?text=+) |
| 2024 | `#7570b3` | ![#7570b3](https://via.placeholder.com/30/7570b3/000000?text=+) |
| 2025 | `#e3298a` | ![#e3298a](https://via.placeholder.com/30/e3298a/000000?text=+) |
| 2026 | `#ee0000` | ![#ee0000](https://via.placeholder.com/30/ee0000/000000?text=+) |

---

## 🎯 Résumé

| Variable | Type | Valeur | Utilisation |
|----------|------|--------|-------------|
| `COULEUR_MOYENNE` | `str` | `#000000` | Ligne de moyenne |
| `ANNEE_COULEURS` | `dict[int, str]` | Voir ci-dessus | Couleurs par année |

---

*Documentation générée automatiquement à partir du code source | Dernière mise à jour : {{ "now" | date: "%d %B %Y" }}*
