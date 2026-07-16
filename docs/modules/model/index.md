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
- **SIM2** : Données **interpolées** sur une grille de 8x8 km (couverture complète du territoire)
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

## 🎯 Avantages des Énumérations

### 1. **Validation automatique**

```python
# ✅ Impossible de passer une valeur invalide
def traiter_donnees(type: MeteoFranceDataType):
    pass

# ❌ Erreur de type à l'exécution
# traiter_donnees("invalid_type")  # TypeError
```

### 2. **Complétion automatique** (IDE)

Les IDE comme PyCharm ou VSCode proposent les valeurs possibles lors de la saisie.

### 3. **Documentation intégrée**

Les énumérations sont auto-documentées avec leurs valeurs possibles.

### 4. **Comparaison sécurisée**

```python
# ✅ Comparaison sûre
if data_type == MeteoFranceDataType.SIM2_MENS:
    print("Données SIM2 mensuelles")

# ❌ Comparaison peu sûre (chaînes de caractères)
if data_type == "SIM2_MENS":
    print("Données SIM2 mensuelles")
```

---

## 📊 Tableau Récapitulatif

| Énumération | Valeurs | Description | Module d'utilisation |
|-------------|---------|-------------|---------------------|
| `OndeCampagneType` | USUELLE, COMPLEMENTAIRE, ALL_CAMPAGNE | Types de campagnes ONDE | `plotting.plot_onde`, `processing.process_onde` |
| `MeteoFranceDataType` | SIM2_QUOT, SIM2_MENS, QUOT, MENS | Types de données météo | `plotting.plot_meteoFrance`, `io.download_meteoFrance` |
| `GeographicScaleClip` | NATIONAL, BASSIN, REGION_ADMINISTRATIVE, DEPARTEMENT_ADMINISTRATIF, REGION_BASSIN, DEPARTEMENT_BASSIN | Échelles géographiques | `plotting.plot_meteoFrance`, `plotting.rasterize` |

---

## 🎓 Exemples Complets

### Exemple 1 : Utilisation avec des conditions

```python
from src.model.enums import MeteoFranceDataType, GeographicScaleClip

def configurer_traitement(data_type: MeteoFranceDataType, scale: GeographicScaleClip):
    """Configure le traitement selon le type et l'échelle."""
    
    # Configuration selon le type de données
    if data_type in [MeteoFranceDataType.SIM2_QUOT, MeteoFranceDataType.SIM2_MENS]:
        print("Données SIM2 (interpolées)")
        resolution = "8x8km"
    else:
        print("Données brutes (stations)")
        resolution = "ponctuelle"
    
    # Configuration selon l'échelle
    match scale:
        case GeographicScaleClip.NATIONAL:
            print("Traitement pour toute la France")
        case GeographicScaleClip.BASSIN:
            print("Traitement par bassin")
        case GeographicScaleClip.REGION_ADMINISTRATIVE:
            print("Traitement par région administrative")
        case _:
            print(f"Traitement à l'échelle {scale}")
    
    return resolution

# Appel
configurer_traitement(
    MeteoFranceDataType.SIM2_MENS,
    GeographicScaleClip.BASSIN
)
```

### Exemple 2 : Boucle sur toutes les valeurs

```python
from src.model.enums import MeteoFranceDataType, GeographicScaleClip

# Traiter tous les types de données météo
for data_type in MeteoFranceDataType:
    print(f"Traitement de {data_type.name}...")
    # Appeler les fonctions de traitement

# Traiter toutes les échelles géographiques
for scale in GeographicScaleClip:
    print(f"Traitement à l'échelle {scale.name}...")
    # Appeler les fonctions de plotting
```

### Exemple 3 : Conversion vers des chaînes

```python
from src.model.enums import MeteoFranceDataType, GeographicScaleClip

# Obtenir le nom d'une énumération
print(MeteoFranceDataType.SIM2_MENS.name)  # "SIM2_MENS"
print(MeteoFranceDataType.SIM2_MENS.value)  # 2 (valeur numérique)

# Obtenir toutes les valeurs
print([e.name for e in MeteoFranceDataType])  # ["SIM2_QUOT", "SIM2_MENS", "QUOT", "MENS"]
print([e.value for e in MeteoFranceDataType])  # [1, 2, 3, 4]

# Vérifier si une valeur existe
if "SIM2_MENS" in [e.name for e in MeteoFranceDataType]:
    print("SIM2_MENS est une valeur valide")
```

---

## 💡 Bonnes Pratiques

### 1. Toujours utiliser les énumérations au lieu des chaînes

```python
# ✅ Bon
type_donnees = MeteoFranceDataType.SIM2_MENS

# ❌ À éviter
# type_donnees = "SIM2_MENS"  # Chaîne de caractères non validée
```

### 2. Importer les énumérations au niveau du module

```python
# ✅ Bon - Import au niveau du module
from src.model.enums import MeteoFranceDataType, GeographicScaleClip, OndeCampagneType

# Utilisation dans tout le module
def ma_fonction(type: MeteoFranceDataType):
    ...

# ❌ À éviter - Import dans chaque fonction
# def ma_fonction():
#     from src.model.enums import MeteoFranceDataType
```

### 3. Utiliser les énumérations dans les signatures de fonctions

```python
# ✅ Bon - Typage fort
def traiter_donnees(
    data_type: MeteoFranceDataType,
    scale: GeographicScaleClip = GeographicScaleClip.BASSIN
) -> None:
    ...

# ❌ À éviter - Pas de typage
# def traiter_donnees(data_type, scale="BASSIN"):
#     ...
```

---

## 📚 Voir aussi

- [Module plotting](../plotting/index.md) - Utilisation des énumérations
- [Module io](../io/index.md) - Téléchargement selon les types
- [Utilisation CLI](../../usage/cli.md) - Options basées sur les énumérations

---

[Retour aux modules](index.md)



