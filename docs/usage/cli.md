---
layout: default
title: Mode CLI
description: "Guide détaillé du mode CLI (Command Line Interface) pour une utilisation avancée"
nav_order: 2
parent: Utilisation
---

# 💻 Mode CLI (Command Line Interface)

**Guide détaillé pour le mode CLI - Pour les utilisateurs avancés**

---

## 🚀 Lancement

```powershell
.\venv\Scripts\python.exe main.py --type [TYPE] [autres options]
```

---

## 📋 Options principales

### Argument obligatoire

| Option | Choix possibles | Description |
|--------|----------------|-------------|
| `--type` | `hydraulicite`, `vcn3`, `meteo_brut_MENS`, `meteo_sim2_MENS`, `meteo_brut_QUOT`, `meteo_sim2_QUOT`, `stations-sites`, `onde_USUELLE`, `onde_ALL` | Type de données à générer |

### Arguments de dates

| Option | Format | Description | Défaut |
|--------|--------|-------------|--------|
| `--start_date` | AAAA-MM ou AAAA-MM-JJ | Date de début (inclusive) | Premier jour du mois précédent |
| `--end_date` | AAAA-MM ou AAAA-MM-JJ | Date de fin (inclusive) | Dernier jour du mois de start_date |

### Arguments spécifiques

| Option | Valeurs | Description | Défaut |
|--------|---------|-------------|--------|
| `--reseau_sandre` | `BSH001`, `custom`, etc. | Réseau SANDRE à utiliser | `BSH001` |
| `--vcn3_graphic` | flag | Générer des graphiques individuels pour VCN3 | Non |
| `--geographic_scale` | `NATIONAL`, `BASSIN`, `REGION_ADMINISTRATIVE`, `DEPARTEMENT_ADMINISTRATIF`, `REGION_BASSIN`, `DEPARTEMENT_BASSIN` | Échelle géographique pour météo/onde | `BASSIN` |
| `--onde_zone_code` | Code zone (ex: `06`) | Code de la zone géographique pour ONDE | `01` |
| `--meteo_aggregate` | flag | Aggréger les données météo sur la période | Non |
| `--meteo_no_index_update` | flag | Désactiver la mise à jour de l'index météo | Non |
| `--meteo_no_update` | flag | Désactiver la mise à jour des données météo | Non |

---

## 🎯 Exemples concrets

### 📊 Données Hydrologiques

#### Hydraulicité pour un mois spécifique
```powershell
.\venv\Scripts\python.exe main.py \
  --type hydraulicite \
  --start_date 2026-01 \
  --reseau_sandre BSH001
```

**Résultat** : `output/QGIS/hydraulicite/hydraulicite-BSH001-2026-01.geojson`

#### VCN3 avec graphiques pour chaque station
```powershell
.\venv\Scripts\python.exe main.py \
  --type vcn3 \
  --start_date 2024-02 \
  --reseau_sandre BSH001 \
  --vcn3_graphic
```

**Résultat** :
- `output/QGIS/frequence_periode_de_retour/periode-de-retour-BSH001-2024-02.geojson`
- Graphiques : `output/VCN3/plot_stations/`

#### Les deux (hydraulicité + VCN3) avec graphiques
```powershell
.\venv\Scripts\python.exe main.py \
  --type vcn3 \
  --start_date 2024-02 \
  --reseau_sandre BSH001 \
  --vcn3_graphic
```

> **Note** : Il n'existe pas d'option "les deux" en CLI. Pour générer les deux, lancez deux commandes séparées.

---

### 🌦️ Données Météo France

#### Données SIM2 quotidiennes pour une période
```powershell
.\venv\Scripts\python.exe main.py \
  --type meteo_sim2_QUOT \
  --start_date 2023-07-01 \
  --end_date 2023-07-31
```

**Résultat** : Données quotidiennes SIM2 pour juillet 2023

#### Données SIM2 mensuelles agrégées
```powershell
.\venv\Scripts\python.exe main.py \
  --type meteo_sim2_MENS \
  --start_date 2025-09-01 \
  --end_date 2026-07-01 \
  --meteo_aggregate
```

**Résultat** : Données mensuelles SIM2 agrégées sur la période, avec somme des précipitations

#### Données brutes quotidiennes
```powershell
.\venv\Scripts\python.exe main.py \
  --type meteo_brut_QUOT \
  --start_date 2026-06-10 \
  --end_date 2026-06-20
```

---

### 🌊 Données ONDE

#### Campagnes usuelles ONDE pour un bassin
```powershell
.\venv\Scripts\python.exe main.py \
  --type onde_USUELLE \
  --start_date 2026-06-01 \
  --geographic_scale BASSIN \
  --onde_zone_code 06
```

**Résultat** : Données ONDE pour le bassin Rhône-Méditerranée (code 06)

#### Toutes les campagnes ONDE (usuelles + complémentaires)
```powershell
.\venv\Scripts\python.exe main.py \
  --type onde_ALL \
  --start_date 2026-06-01 \
  --geographic_scale REGION_ADMINISTRATIVE \
  --onde_zone_code 84
```

**Résultat** : Données ONDE pour la région Auvergne-Rhône-Alpes (code 84)

---

### 📍 Stations et Sites

#### Générer les fichiers de stations et sites
```powershell
.\venv\Scripts\python.exe main.py \
  --type stations-sites \
  --start_date 2026-01 \
  --reseau_sandre custom
```

