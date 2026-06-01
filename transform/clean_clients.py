# =============================================================================
# MEXORA ETL — Nettoyage des Clients
# =============================================================================
# Règles de transformation appliquées :
#   R1 - Déduplication sur email normalisé (conserver l'inscription la plus récente)
#   R2 - Standardisation du genre (cible : 'm' / 'f' / 'inconnu')
#   R3 - Validation des dates de naissance (âge entre 16 et 100 ans)
#   R4 - Validation du format email via regex
#   R5 - Harmonisation des villes via le référentiel géographique
# =============================================================================

import pandas as pd
import logging
import re
from datetime import date


def transform_clients(df: pd.DataFrame, mapping_villes: dict) -> pd.DataFrame:
    """
    Applique l'ensemble des règles de nettoyage sur les clients MEXORA.

    Args:
        df: DataFrame brut des clients
        mapping_villes: Dictionnaire de correspondance des villes

    Returns:
        DataFrame nettoyé
    """
    initial = len(df)
    logging.info(f"[TRANSFORM] Clients — Début du nettoyage ({initial} lignes)")

    # R1 — Déduplication sur email normalisé (garder l'inscription la plus récente)
    df['email_norm']       = df['email'].str.lower().str.strip()
    df['date_inscription'] = pd.to_datetime(df['date_inscription'], errors='coerce')
    df = (
        df.sort_values('date_inscription')
          .drop_duplicates(subset=['email_norm'], keep='last')
    )
    r1_supprimees = initial - len(df)
    logging.info(f"[TRANSFORM] R1 doublons email : {r1_supprimees} lignes supprimées")

    # R2 — Standardisation du genre (cible : 'm' / 'f' / 'inconnu')
    mapping_sexe = {
        'm': 'm',      'f': 'f',       '1': 'm',  '0': 'f',
        'homme': 'm',  'femme': 'f',   'male': 'm', 'female': 'f',
        'h': 'm',
    }
    df['sexe'] = df['sexe'].str.lower().str.strip().map(mapping_sexe).fillna('inconnu')
    nb_inconnu  = (df['sexe'] == 'inconnu').sum()
    logging.info(
        f"[TRANSFORM] R2 genre : standardisé (m/f/inconnu), {nb_inconnu} valeurs inconnues"
    )

    # R3 — Validation des dates de naissance (âge attendu : 16 à 100 ans)
    df['date_naissance'] = pd.to_datetime(df['date_naissance'], errors='coerce')
    today = pd.Timestamp(date.today())
    df['age'] = (today - df['date_naissance']).dt.days // 365
    ages_invalides = ((df['age'] < 16) | (df['age'] > 100)).sum()
    df.loc[(df['age'] < 16) | (df['age'] > 100), 'date_naissance'] = pd.NaT
    df['age'] = (today - df['date_naissance']).dt.days // 365

    # Calcul de la tranche d'âge
    df['tranche_age'] = pd.cut(
        df['age'],
        bins=[0, 18, 25, 35, 45, 55, 65, 200],
        labels=['<18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+'],
        right=False
    )
    df['tranche_age'] = df['tranche_age'].astype(str).replace('nan', 'Inconnu')
    logging.info(
        f"[TRANSFORM] R3 dates naissance : {ages_invalides} âges invalides (< 16 ou > 100 ans)"
    )

    # R4 — Validation du format email par expression régulière
    pattern_email  = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    emails_invalides  = ~df['email'].str.match(pattern_email, na=False)
    nb_emails_invalides = emails_invalides.sum()
    df.loc[emails_invalides, 'email'] = None
    logging.info(
        f"[TRANSFORM] R4 emails : {nb_emails_invalides} emails invalides mis à NULL"
    )

    # R5 — Harmonisation des villes via le référentiel géographique
    df['ville'] = (
        df['ville'].str.strip().str.lower()
          .map(mapping_villes).fillna('Non renseignée')
    )
    non_mappees = (df['ville'] == 'Non renseignée').sum()
    logging.info(f"[TRANSFORM] R5 villes : harmonisées ({non_mappees} non mappées)")

    # Nettoyage des colonnes temporaires internes
    df = df.drop(columns=['email_norm', 'age'], errors='ignore')

    total_supprimees = initial - len(df)
    logging.info(
        f"[TRANSFORM] Clients : {initial} → {len(df)} lignes "
        f"({total_supprimees} supprimées au total)"
    )
    return df
