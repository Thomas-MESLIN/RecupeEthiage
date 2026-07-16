---
layout: default
title: Hydraulicité
description: "Explication détaillée du concept d'hydraulicité"
nav_order: 1
parent: Concepts Clés
grand_parent: ""
---

# 💧 Hydraulicité

**Indicateur clé pour évaluer l'état des ressources en eau**

L'hydraulicité est un indicateur fondamental en hydrologie qui permet de comparer les débits observés avec les débits moyens historiques. Elle fournit une mesure normalisée de l'abondance ou de la rareté de la ressource en eau.

---

## 📋 Définition

L'**hydraulicité** mesure le rapport entre le débit observé sur une période donnée et le débit moyen historique sur la même période. Elle exprime ainsi l'écart par rapport à la normale sous forme d'un ratio ou d'un pourcentage.

**Formule de base**
```
Hydraulicité = (Débit Observé / Débit Moyen Historique) × 100
```

---

## 🎯 À quoi sert l'hydraulicité ?

### 1. Évaluation de la Ressource en Eau

L'hydraulicité permet de :
- **Identifier les périodes d'abondance** : Hydraulicité > 100%
- **Détecter les périodes de pénurie** : Hydraulicité < 100%
- **Quantifier l'intensité des écarts** : Plus l'écart à 100% est grand, plus la situation est exceptionnelle

### 2. Gestion des Ressources

Les gestionnaires utilisent l'hydraulicité pour :
- **Prioriser les usages** en période de faible hydraulicité
- **Déclencher des alertes** sécheresse ou crue
- **Planifier les prélèvements** en fonction de la ressource disponible

### 3. Comparaison Spatio-Temporelle

L'hydraulicité permet de :
- **Comparer différents bassins** entre eux
- **Analyser l'évolution temporelle** sur plusieurs années
- **Identifier les tendances** climatiques et hydrologiques

---

## 📊 Interprétation des Valeurs

| Plage de Valeurs | Interprétation | Niveau d'Alerte |
|------------------|----------------|----------------|
| < 40% | **Très faible** | 🔴 Alerte maximale |
| 40% - 70% | **Faible** | 🟡 Alerte modérée |
| 70% - 130% | **Normale** | 🟢 Situation normale |
| 130% - 160% | **Élevée** | 🟢 Situation favorable |
| > 160% | **Très élevée** | 🟢 Situation très favorable |

### Exemple d'interprétation

```
Bassin : Loire à Orléans
Mois : Juillet 2026
Hydraulicité : 55%

Interprétation : Le débit de la Loire en juillet 2026 est 55% du débit moyen historique. 
Cela correspond à une situation de faible hydraulicité, nécessitant une vigilance accrue.
```

---

## 🔬 Calcul de l'Hydraulicité

### 1. Données Nécessaires

Pour calculer l'hydraulicité, il faut :

- **Débit Moyen Mensuel (QmM) actuel** : Mesure du débit moyen pour le mois en cours
- **Débit Moyen Mensuel historique** : Moyenne du QmM pour le même mois sur la période de référence (1991-2020)

### 2. Période de Référence

La période de référence standard utilisée dans l'application est **1991-2020** :
- 30 ans de données historiques
- Période recommandée par l'Organisation Mondiale de la Météorologie (OMM)
- Permet une bonne représentativité du climat actuel

### 3. Méthode de Calcul

L'application calcule l'hydraulicité comme suit :

```python
# Pseudo-code du calcul
def calculer_hydraulicite(qmm_observé, qmm_moyen_historique):
    if qmm_moyen_historique == 0:
        return None  # Cas particulier à gérer
    
    hydraulicité = (qmm_observé / qmm_moyen_historique) * 100
    return hydraulicité
```

---

## 📁 Implémentation dans l'Application

### Module Responsable

Le calcul de l'hydraulicité est implémenté dans le module [`src/processing/calcul_hydraulicite.py`](../modules/processing/calcul_hydraulicite.md).

### Fonction Principale

```python
from src.processing.calcul_hydraulicite import calcul_hydraulicite_mensuel

# Calcul de l'hydraulicité pour un mois donné
calcul_hydraulicite_mensuel(
    annee_mois="2026-06",
    code_sandre="BSH001"
)
```

### Processus Complet

```
1. Récupération des données QmM nettoyées pour le mois actuel
   ↓
2. Calcul du QmM moyen historique (1991-2020) pour le même mois
   ↓
3. Fusion des données par station
   ↓
4. Calcul du rapport : QmM_observé / QmM_moyen_historique
   ↓
5. Export des résultats en CSV
   ↓
6. Visualisation possible en GeoJSON
```

