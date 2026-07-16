---
layout: default
title: Guide de Démarrage
description: "Installation et configuration de l'outil de récupération et visualisation de données hydrologiques et météorologiques"
nav_order: 2
parent: Accueil
---

# 🚀 Guide de Démarrage

Ce guide vous explique comment installer et configurer l'outil pour commencer à récupérer et visualiser des données hydrologiques et météorologiques.

---

## 📋 Prérequis

Pour utiliser ce programme, vous avez besoin de :

| Éléments | Version Requise | Notes |
|----------|----------------|-------|
| **Système d'exploitation** | Windows | Le programme a été testé sur Windows |
| **Python** | 3.11 ou supérieur | [Télécharger Python](https://www.python.org/downloads/) |
| **Git** | Optionnel | Recommandé pour le téléchargement |
| **Connexion Internet** | Obligatoire | Pour télécharger les données et dépendances |

> ⚠️ **Important** : Si vous êtes sur le réseau interne de votre organisation, vous devrez peut-être configurer un proxy (voir section [Proxy](#-utiliser-un-proxy)).

---

## 📥 Installation

Suivez ces étapes **dans l'ordre** :

### 1. Télécharger le programme

**Option A (recommandée si vous avez Git)** :
```bash
git clone https://github.com/Thomas-MESLIN/RecupeEthiage.git
cd RecupeEthiage
```

**Option B (sans Git)** :
1. Allez sur [la page GitHub](https://github.com/Thomas-MESLIN/RecupeEthiage)
2. Cliquez sur le bouton vert **"Code"**
3. Sélectionnez **"Download ZIP"**
4. Extrayez le fichier ZIP dans un dossier de votre choix

### 2. Créer l'environnement Python

Ouvrez un terminal dans le dossier du projet et exécutez :

```bash
python -m venv venv
```

> ⚠️ Si vous avez plusieurs versions de Python, utilisez `python3-64.exe` à la place de `python`.

### 3. Installer les dépendances

```bash
.\venv\Scripts\pip.exe install -r .\requirements.txt
```

> ⚠️ **Attention** : Cette étape peut prendre plusieurs minutes et nécessite une connexion internet **hors du réseau interne** de votre organisation.

### 4. Vérifier l'installation

Pour vérifier que tout fonctionne correctement :

```bash
.\venv\Scripts\python.exe main.py -h
```

Vous devriez voir s'afficher un message d'aide avec toutes les options disponibles. Si c'est le cas, **bravo, l'installation est terminée !** 🎉

---

## 🔧 Configuration initiale

### Initialisation du projet

Avant la première utilisation, exécutez :

```bash
.\venv\Scripts\python.exe -c "from src.config.init_project import *"
```

Cela crée l'arborescence complète des dossiers de sortie dans `output/`.

### Configuration du Proxy (si nécessaire)

Si vous êtes sur un réseau interne :

1. Copiez le fichier `.env_example` et renommez-le en `.env`
2. Ouvrez le fichier `.env` avec un éditeur de texte
3. Ajoutez vos informations de proxy :

```ini
# Exemple de configuration proxy
HTTP_PROXY="http://votre-proxy.fr:8080"
HTTPS_PROXY="http://votre-proxy.fr:8080"
```

4. Sauvegardez le fichier

> ⚠️ **Important** : Le fichier `.env` ne doit pas être partagé publiquement.

---

## 🎯 Prochaines étapes

Une fois l'installation terminée, vous pouvez :

- **[Utiliser le mode interactif](usage/interactive.md)** - Recommandé pour les débutants
- **[Utiliser le mode CLI](usage/cli.md)** - Pour les utilisateurs avancés
- **[Explorer les concepts clés](concepts/index.md)** - Comprendre les indicateurs

---

## ❌ Dépannage

### Problème : "Python n'est pas reconnu"

**Solution** : Vérifiez que Python est bien installé et ajouté au PATH. Vous pouvez aussi utiliser le chemin complet :

```bash
C:\Chemin\vers\Python\python.exe -m venv venv
```

### Problème : Erreur lors de l'installation des paquets

**Solution 1** : Vérifiez que vous êtes bien connecté à internet (hors réseau interne).

**Solution 2** : Essayez de réinstaller les paquets un par un :

```bash
.\venv\Scripts\pip.exe install cl-hubeau
.\venv\Scripts\pip.exe install pandas
.\venv\Scripts\pip.exe install geopandas
.\venv\Scripts\pip.exe install matplotlib
```

**Solution 3** : Si un paquet spécifique pose problème :

```bash
.\venv\Scripts\pip.exe uninstall nom_du_paquet -y
.\venv\Scripts\pip.exe install -r .\requirements.txt
```

### Problème : Le programme plante avec une erreur obscure

**Solution** :
1. Supprimez le dossier `venv`
2. Supprimez le dossier `output` (si vous voulez tout recommencer)
3. Relancez l'installation depuis le début

---

## 📚 Voir aussi

- [Mode Interactif](usage/interactive.md)
- [Mode CLI](usage/cli.md)
- [Concepts Clés](concepts/index.md)
