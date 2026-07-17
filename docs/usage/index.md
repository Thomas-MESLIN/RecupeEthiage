---
layout: default
title: Utilisation
description: "Comment utiliser l'outil"
nav_order: 3
has_children: true
---

[Retour à l'accueil](index.md)

# 🎯 Utilisation de l'Outil

L'outil propose **deux modes d'utilisation** pour répondre à tous les besoins :

---

## 🔹 Option 1 : Mode Interactif

**Recommandé pour les débutants**

Le mode interactif vous guide pas à pas en vous posant des questions. C'est la méthode la plus simple pour commencer.

### Lancement

```powershell
.\venv\Scripts\python.exe main.py
```

### Fonctionnement

Le programme vous posera une série de questions :

1. **Que souhaitez-vous générer ?**
   - Carte d'HYDRAULICITE (niveaux d'eau)
   - Carte de VCN3/Périodes de retour (étiage)
   - LES DEUX cartes Hubeau
   - Extraits METEO FRANCE
   - ...

2. **Sélection de la date** (format AAAA-MM)
   - Exemple : `2026-01` pour janvier 2026

3. **Sélection du réseau SANDRE**
   - `BSH001` (par défaut)
   - `custom` (utiliser votre liste personnalisée)

4. **Options supplémentaires** selon le type de carte

### Exemple complet

```
Bienvenue dans le client de génération de cartes interactif, que souhaitez vous faire ?
1 : Générer une carte d'hydraulicité
2 : Générer une carte de vcn3/période de retour
3 : Générer les deux (lent au premier lancement)
4 : Générer des extraits MétéoFrance (défaut)
 -> 1

Choix de génération de carte : 1
Choisissez la date que vous voulez générer :
Format AAAA-MM, (mois précédent : 2026-06 par défaut)
 -> 2026-01

Mois sélectionné : 2026-01-01 00:00:00
Choisissez un réseau SANDRE : BSH001 (par défaut)
 -> 

Réseau Sandre sélectionné : BSH001
Génération en cours...
Génération terminée.
```

**Voir aussi** : [Guide détaillé du mode interactif](interactive.md)

---

## 🔹 Option 2 : Mode CLI (Ligne de Commande)

**Pour les utilisateurs avancés**

Le mode CLI permet de lancer directement une commande avec tous les paramètres.

### Structure de base

```powershell
.\venv\Scripts\python.exe main.py --type [TYPE] [autres options]
```

Voir toutes les options : 

```powershell
.\venv\Scripts\python.exe main.py --help
```

### Exemples d'utilisation

**Exemple 1 : Générer une carte d'hydraulicité pour janvier 2026**
```powershell
.\venv\Scripts\python.exe main.py --type hydraulicite --start_date 2026-01 --reseau_sandre BSH001
```

**Exemple 2 : Calculer le VCN3 pour février 2024 avec des graphiques individuels**
```powershell
.\venv\Scripts\python.exe main.py --type vcn3 --start_date 2024-02 --reseau_sandre BSH001 --vcn3_graphic
```

**Exemple 3 : Récupérer les données météo SIM2 quotidiennes pour une période**
```powershell
.\venv\Scripts\python.exe main.py --type meteo_sim2_QUOT --start_date 2023-07-01 --end_date 2023-07-31
```

**Exemple 4 : Récupérer les données ONDE pour le bassin Rhône-Méditerranée (code 06)**
```powershell
.\venv\Scripts\python.exe main.py --type onde_ALL --start_date 2026-06-01 --geographic_scale BASSIN --onde_zone_code 06
```

**Voir aussi** : [Guide détaillé du mode CLI](cli.md)

---

## 📁 Où trouver les résultats ?

Tous les fichiers générés sont stockés dans le dossier **`output/`** à la racine du projet.

### Structure du dossier de sortie

```
output/
├── QGIS/                    # Cartes générées
│   ├── hydraulicite/        # Cartes d'hydraulicité
│   ├── vcn3/                # Cartes de VCN3
│   ├── meteo/               # Cartes météo
│   └── onde/                # Cartes ONDE
├── meteoFrance/             # Données météo téléchargées
│   └── downloaded_data/     # Données brutes
├── site_station_custom/    # Listes personnalisées
└── logs/                   # Journaux d'exécution
```
