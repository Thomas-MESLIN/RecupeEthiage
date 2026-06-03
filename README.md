# Automatisation Récupération données hydrologiques
Ces scripts Python ont pour vocations de récupérer les données hydrologiques via l'API de Hub'eau en passant par le client Python cl_hubeau.

## Scripts
Nous avons différents scripts permettant d'obtenir plusieurs types d'informations différentes : 
### get-all-station-hydrometry.py
Ce script sert de test pour récupérer un échantillon de données de toutes les stations et sites hydrométrique au format geojson.
Ce format est facilement importable dans QGIS à l'aide d'un glisser-déposer.

### recuperation-QmM-1991-2020.py
Ce script sert à récupérer l'historique des données du débit moyen mensuel.

Ces données vont permettre à terme de calculer l'hydraulicité d'une station.

### clean-data.py
Ce script lis les données téléchargés de hydroportail dans `export-data` et de hubeau dans `observations-QmM-france-1991-2020.csv`.

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
# On veut ensuite nettoyer les données qui ne seraient pas historique
clean-data.py

# On calcule ensuite les données avec hydraulicité
hydraulicite.py
# On crée ensuite un geojson avec le script
plot_carte_hydraulicite.py

# VCN3 et période de retour, 
# Pour calculer le vcn3 historique et n'importe quelle VCN3
calcul_vcn3_1991_2020.py
# On calcule ensuite la période de retour
plot_vcn3_periode_de_retour.py
# On plot les résultats dans un geojson
plot_vcn3_periode_de_retour.py
```
### Analyser les données nettoyées
Les données téléchargées et nettoyées peuvent être comparés avec les données d'Hydroportail, 
pour savoir la quantité de différence entre les deux sources de données et les divergences qui existent.
```bash
# Analyser les données de sortie et faire des petites stats dessus
validate-clean-data.py
# Faire des petits graphiques chou.
plot_res_validation_clean.py
```

### Re-télécharger les données déjà récupérées
Si les données que vous avez téléchargées ne sont plus à jour, vous pouvez supprimer le dossier `output` tout entier.

Les dernières données seront re-téléchargé automatiquement.

## Hydroportail
```bash
# Récupérer les données hydroportail (bancal)
test-gather-auto-hydroportail.py
```

## En cas de panne
Si on est face à une superbe panne, qu'il y a une erreur obscure ou autre, 
la meilleure solution est de tout remettre à 0.

Vous pouvez alors supprimer tout ce dossier, re-extraire au propre, re-installer un venv et re-lancer votre requête. 
En priant pour qu'il y ait une mise à jour qui règle le problème. 

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