---

## 🗺️ Visualisation

### Cartographie de l'Hydraulicité

L'application permet de générer des cartes d'hydraulicité au format **GeoJSON**, compatibles avec :
- **QGIS** (Logiciel SIG open-source)
- **Google Earth**
- **Applications web** de cartographie

### Exemple de Visualisation

```python
from src.plotting.plot_grandeur import create_geojson_from_hydraulicite

# Générer une carte d'hydraulicité
create_geojson_from_hydraulicite(
    annee_mois="2026-06",
    code_sandre="BSH001"
)
```

**Résultat** : Fichier `output/QGIS/hydraulicite/hydraulicite-BSH001-2026-06.geojson`

### Palette de Couleurs Standard

L'application utilise une palette de couleurs standardisée pour la visualisation :

| Plage d'Hydraulicité | Couleur | Code Hexadécimal |
|---------------------|---------|------------------|
| < 40% | Rouge foncé | #8B0000 |
| 40-70% | Orange | #FF8C00 |
| 70-100% | Jaune | #FFD700 |
| 100-130% | Vert clair | #90EE90 |
| 130-160% | Vert | #008000 |
| > 160% | Bleu | #0000FF |

---

## 📈 Étude de Cas : Application Pratique

### Scénario : Sécheresse Estivale 2025

**Contexte** : L'été 2025 a été particulièrement sec en Auvergne-Rhône-Alpes.

**Données** :
```
Bassin : Rhône à Lyon
Période : Juillet 2025
QmM observés : 150 m³/s
QmM moyen historique (1991-2020) : 300 m³/s

Calcul : (150 / 300) × 100 = 50%
```

**Interprétation** : 
- Hydraulicité de 50% → Situation de **faible hydraulicité**
- Nécessite une **vigilance accrue** sur les usages
- Peut entraîner des **restrictions de prélèvement**

**Actions** :
1. Activation du plan sécheresse
2. Sensibilisation des usagers
3. Suivi renforcé des cours d'eau

### Scénario : Crue Hivernale 2026

**Contexte** : L'hiver 2025-2026 a connu des précipitations abondantes.

**Données** :
```
Bassin : Saône à Chalon
Période : Janvier 2026
QmM observés : 800 m³/s
QmM moyen historique (1991-2020) : 400 m³/s

Calcul : (800 / 400) × 100 = 200%
```

**Interprétation** :
- Hydraulicité de 200% → Situation d'**hydraulicité très élevée**
- Risque de **crue** et d'**inondation**
- Ressource en eau **abondante**

**Actions** :
1. Surveillance des niveaux
2. Prévision des crues
3. Gestion des retenues d'eau

---

## 🔗 Liens avec Autres Indicateurs

### Complémentarité avec le VCN3

- **Hydraulicité** : Mesure **ponctuelle** (mensuelle) de la ressource
- **VCN3** : Mesure du **débit minimum sur 3 mois** (indicateur de sécheresse durable)

**Exemple** :
- Hydraulicité faible en juillet → **Sécheresse actuelle**
- VCN3 faible en septembre → **Sécheresse persistante** depuis juillet

### Relation avec les Indicateurs Météorologiques

| Indicateur | Relation avec l'Hydraulicité | Délai d'Impact |
|------------|-------------------------------|----------------|
| **SPI** (Indice de Précipitation) | Précipitation → Débit | 1-3 mois |
| **SSWI** (Humidité des Sols) | Sol saturé → Ruissellement | 1-2 mois |
| **Température** | Évapotranspiration → Baisse du débit | Immédiat |

---

## 🎓 Tutorial Pratique

### Étape 1 : Préparation des Données

```python
from src.processing.clean import ensure_historic_cleaned

# S'assurer que les données historiques sont disponibles
ensure_historic_cleaned("BSH001", "QmM")
```

### Étape 2 : Calcul de l'Hydraulicité

```python
from src.processing.calcul_hydraulicite import calcul_hydraulicite_mensuel

# Calculer l'hydraulicité pour le mois courant
calcul_hydraulicite_mensuel(
    annee_mois="2026-06",
    code_sandre="BSH001"
)
```

### Étape 3 : Visualisation

