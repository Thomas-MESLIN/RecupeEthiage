---
layout: default
title: SPI et SSWI
description: "Indices de sécheresse SPI et SSWI"
nav_order: 4
parent: Concepts Clés
grand_parent: ""
---

# 🌡️ SPI et SSWI

**Indices de sécheresse utilisés en météorologie**

---

## 📊 SPI (Standardized Precipitation Index)

**Indice de Précipitation Standardisé**

Le SPI est un indice permettant de caractériser la sécheresse météorologique en comparant les précipitations observées à une période de référence.

### Calcul

Le SPI est calculé sur différentes échelles de temps (1, 3, 6, 12 mois) pour évaluer la sécheresse à différentes temporalités.

### Interprétation

| Valeur | Interprétation |
|--------|----------------|
| ≥ 2.0  | Extrêmement humide |
| 1.5 - 1.99 | Très humide |
| 1.0 - 1.49 | Humide |
| -0.99 - 0.99 | Normal |
| -1.0 - -1.49 | Sec |
| -1.5 - -1.99 | Très sec |
| ≤ -2.0 | Extrêmement sec |

### Utilisation

- Détection des périodes de sécheresse
- Comparaison entre régions
- Analyse historique

---

## 💧 SSWI (Standardized Soil Water Index)

**Indice Standardisé de l'Eau du Sol**

Le SSWI est un indice qui prend en compte à la fois les précipitations et l'évapotranspiration pour évaluer l'humidité du sol.

### Particularités

- **Basé sur un bilan hydrique** : Précipitations - Evapotranspiration
- **Échelle temporelle** : Variables selon les besoins
- **Couverture spatiale** : Grille 8x8km pour les données SIM2

### Interprétation

| Valeur | Interprétation |
|--------|----------------|
| ≥ 1.5  | Extrêmement humide |
| 1.0 - 1.49 | Très humide |
| 0.5 - 0.99 | Humide |
| -0.49 - 0.49 | Normal |
| -0.5 - -0.99 | Sec |
| -1.0 - -1.49 | Très sec |
| ≤ -1.5 | Extrêmement sec |

### Relation avec le SPI

Le SSWI est souvent utilisé en complément du SPI car il intègre l'évapotranspiration, ce qui le rend plus représentatif de l'état réel du sol.

---

## 📈 Comparaison SPI vs SSWI

| Critère | SPI | SSWI |
|---------|-----|------|
| **Données** | Précipitations uniquement | Précipitations + ETP |
| **Complexité** | Simple | Plus complexe |
| **Représentativité** | Météo uniquement | Sol + climat |
| **Utilisation** | Sécheresse météorologique | Sécheresse agricole |

---

## 🔍 Exemple d'Utilisation

```python
# Analyse combinée SPI/SSWI
import pandas as pd

# Charger les données
df = pd.read_csv("output/meteoFrance/downloaded_data/spi_sswi.csv")

# Filtrer les valeurs critiques
secheresse_spi = df[df["SPI"] <= -1.5]
secheresse_sswi = df[df["SSWI"] <= -1.0]

# Combinaison des indicateurs
secheresse_critique = secheresse_spi.merge(secheresse_sswi, how='inner')
```

---

## 🎯 Application dans l'Outil

Dans cet outil, les indices SPI et SSWI sont :

1. **Récupérés** depuis MétéoFrance (données SIM2)
2. **Visualisés** sous forme de cartes GeoJSON
3. **Analysés** pour détecter les périodes de sécheresse
4. **Exportés** pour intégration dans QGIS ou d'autres SIG

---

## 🔗 Liens

- [MétéoFrance](https://www.meteofrance.com/) - Source des données
- [Documentation SPI](https://www.droughtmanagement.info/standardized-precipitation-index-spi/) - Standard international
- [Module Plotting - plot_meteoFrance](../modules/plotting/plot_meteoFrance.md) - Visualisation des indices
