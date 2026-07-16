---
layout: default
title: logging_config.py
description: "Documentation de la configuration du logging"
nav_order: 2
parent: Module Config
grand_parent: Modules
---

# 📝 logging_config.py

**Configuration de la journalisation**

Ce module fournit une configuration centralisée pour tous les logs de l'application.

---

## 📋 Fonction Principale

### setup_logger

Configure un logger avec un nom spécifique.

```python
from src.config.logging_config import setup_logger

logger = setup_logger(name="mon_module")
logger.info("Début du traitement")
logger.debug("Détails du traitement")
logger.warning("Attention, problème détecté")
logger.error("Erreur critique")
```

**Paramètres**
- `name` : Nom du module (ex: "processing", "plotting", "io")

**Retourne** : Logger configuré

---

## 🎯 Configuration

### Format des logs

```
[AAAA-MM-JJ HH:MM:SS] - [NIVEAU] - [NOM] - message
```

### Niveaux de log

| Niveau | Utilisation |
|--------|-------------|
| DEBUG | Messages de débogage détaillés |
| INFO | Informations générales |
| WARNING | Avertissements |
| ERROR | Erreurs |
| CRITICAL | Erreurs critiques |

---

## 📁 Fichiers de Log

Les logs sont écrits dans :
- `output/logs/{name}.log`
- Console (stdout)

---

## 💡 Bonnes Pratiques

- **Un logger par module** : `setup_logger(name="nom_du_module")`
- **Niveau INFO** pour les messages généraux
- **Niveau DEBUG** pour les détails techniques
- **Niveau WARNING/ERROR** pour les problèmes

---

## 🔗 Liens

- [Module Config](index.md)
- [Utilisation du logging dans le code](../../usage/cli.md#journalisation)