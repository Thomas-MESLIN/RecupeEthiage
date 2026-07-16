---
layout: default
title: ONDE
description: "Observatoire National des Établissements"
nav_order: 6
parent: Concepts Clés
grand_parent: ""
---

# 🌊 ONDE - Observatoire National des Établissements

**Suivi des écoulements et assecs en rivière**

ONDE est un réseau de suivi des cours d'eau permettant d'évaluer l'état des écoulements et de détecter les phénomènes d'assèchement.

---

## 📋 Définition

Réseau de points d'observation répartis sur les cours d'eau français, où des agents relèvent régulièrement l'état des écoulements selon une méthodologie standardisée.

---

## 🎯 Utilité

- **Détection des assecs** : Identification des cours d'eau à sec
- **Suivi des écoulements** : Évolution temporelle et spatiale
- **Évaluation écologique** : Impact sur les milieux aquatiques
- **Aide à la gestion** : Priorisation des actions de restauration

---

## 📊 Classification des Écoulements

| Classe | Description | Code |
|--------|-------------|------|
| Écoulement visible | Écoulement normal | 1 |
| Écoulement faible | Débit réduit mais visible | 2 |
| Non visible | Écoulement souterrain | 3 |
| Assec | Cours d'eau complètement à sec | 4 |

---

## 📁 Dans l'Application

**Module** : `src/io/download_Hubeau.py`, `src/plotting/plot_onde.py`, `src/processing/process_onde.py`

**Données** : Récupérées depuis Hub'Eau (API onde)

**Traitement** :
- Agrégation par mois/année
- Calcul de pourcentages par classe
- Génération de graphiques d'évolution

---

## 🗺️ Visualisation

**Cartes et graphiques** :
- **Cartes temporelles** : Évolution mensuelle des écoulements
- **Graphiques** : Répartition des classes par zone géographique
- **Analyse spatiale** : Identification des zones à risque

---

## 💡 Bonnes Pratiques

- **Saisonnalité** : Analyser les données par saison hydrologique
- **Comparaison interannuelle** : Identifier les tendances
- **Intégration avec VCN3** : Corréler assecs et faibles débits

---

## 🔗 Liens

- [Concept VCN3](vcn3.md)
- [Concept Hydraulicité](hydraulicite.md)
- [Module Plotting - plot_onde.py](../modules/plotting/plot_onde.md)
- [Module Processing - process_onde.py](../modules/processing/process_onde.md)


