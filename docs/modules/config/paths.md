---
layout: default
title: paths.py
description: "Documentation des chemins de fichiers"
nav_order: 1
parent: Module Config
grand_parent: Modules
---

# 📁 paths.py

**Définition des chemins de base**

Ce fichier centralise la définition du dossier de sortie principal.

---

## 📋 Constante Principale

### OUTPUT_DIR

Chemin vers le dossier racine de sortie.

```python
from src.config.paths import OUTPUT_DIR

print(OUTPUT_DIR)
# Output: Path("output")
```

---

## 🎯 Utilisation

Tous les autres chemins dans l'application sont construits à partir de `OUTPUT_DIR` :

```python
from src.config.paths import OUTPUT_DIR
from pathlib import Path

# Construction de chemins
csv_path = OUTPUT_DIR / "hubeau" / "downloaded_data" / "stations.csv"
geojson_path = OUTPUT_DIR / "QGIS" / "hydraulicite" / "carte.geojson"
```

---

## 🔗 Liens

- [Module Config](index.md)
- [Module Utils - Fonctions de chemins](../../modules/utils/utils.md)


