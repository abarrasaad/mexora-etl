# =============================================================================
# MEXORA ETL — Configuration & Paramètres
# =============================================================================
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Répertoire racine du projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Chemins vers les fichiers de données sources ---
DATA_DIR = os.path.join(BASE_DIR, 'data')
COMMANDES_PATH = os.path.join(DATA_DIR, 'commandes_mexora.csv')
PRODUITS_PATH  = os.path.join(DATA_DIR, 'produits_mexora.json')
CLIENTS_PATH   = os.path.join(DATA_DIR, 'clients_mexora.csv')
REGIONS_PATH   = os.path.join(DATA_DIR, 'regions_maroc.csv')

# --- Chemin vers les scripts SQL ---
SQL_DIR        = os.path.join(BASE_DIR, 'sql')
CREATE_DWH_SQL = os.path.join(SQL_DIR, 'create_dwh.sql')

# --- Répertoire des logs ---
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# --- Connexion PostgreSQL (lue depuis .env) ---
DB_CONFIG = {
    'host':     os.getenv('DB_HOST', 'localhost'),
    'port':     os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user':     os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
}


def get_connection_string():
    return (
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        f"?client_encoding=utf8"
    )


# --- Schémas PostgreSQL ---
SCHEMA_STAGING  = 'staging_mexora'
SCHEMA_DWH      = 'dwh_mexora'
SCHEMA_REPORTING = 'reporting_mexora'

# --- Constantes ETL ---
CHUNK_SIZE      = 5000           # Taille des chunks pour le chargement par lots
DIM_TEMPS_START = '2020-01-01'
DIM_TEMPS_END   = '2025-12-31'

# --- Seuils de segmentation client ---
SEGMENT_GOLD_THRESHOLD   = 15000   # CA 12 mois >= 15 000 MAD
SEGMENT_SILVER_THRESHOLD = 5000    # CA 12 mois >= 5 000 MAD

# --- Taux TVA Maroc ---
TVA_RATE = 0.20  # 20 %
# =============================================================================
