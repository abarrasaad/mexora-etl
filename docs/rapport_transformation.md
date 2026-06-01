# 🧹 Rapport des Transformations ETL — Mexora Analytics

Ce document liste l'ensemble des règles métier appliquées lors de la phase `TRANSFORM` du pipeline ETL.

---

## 1. Commandes (`commandes_mexora.csv`)

### R1 — Suppression des doublons
- **Règle métier** : Les systèmes transactionnels peuvent générer des doublons sur l'`id_commande`. Il faut conserver uniquement la dernière occurrence.
- **Code Python** :
  ```python
  df = df.drop_duplicates(subset=['id_commande'], keep='last')
