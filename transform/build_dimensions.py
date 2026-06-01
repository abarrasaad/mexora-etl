# =============================================================================
# MEXORA ETL — Construction des Dimensions & Table de Faits
# =============================================================================
import pandas as pd
import numpy as np
import logging
from datetime import date, timedelta
from config.settings import (
    DIM_TEMPS_START, DIM_TEMPS_END,
    SEGMENT_GOLD_THRESHOLD, SEGMENT_SILVER_THRESHOLD, TVA_RATE
)


# ======================== DIM_TEMPS ========================

def build_dim_temps(date_debut: str = DIM_TEMPS_START,
                    date_fin: str = DIM_TEMPS_END) -> pd.DataFrame:
    """
    Génère la dimension temporelle complète entre deux dates.
    Intègre les jours fériés marocains fixes et les périodes Ramadan approximatives.
    """
    dates = pd.date_range(start=date_debut, end=date_fin, freq='D')

    # Jours fériés marocains officiels (dates fixes uniquement)
    feries_fixes = []
    for year in range(dates.year.min(), dates.year.max() + 1):
        feries_fixes.extend([
            f'{year}-01-01',   # Nouvel An
            f'{year}-01-11',   # Manifeste de l'Indépendance
            f'{year}-05-01',   # Fête du Travail
            f'{year}-07-30',   # Fête du Trône
            f'{year}-08-14',   # Allégeance Oued Eddahab
            f'{year}-08-20',   # Révolution du Roi et du Peuple
            f'{year}-08-21',   # Fête de la Jeunesse
            f'{year}-11-06',   # Marche Verte
            f'{year}-11-18',   # Fête de l'Indépendance
        ])

    # Dates Ramadan approximatives 2020-2025 (variables selon le calendrier lunaire)
    ramadan_periodes = [
        ('2020-04-24', '2020-05-23'),
        ('2021-04-13', '2021-05-12'),
        ('2022-04-02', '2022-05-01'),
        ('2023-03-22', '2023-04-20'),
        ('2024-03-10', '2024-04-09'),
        ('2025-02-28', '2025-03-29'),
    ]

    df = pd.DataFrame({
        'id_date':          dates.strftime('%Y%m%d').astype(int),
        'date_complete':    dates,
        'jour':             dates.day,
        'mois':             dates.month,
        'trimestre':        dates.quarter,
        'annee':            dates.year,
        'semaine':          dates.isocalendar().week.astype(int),
        'libelle_jour':     dates.strftime('%A'),
        'libelle_mois':     dates.strftime('%B'),
        'est_weekend':      dates.dayofweek >= 5,
        'est_ferie_maroc':  dates.strftime('%Y-%m-%d').isin(feries_fixes),
    })

    # Indicateur de période Ramadan
    df['periode_ramadan'] = False
    for debut, fin in ramadan_periodes:
        masque = (df['date_complete'] >= debut) & (df['date_complete'] <= fin)
        df.loc[masque, 'periode_ramadan'] = True

    output_cols = [
        'id_date', 'jour', 'mois', 'trimestre', 'annee', 'semaine',
        'libelle_jour', 'libelle_mois', 'est_weekend',
        'est_ferie_maroc', 'periode_ramadan'
    ]

    logging.info(
        f"[TRANSFORM] DIM_TEMPS : {len(df)} jours générés ({date_debut} → {date_fin})"
    )
    return df[output_cols]


# ======================== DIM_PRODUIT ========================

def build_dim_produit(df_produits: pd.DataFrame) -> pd.DataFrame:
    """
    Construit la dimension produit avec colonnes SCD Type 2.

    SCD Type 2 : l'historique des changements est conservé.
    Colonnes ajoutées : date_debut, date_fin, est_actif
    """
    dim = df_produits.rename(columns={
        'id_produit':    'id_produit_nk',
        'nom':           'nom_produit',
        'prix_catalogue': 'prix_standard',
    })

    # Colonnes SCD Type 2
    dim['date_debut'] = pd.Timestamp.today().strftime('%Y-%m-%d')
    dim['date_fin']   = '9999-12-31'
    dim['est_actif']  = dim['actif'] if 'actif' in dim.columns else True

    # Clé de substitution (surrogate key)
    dim = dim.reset_index(drop=True)
    dim['id_produit_sk'] = dim.index + 1

    output_cols = [
        'id_produit_sk', 'id_produit_nk', 'nom_produit', 'categorie',
        'sous_categorie', 'marque', 'fournisseur', 'prix_standard',
        'origine_pays', 'date_debut', 'date_fin', 'est_actif'
    ]

    logging.info(
        f"[TRANSFORM] DIM_PRODUIT : {len(dim)} produits "
        f"(dont {(~dim['est_actif']).sum()} inactifs)"
    )
    return dim[output_cols]


# ======================== DIM_CLIENT ========================

