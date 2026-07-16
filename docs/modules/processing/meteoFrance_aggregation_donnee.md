---
layout: default
title: meteoFrance_aggregation_donnee.py
description: "Documentation de l'agrégation des données MétéoFrance"
nav_order: 5
parent: Module Processing
grand_parent: Modules
---

# 🌦️ meteoFrance_aggregation_donnee.py

**Agrégation spatiale et temporelle des données MétéoFrance**

---

## 📋 Fonctions Principales

### aggregate_range

Agrège les données sur une période donnée.

```python
from src.processing.meteoFrance_aggregation_donnee import aggregate_range
from src.model.enums import GeographicScaleClip, MeteoFranceDataType
from datetime import datetime

aggregate_range(
    geo_scale=GeographicScaleClip.BASSIN,
    data_freq=MeteoFranceDataType.SIM2_MENS,
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31),
    is_data_aggregated=False
)
```

**Paramètres**
- `geo_scale` : Échelle géographique
- `data_freq` : Type de données
- `start_date` : Date de début
- `end_date` : Date de fin
- `is_data_aggregated` : Données déjà agrégées

---

## 🎯 Échelles Géographiques

| Échelle | Description |
|---------|-------------|
| BASSIN | Par bassin versant |
| REGION_ADMINISTRATIVE | Par région administrative |
| DEPARTEMENT | Par département |

---

## 💡 Exemple Complet

```python
from src.processing.meteoFrance_aggregation_donnee import aggregate_range
from src.model.enums import GeographicScaleClip, MeteoFranceDataType
from datetime import datetime

# Agrégation par bassin pour janvier 2026
aggregate_range(
    geo_scale=GeographicScaleClip.BASSIN,
    data_freq=MeteoFranceDataType.SIM2_MENS,
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31)
)
```

---

## 🔗 Liens

- [Module Processing](index.md)
- [Module IO - download_meteoFrance.py](../../modules/io/download_meteoFrance.md)
- [Concept SPI](../../concepts/spi.md)
- [Concept SSWI](../../concepts/sswi.md)


