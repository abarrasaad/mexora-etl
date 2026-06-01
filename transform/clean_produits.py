# =============================================================================
# MEXORA ETL — Nettoyage des Produits
# =============================================================================
# Règles de transformation appliquées :
#   R1 - Harmonisation de la casse des catégories (Title Case)
#   R2 - Gestion des produits inactifs (marquage pour SCD Type 2)
#   R3 - Traitement des prix_catalogue nuls (remplacement par la médiane)
# =============================================================================

import pandas as pd
import logging


def transform_produits(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique l'ensemble des règles de nettoyage sur les produits MEXORA.

    Args:
        df: DataFrame brut des produits

    Returns:
        DataFrame nettoyé
    """
    initial = len(df)
    logging.info(f"[TRANSFORM] Produits — Début du nettoyage ({initial} lignes)")

    # R1 — Harmonisation de la casse des catégories en Title Case
    df['categorie']     = df['categorie'].str.strip().str.lower().str.title()
    df['sous_categorie'] = df['sous_categorie'].str.strip()
    nb_categories = df['categorie'].nunique()
    logging.info(
        f"[TRANSFORM] R1 catégories : harmonisées en Title Case "
        f"({nb_categories} catégories distinctes)"
    )

    # Correction d'encodage : "Électronique" → "Electronique" pour uniformité
    df['categorie'] = df['categorie'].str.replace('Électronique', 'Electronique', regex=False)

    # R2 — Conservation des produits inactifs pour l'historique SCD Type 2
    # Les produits inactifs peuvent apparaître dans des commandes passées ;
    # ils sont donc conservés et marqués plutôt que supprimés.
    nb_inactifs = (
        (~df['actif']).sum()
        if df['actif'].dtype == bool
        else (df['actif'] == False).sum()
    )
    logging.info(
        f"[TRANSFORM] R2 produits inactifs : {nb_inactifs} produits conservés "
        f"(marqués inactifs — SCD Type 2)"
    )

    # R3 — Remplacement des prix_catalogue nuls par la médiane de la catégorie
    prix_null = df['prix_catalogue'].isna().sum()
    if prix_null > 0:
        mediane_par_cat = df.groupby('categorie')['prix_catalogue'].transform('median')
        df['prix_catalogue'] = df['prix_catalogue'].fillna(mediane_par_cat)
        # Secours : médiane globale si toute une catégorie manque de prix
        mediane_globale = df['prix_catalogue'].median()
        df['prix_catalogue'] = df['prix_catalogue'].fillna(mediane_globale)
    logging.info(
        f"[TRANSFORM] R3 prix catalogue : {prix_null} valeurs nulles "
        f"remplacées par la médiane catégorie"
    )

    # Nettoyage des espaces superflus dans les colonnes texte restantes
    df['marque']      = df['marque'].str.strip()
    df['fournisseur'] = df['fournisseur'].str.strip()
    df['nom']         = df['nom'].str.strip()

    logging.info(
        f"[TRANSFORM] Produits : {initial} → {len(df)} lignes (aucune suppression)"
    )
    return df
