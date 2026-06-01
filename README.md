# 🚀 Zara Commerce Analytics — Pipeline ETL & Data Warehouse

Ce dépôt contient l'implémentation d'un pipeline ETL complet (Extract, Transform, Load) en Python, conçu pour alimenter un Data Warehouse modélisé en étoile pour une entreprise de e-commerce marocaine.

---

## 🛠️ Prérequis

Pour exécuter ce pipeline, vous aurez besoin de :
- **Python 3.8+**
- **PostgreSQL 15+** (pour le mode postgres)
- **Java 11+** ou **Docker** (pour lancer Metabase)
- Les librairies Python listées dans `requirements.txt` : `pandas`, `sqlalchemy`, `psycopg2-binary`, `python-dotenv`

---

## ⚙️ Installation pas à pas

1. **Cloner le dépôt**
   ```bash
   git clone <url-du-depot>
   cd zara-etl
   ```

2. **Créer un environnement virtuel (recommandé)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**

   Copier le fichier exemple et renseigner vos identifiants PostgreSQL :
   ```bash
   cp .env.example .env
   ```
   Puis ouvrir `.env` et compléter :
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=ton_username
   DB_PASSWORD=ton_mot_de_passe
   ```

---

## 🎲 Génération des données de test

Les données brutes doivent être placées dans le dossier `data/` :
- `commandes_zara.csv`
- `clients_zara.csv`
- `produits_zara.json`
- `regions_maroc.csv`

---

## 🚀 Exécution du pipeline ETL

Le pipeline peut être lancé dans deux modes :

- **Mode CSV (par défaut)** : génère les tables du Data Warehouse sous forme de fichiers CSV dans `output/`.
  ```bash
  python main.py --mode csv
  ```

- **Mode PostgreSQL** : crée automatiquement les schémas, tables et vues, puis insère toutes les données.
  ```bash
  python main.py --mode postgres
  ```

---

## 🗄️ Ce qui se génère automatiquement en mode PostgreSQL

Lorsque vous lancez `python main.py --mode postgres`, le pipeline effectue automatiquement et dans l'ordre :

1. **Connexion à PostgreSQL** via les variables du fichier `.env`
2. **Exécution de `sql/create_dwh.sql`** qui crée :
   - Le schéma `dwh_zara` avec les 5 dimensions et la table de faits
   - Le schéma `staging_zara` pour les données intermédiaires
   - Le schéma `reporting_zara` avec 3 vues matérialisées analytiques
   - Tous les index de performance
3. **Insertion des données** par chunks de 5 000 lignes
4. **Affichage du résumé** dans les logs

| Schéma | Contenu |
|--------|---------|
| `dwh_zara` | `dim_client`, `dim_produit`, `dim_livreur`, `dim_region`, `dim_temps`, `fait_ventes` |
| `staging_zara` | Données brutes avant transformation |
| `reporting_zara` | `mv_ca_mensuel`, `mv_top_produits`, `mv_performance_livreurs` |

---

## 📁 Structure du projet

```
zara-etl/
├── config/
│   └── settings.py          # Configuration & chemins
├── extract/
│   └── extractor.py         # Fonctions d'extraction (CSV, JSON)
├── transform/
│   ├── clean_commandes.py   # Nettoyage des commandes
│   ├── clean_clients.py     # Nettoyage des clients
│   ├── clean_produits.py    # Nettoyage des produits
│   └── build_dimensions.py  # Construction dimensions & faits
├── load/
│   └── loader.py            # Chargement PostgreSQL & CSV
├── utils/
│   └── logger.py            # Configuration du logging
├── sql/
│   ├── create_dwh.sql       # Création du schéma en étoile
│   ├── check_integrity.sql  # Vérifications d'intégrité
│   └── queries_dashboard.sql# Requêtes analytiques Metabase
├── data/                    # Données sources (non versionnées)
├── output/                  # Fichiers CSV générés
├── logs/                    # Logs d'exécution horodatés
├── main.py                  # Point d'entrée du pipeline
├── requirements.txt
└── .env.example
```

---

## 📊 Modélisation en étoile

Le Data Warehouse suit un schéma en étoile avec :
- **5 dimensions** : `dim_temps`, `dim_produit`, `dim_client`, `dim_region`, `dim_livreur`
- **1 table de faits** : `fait_ventes`
- **SCD Type 2** sur `dim_produit` et `dim_client`
- **3 vues matérialisées** pour le reporting Metabase

---

## 🔍 Règles de transformation appliquées

### Commandes
| Règle | Description |
|-------|-------------|
| R1 | Suppression des doublons sur `id_commande` |
| R2 | Standardisation des dates au format `YYYY-MM-DD` |
| R3 | Harmonisation des noms de villes via le référentiel |
| R4 | Standardisation des statuts de commande |
| R5 | Suppression des lignes avec quantité ≤ 0 |
| R6 | Suppression des commandes test (prix = 0) |
| R7 | Remplacement des livreurs manquants par -1 |

### Clients
| Règle | Description |
|-------|-------------|
| R1 | Déduplication sur email normalisé |
| R2 | Standardisation du genre (m/f/inconnu) |
| R3 | Validation des âges (16 à 100 ans) |
| R4 | Validation des emails par regex |
| R5 | Harmonisation des villes |

### Produits
| Règle | Description |
|-------|-------------|
| R1 | Harmonisation des catégories en Title Case |
| R2 | Conservation des produits inactifs (SCD Type 2) |
| R3 | Remplacement des prix nuls par la médiane catégorie |
