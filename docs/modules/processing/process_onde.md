---
layout: default
title: process_onde.py
description: "Documentation du traitement des données ONDE"
nav_order: 6
parent: Module Processing
grand_parent: Modules
---

# 🌊 process_onde.py

**Traitement des données ONDE (Observatoire National des Établissements)**

---

## 📋 Fonctions Principales

### process_onde_data

Traite les données ONDE pour une campagne.

```python
from src.processing.process_onde import process_onde_data
from datetime import datetime
from src.model.enums import OndeCampagneType

process_onde_data(
    campagne_type=OndeCampagneType.ALL_CAMPAGNE,
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31)
)
```

---

## 🎯 Fonctionnalités

- **Analyse des campagnes** : Suivi des écoulements et assecs
- **Agrégation spatiale** : Par bassin, région, département
- **Agrégation temporelle** : Par mois, année
- **Calcul d'indicateurs** : Pourcentages par classe d'écoulement

---

## 💡 Exemple Complet

```python
from src.processing.process_onde import process_onde_data
from src.model.enums import OndeCampagneType, GeographicScaleClip
from datetime import datetime

# Traiter les données ONDE pour 2026
process_onde_data(
    campagne_type=OndeCampagneType.ALL_CAMPAGNE,
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 12, 31),
    geographic_scale=GeographicScaleClip.BASSIN
)
```

---

## 🔗 Liens

- [Module Processing](index.md)
- [Concept ONDE](../../concepts/onde.md)
- [Module Plotting - plot_onde.py](../../modules/plotting/plot_onde.md)