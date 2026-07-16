---
layout: default
title: Mode Interactif
description: "Guide détaillé du mode interactif pour générer des cartes et données"
nav_order: 1
parent: Utilisation
---

# 🎮 Mode Interactif

**Guide détaillé pour le mode interactif - Recommandé pour les débutants**

---

## 🚀 Lancement

Pour lancer le mode interactif, exécutez simplement :

```bash
.\venv\Scripts\python.exe main.py
```

---

## 📋 Menu Principal

Le programme vous propose 4 options principales :

```
Bienvenue dans l'outil de génération de cartes
Que souhaitez-vous générer ?

1 : Générer une carte d'HYDRAULICITE (niveaux d'eau)
2 : Générer une carte de VCN3/Périodes de retour (étiage)
3 : Générer LES DEUX cartes Hubeau (plus long au premier lancement)
4 : Générer des extraits METEO FRANCE (par défaut)
```

---

## 🔹 Option 1 : Carte d'Hydraulicité

### Description

L'**hydraulicité** est un indicateur qui mesure le **niveau d'eau actuel par rapport à la normale**.
- **> 100%** : Le débit est supérieur à la normale (situation humide)
- **= 100%** : Le débit est normal
- **< 100%** : Le débit est inférieur à la normale (situation sèche)

### Étapes

1. **Sélectionnez l'option 1**
2. **Choisissez le mois** (format AAAA-MM)
   - Exemple : `2026-01` pour janvier 2026
   - Par défaut : le mois précédent
3. **Choisissez un réseau SANDRE**
   - `1` : BSH001 (par défaut)
   - `2` : custom (utiliser votre liste personnalisée)
4. **Génération**
   - Le programme génère automatiquement :
     - La carte d'hydraulicité
     - Les stations ouvertes pour le mois sélectionné
     - Les sites correspondant au réseau

### Résultat

- Fichier GeoJSON : `output/QGIS/hydraulicite/hydraulicite-{code_sandre}-{annee_mois}.geojson`
- Visualisable dans QGIS ou tout logiciel SIG

---

## 🔹 Option 2 : Carte de VCN3

### Description

Le **VCN3** (Volume Current Non-dépassé sur 3 mois) est un indicateur utilisé pour évaluer la **sécheresse**. Il représente le volume d'eau minimal qui n'a pas été dépassé pendant 3 mois consécutifs.

Le programme calcule aussi :
- **Période de retour** : Combien de temps en moyenne il faut attendre pour revoir un tel niveau bas
- **Fréquence de non-dépassement** : La probabilité que ce niveau ne soit pas dépassé

### Étapes

1. **Sélectionnez l'option 2**
2. **Choisissez le mois** (format AAAA-MM)
3. **Choisissez un réseau SANDRE**
4. **Souhaitez-vous générer les graphiques ?** (o/n)
   - **o** : Génère des graphiques individuels pour chaque station (recommandé pour l'analyse)
   - **n** : Génère uniquement les données sans graphiques
5. **Génération**

### Résultat avec graphiques

- Fichier GeoJSON : `output/QGIS/frequence_periode_de_retour/periode-de-retour-{code_sandre}-{annee_mois}.geojson`
- Graphiques par station : `output/VCN3/plot_stations/`
  - `analyse-frequentielle-{code_station}-{mois}.png`
  - `periode-de-retour-{code_station}-{mois}.png`

### Résultat sans graphiques

- Seuls les fichiers GeoJSON sont générés

---

## 🔹 Option 3 : Les Deux Cartes

Combinaison des options 1 et 2. **Plus long au premier lancement** car il calcule les deux indicateurs.

### Étapes

1. **Sélectionnez l'option 3**
2. **Choisissez le mois**
3. **Choisissez un réseau SANDRE**
4. **Souhaitez-vous générer les graphiques ?** (pour le VCN3 uniquement)
5. **Génération**

### Résultat

- Tous les fichiers des options 1 et 2
- Tempo de calcul environ 2x plus long

---

## 🔹 Option 4 : Extraits Météo France (par défaut)

### Description

Génère des extraits de données météorologiques à partir des données MétéoFrance.

### Étapes

1. **Sélectionnez l'option 4**
2. **Sélection de l'échelle temporelle**
   - `1` : MENSUELLE
   - `2` : QUOTIDIENNE (par défaut)
3. **Sélection du type de données**
   - `1` : Données brutes (sans pré-calcul)
   - `2` : SIM2 (par défaut - données interpolées sur grille 8x8km)
4. **Sélection des dates**
   - Date de début (format AAAAMM ou AAAAMMJJ)
   - Date de fin (format AAAAMM ou AAAAMMJJ)
5. **Agrégation des données** (o/n)
   - **o** : Les données sont agrégées sur la période
   - **n** : Des graphiques jour par jour sont générés
6. **Mise à jour des données** (o/n)
   - **o** : Téléchargement des nouvelles données disponibles
   - **n** : Utilisation des données existantes
7. **Mise à jour de l'index** (si mise à jour des données = oui)
   - **o** : Mise à jour de l'index de correspondance
   - **n** : Utilisation de l'index existant

### Résultat

- Fichiers GeoJSON : `output/QGIS/meteoFrance/`
- Graphiques par zone géographique : `output/QGIS/meteoFrance/{type}/plots/`
- Données brutes : `output/meteoFrance/downloaded_data/`

---

## 📋 Tableau récapitulatif

| Option | Type | Durée | Graphiques | Données générées |
|--------|------|-------|-----------|------------------|
| 1 | Hydraulicité | 1 mois | Non | GeoJSON |
| 2 | VCN3 | 1 mois | Optionnel | GeoJSON + PNG |
| 3 | Les deux | 1 mois | Optionnel | GeoJSON + PNG |
| 4 | Météo France | Intervalle | Optionnel | GeoJSON + PNG |

---

## ⚠️ Conseils

1. **Première utilisation** : Commencez par le mode interactif pour comprendre les options
2. **Données historiques** : Le premier lancement peut être long (téléchargement des données)
3. **Espace disque** : Prévoyez au moins 1 Go d'espace libre pour les données
4. **Mise à jour** : Utilisez l'option de mise à jour régulièrement pour avoir les dernières données

---

## 🎯 Prochaines étapes

- [Mode CLI](cli.md) - Pour automatiser vos tâches
- [Concepts Clés](concepts/index.md) - Comprendre les indicateurs
- [Module Plotting](modules/plotting/index.md) - Documentation technique détaillée
