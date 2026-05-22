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
get-all-station-hydrometry.py
# Télécharger l'historique de 1991 à 2020
recuperation-QmM-1991-2020.py
# Récupérer les données hydroportail (bancal)
test-gather-auto-hydroportail.py
# Nettoyer les données de hydroportail et Hub'eau
clean-data.py
# Analyser les données de sortie et faire des petites stats dessus
validate-clean-data.py
# Faire des petits graphiques choupi
plot_res_validation_clean.py
```

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
