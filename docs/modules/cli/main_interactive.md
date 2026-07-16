---
layout: default
title: main_interactive.py
description: "Documentation du mode interactif"
nav_order: 2
parent: Module CLI
grand_parent: Modules
---

# 🎮 main_interactive.py

**Mode Interactif**

Guide l'utilisateur pas à pas via des questions pour une utilisation simplifiée.

---

## 📋 Fonctions Principales

### display_menu

Affiche le menu principal et gère la sélection de l'utilisateur.

```python
from src.cli.main_interactive import display_menu

display_menu()
```

---

### ask_data_type

Demande à l'utilisateur le type de données à traiter.

```python
from src.cli.main_interactive import ask_data_type

data_type = ask_data_type()
```

**Options** :
- 1 : Hydraulicité
- 2 : VCN3
- 3 : MétéoFrance
- 4 : ONDE
- 0 : Quitter

---

### ask_date_range

Demande la période à analyser.

```python
from src.cli.main_interactive import ask_date_range

start_date, end_date = ask_date_range()
```

**Retourne** : Tuple (start_date, end_date) au format AAAA-MM

---

### ask_sandre_code

Demande le code Sandre du réseau à analyser.

```python
from src.cli.main_interactive import ask_sandre_code

code_sandre = ask_sandre_code()
```

**Défaut** : "custom"

---

## 🎯 Exécution

```python
from src.cli.main_interactive import main

if __name__ == "__main__":
    main()
```

---

## 💡 Workflow Complet

```
1. Affichage du menu principal
   ↓
2. Sélection du type de données
   ↓
3. Sélection de la période
   ↓
4. Sélection du réseau Sandre
   ↓
5. Confirmation des paramètres
   ↓
6. Exécution du traitement
   ↓
7. Affichage des résultats
```

---

## 🔗 Liens

- [Module CLI](index.md)
- [Mode CLI](main_cli.md)
- [Utilisation Interactive](../../usage/interactive.md)


