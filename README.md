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
