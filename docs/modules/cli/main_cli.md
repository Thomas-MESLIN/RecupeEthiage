---
layout: default
title: main_cli.py
description: "Documentation du mode CLI"
nav_order: 1
parent: Module CLI
grand_parent: Modules
---

# 💻 main_cli.py

**Mode Command Line Interface (CLI)**

Gère l'exécution de l'outil via la ligne de commande pour une utilisation automatisée.

---

## 📋 Fonctions Principales

### setup_parser

Configure l'analyseur d'arguments de la ligne de commande.

```python
from src.cli.main_cli import setup_parser

parser = setup_parser()
args = parser.parse_args()
```

---

### mode_cli

Exécute le mode CLI avec les arguments fournis.

```python
from src.cli.main_cli import mode_cli

mode_cli(args)
```

---

### main

Fonction principale qui route selon le type de données.

```python
from src.cli.main_cli import main

if __name__ == "__main__":
    main()
```

---

## 🎯 Commandes Disponibles

### Hydraulicité

```powershell
.\venv\Scripts\python.exe main.py --type hydraulicite --start_date 2026-01 --reseau_sandre BSH001
```

### VCN3

```powershell
.\venv\Scripts\python.exe main.py --type vcn3 --start_date 2026-01 --reseau_sandre BSH001 --vcn3_graphic
```

### ONDE

```powershell
.\venv\Scripts\python.exe main.py --type onde --start_date 2026-01 --end_date 2026-06 --reseau_sandre BSH001
```

### MétéoFrance

```powershell
.\venv\Scripts\python.exe main.py --type meteofrance --start_date 2026-01 --end_date 2026-06
```

---

## ⚙️ Options Globales

| Option | Description | Type | Défaut |
|--------|-------------|------|--------|
| `--type` | Type de données à traiter | str | Obligatoire |
| `--start_date` | Date de début (AAAA-MM) | str | Obligatoire |
| `--end_date` | Date de fin (AAAA-MM) | str | `--start_date` |
| `--reseau_sandre` | Code du réseau Sandre | str | "custom" |
| `--output_path` | Chemin de sortie | str | "output/" |

---

## 💡 Exemples Complets

### Analyse complète pour un mois

```powershell
# Hydraulicité + VCN3 + graphiques
.\venv\Scripts\python.exe main.py --type hydraulicite --start_date 2026-06 --reseau_sandre BSH001
.\venv\Scripts\python.exe main.py --type vcn3 --start_date 2026-06 --reseau_sandre BSH001 --vcn3_graphic
```

### Analyse multi-mois

```powershell
# De janvier à juin 2026
.\venv\Scripts\python.exe main.py --type hydraulicite --start_date 2026-01 --end_date 2026-06 --reseau_sandre BSH001
```

---

## 🔗 Liens

- [Module CLI](index.md)
- [Mode Interactif](main_interactive.md)
- [Utilisation CLI](../../usage/cli.md)


