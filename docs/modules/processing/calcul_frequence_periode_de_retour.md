---
layout: default
title: calcul_frequence_periode_de_retour.py
description: "Documentation de l'analyse fréquentielle des périodes de retour"
nav_order: 4
parent: Module Processing
grand_parent: Modules
---

# 📈 calcul_frequence_periode_de_retour.py

**Analyse fréquentielle des périodes de retour**

---

## 📋 Fonctions Principales

### fit_lognormal_lmom

Estimateur des L-moments pour la loi Log-Normale.

```python
from src.processing.calcul_frequence_periode_de_retour import fit_lognormal_lmom
import numpy as np

z = np.array([1.2, 1.5, 1.8, 2.1, 2.4])
params = fit_lognormal_lmom(z)  # (sigma, 0, mu_exp)
```

**Retourne** : Tuple (sigma, 0, exp(mu))

---

### vcn3_frequence_retour

Calcule la fréquence de retour du VCN3.

```python
from src.processing.calcul_frequence_periode_de_retour import vcn3_frequence_retour
import numpy as np

y = np.array([85, 90, 78, 95, 88, 92, 82])
resultat = vcn3_frequence_retour(
    y=y,
    T_grid=np.array([2, 5, 10, 20, 50, 100]),
    split_zeros=True,
    IC_level=0.95,
    n_sim=1000
)
```

**Paramètres**
- `y` : Série de VCN3 annuels (m³/s)
- `T_grid` : Périodes de retour à calculer (ans)
- `split_zeros` : Séparer les années à débit nul
- `IC_level` : Niveau de confiance
- `n_sim` : Nombre de simulations bootstrap

**Retourne** : Dict avec params, quantiles, empirical, pcdf

---

### get_period_from_flow

Retrouve la période de retour pour un débit observé.

```python
from src.processing.calcul_frequence_periode_de_retour import get_period_from_flow

resultat = get_period_from_flow(
    q_obs=85.5,
    res=resultat_vcn3_frequence_retour
)
```

**Retourne** : Dict avec debit_obs, frequence_non_depassement, Periode_de_retour, IC

---

### ensure_frequence_non_depassement_periode_retour_calcule

S'assure que les périodes de retour sont calculées.

```python
from src.processing.calcul_frequence_periode_de_retour import ensure_frequence_non_depassement_periode_retour_calcule

ensure_frequence_non_depassement_periode_retour_calcule(
    annee_mois="2026-06",
    code_sandre="BSH001",
    is_result_plotted=False
)
```

**Résultat** : `output/VCN3/analyse_frequence_periode/periode-de-retour-{code_sandre}-{annee_mois}.csv`

---

## 💡 Exemple Complet

```python
from src.processing.calcul_frequence_periode_de_retour import (
    vcn3_frequence_retour,
    get_period_from_flow,
    ensure_frequence_non_depassement_periode_retour_calcule
)

# 1. Calculer pour une série de VCN3
import numpy as np
y = np.array([85, 90, 78, 95, 88])
resultat = vcn3_frequence_retour(y)

# 2. Trouver la période de retour pour un débit
resultat_station = get_period_from_flow(85.5, resultat)

# 3. Calculer pour un mois complet
ensure_frequence_non_depassement_periode_retour_calcule("2026-06", "BSH001")
```

---

## 🔗 Liens

- [Module Processing](index.md)
- [Concept Période de Retour](../../concepts/periode_de_retour.md)
- [Concept VCN3](../../concepts/vcn3.md)
- [Module Plotting - Visualisation](../../modules/plotting/plot_grandeur.md)