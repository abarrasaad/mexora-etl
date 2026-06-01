-- ============================================================
-- SECTION 1 — Création des schémas
-- ============================================================
CREATE SCHEMA IF NOT EXISTS dwh_mexora;
CREATE SCHEMA IF NOT EXISTS staging_mexora;
CREATE SCHEMA IF NOT EXISTS reporting_mexora;

-- ============================================================
-- SECTION 2 — Création des tables dimensions
-- ============================================================
DROP TABLE IF EXISTS dwh_mexora.dim_temps CASCADE;
CREATE TABLE dwh_mexora.dim_temps (
    id_date         INT PRIMARY KEY,
    jour            INT,
    mois            INT,
    trimestre       INT,
    annee           INT,
    semaine         INT,
    libelle_jour    VARCHAR(50),
    libelle_mois    VARCHAR(50),
    est_weekend     BOOLEAN,
    est_ferie_maroc BOOLEAN,
    periode_ramadan BOOLEAN
);

DROP TABLE IF EXISTS dwh_mexora.dim_produit CASCADE;
CREATE TABLE dwh_mexora.dim_produit (
    id_produit_sk  SERIAL PRIMARY KEY,
    id_produit_nk  VARCHAR(50),
    nom_produit    VARCHAR(255),
    categorie      VARCHAR(100),
    sous_categorie VARCHAR(100),
    marque         VARCHAR(100),
    fournisseur    VARCHAR(100),
    prix_standard  NUMERIC(10, 2),
    origine_pays   VARCHAR(100),
    date_debut     DATE,
    date_fin       DATE,
    est_actif      BOOLEAN
);

DROP TABLE IF EXISTS dwh_mexora.dim_client CASCADE;
CREATE TABLE dwh_mexora.dim_client (
    id_client_sk      SERIAL PRIMARY KEY,
    id_client_nk      VARCHAR(50),
    nom_complet       VARCHAR(255),
    tranche_age       VARCHAR(50),
    sexe              VARCHAR(20),
    ville             VARCHAR(100),
    region_admin      VARCHAR(100),
    segment_client    VARCHAR(50),
    canal_acquisition VARCHAR(100),
    date_debut        DATE,
    date_fin          DATE,
    est_actif         BOOLEAN
);

DROP TABLE IF EXISTS dwh_mexora.dim_region CASCADE;
CREATE TABLE dwh_mexora.dim_region (
    id_region    SERIAL PRIMARY KEY,
    ville        VARCHAR(100),
    province     VARCHAR(100),
    region_admin VARCHAR(100),
    zone_geo     VARCHAR(50),
    pays         VARCHAR(50)
);

DROP TABLE IF EXISTS dwh_mexora.dim_livreur CASCADE;
CREATE TABLE dwh_mexora.dim_livreur (
    id_livreur      SERIAL PRIMARY KEY,
    id_livreur_nk   VARCHAR(50),
    nom_livreur     VARCHAR(255),
    type_transport  VARCHAR(50),
    zone_couverture VARCHAR(100)
);

-- ============================================================
-- SECTION 3 — Création de la table de faits
-- ============================================================
DROP TABLE IF EXISTS dwh_mexora.fait_ventes CASCADE;
CREATE TABLE dwh_mexora.fait_ventes (
    id_vente               SERIAL PRIMARY KEY,
    id_date                INT REFERENCES dwh_mexora.dim_temps(id_date),
    id_produit             INT REFERENCES dwh_mexora.dim_produit(id_produit_sk),
    id_client              INT REFERENCES dwh_mexora.dim_client(id_client_sk),
    id_region              INT REFERENCES dwh_mexora.dim_region(id_region),
    id_livreur             INT REFERENCES dwh_mexora.dim_livreur(id_livreur),
    quantite_vendue        INT           NOT NULL,
    montant_ht             NUMERIC(15, 2) NOT NULL,
    montant_ttc            NUMERIC(15, 2) NOT NULL,
    cout_livraison         NUMERIC(10, 2),
    delai_livraison_jours  INT,
    remise_pct             NUMERIC(5, 2),
    date_chargement        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut_commande        VARCHAR(50)   NOT NULL
);

-- ============================================================
-- SECTION 4 — Création des index de performance
-- ============================================================
CREATE INDEX idx_fv_date    ON dwh_mexora.fait_ventes(id_date);
CREATE INDEX idx_fv_produit ON dwh_mexora.fait_ventes(id_produit);
CREATE INDEX idx_fv_client  ON dwh_mexora.fait_ventes(id_client);
CREATE INDEX idx_fv_region  ON dwh_mexora.fait_ventes(id_region);
CREATE INDEX idx_fv_livreur ON dwh_mexora.fait_ventes(id_livreur);
CREATE INDEX idx_fv_date_region ON dwh_mexora.fait_ventes(id_date, id_region)
    INCLUDE (montant_ttc, quantite_vendue);
