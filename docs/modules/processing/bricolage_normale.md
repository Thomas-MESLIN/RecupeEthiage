---
layout: default
title: bricolage_normale.py
description: "Documentation du calcul des normales climatiques"
nav_order: 8
parent: Module Processing
grand_parent: Modules
---

# 🌡️ bricolage_normale.py

**Calcul des normales climatiques**

---

## 📋 Description

Ce script calcule les normales climatiques à partir des données historiques MétéoFrance.

---

## 🎯 Fonctionnalité

- **Calcul des rapports aux normales** : Compare les données actuelles avec les normales historiques
- **Période de référence** : 1991-2020
- **Agrégation spatiale** : Par zone géographique

---

## 📁 Exemple de Code

```python
from src.processing.bricolage_normale import calculate_normale_ratio
from datetime import datetime
from src.model.enums import GeographicScaleClip, MeteoFranceDataType

# Calculer le rapport aux normales
ratio = calculate_normale_ratio(
    start_date=datetime(2026, 6, 1),
    end_date=datetime(2026, 6, 30),
    geo_scale=GeographicScaleClip.BASSIN,
    code_zone="06"
)
```

---

## 💡 Utilisation

Ce module est utilisé pour :
- **Cartographie des écarts aux normales**
- **Détection des anomalies climatiques**
- **Analyse des tendances**

---

## 🔗 Liens

- [Module Processing](index.md)
- [Module Plotting - plot_meteoFrance.py](../../modules/plotting/plot_meteoFrance.md)
- [Module IO - download_meteoFrance.py](../../modules/io/download_meteoFrance.md)


