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


