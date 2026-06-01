-- =============================================================
-- Mexora ETL — Requêtes Dashboard Metabase
-- Fichier : queries_dashboard.sql
-- Description : 5 requêtes analytiques pour le dashboard décisionnel
-- =============================================================


-- =============================================================
-- Q1 — Évolution du CA mensuel par région (12 mois glissants)
-- Visualisation : Line chart — Axe X = mois, Axe Y = ca_total
--                Groupé par region_admin
-- =============================================================

SELECT
    annee,
    mois,
    libelle_mois,
    region_admin,
    SUM(ca_ttc)            AS ca_total,
    SUM(nb_commandes)      AS nb_commandes,
    SUM(nb_clients_actifs) AS nb_clients
FROM reporting_mexora.mv_ca_mensuel
GROUP BY annee, mois, libelle_mois, region_admin
ORDER BY annee, mois;


-- =============================================================
-- Q2 — Top 10 produits les plus vendus à Tanger par trimestre
-- Visualisation : Bar chart horizontal — nom_produit / ca_total
-- Filtre interactif : trimestre et année
-- =============================================================

SELECT
    t.annee,
    t.trimestre,
    p.nom_produit,
    p.categorie,
    SUM(f.quantite_vendue) AS qte_totale,
    SUM(f.montant_ttc)     AS ca_total
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_temps   t ON f.id_date    = t.id_date
JOIN dwh_mexora.dim_produit p ON f.id_produit = p.id_produit_sk
JOIN dwh_mexora.dim_region  r ON f.id_region  = r.id_region
WHERE r.ville           = 'Tanger'
  AND f.statut_commande = 'livré'
  AND p.est_actif       = TRUE
GROUP BY t.annee, t.trimestre, p.nom_produit, p.categorie
ORDER BY t.annee, t.trimestre, ca_total DESC
LIMIT 40;


-- =============================================================
-- Q3 — Panier moyen et CA par segment client (Gold/Silver/Bronze)
-- Visualisation : Pie chart (répartition CA) + tableau panier moyen
-- =============================================================

SELECT
    c.segment_client,
    COUNT(DISTINCT f.id_vente)                                           AS nb_commandes,
    ROUND(SUM(f.montant_ttc) / NULLIF(COUNT(DISTINCT f.id_vente), 0), 2) AS panier_moyen,
    ROUND(SUM(f.montant_ttc), 2)                                         AS ca_total
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_client c ON f.id_client = c.id_client_sk
WHERE f.statut_commande = 'livré'
  AND c.est_actif       = TRUE
GROUP BY c.segment_client
ORDER BY panier_moyen DESC;


-- =============================================================
-- Q4 — Taux de retour par catégorie de produit
-- Visualisation : Bar chart horizontal avec seuil d'alerte à 5 %
-- =============================================================

SELECT
    p.categorie,
    COUNT(*) FILTER (WHERE f.statut_commande = 'retourné') AS nb_retours,
    COUNT(*)                                                AS nb_total,
    ROUND(
        COUNT(*) FILTER (WHERE f.statut_commande = 'retourné') * 100.0
        / NULLIF(COUNT(*), 0), 2
    )                                                       AS taux_retour_pct
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_produit p ON f.id_produit = p.id_produit_sk
WHERE p.est_actif = TRUE
GROUP BY p.categorie
ORDER BY taux_retour_pct DESC;


-- =============================================================
-- Q5 — Effet Ramadan sur les ventes alimentaires
-- Visualisation : Bar chart — période / volume_total et ca_total
-- =============================================================

SELECT
    CASE
        WHEN t.periode_ramadan = TRUE THEN 'Pendant Ramadan'
        ELSE 'Hors Ramadan'
    END                            AS periode,
    SUM(f.quantite_vendue)         AS volume_total,
    ROUND(AVG(f.montant_ttc), 2)   AS panier_moyen,
    ROUND(SUM(f.montant_ttc), 2)   AS ca_total,
    COUNT(DISTINCT f.id_vente)     AS nb_commandes
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_temps   t ON f.id_date    = t.id_date
JOIN dwh_mexora.dim_produit p ON f.id_produit = p.id_produit_sk
WHERE p.categorie       = 'Alimentation'
  AND f.statut_commande = 'livré'
GROUP BY t.periode_ramadan
ORDER BY t.periode_ramadan DESC;


