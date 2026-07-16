---
layout: default
title: SSWI
description: "Indice Standardisé d'Humidité des Sols"
nav_order: 5
parent: Concepts Clés
grand_parent: ""
---

# 🌱 SSWI - Indice Standardisé d'Humidité des Sols

**Évaluation de l'humidité du sol**

Le SSWI (Standardized Soil Wetness Index) mesure le contenu en eau des sols par rapport à la capacité de rétention, standardisé pour permettre des comparaisons spatiales.

---

## 📋 Définition

Indice qui évalue l'humidité des sols en comparant le contenu en eau actuel avec les valeurs historiques, sur différentes profondeurs de sol.

**Formule** : SSWI = (W - μ) / σ
- W : Contenu en eau actuel du sol
- μ : Moyenne historique du contenu en eau
- σ : Écart-type historique

---

## 🎯 Utilité

- **Agriculture** : Décision d'irrigation, prévention des stress hydriques
- **Gestion des risques** : Prévision des inondations par saturation des sols
- **Écologie** : Impact sur les écosystèmes terrestres

---

## 📊 Interprétation

| SSWI | Classe | Interprétation |
|------|--------|----------------|
| ≥ 2.0 | Extrêmement humide | Sols saturés, risque d'inondation |
| 1.5-1.99 | Très humide | Sols très humides |
| 1.0-1.49 | Modérément humide | Sols humides |
| -0.99 à 0.99 | Presque normal | Humidité proche de la normale |
| -1.49 à -1.0 | Modérément sec | Stress hydrique léger |
| -1.99 à -1.5 | Très sec | Stress hydrique marqué |
| ≤ -2.0 | Extrêmement sec | Stress hydrique sévère |

---

## 🔬 Profondeurs Analysées

| Profondeur | Indice | Utilisation |
|------------|--------|------------|
| Surface (0-10 cm) | SSWI1 | Réponse immédiate aux précipitations |
| Racinaire (0-100 cm) | SSWI2 | Impact sur l'agriculture |
| Profond (0-200 cm) | SSWI3 | Impact sur les nappes |

---

## 📁 Dans l'Application

**Module** : `src/plotting/plot_meteoFrance.py` et `src/io/download_meteoFrance.py`

**Données** : Issue des données MétéoFrance (SIM2)

**Visualisation** : Cartes GeoJSON avec codage couleur par classe

---

## 💡 Bonnes Pratiques

- **Combiner avec SPI** : SPI (précipitations) + SSWI (humidité) = analyse complète
- **Comparer profondeurs** : Analyse multi-niveaux pour comprendre l'impact total
- **Seuils d'alerte** : Adapter aux types de sols et cultures

---

## 🔗 Liens

- [Concept SPI](spi.md)
- [Concept Hydraulicité](hydraulicite.md)
- [Module Plotting - plot_meteoFrance.py](../modules/plotting/plot_meteoFrance.md)