# Tests

Ce dossier contient les tests unitaires et d'intégration pour le projet.

## Structure

```
tests/
├── __init__.py
├── conftest.py              # Configuration et fixtures pytest
├── README.md               # Ce fichier
├── integration/
│   ├── __init__.py
│   └── test_integration.py # Tests d'intégration
└── unit/
    ├── __init__.py
    ├── test_cli.py         # Tests pour le module CLI
    ├── test_config.py      # Tests pour le module config
    ├── test_io.py          # Tests pour le module IO
    ├── test_plotting.py    # Tests pour le module plotting
    ├── test_processing.py  # Tests pour le module processing
    ├── test_scripts.py     # Tests pour les scripts
    └── test_utils.py       # Tests pour le module utils
```

## Prérequis

Assurez-vous d'avoir installé les dépendances de test :

```bash
pip install -r requirements-test.txt
```

## Exécution des tests

### Exécuter tous les tests

```bash
pytest
```

### Exécuter uniquement les tests unitaires

```bash
pytest tests/unit/
```

### Exécuter uniquement les tests d'intégration

```bash
pytest tests/integration/
```

### Exécuter avec couverture de code

```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

La couverture sera affichée dans le terminal et un rapport HTML sera généré dans le dossier `htmlcov/`.

### Exécuter un test spécifique

```bash
pytest tests/unit/test_config.py::TestPaths::test_root_dir_exists
```

### Exécuter avec des marqueurs

```bash
# Exécuter uniquement les tests marqués comme lents
pytest -m slow

# Exécuter tous les tests sauf les lents
pytest -m "not slow"

# Exécuter les tests d'intégration
pytest -m integration
```

## Organisation des tests

### Tests Unitaires

Les tests unitaires se trouvent dans `tests/unit/` et testent des fonctions individuelles :

- **test_config.py** : Tests pour les modules de configuration (paths, logging, styles, enums)
- **test_utils.py** : Tests pour les utilitaires (gestion des chemins, fichiers, proxy)
- **test_io.py** : Tests pour les modules d'entrée/sortie (download_Hubeau, download_meteoFrance)
- **test_processing.py** : Tests pour les modules de traitement (station, clean, calcul_vcn3, etc.)
- **test_plotting.py** : Tests pour les modules de visualisation
- **test_cli.py** : Tests pour l'interface en ligne de commande
- **test_scripts.py** : Tests pour les scripts principaux

### Tests d'Intégration

Les tests d'intégration se trouvent dans `tests/integration/` et testent l'interaction entre plusieurs modules :

- **test_integration.py** : Tests d'intégration pour les workflows complets

## Fixtures

Des fixtures communes sont définies dans `tests/conftest.py` :

- `project_root` : Chemin vers la racine du projet
- `output_dir` : Chemin vers le dossier output
- `data_dir` : Chemin vers le dossier data
- `temp_dir` : Dossier temporaire pour les tests
- `temp_csv_file` : Fichier CSV temporaire
- `sample_dataframe` : DataFrame d'exemple
- `empty_dataframe` : DataFrame vide
- `sample_stations_dataframe` : DataFrame de stations d'exemple
- `sample_sites_dataframe` : DataFrame de sites d'exemple
- `sample_vcn3_data` : Données VCN3 d'exemple
- `mock_date` : Date d'exemple
- `mock_annee_mois` : Année-mois d'exemple
- `mock_code_sandre` : Code Sandre d'exemple

## Bonnes pratiques

1. **Isolation** : Chaque test doit être indépendant des autres
2. **Mocking** : Utilisez `unittest.mock` pour les dépendances externes (API, fichiers, etc.)
3. **Fixtures** : Utilisez les fixtures pour les données communes
4. **Noms descriptifs** : Les noms des tests doivent décrire ce qu'ils testent
5. **Assertions claires** : Utilisez des assertions explicites

## Exemple de test

```python
import pytest
from unittest.mock import patch

class TestExample:
    """Exemple de classe de test"""
    
    def test_example_function(self):
        """Test d'une fonction exemple"""
        # Arrange
        input_value = 5
        expected = 10
        
        # Act
        result = input_value * 2
        
        # Assert
        assert result == expected
    
    @patch('module_to_test.external_function')
    def test_with_mocking(self, mock_external):
        """Test avec mocking"""
        mock_external.return_value = "mocked value"
        
        # Le code qui utilise external_function
        result = function_under_test()
        
        assert result == "expected result"
        mock_external.assert_called_once()
```

## Couverture de code

Pour obtenir un rapport de couverture détaillé :

```bash
pytest --cov=src --cov-report=html --cov-report=term
```

- `--cov=src` : Mesure la couverture du dossier src
- `--cov-report=html` : Génère un rapport HTML
- `--cov-report=term` : Affiche la couverture dans le terminal

## Résolution des problèmes

### Erreur : ModuleNotFoundError

Si vous obtenez une erreur `ModuleNotFoundError`, assurez-vous que :
1. Le dossier `src` est dans le PYTHONPATH
2. Vous exécutez les tests depuis la racine du projet
3. Toutes les dépendances sont installées

### Erreur : Fixture non trouvée

Si une fixture n'est pas trouvée, vérifiez que :
1. Le fichier `conftest.py` est dans le bon dossier
2. La fixture est définie avec le décorateur `@pytest.fixture`

### Tests lents

Pour sauter les tests marqués comme lents :

```bash
pytest -m "not slow"
```

## Contribution

Pour ajouter de nouveaux tests :

1. Créez un nouveau fichier de test dans `tests/unit/` ou `tests/integration/`
2. Suivez les conventions de nommage existantes
3. Ajoutez des fixtures si nécessaire dans `conftest.py`
4. Assurez-vous que les nouveaux tests passent

## Framework de test

Ce projet utilise **pytest** comme framework de test principal. Pytest offre :

- Une syntaxe simple et lisible
- Des fixtures puissantes
- Des plugins nombreux (couverture, mocking, etc.)
- Une bonne intégration avec les outils CI/CD
- Une exécution rapide des tests
