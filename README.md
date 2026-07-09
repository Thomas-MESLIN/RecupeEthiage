# Automatisation Récupération données hydrologiques
Ces scripts Python ont pour vocations de : 
- Récupérer les données hydrologiques via l'API de Hub'eau en passant par le client Python cl_hubeau.
- Récupérer les données Onde les plus récentes sur un mois via Hub'eau.
- Récupérer les données météorologiques via DataGouv par le client Python datagouv-client.
- Procéder au calcul de l'hydraulicité et du VCN3 (période de retour et fréquence de non-dépassement) d'un mois particulier.
- Extraire n'importe quel intervalle de temps, à n'importe quelle granularité temporelle (mensuelle,quotienne,SIM2,...) et sur n'importe quel territoire.

## Prérequis
Avoir Python d'installé avec une version pas si vieille de préférence. (>3.11)

## Installation
Clonez le dépôt localement (via git clone), ou télécharger via l'onglet Code.

Dans le dossier, faite clic droit (sans sélectionner de fichier) et ouvrez le terminal.

Dans le terminal (utilisez tab pour avoir de l'autocomplétion), rentrez : 
```bash
# On créer l'environnement virtuel pour Python. (l'endroit où il stocke ses paquets)
python3-64.exe -m venv venv

# On installe les paquets nécessaire, attention, vous ne pouvez pas installer les paquets en étant sur le réseau interne.
.\venv\Scripts\pip.exe install -r .\requirements.txt

# On vérifie que le programme s'est correctement installé.
.\venv\Scripts\python.exe main.py -h
```

Vous avez besoin d'avoir accès à internet normal, le temps de télécharger les paquets.

## Lancer le programme

Si vous êtes dans un réseau interne -> voir la section _Utiliser un proxy_.

```bash
# On lance le programme principal en version interactive.
.\venv\Scripts\python.exe main.py
```

On peut aussi lancer la version complète en CLI (commande Line Interface). 
```bash
# On lance le programme principal en CLI.
.\venv\Scripts\python.exe main.py -h
```

### Exemple d'utilisation : 
TODO, ajouter image pour chaque sortie. + ajouter commande Onde
```bash
# Les type hydraulicité et VCN3 fonctionne au mois. Ainsi la end-date n'est pas pris en compte. (comportement à travailler)
# On récupère l'hydraulicité du mois de Janvier 2026 sur les stations de la liste custom.
.\venv\Scripts\python.exe .\main.py --type hydraulicite --start_date 2026-01 --reseau_sandre custom

# On récupère le vcn3 du mois de Février 2024 sur les stations de le réseaux sandre BSH001.
.\venv\Scripts\python.exe .\main.py --type hydraulicite --start_date 2024-02 --reseau_sandre BSH001

# On récupère les données SIM2 de météoFrance pour le mois unique de juillet 2023
.\venv\Scripts\python.exe .\main.py --type meteo_sim2_QUOT --start_date 2023-07-01 --end_date 2023-07-31

# On récupère les données SIM2 de météoFrance pour le mois unique de la fin juin 
.\venv\Scripts\python.exe .\main.py --type meteo_sim2_QUOT --start_date 2026-06-15 --end_date 2026-06-25

# On récupère les données SIM2 de météoFrance qu'on aggrège pour avoir idée de la pluie cumulée depuis le début de l'année hydrologique
.\venv\Scripts\python.exe .\main.py --type meteo_sim2_MENS --start_date 2025-09-01 --end_date 2026-07-01 --meteo_aggregate
```
## main.py
Le fichier main sert à lancer tout le reste des fichiers.

Il permet de générer des geojson d'hydraulicité, de fréquence de non-dépassement et période de retour.

Il permet aussi de générer des geojson contenant les données Quotidiennes, Mensuelles, Quotidiennes-SIM2, Mensuelles-SIM2.
Les cartes générés sont formattés aux échelles NATIONAL, BASSIN, REGIONAL-BASSIN, DEPARTEMENTAL-BASSIN. On peut modifier le code pour selectionner les régions ADMINISTRATIVE.

Il génère aussi les cartes des différentes stations et sites qui existent.
## Scripts
Nous avons différents scripts permettant d'obtenir plusieurs types d'informations différentes : 

## Hydraulicité et Hub'Eau
Les données récupérées via Hub'Eau sont indexé par mois et par réseau Sandre.

On peut décider d'utiliser une liste de station personnalisée, vous pouvez alors remplir les deux fichiers : 
- `liste_site_custom.csv`
- `liste_station_custom.csv`

Pour chaque site, le script récupère les stations correspondantes. S'il y a plus d'une station, il les choisit toutes.
Si vous voulez qu'il ne choisisse qu'une seule des stations d'un site, indiquez cette station dans le fichier `liste_station_custom.csv`.

Le fichier généré résumant les stations et sites utilisés est généré à `output/site_station_custom/liste_site_et_station_custom.csv`.

## MétéoFrance collecte
Le script génère des fichiers pour chaque département/régions/bassin spécifié dans les fichiers :
 - `liste_bassin.csv` (contient 1 seul chiffre, votre bassin versant)
 - `liste_departement.csv`
 - `liste_region.csv`

Les zones géographiques peuvent être généré avec l'underscore BASSIN/ADMINISTRATIF : 
 - BASSIN : La zone géographique est découpé pour qu'il ne reste que la partie présente dans le bassin versant.
 - ADMINISTRATIF : La zone géographique est conservée en entier.

Vous pouvez retrouver les codes des régions et des bassins après leur téléchargement (automatique) dans le dossier `output/meteoFrance/downloaded_data/delimitation_qgis/*.geojson` (ctrl+f "CdBH"/"code").

## MétéoFrance ressource interprétation
Les données SIM2 extraite via MétéoFrance fournissent des indicateurs : 
 - SSWI (Standardized Soil Wetness Index) -> mesurer la sécheresse du sol (https://www.drias-eau.fr/accompagnement/sections/383)
 - SPI (Standardized Precipitation Index) -> mesurer la sécheresse météorologique (https://www.drias-climat.fr/accompagnement/sections/348)

### Analyser les données nettoyées
Les données téléchargées et nettoyées peuvent être comparés avec les données d'Hydroportail, 
pour savoir la quantité de différence entre les deux sources de données et les divergences qui existent.
```bash
# Analyser les données de sortie et faire des petites stats dessus
validate-clean-data.py
# Faire des petits graphiques chou.
plot_res_validation_clean.py
```

### Sortie des scripts

Tous les fichiers générés et téléchargés par tous les scripts vont dans le dossier `output`. 

## Hub'Eau
Hub'Eau prend soin de collecter des données depuis plusieurs API : 

### Onde (API Ecoulement des cours d'eau)
Les données ondes peuvent être récupéré au mois via 


Les geojson vont dans le dossier `output/QGIS`.


### Re-télécharger les données déjà récupérées
Les dernières données seront re-téléchargé automatiquement lorsqu'elles ne sont plus à jour.

## En cas de panne
Si on est face à une superbe panne, qu'il y a une erreur obscure ou autre, 
la solution la plus simple est de tout remettre à 0.

Vous pouvez alors supprimer tout ce dossier, re-extraire au propre, re-installer un venv et re-lancer votre requête. 
En priant pour qu'il y ait une mise à jour qui règle le problème. 

### Si un paquet bug et ne veut pas fonctionner
1. On désinstalle le paquet : `.\venv\Scripts\pip.exe uninstall [nom_du_paquet] -y`
2. On réinstalle tout : `.\venv\Scripts\pip.exe install -r .\requirements.txt`

## Utiliser un proxy
Vous pouvez utiliser un proxy pour pouvoir télécharger vos données via votre réseau interne.

Le proxy peut être défini en copiant `.env_example` vers `.env` et en remplissant avec votre proxy.

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
