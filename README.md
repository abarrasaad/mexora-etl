# 🚀 Mexora Analytics — Pipeline ETL & Data Warehouse

Bienvenue dans le dépôt du Miniprojet 1 pour **Mexora Analytics**.
Ce projet consiste à concevoir et implémenter un pipeline ETL complet (Extract, Transform, Load) en Python, afin d'alimenter un Data Warehouse modélisé en étoile pour une entreprise de e-commerce marocaine.

---

## 🛠️ Prérequis

Pour exécuter ce pipeline, vous aurez besoin des éléments suivants :
- **Python 3.8+**
- **PostgreSQL 15+** (si vous souhaitez charger les données en base)
- **Java 11+** ou **Docker** (pour lancer Metabase)
- Les librairies Python listées dans `requirements.txt` : `pandas`, `sqlalchemy`, `psycopg2-binary`, `python-dotenv`

---

## ⚙️ Installation pas à pas

1. **Cloner le dépôt**
   ```bash
   git clone <url-du-depot>
   cd mexora_etl
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

Les données brutes ne sont pas fournies dans le dépôt. Vous devez les générer à l'aide du script prévu à cet effet, qui injectera automatiquement les anomalies et problèmes intentionnels requis par le cahier des charges.

```bash
python data/generate_all_data.py
```

Cela crée 4 fichiers dans le dossier `data/` : `commandes_mexora.csv`, `clients_mexora.csv`, `produits_mexora.json` et `regions_maroc.csv`.

---

## 🚀 Exécution du pipeline ETL

Le pipeline peut être lancé dans deux modes différents :

- **Mode CSV (par défaut)** : Extrait, nettoie, transforme les données et génère les tables du Data Warehouse sous forme de fichiers CSV dans le dossier `output/`.
  ```bash
  python main.py --mode csv
  ```

- **Mode PostgreSQL** : Crée automatiquement les schémas, tables et vues dans votre base PostgreSQL, puis insère toutes les données. Aucune manipulation manuelle de SQL n'est nécessaire.
  ```bash
  python main.py --mode postgres
  ```

---

## 🗄️ Ce qui se génère automatiquement en mode PostgreSQL

Lorsque vous lancez `python main.py --mode postgres`, le pipeline effectue **automatiquement et dans l'ordre** :

1. **Connexion à PostgreSQL** via les variables du fichier `.env`
2. **Exécution de `sql/create_dwh.sql`** qui crée :
   - Le schéma `dwh_mexora` avec les 5 tables de dimension et la table de faits
   - Le schéma `staging_mexora` pour les données brutes intermédiaires
   - Le schéma `reporting_mexora` avec 3 vues matérialisées analytiques prêtes pour Metabase
   - Tous les index de performance
3. **Insertion des données** dans toutes les tables (par chunks de 5 000 lignes)
4. **Affichage du résumé** dans les logs avec le nombre de lignes chargées et le CA total

| Schéma | Contenu |
|--------|---------|
| `dwh_mexora` | `dim_client`, `dim_produit`, `dim_livreur`, `dim_region`, `dim_temps`, `fait_ventes` |
| `staging_mexora` | Données brutes avant transformation |
| `reporting_mexora` | `mv_ca_mensuel`, `mv_top_produits`, `mv_performance_livreurs` — vues SQL analytiques pour les dashboards |

---

## 📊 Connexion et configuration de Metabase

Metabase est l'outil de visualisation utilisé pour explorer les données du DWH.

### 1. Télécharger et lancer Metabase

Depuis [https://www.metabase.com/start/oss/](https://www.metabase.com/start/oss/), choisissez votre méthode :

**Option Docker (recommandée) :**
```bash
docker run -d -p 3000:3000 --name metabase metabase/metabase
```

**Option jar :**
```bash
java -jar metabase.jar
```

### 2. Ouvrir l'interface

Ouvrir [http://localhost:3000](http://localhost:3000) dans votre navigateur.

### 3. Créer un compte administrateur

Lors du premier lancement, Metabase vous guide pour créer un compte admin.

### 4. Connecter Metabase à PostgreSQL

- Aller dans **Paramètres → Admin → Bases de données → Ajouter une base de données**
- Choisir **PostgreSQL**
- Renseigner :
  - **Host** : `localhost`
  - **Port** : `5432`
  - **Database name** : la valeur de `DB_NAME` dans votre `.env`
  - **Username / Password** : vos identifiants PostgreSQL
- Cliquer sur **Enregistrer**

### 5. Explorer les données

Metabase scannera automatiquement les schémas `dwh_mexora` et `reporting_mexora`.

Pour créer des visualisations :
- Aller dans **Nouvelle question** → choisir le schéma `dwh_mexora`
- Les tables `dim_*` et `fait_ventes` sont directement disponibles
- Les vues analytiques pré-calculées sont dans le schéma `reporting_mexora`

---

## 📂 Structure complète du projet

```text
mexora_etl/
├── config/
│   └── settings.py              # Paramètres lus depuis .env (connexion BDD, chemins, constantes)
├── data/                        # Données brutes générées (ignorées par git)
│   ├── generate_all_data.py     # Script de génération des données avec anomalies intentionnelles
│   └── ... (CSV/JSON générés)
├── extract/
│   └── extractor.py             # Fonctions d'extraction brute (CSV → DataFrame, JSON → DataFrame)
├── transform/
│   ├── clean_commandes.py       # Règles R1–R7 de nettoyage des commandes
│   ├── clean_clients.py         # Règles R1–R5 de nettoyage des clients
│   ├── clean_produits.py        # Règles R1–R3 de nettoyage des produits
│   └── build_dimensions.py      # Construction des 5 dimensions et de la table de faits
├── load/
│   └── loader.py                # Chargement PostgreSQL (replace/append) et fallback CSV
├── utils/
│   └── logger.py                # Logging dual : console + fichier horodaté
├── sql/
│   ├── create_dwh.sql           # Schémas + tables + index + vues matérialisées (auto-exécuté)
│   ├── queries_dashboard.sql    # 5 requêtes analytiques pour les dashboards Metabase
│   └── check_integrity.sql      # Vérifications d'intégrité référentielle
├── logs/                        # Fichiers de log horodatés (ignorés par git)
├── output/                      # Fichiers CSV finaux en mode csv (ignorés par git)
├── main.py                      # Point d'entrée — orchestre Extract → Transform → Load
├── requirements.txt             # Dépendances Python
├── .env.example                 # Template des variables d'environnement (à copier en .env)
├── .gitignore                   # Exclut .env, venv/, logs/, output/, __pycache__/
├── README.md                    # Ce fichier
└── rapport_transformations.md   # Documentation détaillée des règles métier ETL
```

---

## 📈 Bilan de l'exécution et Performances

Notre pipeline a été optimisé pour être extrêmement performant grâce à l'utilisation native de `pandas`.

**Chiffres clés du dernier run :**
- **Données en entrée** : 50 000 commandes
- **Nettoyage initial** : 2 697 lignes rejetées (doublons, prix nuls, quantités invalides)
- **Validation dimensionnelle** : 1 716 lignes rejetées (intégrité référentielle non respectée)
- **Sortie finale** : **45 587 lignes saines** chargées dans `FAIT_VENTES`
- **Temps d'exécution (mode CSV)** : **~5.5 secondes**
- **Temps d'exécution (mode PostgreSQL)** : **~35 secondes**

### 📝 Exemple de sortie des logs (Console)

```log
2026-04-22 22:54:09,680 — INFO — ============================================================
2026-04-22 22:54:09,680 — INFO — DÉMARRAGE PIPELINE ETL MEXORA
2026-04-22 22:54:09,680 — INFO — Mode de chargement : POSTGRES
2026-04-22 22:54:09,680 — INFO — ============================================================
...
2026-04-22 22:54:10,056 — INFO — [INIT] Exécution de create_dwh.sql — création des schémas et tables...
2026-04-22 22:54:10,500 — INFO — [INIT] Schémas, tables et vues créés avec succès.
...
2026-04-22 22:54:12,473 — INFO — [TRANSFORM] Commandes : 50000 → 47303 lignes (2697 supprimées, 5.4%)
...
2026-04-22 22:54:13,857 — INFO — [TRANSFORM] FAIT_VENTES : 45587 lignes construites
2026-04-22 22:54:13,860 — INFO — [TRANSFORM] CA total TTC : 2,256,549,112.80 MAD
...
2026-04-22 22:54:15,178 — INFO — PIPELINE ETL MEXORA — TERMINÉ AVEC SUCCÈS
2026-04-22 22:54:15,178 — INFO — Durée totale : 34.5 secondes
2026-04-22 22:54:15,180 — INFO — ============================================================
```
