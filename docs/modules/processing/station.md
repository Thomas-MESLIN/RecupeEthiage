---
layout: default
title: station.py
description: "Documentation de la gestion des stations"
nav_order: 7
parent: Module Processing
grand_parent: Modules
---

# 📍 station.py

**Gestion des stations de mesure**

---

## 📋 Fonctions Principales

### get_stations

Récupère les stations pour un code Sandre et une période.

```python
from src.processing.station import get_stations

df_stations = get_stations("BSH001", "2026-06")
```

**Paramètres**
- `code_sandre` : Code du réseau Sandre
- `annee_mois` : Période au format AAAA-MM

**Retourne** : DataFrame avec les stations

---

### get_stations_from_list

Récupère les stations à partir d'une liste de codes.

```python
from src.processing.station import get_stations_from_list

stations_list = ["H000001", "H000002"]
df = get_stations_from_list(stations_list, "2026-06")
```

---

## 💡 Exemple Complet

```python
from src.processing.station import get_stations

# Récupérer toutes les stations actives pour BSH001 en juin 2026
df = get_stations("BSH001", "2026-06")

print(f"Nombre de stations : {len(df)}")
print(df.head())
```

---

## 🔗 Liens

- [Module Processing](index.md)
- [Module IO - download_Hubeau.py](../../modules/io/download_Hubeau.md)