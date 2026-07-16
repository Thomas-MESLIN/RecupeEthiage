---
layout: default
title: download_meteoFrance.py
description: "Documentation du téléchargement des données MétéoFrance"
nav_order: 2
parent: Module IO
grand_parent: Modules
---

# 🌦️ download_meteoFrance.py

**Récupération des données météorologiques depuis MétéoFrance**

---

## 📋 Fonctions Principales

### get_data_in_range

Récupère les données pour une période donnée.

```python
from src.io.download_meteoFrance import get_data_in_range
from src.model.enums import MeteoFranceDataType
from datetime import datetime

df = get_data_in_range(
    data_freq=MeteoFranceDataType.SIM2_MENS,
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31),
    has_index_update=True,
    is_data_update_allowed=True
)
```

**Paramètres**
- `data_freq` : Type de données (SIM2_QUOT, SIM2_MENS, QUOT, MENS)
- `start_date` : Date de début
- `end_date` : Date de fin
- `has_index_update` : Mettre à jour l'index
- `is_data_update_allowed` : Autoriser la mise à jour

---

### get_geographic_list

Récupère la liste des zones géographiques.

```python
from src.io.download_meteoFrance import get_geographic_list
from src.model.enums import GeographicScaleClip

# Récupérer les bassins
bassins = get_geographic_list(GeographicScaleClip.BASSIN)

# Récupérer les régions
regions = get_geographic_list(GeographicScaleClip.REGION_ADMINISTRATIVE)

# Récupérer les départements
departements = get_geographic_list(GeographicScaleClip.DEPARTEMENT)
```

**Paramètres**
- `geo_scale` : Échelle géographique (BASSIN, REGION_ADMINISTRATIVE, DEPARTEMENT)

---

### download_and_extract

Télécharge et extrait les données brutes.

```python
from src.io.download_meteoFrance import download_and_extract
from src.model.enums import MeteoFranceDataType
from datetime import datetime

download_and_extract(
    data_type=MeteoFranceDataType.QUOT,
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31)
)
```

---

## 🎯 Types de Données

| Type | Description | Fréquence | Résolution |
|------|-------------|-----------|------------|
| SIM2_QUOT | Données quotidiennes interpolées | Quotidienne | 8x8 km |
| SIM2_MENS | Données mensuelles interpolées | Mensuelle | 8x8 km |
| QUOT | Données quotidiennes brutes | Quotidienne | Station |
| MENS | Données mensuelles brutes | Mensuelle | Station |

---

## 🔗 Liens

- [Module IO](index.md)
- [Concept SPI](../../concepts/spi.md)
- [Concept SSWI](../../concepts/sswi.md)
- [MétéoFrance](https://www.meteofrance.com/)