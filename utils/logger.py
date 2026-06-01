# =============================================================================
# MEXORA ETL — Configuration du Logging
# =============================================================================
import logging
import os
from datetime import datetime
from config.settings import LOGS_DIR


def setup_logging():
    """
    Configure le système de logging pour le pipeline ETL MEXORA.
    Les logs sont écrits à la fois dans un fichier horodaté et dans la console.

    Returns:
        logging.Logger: Le logger configuré.
    """
    log_filename = f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_filepath = os.path.join(LOGS_DIR, log_filename)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s — %(levelname)s — %(message)s',
        handlers=[
            logging.FileHandler(log_filepath, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger('mexora_etl')
    logger.info(f"Logging initialisé — fichier : {log_filepath}")
    return logger
