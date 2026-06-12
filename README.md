# Automatisation Récupération données hydrologiques
Ces scripts Python ont pour vocations de récupérer les données hydrologiques via l'API de Hub'eau en passant par le client Python cl_hubeau.

## main.py
Le fichier main sert à lancer tout le reste des fichiers.

Il permet de générer des cartes d'hydraulicité, de fréquence de non-dépassement et période de retour.

Il génère aussi les cartes des différentes stations et sites qui existent.
## Scripts
Nous avons différents scripts permettant d'obtenir plusieurs types d'informations différentes : 

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

Les dernières données seront re-téléchargé automatiquement et tout ce met à jour automatiquement.

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
