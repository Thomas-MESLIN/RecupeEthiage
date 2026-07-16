---
layout: default
title: Données
description: "Description des sources de données et formats utilisés"
nav_order: 5
parent: ""
has_children: true
---

# 📊 Données

**Sources et formats des données utilisées par l'application**

---

## 🗂️ Sources de Données

| Source | Type | Couverture | Fréquence |
|--------|------|-----------|-----------|
| [Hub'Eau](https://hubeau.eaufrance.fr/) | Hydrologie | France | Quotidienne/Mensuelle |
| [MétéoFrance](https://www.meteofrance.com/) | Météorologie | France | Quotidienne |
| [INSEE](https://www.insee.fr/) | Géographie | France | Static |
| [ONDE](https://onde.eaufrance.fr/) | Écologie | France | Mensuelle/Annuelle |

---

## 📁 Structure des Données

### Données Brutes

```
output/
├── hubeau/
│   └── downloaded_data/
│       ├── observations_elaboree/  # CSV : QmM, QmnJ
│       ├── stations/               # CSV : Métadonnées
│       └── sites/                  # CSV : Sites
│
└── meteoFrance/
    └── downloaded_data/           # CSV : Précipitations, SPI, SSWI
```

### Données Traitées

```
output/
├── hubeau/
│   └── cleaned_data/              # CSV : Données nettoyées
│
├── QmM_moyen/                    # CSV : Moyennes historiques
├── hydraulicite/                 # CSV/GeoJSON : Résultats
├── VCN3/                         # CSV/GeoJSON : VCN3 et analyses
└── meteoFrance/
    └── ...                        # GeoJSON : Cartes météo
```

---

## 🔗 Liens

- [Module IO](../modules/io/index.md)
- [Module Processing](../modules/processing/index.md)
- [Concepts Clés](../concepts/index.md)


