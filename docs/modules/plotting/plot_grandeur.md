---
layout: default
title: plot_grandeur
description: "Documentation des fonctions de création de cartes GeoJSON pour l'hydraulicité et les périodes de retour"
nav_order: 1
parent: Module Plotting
grand_parent: Modules
---

# 📈 plot_grandeur

**Création de cartes GeoJSON pour les indicateurs hydrologiques**

---

## create_geojson_from_hydraulicite

Crée une carte GeoJSON de l'hydraulicité à partir des données de stations.

```python
def create_geojson_from_hydraulicite(
    annee_mois: str,
    code_sandre: str,
    is_result_plotted: bool = False
)
```

**Paramètres**
- `annee_mois` : Période au format AAAA-MM (ex: "2026-06")
- `code_sandre` : Code du réseau Sandre (ex: "BSH001")
- `is_result_plotted` : Si True, génère également des graphiques par station

**Processus**
1. Charge les données d'hydraulicité calculées
2. Fusionne avec les géométries des stations
3. Crée un GeoDataFrame avec les propriétés d'hydraulicité
4. Exporte en GeoJSON dans `output/QGIS/hydraulicite/`

**Exemple**
```python
from src.plotting.plot_grandeur import create_geojson_from_hydraulicite

create_geojson_from_hydraulicite(
    annee_mois="2026-06",
    code_sandre="BSH001",
    is_result_plotted=True
)
```

**Résultat** : `output/QGIS/hydraulicite/hydraulicite-BSH001-2026-06.geojson`

---

## create_geojson_from_periode_de_retour

Crée une carte GeoJSON des périodes de retour VCN3.

```python
def create_geojson_from_periode_de_retour(
    annee_mois: str,
    code_sandre: str,
    is_result_plotted: bool = False
)
```

**Paramètres**
- `annee_mois` : Période au format AAAA-MM (ex: "2026-06")
- `code_sandre` : Code du réseau Sandre (ex: "BSH001")
- `is_result_plotted` : Si True, génère les graphiques individuels par station

**Processus**
1. Charge les données de périodes de retour calculées
2. S'assure que le calcul est à jour via `ensure_frequence_non_depassement_periode_retour_calcule`
3. Fusionne avec les géométries des stations
4. Crée un GeoDataFrame avec les propriétés de période de retour
5. Exporte en GeoJSON dans `output/QGIS/vcn3/analyse_frequence_periode/`

**Exemple**
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

## 🗺️ Visualisation

Les fichiers GeoJSON générés sont compatibles avec :
- **QGIS** : Logiciel SIG open-source
- **Google Earth** : Visualisation 3D
- **Applications web** : Intégration dans des cartes interactives

---

## 🔗 Liens

- [Concept Hydraulicité](../../concepts/hydraulicite.md)
- [Concept Période de Retour](../../concepts/periode_de_retour.md)
- [Module Processing - calcul_hydraulicite.py](../../modules/processing/calcul_hydraulicite.md)
- [Module Processing - calcul_frequence_periode_de_retour.py](../../modules/processing/calcul_frequence_periode_de_retour.md)


