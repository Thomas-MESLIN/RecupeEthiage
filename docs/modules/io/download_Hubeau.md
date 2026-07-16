---
layout: default
title: download_Hubeau.py
description: "Documentation du téléchargement des données Hub'Eau"
nav_order: 1
parent: Module IO
grand_parent: Modules
---

# 🌊 download_Hubeau.py

**Récupération des données hydrologiques depuis Hub'Eau**

---

## 📋 Fonctions Principales

### ensure_station_downloaded

S'assure que le fichier des stations est téléchargé et à jour.

```python
from src.io.download_Hubeau import ensure_station_downloaded
ensure_station_downloaded()
```

**Chemin** : `output/hubeau/downloaded_data/stations/stations.csv`

---

### ensure_sites_downloaded

S'assure que le fichier des sites est téléchargé.

```python
from src.io.download_Hubeau import ensure_sites_downloaded
ensure_sites_downloaded()
```

**Chemin** : `output/hubeau/downloaded_data/sites/sites.csv`

---

### ensure_grandeur_mensuel_downloaded

Télécharge les données mensuelles pour une grandeur donnée.

```python
from src.io.download_Hubeau import ensure_grandeur_mensuel_downloaded

ensure_grandeur_mensuel_downloaded("2026-06", "QmM")
```

**Paramètres**
- `annee_mois` : Période au format AAAA-MM
- `grandeur` : "QmM" ou "QmnJ"

**Chemin** : `output/hubeau/downloaded_data/observations_elaboree/observations-{grandeur}-AURA-{annee_mois}.csv`

---

### ensure_grandeur_historique_downloaded

Télécharge les données historiques (1991-2020) pour une grandeur.

```python
from src.io.download_Hubeau import ensure_grandeur_historique_downloaded

ensure_grandeur_historique_downloaded("QmM")
```

**Chemin** : `output/hubeau/downloaded_data/observations_elaboree/observations-{grandeur}-AURA-1991-2020.csv`

---

### ensure_onde_campagne_downloaded

Télécharge les campagnes ONDE.

```python
from src.io.download_Hubeau import ensure_onde_campagne_downloaded

ensure_onde_campagne_downloaded()
```

**Chemin** : `output/hubeau/downloaded_data/onde/campagnes_onde.csv`

---

## 🎯 Utilisation Typique

```python
from src.io.download_Hubeau import (
    ensure_station_downloaded,
    ensure_sites_downloaded,
    ensure_grandeur_mensuel_downloaded
)

# Télécharger les métadonnées
ensure_station_downloaded()
ensure_sites_downloaded()

# Télécharger les données pour juin 2026
ensure_grandeur_mensuel_downloaded("2026-06", "QmM")
ensure_grandeur_mensuel_downloaded("2026-06", "QmnJ")
```

---

## 🔗 Liens

- [Module IO](index.md)
- [Concepts Hydrologiques](../../concepts/hydraulicite.md)
- [API Hub'Eau](https://hubeau.eaufrance.fr/)