CREATE INDEX idx_fv_statut_livre ON dwh_mexora.fait_ventes(statut_commande)
    WHERE statut_commande = 'livré';

-- ============================================================
-- SECTION 5 — Création des vues matérialisées (reporting)
-- ============================================================

-- 1. Vue CA Mensuel
DROP MATERIALIZED VIEW IF EXISTS reporting_mexora.mv_ca_mensuel CASCADE;
CREATE MATERIALIZED VIEW reporting_mexora.mv_ca_mensuel AS
SELECT
    t.annee,
    t.mois,
    t.libelle_mois,
    t.periode_ramadan,
    r.region_admin,
    r.zone_geo,
    p.categorie,
    SUM(f.montant_ttc)           AS ca_ttc,
    SUM(f.montant_ht)            AS ca_ht,
    COUNT(DISTINCT f.id_client)  AS nb_clients_actifs,
    SUM(f.quantite_vendue)       AS volume_vendu,
    AVG(f.montant_ttc)           AS panier_moyen,
    COUNT(DISTINCT f.id_vente)   AS nb_commandes
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_temps   t ON f.id_date    = t.id_date
JOIN dwh_mexora.dim_region  r ON f.id_region  = r.id_region
JOIN dwh_mexora.dim_produit p ON f.id_produit = p.id_produit_sk
WHERE f.statut_commande = 'livré'
GROUP BY t.annee, t.mois, t.libelle_mois, t.periode_ramadan,
         r.region_admin, r.zone_geo, p.categorie
WITH DATA;
CREATE INDEX idx_mv_ca_annee_mois ON reporting_mexora.mv_ca_mensuel(annee, mois);
CREATE INDEX idx_mv_ca_region     ON reporting_mexora.mv_ca_mensuel(region_admin);
CREATE INDEX idx_mv_ca_categorie  ON reporting_mexora.mv_ca_mensuel(categorie);

-- 2. Vue Top Produits
DROP MATERIALIZED VIEW IF EXISTS reporting_mexora.mv_top_produits CASCADE;
CREATE MATERIALIZED VIEW reporting_mexora.mv_top_produits AS
SELECT
    t.annee,
    t.trimestre,
    p.nom_produit,
    p.categorie,
    p.marque,
    SUM(f.quantite_vendue)      AS qte_totale,
    SUM(f.montant_ttc)          AS ca_total,
    COUNT(DISTINCT f.id_client) AS nb_clients_distincts,
    RANK() OVER (
        PARTITION BY t.annee, t.trimestre, p.categorie
        ORDER BY SUM(f.montant_ttc) DESC
    ) AS rang_dans_categorie
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_temps   t ON f.id_date    = t.id_date
JOIN dwh_mexora.dim_produit p ON f.id_produit = p.id_produit_sk
WHERE f.statut_commande = 'livré'
GROUP BY t.annee, t.trimestre, p.nom_produit, p.categorie, p.marque
WITH DATA;

-- 3. Vue Performance Livreurs
DROP MATERIALIZED VIEW IF EXISTS reporting_mexora.mv_performance_livreurs CASCADE;
CREATE MATERIALIZED VIEW reporting_mexora.mv_performance_livreurs AS
SELECT
    l.nom_livreur,
    l.zone_couverture,
    t.annee,
    t.mois,
    COUNT(*)                                    AS nb_livraisons,
    AVG(f.delai_livraison_jours)                AS delai_moyen_jours,
    COUNT(*) FILTER (WHERE f.delai_livraison_jours > 3) AS nb_livraisons_retard,
    ROUND(
        COUNT(*) FILTER (WHERE f.delai_livraison_jours > 3) * 100.0
        / NULLIF(COUNT(*), 0), 2
    )                                           AS taux_retard_pct
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_livreur l ON f.id_livreur = l.id_livreur
JOIN dwh_mexora.dim_temps   t ON f.id_date    = t.id_date
WHERE f.statut_commande IN ('livré', 'retourné')
  AND f.delai_livraison_jours IS NOT NULL
GROUP BY l.nom_livreur, l.zone_couverture, t.annee, t.mois
WITH DATA;

-- ============================================================
-- SECTION 6 — Refresh des vues matérialisées
-- ============================================================
REFRESH MATERIALIZED VIEW reporting_mexora.mv_ca_mensuel;
REFRESH MATERIALIZED VIEW reporting_mexora.mv_top_produits;
REFRESH MATERIALIZED VIEW reporting_mexora.mv_performance_livreurs;
