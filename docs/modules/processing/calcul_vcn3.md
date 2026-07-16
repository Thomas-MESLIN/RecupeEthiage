---
layout: default
title: calcul_vcn3.py
description: "Documentation du calcul du VCN3"
nav_order: 3
parent: Module Processing
grand_parent: Modules
---

# 🔬 calcul_vcn3.py

**Calcul du Volume Current Non-dépassé sur 3 mois**

---

## 📋 Fonctions Principales

### get_qmnj

Récupère les QmnJ à partir des données nettoyées.

```python
from src.processing.calcul_vcn3 import get_qmnj

df = get_qmnj("BSH001", "2026-06")
```

**Paramètres**
- `code_sandre` : Code du réseau Sandre
- `date_mois` : Période au format AAAA-MM

---

### get_all_stations

Récupère un DataFrame contenant toutes les stations.

```python
from src.processing.calcul_vcn3 import get_all_stations

df_stations = get_all_stations("BSH001")
```

---

### get_df_moyenne_glissante

Calcule la moyenne glissante sur les données.

```python
from src.processing.calcul_vcn3 import get_df_moyenne_glissante

df_moyenne = get_df_moyenne_glissante("2026-06", "BSH001")
```

---

### ensure_calcul_vcn3_calcule

S'assure que le VCN3 est calculé et à jour.

```python
from src.processing.calcul_vcn3 import ensure_calcul_vcn3_calcule

ensure_calcul_vcn3_calcule("2026-06", "BSH001")
```

**Processus**
1. Nettoie les données QmnJ si nécessaire
2. Charge les données
3. Calcule la moyenne glissante sur 3 mois
4. Identifie le VCN3 pour chaque station
5. Exporte en CSV

**Résultat** : `output/VCN3/mensuel/VCN3-{code_sandre}-{annee_mois}.csv`

---

### find_vcn3_min

Trouve le VCN3 minimum sur une période.

```python
from src.processing.calcul_vcn3 import find_vcn3_min
from datetime import datetime

res_min, date_min = find_vcn3_min(
    datetime(1991, 1, 1),
    datetime.today(),
    6,  # mois
    "BSH001",
    "H000001"  # code_station
)
```

**Retourne** : Tuple (valeur_min, date)

---

## 💡 Exemple Complet

```python
from src.processing.calcul_vcn3 import ensure_calcul_vcn3_calcule

# Calculer le VCN3 pour juin 2026
ensure_calcul_vcn3_calcule("2026-06", "BSH001")
```

---

## 🔗 Liens

- [Module Processing](index.md)
- [Concept VCN3](../../concepts/vcn3.md)
- [Module Plotting - Visualisation](../../modules/plotting/plot_grandeur.md)


