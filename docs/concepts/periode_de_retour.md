---
layout: default
title: Période de Retour
description: "Analyse statistique des événements hydrologiques extrêmes"
nav_order: 3
parent: Concepts Clés
grand_parent: ""
---

# 📈 Période de Retour

**Analyse fréquentielle des événements hydrologiques extrêmes**

La période de retour est un concept statistique permettant d'estimer la fréquence d'occurrence d'un événement hydrologique donné, basé sur son intensité.

---

## 📋 Définition

**Période de Retour (T)** = Intervalle de temps moyen entre deux occurrences d'un événement d'une intensité donnée.

**Formule** : T = 1 / P, où P = probabilité annuelle de non-dépassement

**Exemple** : Un événement avec T=10 ans a 10% de chances de se produire chaque année.

---

## 🎯 Utilité

- **Dimensionnement** : Ouvrages hydrauliques, barrages, digues
- **Gestion des risques** : Planification des mesures de protection
- **Réglementation** : Définition de seuils pour les alertes

---

## 📊 Interprétation

| Période de Retour | Probabilité Annuelle | Qualification |
|-------------------|---------------------|---------------|
| < 2 ans | > 50% | Très fréquent |
| 2-5 ans | 20-50% | Fréquent |
| 5-10 ans | 10-20% | Occasionnel |
| 10-20 ans | 5-10% | Peu fréquent |
| 20-50 ans | 2-5% | Rare |
| > 50 ans | < 2% | Très rare |

---

## 🔬 Méthodologie

### Implémentation dans l'Application

**Module** : [`src/processing/calcul_frequence_periode_de_retour.py`](../modules/processing/calcul_frequence_periode_de_retour.md)

**Méthode** : Loi Log-Normale avec estimation par L-moments et bootstrap paramétrique

**Fonction principale** :
```python
from src.processing.calcul_frequence_periode_de_retour import vcn3_frequence_retour

resultat = vcn3_frequence_retour(
    y=serie_vcn3,
    T_grid=[2, 5, 10, 20, 50, 100],
    split_zeros=True,
    IC_level=0.95,
    n_sim=1000
)
```

### Paramètres Clés

- **y** : Série de VCN3 annuels (m³/s)
- **T_grid** : Périodes de retour à calculer
- **split_zeros** : Séparer les années à débit nul
- **IC_level** : Niveau de confiance (0.95 = 95%)
- **n_sim** : Nombre de simulations bootstrap

---

## 📁 Résultats Produits

```
{
    "params": (sigma, loc, scale),  # Paramètres de la loi
    "quantiles": {
        "T": [2, 5, 10, 20, 50, 100],
        "q": [10, 5, 2, 1, 0.5, 0.2],  # Débits correspondants
        "IC_low": [...],  # Intervalles de confiance bas
        "IC_high": [...]  # Intervalles de confiance haut
    },
    "pcdf": {
        "x": [...],  # Grille de débits
        "cdf": [...],  # Fonction de répartition
        "IC_low": [...],
        "IC_high": [...]
    }
}
```

---

## 🗺️ Visualisation

### Graphique de Fréquence

L'application génère :
- **Courbe de fréquence empirique** : Points observés
- **Courbe théorique** : Ajustement Log-Normale
- **Intervalles de confiance** : 95% via bootstrap

---

## 🎓 Exemple d'Utilisation

```python
# Calcul pour une station
from src.processing.calcul_frequence_periode_de_retour import get_result_station

resultat = get_result_station(
    code_station="H000001",
    mois="07",
    code_sandre="BSH001",
    vcn3_observation=85.5,
    plot_resultat=True
)

# Interprétation
print(f"Débit observé: {resultat['debit_obs']} m³/s")
print(f"Période de retour: {resultat['Periode_de_retour']:.1f} ans")
print(f"IC 95%: [{resultat['Periode_de_retour_interval_confiance_bas']:.1f}, {resultat['Periode_de_retour_interval_confiance_haut']:.1f}] ans")
```

---

## 💡 Bonnes Pratiques

- **Minimum 5 valeurs positives** requises pour un calcul fiable
- **Période d'observation** : Au moins 20 ans pour une estimation robuste
- **Vérifier les intervalles de confiance** : Large intervalle = incertitude élevée

---

## 🔗 Liens

- [Module Processing - Analyse fréquentielle](../modules/processing/calcul_frequence_periode_de_retour.md)
- [Concept VCN3](vcn3.md)
- [Concept Hydraulicité](hydraulicite.md)


