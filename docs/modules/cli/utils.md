---
layout: default
title: utils.py
description: "Documentation des utilitaires CLI"
nav_order: 3
parent: Module CLI
grand_parent: Modules
---

# 🛠️ utils.py

**Fonctions utilitaires pour le CLI**

---

## 📋 Fonctions

### get_user_input

Demande une entrée à l'utilisateur avec validation.

```python
from src.cli.utils import get_user_input

response = get_user_input("Entrez votre choix : ", ["1", "2", "3"])
```

**Paramètres**
- `prompt` : Message à afficher
- `valid_options` : Options valides

---

### validate_date

Valide une date au format AAAA-MM.

```python
from src.cli.utils import validate_date

if validate_date("2026-06"):
    print("Date valide")
```

---

## 🔗 Liens

- [Module CLI](index.md)
- [Mode Interactif](main_interactive.md)
- [Mode CLI](main_cli.md)