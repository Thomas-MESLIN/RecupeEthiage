---
layout: default
title: calcul_hydraulicite.py
description: "Documentation du calcul de l'hydraulicité"
nav_order: 2
parent: Module Processing
grand_parent: Modules
---

# 📊 calcul_hydraulicite.py

**Calcul de l'hydraulicité**

---

## 📋 Fonctions Principales

### calcul_hydraulicite_mensuel

Calcule l'hydraulicité pour un mois donné.

```python
from src.processing.calcul_hydraulicite import calcul_hydraulicite_mensuel

calcul_hydraulicite_mensuel(
    annee_mois="2026-06",
    code_sandre="BSH001"
)
```

**Paramètres**
- `annee_mois` : Période au format AAAA-MM
- `code_sandre` : Code du réseau Sandre

**Processus**
1. Nettoie les données si nécessaire via `clean.ensure_single_month_cleaned`
2. Charge les données nettoyées
3. Calcule le QmM moyen historique (1991-2020) si nécessaire
4. Fusionne données actuelles et historiques
5. Calcule le ratio : QmM_observé / QmM_moyen_historique
6. Exporte en CSV

**Résultat** : `output/hydraulicite/hydraulicite-{code_sandre}-{annee_mois}.csv`

---

### ensure_QmM_moyen_historic_calculated

S'assure que le QmM moyen historique est calculé.

```python
from src.processing.calcul_hydraulicite import ensure_QmM_moyen_historic_calculated

ensure_QmM_moyen_historic_calculated("BSH001")
```

**Résultat** : `output/QmM_moyen/QmM_moyennes_{code_sandre}_1991_2020.csv`

---

### get_qmm

Récupère les QmM à partir des données nettoyées.

```python
from src.processing.calcul_hydraulicite import get_qmm

df = get_qmm("BSH001", "2026-06")
```

---

### get_all_qmm

Récupère toutes les données QmM de la période 1991-2020.

```python
from src.processing.calcul_hydraulicite import get_all_qmm

df_all = get_all_qmm("BSH001")
```

---

## 💡 Exemple Complet

```python
from src.processing.calcul_hydraulicite import (
    ensure_QmM_moyen_historic_calculated,
    calcul_hydraulicite_mensuel
)

# 1. S'assurer que les moyennes historiques sont calculées
ensure_QmM_moyen_historic_calculated("BSH001")

# 2. Calculer l'hydraulicité pour juin 2026
calcul_hydraulicite_mensuel("2026-06", "BSH001")
```

---

## 🔗 Liens

- [Module Processing](index.md)
- [Concept Hydraulicité](../../concepts/hydraulicite.md)
- [Module Plotting - Visualisation](../../modules/plotting/plot_grandeur.md)