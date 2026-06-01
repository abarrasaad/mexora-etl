# =============================================================================
# MEXORA ETL — Module de Chargement (Load)
# =============================================================================
# Stratégies de chargement :
#   - Dimensions  : TRUNCATE + RELOAD (replace)
#   - Table de faits : insertion par chunks (append progressif)
# =============================================================================

import pandas as pd
import logging
import sqlalchemy
from config.settings import SCHEMA_DWH, CHUNK_SIZE


def charger_dimension(df: pd.DataFrame, table_name: str, engine, if_exists: str = 'replace'):
    try:
        # Drop manually with CASCADE to handle FK and materialized view dependencies
        with engine.begin() as conn:
            conn.execute(sqlalchemy.text(
                f"DROP TABLE IF EXISTS {SCHEMA_DWH}.{table_name} CASCADE"
            ))

        df.to_sql(
            name=table_name,
            con=engine,
            schema=SCHEMA_DWH,
            if_exists='append',   # table is already gone, so append = fresh insert
            index=False,
            method='multi',
            chunksize=CHUNK_SIZE
        )
        logging.info(
            f"[LOAD] {table_name} : {len(df)} lignes chargées dans {SCHEMA_DWH}.{table_name}"
        )
    except Exception as e:
        logging.error(f"[LOAD] Erreur lors du chargement de {table_name} : {e}")
        raise


def charger_faits(df: pd.DataFrame, table_name: str, engine):
    try:
        with engine.begin() as conn:
            conn.execute(sqlalchemy.text(
                f"DROP TABLE IF EXISTS {SCHEMA_DWH}.{table_name} CASCADE"
            ))

        total  = len(df)
        loaded = 0
        for i in range(0, total, CHUNK_SIZE):
            chunk = df.iloc[i:i + CHUNK_SIZE]
            chunk.to_sql(
                name=table_name,
                con=engine,
                schema=SCHEMA_DWH,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=CHUNK_SIZE
            )
            loaded += len(chunk)
            logging.info(f"[LOAD] {table_name} : {loaded}/{total} lignes chargées")

        logging.info(f"[LOAD] {table_name} : chargement terminé ({total} lignes)")
    except Exception as e:
        logging.error(f"[LOAD] Erreur lors du chargement de {table_name} : {e}")
        raise


def sauvegarder_csv(df: pd.DataFrame, filepath: str, description: str = ''):
    """
    Sauvegarde un DataFrame en CSV (mode alternatif si PostgreSQL non disponible).

    Args:
        df:          DataFrame à sauvegarder
        filepath:    Chemin de destination
        description: Label pour le log
    """
    df.to_csv(filepath, index=False, encoding='utf-8')
    logging.info(f"[LOAD] {description} : {len(df)} lignes sauvegardées dans {filepath}")
