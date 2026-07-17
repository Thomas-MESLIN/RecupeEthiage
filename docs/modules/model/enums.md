---
layout: default
title: enums.py
description: "Documentation des énumérations"
nav_order: 1
parent: Module Model
grand_parent: Modules
---

# 📊 enums.py

**Définition des énumérations**

Ce module contient toutes les énumérations utilisées dans l'application.

---

## 📋 Énumérations Définies

### GeographicScaleClip

Échelles géographiques pour le découpage territorial.

```python
from src.model.enums import GeographicScaleClip

# Valeurs disponibles
GeographicScaleClip.BASSIN        # Bassin versant
GeographicScaleClip.REGION_ADMINISTRATIVE  # Région administrative
GeographicScaleClip.REGION_BASSIN  # Région coupée par le Bassin
GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF  # Département Administratif
GeographicScaleClip.DEPARTEMENT_BASSIN  # Département coupé par le Bassin
```

---

### MeteoFranceDataType

Types de données MétéoFrance.

```python
from src.model.enums import MeteoFranceDataType

# Valeurs disponibles
MeteoFranceDataType.SIM2_QUOT   # Données quotidiennes analysées par MétéoFrance
MeteoFranceDataType.SIM2_MENS   # Données mensuelles analysées par MétéoFrance
MeteoFranceDataType.QUOT        # Données quotidiennes brutes
MeteoFranceDataType.MENS        # Données mensuelles brutes
```

---

### OndeCampagneType

Types de campagnes ONDE.

```python
from src.model.enums import OndeCampagneType

# Valeurs disponibles
OndeCampagneType.ALL_CAMPAGNE    # Toutes les campagnes
OndeCampagneType.USUELLE         # Les campagnes usuelles uniquement
OndeCampagneType.COMPLEMENTAIRE  # Les campagnes complémentaires uniquement
```

---

## 💡 Bonnes Pratiques

- **Toujours utiliser les énumérations** plutôt que des strings codés en dur
- **Vérifier les valeurs disponibles** avant utilisation
- **Documenter** les nouvelles énumérations ajoutées

---

## 🔗 Liens

- [Module Model](index.md)
- [Module Plotting](../../modules/plotting/index.md)
- [Module Processing](../../modules/processing/index.md)


