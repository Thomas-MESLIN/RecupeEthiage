from pathlib import Path

# Renvoie la racine du projet.
ROOT_DIR = Path(__file__).resolve().parents[2]

# Tous les autres fichiers doivent être construits à partir de ROOT_DIR...
OUTPUT_DIR = ROOT_DIR / "output"
DATA_DIR = ROOT_DIR / "data"
SRC_DIR = ROOT_DIR / "src"
