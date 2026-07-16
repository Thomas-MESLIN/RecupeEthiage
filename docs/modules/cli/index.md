---
layout: default
title: Module CLI
description: "Documentation du module d'interface en ligne de commande"
nav_order: 5
parent: Modules
has_children: true
---

# 🎮 Module CLI

**Documentation de l'interface en ligne de commande et du mode interactif**

Le module `cli` gère **toute l'interaction avec l'utilisateur**, que ce soit via la ligne de commande (CLI) ou le mode interactif.

---

## 🗂️ Structure du Module

```
src/cli/
├── __init__.py
├── main_cli.py         # Mode CLI
├── main_interactive.py # Mode interactif
└── utils.py            # Fonctions utilitaires pour le CLI
```

---

## 📋 Modules par Fichier

### 💻 [main_cli.py](main_cli.md)

**Gère le mode CLI (Command Line Interface)** - Pour une utilisation automatisée.

Fonctionnalités principales :
- Parsing des arguments en ligne de commande
- Validation des paramètres
- Appel des fonctions de traitement appropriées
- Gestion des options spécifiques à chaque type de données

**Points d'entrée** :
- `setup_parser()` : Configure l'analyseur d'arguments
- `mode_cli(args)` : Exécute le mode CLI avec les arguments fournis
- `main()` : Fonction principale qui route selon le type

**Utilisation** :
```powershell
# Exemple de commandes
.\venv\Scripts\python.exe main.py --type hydraulicite --start_date 2026-01 --reseau_sandre BSH001
.\venv\Scripts\python.exe main.py --type vcn3 --start_date 2026-01 --reseau_sandre BSH001 --vcn3_graphic
```

### 🎮 [main_interactive.py](main_interactive.md)

**Gère le mode interactif** - Pour une utilisation guidée.

Fonctionnalités principales :
- Affichage de menus
- Saisie utilisateur avec validation
- Guidage pas à pas
- Appel des mêmes fonctions que le mode CLI

**Fonctions principales** :
- `mode_interactif()` : Point d'entrée du mode interactif
- `generer_carte_hubeau()` : Génération des cartes hydrologiques
- `generer_carte_meteo()` : Génération des cartes météorologiques
- `demander_avec_choix()` : Saisie avec sélection parmi des options
- `demander_ou_non()` : Saisie oui/non
- `demander_date()` : Saisie d'une date

**Utilisation** :
```powershell
# Lancer le mode interactif
.\venv\Scripts\python.exe main.py
```

### 🧰 [utils.py](utils.md)

**Fonctions utilitaires pour le CLI et le mode interactif.**

Fonctionnalités principales :
- Conversion des chaînes de dates en objets datetime
- Validation des entrées utilisateur
- Formatage des dates
- Gestion des erreurs

**Utilisation** :
```python
from src.cli.utils import formater_date_vers_datetime, demander_date

# Convertir une chaîne en datetime
date = formater_date_vers_datetime("2026-01", est_debut=True)

# Demander une date à l'utilisateur
date_selectionnee = demander_date("Choisissez une date", "AAAA-MM")
```

---

## 🎯 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                                │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  parseur = setup_parser()                                 ││
│  │  args = parseur.parse_args()                              ││
│  │  if args.type is None:                                     ││
│  │      mode_interactif()                                    ││
│  │  else:                                                     ││
│  │      mode_cli(args)                                        ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                    │                        │
                    ▼                        ▼
┌───────────────────────────┐    ┌─────────────────────────────┐
│      Mode Interactif       │    │        Mode CLI               │
│  (main_interactive.py)     │    │      (main_cli.py)            │
│                            │    │                              │
│ - Menus guidés            │    │ - Arguments en ligne         │
│ - Saisie interactive       │    │ - Validation automatique    │
│ - Questions/réponses       │    │ - Scripts automatisés        │
│ - Appel des fonctions       │    │ - Appel des fonctions        │
└───────────────────────────┘    └─────────────────────────────┘
                    │                        │
                    └────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    Modules de Traitement                     │
│  (plotting, processing, io, etc.)                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Comparaison Mode Interactif vs CLI

| Critère | Mode Interactif | Mode CLI |
|---------|----------------|---------|
| **Facilité d'utilisation** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Rapidité** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Automatisation** | ⭐ | ⭐⭐⭐⭐⭐ |
| **Approprié pour** | Débutants, exploration | Scripts, intégration |
| **Validation** | Interactive | Automatique |
| **Historique** | Pas de trace | Commandes enregistrables |

---

## 🎓 Exemple : Ajouter une Nouvelle Option

### Étape 1 : Ajouter dans le parseur CLI

```python
# Dans main_cli.py, fonction setup_parser()

parser.add_argument(
    "--nouvelle_option",
    action='store_true',
    help="Description de la nouvelle option"
)
```

### Étape 2 : Gérer dans mode_cli()

```python
# Dans main_cli.py, fonction mode_cli() ou main()

def main(type_carte, ..., nouvelle_option=False):
    if nouvelle_option:
        print("Nouvelle option activée")
        # Appeler la fonction correspondante
```

### Étape 3 : Ajouter dans le mode interactif

```python
# Dans main_interactive.py

nouvelle_option_active = demander_ou_non(
    "Souhaitez-vous activer la nouvelle option ?"
)

# Appeler avec le paramètre
generer_carte(..., nouvelle_option=nouvelle_option_active)
```

---

## 💡 Bonnes Pratiques

### 1. Toujours valider les entrées utilisateur

```python
# ✅ Bon - Validation dans le mode interactif
while True:
    choix = input("Sélectionnez une option (1-4) : ")
    if choix in ["1", "2", "3", "4"]:
        break
    print("Choix invalide, veuillez réessayer")

# Dans main_cli.py, argparse gère la validation
```

### 2. Utiliser des messages d'erreur clairs

```python
# ✅ Bon - Message d'erreur explicite
if not path.exists():
    raise FileNotFoundError(
        f"Le fichier {path} n'existe pas. "
        "Veuillez d'abord télécharger les données avec l'option --update"
    )

# ❌ À éviter - Message vague
if not path.exists():
    raise FileNotFoundError(f"Fichier non trouvé : {path}")
```

### 3. Conserver la cohérence entre CLI et interactif

```python
# ✅ Bon - Même fonction appelée par les deux modes
def generer_carte(type_carte, **options):
    # Logique commune
    ...

# Appel depuis CLI
if args.type == "hydraulicite":
    generer_carte("hydraulicite", **vars(args))

# Appel depuis interactif
choix = demander_avec_choix(...)
if choix == "1":
    generer_carte("hydraulicite", **options_interactives)
```

### 4. Documenter les nouvelles options

```python
# ✅ Bon - Aide complète
parser.add_argument(
    "--nouvelle_option",
    action='store_true',
    help="""
    Active la nouvelle fonctionnalité.
    
    Cette option permet de :
    - Faire X
    - Faire Y
    - Améliorer Z
    
    Exemple : python main.py --type test --nouvelle_option
    """
)

# ❌ À éviter - Aide minimale
parser.add_argument("--nouvelle_option", help="Active X")
```

---

## 📚 Voir aussi

- [Utilisation CLI](../../usage/cli.md) - Guide utilisateur du mode CLI
- [Utilisation Interactif](../../usage/interactive.md) - Guide utilisateur du mode interactif
- [Module plotting](../plotting/index.md) - Fonctions appelées par le CLI

---

## 🔗 Navigation

- [main_cli.py](main_cli.md)
- [main_interactive.py](main_interactive.md)
- [utils.py](utils.md)

---

[Retour aux modules](index.md)



