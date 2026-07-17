---
layout: default
title: Module Model
description: "Documentation du module model - Énumérations et types de données"
nav_order: 7
parent: Modules
has_children: true
---

# 📊 Module Model

**Documentation des énumérations et types de données**

Le module `model` contient **toutes les définitions de types et énumérations** utilisées dans l'application, permettant une **typage fort** et une **validation des paramètres**.

---

## 🗂️ Structure du Module

```
src/model/
└── enums.py    # Toutes les énumérations
```

---

## 📋 Énumérations Définies

### 🌊 OndeCampagneType

**Type de campagne ONDE (Observatoire National des Établissements)**

| Valeur | Description | Code |
|--------|-------------|------|
| `USUELLE` | Campagnes régulières | `"U"` |
| `COMPLEMENTAIRE` | Campagnes supplémentaires (situations particulières) | `"C"` |
| `ALL_CAMPAGNE` | Toutes les campagnes (usuelles + complémentaires) | `"A"` |

**Utilisation** :
```python
from src.model.enums import OndeCampagneType

# Sélectionner un type de campagne
campagne = OndeCampagneType.ALL_CAMPAGNE

# Comparaison
if campagne == OndeCampagneType.USUELLE:
    print("Campagne usuelle sélectionnée")
```

---

### 🌦️ MeteoFranceDataType

**Type de données météorologiques**

| Valeur | Description | Fréquence |
|--------|-------------|-----------|
| `SIM2_QUOT` | Données SIM2 quotidiennes | Quotidienne |
| `SIM2_MENS` | Données SIM2 mensuelles | Mensuelle |
| `QUOT` | Données brutes quotidiennes | Quotidienne |
| `MENS` | Données brutes mensuelles | Mensuelle |

**Différence SIM2 vs brute** :
- **SIM2** : Données **ayant subi une analyse de MétéoFrance** sur une grille de 8x8 km (couverture complète du territoire)
- **Brute** : Données de **stations ponctuelles** (mesures réelles aux points de mesure)

**Utilisation** :
```python
from src.model.enums import MeteoFranceDataType

# Sélectionner un type de données
type_donnees = MeteoFranceDataType.SIM2_MENS

# Passer à une fonction
from src.io.download_meteoFrance import get_data_in_range
from datetime import datetime

df = get_data_in_range(
    type_donnees,
    datetime(2026, 1, 1),
    datetime(2026, 1, 31)
)
```

---

### 🗺️ GeographicScaleClip

**Échelles géographiques pour le découpage des données**

| Valeur | Description | Code | Utilisation |
|--------|-------------|------|-------------|
| `NATIONAL` | Toute la France | `"NATIONAL"` | Données nationales |
| `BASSIN` | Par bassin hydrographique | `"BASSIN"` | Découpage par bassin |
| `REGION_ADMINISTRATIVE` | Par région administrative | `"REGION_ADMINISTRATIVE"` | Découpage par région administrative |
| `DEPARTEMENT_ADMINISTRATIF` | Par département administratif | `"DEPARTEMENT_ADMINISTRATIF"` | Découpage par département |
| `REGION_BASSIN` | Par région de bassin | `"REGION_BASSIN"` | Découpage par région bassin |
| `DEPARTEMENT_BASSIN` | Par département de bassin | `"DEPARTEMENT_BASSIN"` | Découpage par département bassin |

**Utilisation** :
```python
from src.model.enums import GeographicScaleClip

# Sélectionner une échelle
echelle = GeographicScaleClip.BASSIN

# Passer à une fonction de plotting
from src.plotting.plot_meteoFrance import export_all_format_geojson_range
from datetime import datetime

export_all_format_geojson_range(
    geo_scale=echelle,
    data_freq=MeteoFranceDataType.SIM2_MENS,
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31),
    is_data_aggregated=False
)
```

---

## 📊 Tableau Récapitulatif

| Énumération | Valeurs | Description | Module d'utilisation |
|-------------|---------|-------------|---------------------|
| `OndeCampagneType` | USUELLE, COMPLEMENTAIRE, ALL_CAMPAGNE | Types de campagnes ONDE | `plotting.plot_onde`, `processing.process_onde` |
| `MeteoFranceDataType` | SIM2_QUOT, SIM2_MENS, QUOT, MENS | Types de données météo | `plotting.plot_meteoFrance`, `io.download_meteoFrance` |
| `GeographicScaleClip` | NATIONAL, BASSIN, REGION_ADMINISTRATIVE, DEPARTEMENT_ADMINISTRATIF, REGION_BASSIN, DEPARTEMENT_BASSIN | Échelles géographiques | `plotting.plot_meteoFrance`, `plotting.rasterize` |

---

## 📚 Voir aussi

- [Module plotting](../plotting/index.md) - Utilisation des énumérations
- [Module io](../io/index.md) - Téléchargement selon les types
- [Utilisation CLI](../../usage/cli.md) - Options basées sur les énumérations

---

[Retour aux modules](index.md)



