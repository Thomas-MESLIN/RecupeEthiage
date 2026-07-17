---
layout: default
title: pynsee_departement.py
description: "Documentation des correspondances géographiques INSEE"
nav_order: 3
parent: Module IO
grand_parent: Modules
---

# 🗺️ pynsee_departement.py

**Correspondances entre régions et départements**

---

## 📋 Fonction Principale

### get_departements_from_regions

Récupère la liste des départements pour une ou plusieurs régions.

```python
from src.io.pynsee_departement import get_departements_from_regions

# Pour une région
code_region = "84"  # Auvergne-Rhône-Alpes
departements = get_departements_from_regions(code_region)
```

**Paramètres**
- `regions` : Code région ou liste de codes région

**Retourne**
- Liste des codes départements

---

## 🎯 Utilisation

Cette fonction est utilisée pour :
- **Filtrer les données** par région/département
- **Adapter les requêtes** aux zones géographiques spécifiques
- **Convertir les codes** région en départements pour les API MétéoFrance

---

## 📊 Exemple Complet

```python
from src.io.pynsee_departement import get_departements_from_regions

# Récupérer les départements de Auvergne-Rhône-Alpes
departements_ara = get_departements_from_regions("84")
print(f"Départements ARA : {departements_ara}")
```

---

## 🔗 Liens

- [Module IO](index.md)
- [Module Plotting - plot_meteoFrance.py](../../modules/plotting/plot_meteoFrance.md)
- [INSEE](https://www.insee.fr/)


