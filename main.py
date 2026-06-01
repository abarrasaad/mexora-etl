# =============================================================================
# MEXORA ETL — Point d'Entrée du Pipeline
# =============================================================================
# Orchestre l'ensemble du pipeline ETL :
#   1. EXTRACT   — Extraction des données brutes (CSV, JSON)
#   2. TRANSFORM — Nettoyage, harmonisation, construction des dimensions
#   3. LOAD      — Chargement dans le Data Warehouse (CSV ou PostgreSQL)
#
# Usage : python main.py [--mode csv|postgres]
# =============================================================================

import os
import sys
import logging
from datetime import datetime

# Ajout du répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import (
    COMMANDES_PATH, PRODUITS_PATH, CLIENTS_PATH, REGIONS_PATH,
    CREATE_DWH_SQL, get_connection_string, LOGS_DIR
)
from utils.logger import setup_logging
from extract.extractor import (
    extract_commandes, extract_produits, extract_clients, extract_regions
)
from transform.clean_commandes import transform_commandes, charger_referentiel_villes
from transform.clean_clients import transform_clients
from transform.clean_produits import transform_produits
from transform.build_dimensions import (
    build_dim_temps, build_dim_produit, build_dim_client,
    build_dim_region, build_dim_livreur, build_fait_ventes
)
from load.loader import sauvegarder_csv


def initialiser_base(engine):
    """
    Exécute le script SQL create_dwh.sql pour créer les schémas, les tables,
    les index et les vues matérialisées AVANT toute insertion de données.
    Appelé automatiquement en mode postgres.
    """
    import sqlalchemy
    logging.info("[INIT] Exécution de create_dwh.sql — création des schémas et tables...")
    with open(CREATE_DWH_SQL, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    with engine.begin() as conn:
        for statement in sql_script.split(';'):
            stmt = statement.strip()
            if stmt:
                try:
                    conn.execute(sqlalchemy.text(stmt))
                except Exception as e:
                    # Les erreurs de DROP IF EXISTS sont ignorées silencieusement
                    logging.debug(f"[INIT] Info SQL : {e}")
    logging.info("[INIT] Schémas, tables et vues créés avec succès.")


def run_pipeline(mode: str = 'csv'):
    """
    Orchestre le pipeline ETL complet de MEXORA.

    Args:
        mode: 'csv'      → génère les tables en fichiers CSV dans output/
              'postgres' → charge les données dans PostgreSQL
    """
    start  = datetime.now()
    logger = setup_logging()

    logging.info("=" * 60)
    logging.info("DÉMARRAGE PIPELINE ETL — MEXORA")
    logging.info(f"Mode de chargement : {mode.upper()}")
    logging.info(f"Date d'exécution   : {start.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 60)

    try:
        # =================================================================
        # 1. EXTRACT — Chargement des données brutes
        # =================================================================
        logging.info("")
        logging.info("--- PHASE EXTRACT ---")
        df_commandes_raw = extract_commandes(COMMANDES_PATH)
        df_produits_raw  = extract_produits(PRODUITS_PATH)
        df_clients_raw   = extract_clients(CLIENTS_PATH)
        df_regions       = extract_regions(REGIONS_PATH)

        # =================================================================
        # 2. TRANSFORM — Nettoyage et construction des dimensions
        # =================================================================
        logging.info("")
        logging.info("--- PHASE TRANSFORM ---")

        logging.info("")
        logging.info("[TRANSFORM] === Nettoyage des commandes ===")
        df_commandes = transform_commandes(df_commandes_raw, REGIONS_PATH)

        logging.info("")
        logging.info("[TRANSFORM] === Nettoyage des produits ===")
        df_produits = transform_produits(df_produits_raw)

        logging.info("")
        logging.info("[TRANSFORM] === Nettoyage des clients ===")
        mapping_villes = charger_referentiel_villes(REGIONS_PATH)
        df_clients = transform_clients(df_clients_raw, mapping_villes)

        logging.info("")
        logging.info("[TRANSFORM] === Construction des dimensions ===")
        dim_temps   = build_dim_temps()
        dim_produit = build_dim_produit(df_produits)
        dim_client  = build_dim_client(df_clients, df_commandes)
        dim_region  = build_dim_region(df_regions)
        dim_livreur = build_dim_livreur(df_commandes)

        logging.info("")
        logging.info("[TRANSFORM] === Construction de la table de faits ===")
        fait_ventes = build_fait_ventes(
            df_commandes, dim_temps, dim_client,
            dim_produit, dim_region, dim_livreur
        )

        # =================================================================
        # 3. LOAD — Chargement des données transformées
        # =================================================================
        logging.info("")
        logging.info("--- PHASE LOAD ---")

        if mode == 'csv':
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
            os.makedirs(output_dir, exist_ok=True)

            sauvegarder_csv(dim_temps,   os.path.join(output_dir, 'dim_temps.csv'),   'DIM_TEMPS')
            sauvegarder_csv(dim_produit, os.path.join(output_dir, 'dim_produit.csv'), 'DIM_PRODUIT')
            sauvegarder_csv(dim_client,  os.path.join(output_dir, 'dim_client.csv'),  'DIM_CLIENT')
            sauvegarder_csv(dim_region,  os.path.join(output_dir, 'dim_region.csv'),  'DIM_REGION')
            sauvegarder_csv(dim_livreur, os.path.join(output_dir, 'dim_livreur.csv'), 'DIM_LIVREUR')
            sauvegarder_csv(fait_ventes, os.path.join(output_dir, 'fait_ventes.csv'), 'FAIT_VENTES')

        elif mode == 'postgres':
            import sqlalchemy
            from load.loader import charger_dimension, charger_faits

            engine = sqlalchemy.create_engine(get_connection_string())
            logging.info("[LOAD] Connexion PostgreSQL établie")

            # Création automatique des schémas, tables et vues avant insertion
            initialiser_base(engine)

            charger_dimension(dim_temps,   'dim_temps',   engine)
            charger_dimension(dim_produit, 'dim_produit', engine)
            charger_dimension(dim_client,  'dim_client',  engine)
            charger_dimension(dim_region,  'dim_region',  engine)
            charger_dimension(dim_livreur, 'dim_livreur', engine)
            charger_faits(fait_ventes, 'fait_ventes', engine)

        # =================================================================
        # RÉSUMÉ FINAL
        # =================================================================
        duree = (datetime.now() - start).total_seconds()
        logging.info("")
        logging.info("=" * 60)
        logging.info("PIPELINE ETL MEXORA — TERMINÉ AVEC SUCCÈS")
        logging.info(f"Durée totale       : {duree:.1f} secondes")
        logging.info(f"Dimensions chargées: 5")
        logging.info(f"Lignes FAIT_VENTES : {len(fait_ventes):,}")
        logging.info(f"CA total TTC       : {fait_ventes['montant_ttc'].sum():,.2f} MAD")
        logging.info("=" * 60)

    except Exception as e:
        logging.error(f"ERREUR PIPELINE : {e}", exc_info=True)
        raise


if __name__ == '__main__':
    mode = 'csv'
    if len(sys.argv) > 1 and sys.argv[1] == '--mode':
        mode = sys.argv[2] if len(sys.argv) > 2 else 'csv'

    run_pipeline(mode=mode)
