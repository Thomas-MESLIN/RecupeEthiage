---
layout: default
title: SPI
description: "Indice de Précipitation Standardisé"
nav_order: 4
parent: Concepts Clés
grand_parent: ""
---

# 🌧️ SPI - Indice de Précipitation Standardisé

**Mesure de la sécheresse météorologique**

Le SPI (Standardized Precipitation Index) quantifie le déficit ou l'excédent de précipitations sur différentes échelles de temps.

---

## 📋 Définition

Indice qui compare les précipitations cumulées sur une période donnée avec les valeurs historiques, standardisé pour permettre des comparaisons spatiales et temporelles.

**Formule** : SPI = (X - μ) / σ
- X : Précipitations cumulées sur la période
- μ : Moyenne historique des précipitations sur cette période
- σ : Écart-type historique

---

## 🎯 Utilité

- **Détection précoce** des sécheresses météorologiques
- **Comparaison** entre régions aux climats différents
- **Suivi** sur différentes échelles (1, 3, 6, 12, 24 mois)

---

## 📊 Interprétation

| SPI | Classe | Interprétation |
|-----|--------|----------------|
| ≥ 2.0 | Extrêmement humide | Pluies exceptionnelles |
| 1.5-1.99 | Très humide | Pluies très abondantes |
| 1.0-1.49 | Modérément humide | Pluies supérieures à la normale |
| -0.99 à 0.99 | Presque normal | Précipitations proches de la normale |
| -1.49 à -1.0 | Modérément sec | Déficit de précipitations |
| -1.99 à -1.5 | Très sec | Sécheresse marquée |
| ≤ -2.0 | Extrêmement sec | Sécheresse extrême |

---

## 🔬 Échelles de Temps

| Échelle | Utilisation |
|---------|------------|
| 1 mois | Sécheresse courte (impact agriculture) |
| 3 mois | Sécheresse saisonnière |
| 6 mois | Impact sur les nappes phréatiques |
| 12 mois | Sécheresse hydrologique |
| 24 mois | Tendances climatiques |

---

## 📁 Dans l'Application

**Module** : `src/plotting/plot_meteoFrance.py` et `src/io/download_meteoFrance.py`

**Données** : Issue des données MétéoFrance (SIM2)

**Visualisation** : Cartes GeoJSON avec palettes de couleurs standardisées

---

## 💡 Bonnes Pratiques

- Toujours calculer **plusieurs échelles** pour une analyse complète
- Comparer avec **d'autres indicateurs** (SSWI, VCN3)
- **Période de référence** : 1991-2020

---

## 🔗 Liens

- [Concept SSWI](sswi.md)
- [Concept VCN3](vcn3.md)
- [Module Plotting - plot_meteoFrance.py](../modules/plotting/plot_meteoFrance.md)


