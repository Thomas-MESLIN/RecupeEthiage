---
layout: default
title: Sources de Données
description: "Détail des sources de données utilisées par l'application"
nav_order: 1
parent: Données
grand_parent: ""
---

# 📡 Sources de Données

**Origines et caractéristiques des données utilisées**

---

## 🌊 Hub'Eau

**Source principale pour les données hydrologiques**

- **URL** : [https://hubeau.eaufrance.fr/](https://hubeau.eaufrance.fr/)
- **Type** : API REST
- **Couverture** : France métropolitaine
- **Fréquence** : Quotidienne et mensuelle
- **Données disponibles** :
  - Observations élaborées (QmM, QmnJ)
  - Métadonnées des stations
  - Informations sur les sites

### Accès

L'accès se fait via l'API officielle avec authentification.

---

## 🌦️ MétéoFrance

**Source pour les données météorologiques**

- **URL** : [https://www.meteofrance.com/](https://www.meteofrance.com/)
- **Type** : API et fichiers CSV
- **Couverture** : France métropolitaine et outre-mer
- **Fréquence** : Quotidienne
- **Données disponibles** :
  - Précipitations (RR)
  - Indice SPI (Standardized Precipitation Index)
  - Indice SSWI (Standardized Soil Water Index)
  - Evapotranspiration (ETP)
  - Température

### Particularités

- Données SIM2 : interpolées sur grille 8x8km
- Données brutes : mesures de stations

---

## 🗺️ INSEE

**Source pour les données géographiques**

- **URL** : [https://www.insee.fr/](https://www.insee.fr/)
- **Type** : Fichiers de correspondance
- **Couverture** : France
- **Fréquence** : Statique (mise à jour occasionnelle)
- **Données disponibles** :
  - Correspondance régions-départements
  - Découpage administratif

---

## 🏞️ ONDE

**Observatoire National des Établissements**

- **URL** : [https://onde.eaufrance.fr/](https://onde.eaufrance.fr/)
- **Type** : Base de données
- **Couverture** : France métropolitaine
- **Fréquence** : Mensuelle et annuelle
- **Données disponibles** :
  - Campagnes usuelle
  - Campagnes complémentaires
  - Observations écologiques des cours d'eau

---

## 📊 Réseau SANDRE

**Système d'Information sur l'Eau**

- **URL** : [https://sandre.eaufrance.fr/](https://sandre.eaufrance.fr/)
- **Type** : Référentiel
- **Couverture** : France
- **Fréquence** : Statique
- **Données disponibles** :
  - Codes des réseaux hydrographiques
  - Métadonnées des stations

---

## 🔗 Liens

- [Module IO](../modules/io/index.md) - Documentation technique de l'accès aux données
- [Module Processing](../modules/processing/index.md) - Traitement des données
