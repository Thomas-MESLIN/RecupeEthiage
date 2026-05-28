# Automatisation Récupération données hydrologique
Ces scripts Python ont pour vocations de récupérer les données hydraulogique via l'API de Hub'eau en passant par le client Python cl_hubeau.

## Scripts
Nous avons différents scripts permettant d'obtenir plusieurs type d'informations différentes : 
### get-all-station-hydrometry.py
#### Description
Ce script sert de test pour récupérer un échantillon de données de toutes les stations et sites hydrométrique au format geojson.
Ce format est facilement importable dans QGIS à l'aide d'un glisser-déposer.
#### Utilisation
Il suffit de lancer le script... (TODO)

### recuperation-QmM-1991-2020.py
Ce script sert à récupérer l'historique des données du débit moyen mensuel.

Ces données vont permettre à terme de calculer l'hydraulicité d'une station.

### clean-data.py
Ce script lis les données téléchargés de hydroportail dans export-data  et de hubeau dans observations-QmM-france-1991-2020.csv.

Il met ensuite les données nettoyées de Hydroportail et Hubeau dans les fichiers correspondants :
 - output/hubeau/cleaned_data
 - output/hydroportail/cleaned_data

Les données nettoyées ont les doublons en moins, les données vides en moins et essayent d'être complété quand d'autres enregistrements existent.
## Nettoyer et exporter les différences de données
Pour nettoyer les données de A à Z.
```bash
# Télécharger les listes de stations Hub'eau
get-all-station-sites-hydrometry.py
# Télécharger l'historique de 1991 à 2020
recuperation-QmM-1991-2020.py
# Nettoyer les données de hydroportail et Hub'eau
clean-historic-data.py
# On télécharge les données du ou des mois souhaités.

# On veut ensuite nettoyer les données qui ne seraient pas historique
clean-data.py
# On calcule ensuite les données avec hydraulicité
hydraulicite.py
# On crée ensuite un geojson avec le script
plot_carte_hydraulicite-test.py
```
### Analyser les données nettoyées
```bash
# Analyser les données de sortie et faire des petites stats dessus
validate-clean-data.py
# Faire des petits graphiques choupi
plot_res_validation_clean.py
```

### Re-télécharger les données déjà récupérées
Si les données que vous avez téléchargées ne sont plus à jour, vous pouvez supprimer le dossier `output` tout entier.

Les dernière données seront re-téléchargé automatiquement.
## Hydroportail
```bash
# Récupérer les données hydroportail (bancal)
test-gather-auto-hydroportail.py
```

## En cas de panne
Si on est face à une superbe panne, qu'il y a une erreur obscure ou autre, 
la meilleure solution est de tout remettre à 0.

Vous pouvez alors supprimer tout ce dossier, re-extraire au propre, re-installer un venv et re-lancer votre requête. 
En priant pour qu'il y ai une mise à jour qui règle le problème. 

## Documentation Source
### API Hub'eau
Source des données, donne des informations sur les différents champs pouvant être remplis :
- https://hubeau.eaufrance.fr/page/api-hydrometrie#/hydrometrie/observationsElaborees%20csv
### Client API
Client Python qui va chercher les données dans Hub'eau, maintenu par la DREAL Haut-de-France.
- https://tgrandje.github.io/cl-hubeau/hydrometry/
- https://github.com/tgrandje/cl-hubeau

### Unités
Tous les acronymes des unités peuvent être retrouvé ici → https://www.sandre.eaufrance.fr/?urn=urn:sandre:donnees:513::::::referentiel:3.1:html