def build_dim_client(df_clients: pd.DataFrame, df_commandes: pd.DataFrame) -> pd.DataFrame:
    """
    Construit la dimension client avec segmentation Gold/Silver/Bronze
    et colonnes SCD Type 2.
    """
    # Calcul préalable des segments
    segments = calculer_segments_clients(df_commandes)

    dim = df_clients.copy()
    dim['nom_complet'] = dim['prenom'].str.strip() + ' ' + dim['nom'].str.strip()
    dim = dim.rename(columns={'id_client': 'id_client_nk'})

    # Jointure avec les segments calculés
    dim = dim.merge(
        segments[['id_client', 'segment_client']],
        left_on='id_client_nk', right_on='id_client', how='left'
    )
    dim['segment_client'] = dim['segment_client'].fillna('Bronze')
    dim = dim.drop(columns=['id_client'], errors='ignore')

    # Colonnes SCD Type 2
    dim['date_debut'] = pd.Timestamp.today().strftime('%Y-%m-%d')
    dim['date_fin']   = '9999-12-31'
    dim['est_actif']  = True

    # Clé de substitution
    dim = dim.reset_index(drop=True)
    dim['id_client_sk'] = dim.index + 1

    dim['region_admin'] = dim.get('region_admin', 'Non renseignée')

    output_cols = [
        'id_client_sk', 'id_client_nk', 'nom_complet', 'tranche_age',
        'sexe', 'ville', 'region_admin', 'segment_client',
        'canal_acquisition', 'date_debut', 'date_fin', 'est_actif'
    ]

    for col in output_cols:
        if col not in dim.columns:
            dim[col] = None

    logging.info(f"[TRANSFORM] DIM_CLIENT : {len(dim)} clients")
    logging.info(
        f"[TRANSFORM] Segments — Gold: {(dim['segment_client'] == 'Gold').sum()}, "
        f"Silver: {(dim['segment_client'] == 'Silver').sum()}, "
        f"Bronze: {(dim['segment_client'] == 'Bronze').sum()}"
    )
    return dim[output_cols]


