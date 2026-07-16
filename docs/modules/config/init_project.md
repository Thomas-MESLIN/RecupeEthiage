---
layout: default
title: init_project.py
description: "Documentation de l'initialisation du projet"
nav_order: 4
parent: Module Config
grand_parent: Modules
---

# 🚀 init_project.py

**Initialisation des dossiers et configuration**

---

## 📋 Fonction Principale

### init_project_structure

Initialise la structure des dossiers du projet.

```python
from src.config.init_project import init_project_structure

init_project_structure()
```

**Crée les dossiers** :
```
output/
├── hubeau/
│   ├── downloaded_data/
│   │   ├── observations_elaboree/
│   │   ├── stations/
│   │   └── sites/
│   └── cleaned_data/
├── QmM_moyen/
├── hydraulicite/
├── VCN3/
│   ├── moyenne_historique/
│   ├── mensuel/
│   ├── stations/
│   └── analyse_frequence_periode/
├── meteoFrance/
│   └── downloaded_data/
├── logs/
└── QGIS/
    ├── hydraulicite/
    ├── vcn3/
    │   └── analyse_frequence_periode/
    └── meteo/
```

---

## 🎯 Utilisation

Appelé automatiquement au premier lancement ou via le script d'initialisation.

```python
# Initialisation explicite
from src.config.init_project import init_project_structure
init_project_structure()
```

---

## 🔗 Liens

- [Module Config](index.md)
- [Structure des fichiers](../../data/index.md)


