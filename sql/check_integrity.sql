-- ============================================================
-- Mexora Analytics -- Verification de l'Integrite du DWH
-- ============================================================

-- 1. Cles etrangeres orphelines
SELECT 'FK id_date orpheline' AS verification,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END AS resultat
FROM dwh_mexora.fait_ventes f LEFT JOIN dwh_mexora.dim_temps d ON f.id_date = d.id_date WHERE d.id_date IS NULL
UNION ALL
SELECT 'FK id_produit orpheline',
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END
FROM dwh_mexora.fait_ventes f LEFT JOIN dwh_mexora.dim_produit d ON f.id_produit = d.id_produit_sk WHERE d.id_produit_sk IS NULL
UNION ALL
SELECT 'FK id_client orpheline',
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END
FROM dwh_mexora.fait_ventes f LEFT JOIN dwh_mexora.dim_client d ON f.id_client = d.id_client_sk WHERE d.id_client_sk IS NULL
UNION ALL
SELECT 'FK id_region orpheline',
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END
FROM dwh_mexora.fait_ventes f LEFT JOIN dwh_mexora.dim_region d ON f.id_region = d.id_region WHERE d.id_region IS NULL
UNION ALL
SELECT 'FK id_livreur orpheline',
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END
FROM dwh_mexora.fait_ventes f LEFT JOIN dwh_mexora.dim_livreur d ON f.id_livreur = d.id_livreur WHERE d.id_livreur IS NULL;

-- 2. NULL invalides
SELECT 'NULL dans montant_ttc' AS verification,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END AS resultat
FROM dwh_mexora.fait_ventes WHERE montant_ttc IS NULL
UNION ALL
SELECT 'NULL dans montant_ht',
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END
FROM dwh_mexora.fait_ventes WHERE montant_ht IS NULL
UNION ALL
SELECT 'NULL dans quantite_vendue',
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END
FROM dwh_mexora.fait_ventes WHERE quantite_vendue IS NULL
UNION ALL
SELECT 'NULL dans id_date',
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END
FROM dwh_mexora.fait_ventes WHERE id_date IS NULL
UNION ALL
SELECT 'NULL dans id_client',
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END
FROM dwh_mexora.fait_ventes WHERE id_client IS NULL
UNION ALL
SELECT 'NULL dans id_produit',
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END
FROM dwh_mexora.fait_ventes WHERE id_produit IS NULL
UNION ALL
SELECT 'NULL dans id_region',
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END
FROM dwh_mexora.fait_ventes WHERE id_region IS NULL;

-- 3. Valeurs incoherentes
SELECT 'quantite_vendue <= 0' AS verification,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END AS resultat
FROM dwh_mexora.fait_ventes WHERE quantite_vendue <= 0
UNION ALL
SELECT 'montant_ttc < 0',
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END
FROM dwh_mexora.fait_ventes WHERE montant_ttc < 0
UNION ALL
SELECT 'remise_pct hors de [0, 100]',
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END
FROM dwh_mexora.fait_ventes WHERE remise_pct < 0 OR remise_pct > 100;

-- 4. Statuts invalides
SELECT 'statut_commande invalide' AS verification,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END AS resultat
FROM dwh_mexora.fait_ventes WHERE statut_commande NOT IN ('livre', 'annule', 'en_cours', 'retourne');

-- 5. SCD Type 2
SELECT 'SCD2 dim_produit doublons actifs' AS verification,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END AS resultat
FROM (
    SELECT id_produit_nk FROM dwh_mexora.dim_produit WHERE est_actif = TRUE GROUP BY id_produit_nk HAVING COUNT(*) > 1
) sub
UNION ALL
SELECT 'SCD2 dim_client doublons actifs',
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERREUR : ' || COUNT(*) || ' lignes invalides' END
FROM (
    SELECT id_client_nk FROM dwh_mexora.dim_client WHERE est_actif = TRUE GROUP BY id_client_nk HAVING COUNT(*) > 1
) sub;

-- 6. Vues materialisees non vides
SELECT 'mv_ca_mensuel non vide' AS verification,
    CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'ERREUR : 0 lignes' END AS resultat
FROM reporting_mexora.mv_ca_mensuel
UNION ALL
SELECT 'mv_top_produits non vide',
    CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'ERREUR : 0 lignes' END
FROM reporting_mexora.mv_top_produits
UNION ALL
SELECT 'mv_performance_livreurs non vide',
    CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'ERREUR : 0 lignes' END
FROM reporting_mexora.mv_performance_livreurs;

-- 7. Volumetrie finale
SELECT 'dim_temps'   AS table_name, COUNT(*) AS nb_lignes FROM dwh_mexora.dim_temps
UNION ALL
SELECT 'dim_produit', COUNT(*) FROM dwh_mexora.dim_produit
UNION ALL
SELECT 'dim_client',  COUNT(*) FROM dwh_mexora.dim_client
UNION ALL
SELECT 'dim_region',  COUNT(*) FROM dwh_mexora.dim_region
UNION ALL
SELECT 'dim_livreur', COUNT(*) FROM dwh_mexora.dim_livreur
UNION ALL
SELECT 'fait_ventes', COUNT(*) FROM dwh_mexora.fait_ventes;