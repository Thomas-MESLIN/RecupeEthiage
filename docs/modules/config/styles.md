---
layout: default
title: styles.py
description: "Documentation des styles et couleurs"
nav_order: 3
parent: Module Config
grand_parent: Modules
---

# 🎨 styles.py

**Définition des styles et palettes de couleurs**

Ce module centralise toutes les constantes de style utilisées pour la visualisation.

---

## 📋 Constantes de Couleurs

### ANNEE_COULEURS

Palette de couleurs pour les différentes années.

```python
from src.config.styles import ANNEE_COULEURS

# Accès
couleur_2020 = ANNEE_COULEURS[2020]
couleur_2021 = ANNEE_COULEURS[2021]
```

---

### COULEUR_MOYENNE

Couleur utilisée pour la moyenne de référence.

```python
from src.config.styles import COULEUR_MOYENNE

# Utilisation
plt.axhline(y=moyenne, color=COULEUR_MOYENNE, linestyle='--')
```

---

## 🎯 Palettes par Indicateur

### Hydraulicité

| Plage | Couleur | Code |
|-------|---------|------|
| < 40% | Rouge | #8B0000 |
| 40-70% | Orange | #FF8C00 |
| 70-100% | Jaune | #FFD700 |
| 100-130% | Vert clair | #90EE90 |
| 130-160% | Vert | #008000 |
| > 160% | Bleu | #0000FF |

### SPI/SSWI

| Plage | Couleur |
|-------|---------|
| ≤ -2.0 | Rouge foncé |
| -1.99 à -1.5 | Rouge |
| -1.49 à -1.0 | Orange |
| -0.99 à 0.99 | Jaune |
| 1.0-1.49 | Vert clair |
| 1.5-1.99 | Vert |
| ≥ 2.0 | Vert foncé |

---

## 💡 Utilisation

```python
from src.config.styles import ANNEE_COULEURS, COULEUR_MOYENNE
import matplotlib.pyplot as plt

# Créer un graphique avec les couleurs standard
fig, ax = plt.subplots()

# Tracer les données de chaque année avec sa couleur
for year, data in data_by_year.items():
    ax.plot(data, color=ANNEE_COULEURS[year], label=str(year))

# Ajouter la moyenne
ax.axhline(y=mean_value, color=COULEUR_MOYENNE, linestyle='--', label='Moyenne')

plt.legend()
plt.show()
```

---

## 🔗 Liens

- [Module Config](index.md)
- [Module Plotting](../../modules/plotting/index.md)