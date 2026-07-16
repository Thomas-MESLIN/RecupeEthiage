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
GeographicScaleClip.DEPARTEMENT  # Département
```

---

### MeteoFranceDataType

Types de données MétéoFrance.

```python
from src.model.enums import MeteoFranceDataType

# Valeurs disponibles
MeteoFranceDataType.SIM2_QUOT   # Données quotidiennes interpolées
MeteoFranceDataType.SIM2_MENS   # Données mensuelles interpolées
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
OndeCampagneType.ONE_CAMPAGNE    # Une campagne spécifique
```

---

## 🎯 Utilisation

```python
from src.model.enums import GeographicScaleClip, MeteoFranceDataType

# Exemple avec plot_meteoFrance
export_all_format_geojson_range(
    geo_scale=GeographicScaleClip.BASSIN,
    data_freq=MeteoFranceDataType.SIM2_MENS,
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31)
)
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


