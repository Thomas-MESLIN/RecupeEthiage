---
layout: default
title: VCN3
description: "Explication détaillée du Volume Current Non-dépassé sur 3 mois"
nav_order: 2
parent: Concepts Clés
grand_parent: ""
---

# 🔬 VCN3 - Volume Current Non-dépassé sur 3 mois

**Indicateur clé de sécheresse hydrologique**

Le VCN3 est un indicateur essentiel pour évaluer la sécheresse des cours d'eau. Il représente le volume minimal d'écoulement sur une période de 3 mois, permettant de détecter les périodes de basses eaux prolongées.

---

## 📋 Définition

**VCN3** = Volume Current Non-dépassé sur 3 mois = Débit minimal moyen sur 3 mois consécutifs.

Il s'agit du **débit moyen journalier minimal** observé sur une période glissante de 3 mois.

**Formule** : VCN3 = min(moyenne(QmnJ[i:i+90])) pour i variant sur l'année

---

## 🎯 Utilité du VCN3

### 1. Détection de Sécheresse Prolongée
- Identifie les périodes où les débits sont **structurellement bas** sur plusieurs mois
- Distingue les sécheresses **conjoncturelles** (quelques jours) des sécheresses **structurelles** (plusieurs mois)

### 2. Gestion de la Ressource
- **Seuils d'alerte** : Déclenchement de mesures de restriction
- **Planification** : Anticipation des pénuries d'eau
- **Évaluation** : Impact des sécheresses sur les écosystèmes aquatiques

### 3. Comparaison Spatiale et Temporelle
- Comparaison entre **différents bassins versants**
- Analyse de **l'évolution interannuelle**
- Étude des **tendances climatiques**

---

## 📊 Interprétation

| Plage de VCN3 | Interprétation | Niveau d'Alerte |
|---------------|----------------|----------------|
| < 10% QMNA* | **Sécheresse extrême** | 🔴 Critique |
| 10-20% QMNA | **Sécheresse sévère** | 🟠 Élevé |
| 20-40% QMNA | **Sécheresse modérée** | 🟡 Modéré |
| 40-80% QMNA | **Situation normale** | 🟢 Normal |
| > 80% QMNA | **Situation très humide** | 🟢 Favorable |

*QMNA = Module de Créance Non-Accidentel (débit moyen annuel)

---

## 🔬 Méthodologie de Calcul

### 1. Données Nécessaires
- **QmnJ** : Débit Moyen Journalier sur la période d'analyse
- **Période de référence** : 1991-2020 pour le calcul des normales

### 2. Algorithme
```python
def calculer_vcn3(serie_qmnj):
    """Calcule le VCN3 à partir d'une série de QmnJ"""
    vcn3_values = []
    
    # Parcourir la série avec une fenêtre de 3 mois (90 jours)
    for i in range(len(serie_qmnj) - 89):
        window = serie_qmnj[i:i+90]
        mean_window = window.mean()
        vcn3_values.append(mean_window)
    
    # Le VCN3 est la valeur minimale de ces moyennes
    return min(vcn3_values)
```

### 3. Implémentation dans l'Application

**Module** : [`src/processing/calcul_vcn3.py`](../modules/processing/calcul_vcn3.md)

**Fonction principale** :
```python
from src.processing.calcul_vcn3 import ensure_calcul_vcn3_calcule

ensure_calcul_vcn3_calcule("2026-06", "BSH001")
```

---

## 📁 Processus Complet

```
1. Récupération des QmnJ nettoyés
   ↓
2. Calcul des moyennes glissantes sur 3 mois
   ↓
3. Identification du minimum pour chaque année
   ↓
4. Calcul du VCN3 mensuel
   ↓
5. Comparaison avec les normales historiques
   ↓
6. Export en CSV et GeoJSON
```

---

## 🗺️ Visualisation

### Cartographie VCN3
```python
from src.plotting.plot_grandeur import create_geojson_from_periode_de_retour

create_geojson_from_periode_de_retour(
    annee_mois="2026-06",
    code_sandre="BSH001",
    is_result_plotted=True
)
```

**Résultat** : `output/QGIS/vcn3/analyse_frequence_periode/periode-de-retour-BSH001-2026-06.geojson`

---

## 📈 Étude de Cas

### Sécheresse 2025 en Auvergne-Rhône-Alpes

**Données** :
- Station : Rhône à Lyon
- VCN3 Juillet 2025 : 85 m³/s
- VCN3 moyen historique : 200 m³/s
- **VCN3 relatif** : (85/200) × 100 = 42.5%

**Interprétation** : Sécheresse modérée nécessitant une surveillance renforcée.

### Comparaison Interannuelle

| Année | VCN3 (m³/s) | % du Normal | Situation |
|-------|--------------|------------|-----------|
| 2022 | 65 | 32.5% | Sécheresse sévère |
| 2023 | 78 | 39% | Sécheresse modérée |
| 2024 | 150 | 75% | Situation normale |
| 2025 | 85 | 42.5% | Sécheresse modérée |

---

## 🔗 Complémentarité avec l'Hydraulicité

| Indicateur | Type | Période | Utilisation |
|------------|------|---------|------------|
| **Hydraulicité** | Mesure ponctuelle | Mensuelle | État actuel |
| **VCN3** | Minimum glissant | 3 mois | Sécheresse durable |

**Exemple** :
- Hydraulicité Juillet = 60% → Sécheresse **actuelle**
- VCN3 Juillet = 45% → Sécheresse **persistante** depuis mai

---

## 🎓 Tutorial Rapide

```python
# 1. Préparer les données
from src.processing.clean import ensure_historic_cleaned
ensure_historic_cleaned("BSH001", "QmnJ")

# 2. Calculer les VCN3
from src.processing.calcul_vcn3 import ensure_calcul_vcn3_calcule
ensure_calcul_vcn3_calcule("2026-06", "BSH001")

# 3. Analyser les fréquences de retour
from src.processing.calcul_frequence_periode_de_retour import ensure_frequence_non_depassement_periode_retour_calcule
ensure_frequence_non_depassement_periode_retour_calcule("2026-06", "BSH001")
```

---

## 💡 Bonnes Pratiques

- **Période de référence** : Toujours utiliser 1991-2020 pour la cohérence
- **Fenêtre glissante** : 90 jours pour 3 mois (moyenne mensuelle de 30 jours)
- **Gestion des lacunes** : Exclure les années avec données manquantes
- **Seuils d'alerte** : Adapter aux spécificités locales

---

## 🔍 Dépannage

**Problème** : VCN3 toujours égal à 0
- **Cause** : Données QmnJ manquantes ou nulles
- **Solution** : Vérifier la qualité des données sources

**Problème** : VCN3 aberrants
- **Cause** : Séries temporelles incomplètes
- **Solution** : Filtrer les séries avec < 90% de données valides

---

## 🔗 Liens Utiles

- [Module Processing - calcul_vcn3.py](../modules/processing/calcul_vcn3.md)
- [Module Processing - calcul_frequence_periode_de_retour.py](../modules/processing/calcul_frequence_periode_de_retour.md)
- [Concept Hydraulicité](hydraulicite.md)
- [Concept Période de Retour](periode_de_retour.md)