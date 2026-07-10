"""
Script principal pour générer des cartes et données hydrologiques/météorologiques.

Ce script propose deux modes d'utilisation :
1. Mode interactif : Lancez le script sans arguments pour être guidé pas à pas
2. Mode CLI (ligne de commande) : Utilisez des arguments pour automatiser les tâches

Fonctionnalités disponibles :
- Génération de cartes d'hydraulicité
- Génération de cartes de VCN3/périodes de retour
- Export de données Météo France (brutes ou SIM2, mensuelles ou quotidiennes)
- Export de données ONDE (campagnes habituelles ou toutes campagnes)

Pour plus d'informations, exécutez : python main.py --help
"""

import argparse
from pynsee.utils import clear_all_cache
from src.cli.main_cli import setup_parser, mode_cli
from src.cli.main_interactive import mode_interactif
from src.config.logging_config import setup_logger

# Configuration du logger
logger = setup_logger(name="main")


def run():
    """
    Point d'entrée principal pour l'application.
    Décide entre le mode CLI et le mode interactif.
    """
    # Nettoyer le cache de Pynsee
    clear_all_cache()
    
    # Configuration du parseur d'arguments
    parser = setup_parser()
    args = parser.parse_args()
    
    # Logique de décision : CLI ou interactif
    if args.type is None:
        logger.info("Aucun type de carte spécifié.")
        logger.info("Lancement du mode interactif...\n")
        mode_interactif()
    else:
        # Mode CLI
        mode_cli(args)
    
    logger.info("\n" + "="*60)
    logger.info("GENERATION TERMINEE AVEC SUCCES !")
    logger.info("="*60)


if __name__ == "__main__":
    run()
