---
layout: default
title: utils_proxy.py
description: "Configuration automatique du proxy réseau"
nav_order: 3
parent: Module Utils
grand_parent: Modules
---

# 🌐 set_up_working_proxy()

**Configuration automatique du proxy pour l'accès internet**

---

## 🎯 Description

`set_up_working_proxy()` configure automatiquement les paramètres de proxy réseau nécessaires pour accéder à internet.

---

## 📋 Utilisation

### Appel unique au démarrage

```python
from src.utils.utils_proxy import set_up_working_proxy

# Appeler une seule fois au démarrage de l'application
set_up_working_proxy()
```

---

## 🔧 Fonctionnement

1. Charge le fichier `.env` pour obtenir les paramètres de proxy
2. Teste la connexion avec Hub'Eau
3. Si succès : utilise la configuration actuelle
4. Si échec : tente sans proxy
5. Affiche le résultat

---

## 💡 Bonnes Pratiques

- Appel unique via le cache `@cache`
- Toujours appeler avant les opérations réseau

---

## 📁 Fichier .env

**Exemple**
```bash
HTTP_PROXY=http://proxy.dreal.fr:8080
HTTPS_PROXY=http://proxy.dreal.fr:8080
```

---

## 🔗 Liens

- [Module Utils](index.md)