def calculer_segments_clients(df_commandes: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule le segment client (Gold/Silver/Bronze) basé sur le chiffre d'affaires
    cumulé des 12 derniers mois pour chaque client.

    Règles métier :
      Gold   : CA 12 mois >= 15 000 MAD
      Silver : CA 12 mois >= 5 000 MAD
      Bronze : CA 12 mois <  5 000 MAD
    """
    date_limite = pd.Timestamp(date.today() - timedelta(days=365))

    df_recents = df_commandes[
        (df_commandes['date_commande'] >= date_limite) &
        (df_commandes['statut'] == 'livré')
    ].copy()

    df_recents['montant_ttc'] = (
        df_recents['quantite'].astype(float) * df_recents['prix_unitaire'].astype(float)
    )

    ca_par_client          = df_recents.groupby('id_client')['montant_ttc'].sum().reset_index()
    ca_par_client.columns  = ['id_client', 'ca_12m']

    def segmenter(ca):
        if ca >= SEGMENT_GOLD_THRESHOLD:
            return 'Gold'
        elif ca >= SEGMENT_SILVER_THRESHOLD:
            return 'Silver'
        else:
            return 'Bronze'

    ca_par_client['segment_client'] = ca_par_client['ca_12m'].apply(segmenter)

    logging.info(f"[TRANSFORM] Segmentation : {len(ca_par_client)} clients analysés")
    return ca_par_client[['id_client', 'segment_client', 'ca_12m']]


# ======================== DIM_REGION ========================

def build_dim_region(df_regions: pd.DataFrame) -> pd.DataFrame:
    """
    Construit la dimension géographique à partir du référentiel officiel des régions.
    """
    dim = df_regions.rename(columns={'nom_ville_standard': 'ville'})
    dim['pays']      = 'Maroc'
    dim              = dim.reset_index(drop=True)
    dim['id_region'] = dim.index + 1

    output_cols = ['id_region', 'ville', 'province', 'region_admin', 'zone_geo', 'pays']

    logging.info(f"[TRANSFORM] DIM_REGION : {len(dim)} régions")
    return dim[output_cols]


# ======================== DIM_LIVREUR ========================

def build_dim_livreur(df_commandes: pd.DataFrame) -> pd.DataFrame:
    """
    Construit la dimension livreur à partir des identifiants présents dans les commandes.
    Les attributs livreur sont générés (non disponibles dans la source).
    """
    livreurs = df_commandes['id_livreur'].dropna().unique()
    livreurs = [l for l in livreurs if l not in ('-1', '')]

    types_transport = ['Moto', 'Voiture', 'Camionnette', 'Vélo']
    zones           = ['Nord', 'Centre', 'Sud', 'Est']

    records = []
    for i, lid in enumerate(sorted(livreurs)):
        records.append({
            'id_livreur':      i + 1,
            'id_livreur_nk':   lid,
            'nom_livreur':     f'Livreur_{lid}',
            'type_transport':  types_transport[i % len(types_transport)],
            'zone_couverture': zones[i % len(zones)],
        })

    # Livreur sentinelle pour les commandes sans livreur identifié
    records.append({
        'id_livreur':      len(records) + 1,
        'id_livreur_nk':   '-1',
        'nom_livreur':     'Inconnu',
        'type_transport':  'Non renseigné',
        'zone_couverture': 'Non renseignée',
    })

    dim = pd.DataFrame(records)
    logging.info(f"[TRANSFORM] DIM_LIVREUR : {len(dim)} livreurs (dont 1 inconnu)")
    return dim


# ======================== FAIT_VENTES ========================

def build_fait_ventes(df_commandes: pd.DataFrame,
                      dim_temps: pd.DataFrame,
                      dim_client: pd.DataFrame,
                      dim_produit: pd.DataFrame,
                      dim_region: pd.DataFrame,
                      dim_livreur: pd.DataFrame) -> pd.DataFrame:
    """
    Construit la table de faits FAIT_VENTES en résolvant les clés de substitution
    (surrogate keys) de toutes les dimensions.

    Mesures calculées :
      - montant_ht              : quantite × prix_unitaire            (additive)
      - montant_ttc             : montant_ht × (1 + TVA)              (additive)
      - cout_livraison          : estimé selon la quantité            (additive)
      - delai_livraison_jours   : date_livraison − date_commande      (semi-additive)
      - remise_pct              : non disponible dans la source        (non-additive)
    """
    fait = df_commandes.copy()

    # --- Clé temporelle ---
    fait['id_date'] = fait['date_commande'].dt.strftime('%Y%m%d').astype(int)

    # --- Clé produit ---
    produit_mapping = dim_produit.set_index('id_produit_nk')['id_produit_sk'].to_dict()
    fait['id_produit'] = fait['id_produit'].map(produit_mapping)

    # --- Clé client ---
    client_mapping = dim_client.set_index('id_client_nk')['id_client_sk'].to_dict()
    fait['id_client'] = fait['id_client'].map(client_mapping)

    # --- Clé région ---
    region_mapping = dim_region.set_index('ville')['id_region'].to_dict()
    fait['id_region'] = fait['ville_livraison'].map(region_mapping)

    # --- Clé livreur ---
    livreur_mapping = dim_livreur.set_index('id_livreur_nk')['id_livreur'].to_dict()
    fait['id_livreur'] = fait['id_livreur'].map(livreur_mapping)

    # --- Mesures additives ---
    fait['quantite_vendue'] = fait['quantite'].astype(int)
    fait['montant_ht']      = (fait['quantite_vendue'] * fait['prix_unitaire'].astype(float)).round(2)
    fait['montant_ttc']     = (fait['montant_ht'] * (1 + TVA_RATE)).round(2)

    # Coût de livraison estimé (5 MAD/unité + 10 MAD fixe, plafonné à 50 MAD)
    fait['cout_livraison'] = (fait['quantite_vendue'] * 5 + 10).clip(upper=50).astype(float)

    # --- Mesures semi-additives ---
    fait['delai_livraison_jours'] = (
        fait['date_livraison'] - fait['date_commande']
    ).dt.days
    fait.loc[fait['delai_livraison_jours'] < 0, 'delai_livraison_jours'] = None

    # --- Mesures non-additives ---
    fait['remise_pct'] = 0.0   # Pas de remise dans les données sources

    fait['statut_commande'] = fait['statut']

    # Suppression des lignes sans correspondance dimensionnelle
    avant = len(fait)
    fait  = fait.dropna(subset=['id_date', 'id_produit', 'id_client'])
    apres = len(fait)
    if avant > apres:
        logging.warning(
            f"[TRANSFORM] FAIT_VENTES : {avant - apres} lignes sans correspondance "
            f"dimension supprimées"
        )

    # Métadonnées ETL
    fait['date_chargement'] = pd.Timestamp.now()

    # Clé de substitution de la table de faits
    fait = fait.reset_index(drop=True)
    fait['id_vente'] = fait.index + 1

    output_cols = [
        'id_vente', 'id_date', 'id_produit', 'id_client', 'id_region',
        'id_livreur', 'quantite_vendue', 'montant_ht', 'montant_ttc',
        'cout_livraison', 'delai_livraison_jours', 'remise_pct',
        'date_chargement', 'statut_commande'
    ]

    logging.info(f"[TRANSFORM] FAIT_VENTES : {len(fait)} lignes construites")
    logging.info(f"[TRANSFORM] CA total HT  : {fait['montant_ht'].sum():,.2f} MAD")
    logging.info(f"[TRANSFORM] CA total TTC : {fait['montant_ttc'].sum():,.2f} MAD")
    return fait[output_cols]