```python
from src.plotting.plot_grandeur import create_geojson_from_hydraulicite

# Générer la carte
create_geojson_from_hydraulicite(
    annee_mois="2026-06",
    code_sandre="BSH001"
)
```

### Étape 4 : Analyse

```python
import pandas as pd
from src.utils.utils import get_path_hydraulicite

# Charger les résultats
df_hydraulicite = pd.read_csv(get_path_hydraulicite("BSH001", "2026-06"))

# Analyser les résultats
moyenne_hydraulicite = df_hydraulicite["hydraulicite"].mean()
min_hydraulicite = df_hydraulicite["hydraulicite"].min()
max_hydraulicite = df_hydraulicite["hydraulicite"].max()

print(f"Hydraulicité moyenne : {moyenne_hydraulicite:.1f}%")
print(f"Hydraulicité minimale : {min_hydraulicite:.1f}%")
print(f"Hydraulicité maximale : {max_hydraulicite:.1f}%")

# Identifier les stations problématiques
stations_faible = df_hydraulicite[df_hydraulicite["hydraulicite"] < 70]
print(f"Stations avec faible hydraulicité : {len(stations_faible)}")
```

---

## 💡 Astuces et Bonnes Pratiques

### 1. Choix de la Période de Référence

- **1991-2020** : Période standard recommandée
- **1981-2010** : Alternative parfois utilisée
- **À éviter** : Périodes trop courtes (< 20 ans) ou trop anciennes

### 2. Gestion des Stations à Données Manquantes

```python
# Exclure les stations avec des données manquantes
valid_stations = df_hydraulicite.dropna(subset=["hydraulicite"])
```

### 3. Calcul de Moyennes Territoriales

```python
# Calculer la moyenne par bassin versant
moyenne_bassin = df_hydraulicite.groupby("code_bassin")["hydraulicite"].mean()
```

### 4. Suivi Temporel

```python
# Analyser l'évolution sur plusieurs mois
moyennes_mensuelles = []
for mois in ["2026-01", "2026-02", "2026-03"]:
    df = pd.read_csv(get_path_hydraulicite("BSH001", mois))
    moyennes_mensuelles.append(df["hydraulicite"].mean())
```

---

## 🔍 Dépannage

### Problème : Valeurs d'hydraulicité aberrantes

**Cause possible** : Données manquantes ou erreurs de mesure

**Solution** :
```python
# Vérifier les données sources
df_clean = pd.read_csv(get_path_clean_csv("BSH001", "2026-06", "QmM"))
print(f"Nombre de valeurs manquantes : {df_clean['resultat_obs_elab'].isna().sum()}")
```

### Problème : Hydraulicité toujours à 100%

**Cause possible** : Utilisation des mêmes données pour l'observé et l'historique

**Solution** :
```python
# Vérifier que l'on utilise bien des périodes différentes
print(f"Période observée : 2026-06")
print(f"Période historique : 1991-2020")
```

### Problème : Division par zéro

**Cause possible** : Station avec QmM moyen historique égal à 0

**Solution** :
```python
# Filtrer les stations avec QmM moyen nul
valid_data = df[df["QmM_moyenne"] > 0]
```

---

## 📚 Références et Lecture Complémentaire

### Documentation Officielle

- **Hub'Eau** : [Documentation sur les indicateurs hydrologiques](https://hubeau.eaufrance.fr/)
- **Banque Hydro** : [Base de données hydrométriques](https://www.hydro.eaufrance.fr/)

### Ouvrages de Référence

- "Hydrologie : Une science pour l'ingénieur" - André Musy et Lionel De-cluster
- "Hydrologie continentale" - Jean Margat

### Sites Web Utiles

- [Portail Hydrologique Français](https://www.hydro.eaufrance.fr/)
- [Banque de données Ades](https://ades.eaufrance.fr/)
- [Service Central d'Hydrométéorologie et d'Appui à la Prévision des Inondations (SCHAPI)](https://www.schapi.fr/)

---

## 🔗 Liens Internes

- [Module Processing - calcul_hydraulicite.py](../modules/processing/calcul_hydraulicite.md)
- [Module Plotting - Visualisation de l'hydraulicité](../modules/plotting/plot_grandeur.md)
- [Concept VCN3](vcn3.md) - Indicateur complémentaire
- [Concept Période de Retour](periode_de_retour.md) - Analyse statistique
- [Tutoriel : Analyse Complète](../../usage/cli.md#analyse-hydrologique-complète)

---

*Dernière mise à jour : {{ "now" | date: "%d %B %Y" }}*