**Résultat** :
- `output/QGIS/stations/stations-ouverte-custom-2026-01.geojson`
- `output/QGIS/sites/sites-custom.geojson`
- `output/QGIS/stations/stations-custom.geojson`
- `output/QGIS/stations/stations.geojson`
- `output/QGIS/sites/sites.geojson`

---

## 📚 Codes géographiques utiles

### Bassins

| Code | Bassin |
|------|--------|
| `01` | Artois-Picardie |
| `02` | Meuse |
| `03` | Moselle |
| `04` | Rhin |
| `05` | Loire-Bretagne |
| `06` | Rhône-Méditerranée |
| `07` | Adour-Garonne |
| `08` | Garonne |
| `09` | Charente |
| `10` | Seine-Normandie |

### Régions Administratives

| Code | Région |
|------|--------|
| `84` | Auvergne-Rhône-Alpes |
| `27` | Bourgogne-Franche-Comté |
| `53` | Bretagne |
| `24` | Centre-Val de Loire |
| `94` | Corse |
| `44` | Grand Est |
| `11` | Île-de-France |
| `32` | Hauts-de-France |
| `93` | Normandie |
| `75` | Nouvelle-Aquitaine |
| `76` | Occitanie |
| `52` | Pays de la Loire |
| `91` | Provence-Alpes-Côte d'Azur |

---

## 🎯 Astuces CLI

### 1. Voir l'aide complète
```powershell
.\venv\Scripts\python.exe main.py --help
```

### 2. Utiliser des listes personnalisées
```powershell
--reseau_sandre custom
```

Cela utilise les stations définies dans `liste_site_custom.csv` et `liste_station_custom.csv` à la racine du projet.

### 3. Désactiver la mise à jour des données
```powershell
--meteo_no_update
```

Utile pour les tests ou lorsque vous travaillez hors ligne.

### 4. Échelles géographiques disponibles

```powershell
--geographic_scale NATIONAL        # Toute la France
--geographic_scale BASSIN         # Par bassin (défaut)
--geographic_scale REGION_ADMINISTRATIVE  # Par région administrative
--geographic_scale DEPARTEMENT_ADMINISTRATIF  # Par département
--geographic_scale REGION_BASSIN  # Par région bassin
--geographic_scale DEPARTEMENT_BASSIN  # Par département bassin
```

---

## 🔄 Scripts d'automatisation

### Exemple 1 : Générer toutes les données du mois précédent

```powershell
# Récupérer la date du mois précédent
$month = (Get-Date).AddMonths(-1).ToString("yyyy-MM")

# Générer hydraulicité et VCN3
.\venv\Scripts\python.exe main.py --type hydraulicite --start_date $month --reseau_sandre BSH001
.\venv\Scripts\python.exe main.py --type vcn3 --start_date $month --reseau_sandre BSH001 --vcn3_graphic
```

### Exemple 2 : Générer les données météo pour toute l'année

```powershell
# Générer pour chaque mois de l'année 2025
for $month in @("01","02","03","04","05","06","07","08","09","10","11","12") {
    .\venv\Scripts\python.exe main.py \
        --type meteo_sim2_MENS \
        --start_date "2025-$month" \
        --end_date "2025-$month"
}
```

### Exemple 3 : Mettre à jour toutes les données ONDE pour un bassin

```powershell
# Pour le bassin Rhône-Méditerranée (06)
.\venv\Scripts\python.exe main.py \
  --type onde_ALL \
  --start_date 2024-01-01 \
  --end_date 2026-06-30 \
  --geographic_scale BASSIN \
  --onde_zone_code 06
```

---

## ⚠️ Erreurs courantes et solutions

### Erreur : "Le code pour la zone géographique n'est pas précisé"

**Solution** : Vérifiez que vous avez bien spécifié `--onde_zone_code` ou `--code_zone` selon le type.

### Erreur : "Aucune zone trouvée avec le code XX"

**Solution** : Vérifiez le code géographique. Consultez les [codes géographiques](#codes-géographiques-utilises).

### Erreur : "L'intervalle de données est vide"

**Solution** : Vérifiez que vos dates sont valides et que des données existent pour cette période.

### Erreur : "La colonne XX n'existe pas dans le DataFrame"

**Solution** : Vérifiez que vous utilisez le bon type de données. Certaines colonnes sont spécifiques à certains types.

---

## 📊 Tableau récapitulatif des commandes

| Objectif | Commande |
|----------|----------|
| Hydraulicité du mois dernier | `--type hydraulicite` |
| VCN3 du mois dernier | `--type vcn3` |
| VCN3 avec graphiques | `--type vcn3 --vcn3_graphic` |
| Météo SIM2 quotidienne | `--type meteo_sim2_QUOT --start_date AAAA-MM-JJ --end_date AAAA-MM-JJ` |
| Météo SIM2 mensuelle | `--type meteo_sim2_MENS --start_date AAAA-MM --end_date AAAA-MM` |
| Météo SIM2 agrégée | `--type meteo_sim2_MENS --start_date AAAA-MM --end_date AAAA-MM --meteo_aggregate` |
| ONDE usuelle | `--type onde_USUELLE --start_date AAAA-MM --geographic_scale BASSIN --onde_zone_code XX` |
| ONDE toutes campagnes | `--type onde_ALL --start_date AAAA-MM --geographic_scale BASSIN --onde_zone_code XX` |
| Stations et sites | `--type stations-sites` |

---

## 🎯 Prochaines étapes

- [Mode Interactif](interactive.md) - Pour une approche guidée
- [Module Plotting](modules/plotting/index.md) - Documentation technique détaillée
- [Concepts Clés](concepts/index.md) - Comprendre les indicateurs



