"""
Mexora Analytics — Générateur de données brutes
Génère les 4 fichiers avec les problèmes intentionnels exigés par l'énoncé.
"""
import csv
import json
import random
import os
from datetime import datetime, timedelta

random.seed(42)
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# 1. RÉGIONS MAROC (référentiel propre — aucun problème)
# =============================================================================
REGIONS_DATA = [
    ("TNG", "Tanger", "Tanger-Assilah", "Tanger-Tétouan-Al Hoceïma", "Nord", 1065601, "90000"),
    ("TET", "Tétouan", "Tétouan", "Tanger-Tétouan-Al Hoceïma", "Nord", 380787, "93000"),
    ("ALH", "Al Hoceïma", "Al Hoceïma", "Tanger-Tétouan-Al Hoceïma", "Nord", 395644, "32000"),
    ("CAS", "Casablanca", "Casablanca", "Casablanca-Settat", "Centre", 3359818, "20000"),
    ("MOH", "Mohammedia", "Mohammedia", "Casablanca-Settat", "Centre", 208612, "28800"),
    ("SET", "Settat", "Settat", "Casablanca-Settat", "Centre", 142250, "26000"),
    ("RBT", "Rabat", "Rabat", "Rabat-Salé-Kénitra", "Centre", 577827, "10000"),
    ("SLA", "Salé", "Salé", "Rabat-Salé-Kénitra", "Centre", 982163, "11000"),
    ("KNT", "Kénitra", "Kénitra", "Rabat-Salé-Kénitra", "Centre", 431282, "14000"),
    ("FES", "Fès", "Fès", "Fès-Meknès", "Centre", 1150131, "30000"),
    ("MEK", "Meknès", "Meknès", "Fès-Meknès", "Centre", 632079, "50000"),
    ("MRK", "Marrakech", "Marrakech", "Marrakech-Safi", "Sud", 928850, "40000"),
    ("SFI", "Safi", "Safi", "Marrakech-Safi", "Sud", 308508, "46000"),
    ("AGD", "Agadir", "Agadir-Ida Ou Tanane", "Souss-Massa", "Sud", 421844, "80000"),
    ("OUJ", "Oujda", "Oujda-Angad", "L'Oriental", "Est", 494252, "60000"),
    ("NAD", "Nador", "Nador", "L'Oriental", "Est", 161726, "62000"),
    ("BNM", "Béni Mellal", "Béni Mellal", "Béni Mellal-Khénifra", "Centre", 192676, "23000"),
    ("ERR", "Errachidia", "Errachidia", "Drâa-Tafilalet", "Sud", 92374, "52000"),
    ("LAY", "Laâyoune", "Laâyoune", "Laâyoune-Sakia El Hamra", "Sud", 217732, "70000"),
    ("DAK", "Dakhla", "Oued Ed-Dahab", "Dakhla-Oued Ed-Dahab", "Sud", 106277, "73000"),
    ("TAZ", "Taza", "Taza", "Fès-Meknès", "Centre", 148406, "35000"),
    ("KHM", "Khémisset", "Khémisset", "Rabat-Salé-Kénitra", "Centre", 131542, "15000"),
    ("ELJ", "El Jadida", "El Jadida", "Casablanca-Settat", "Centre", 194934, "24000"),
    ("GUE", "Guelmim", "Guelmim", "Guelmim-Oued Noun", "Sud", 118318, "81000"),
    ("OUA", "Ouarzazate", "Ouarzazate", "Drâa-Tafilalet", "Sud", 71067, "45000"),
    ("TAN", "Tan-Tan", "Tan-Tan", "Guelmim-Oued Noun", "Sud", 73209, "82000"),
    ("KHO", "Khouribga", "Khouribga", "Béni Mellal-Khénifra", "Centre", 196196, "25000"),
    ("LRK", "Larache", "Larache", "Tanger-Tétouan-Al Hoceïma", "Nord", 125008, "92000"),
    ("CHF", "Chefchaouen", "Chefchaouen", "Tanger-Tétouan-Al Hoceïma", "Nord", 42786, "91000"),
    ("IFR", "Ifrane", "Ifrane", "Fès-Meknès", "Centre", 33873, "53000"),
]

VILLES_STANDARD = [r[1] for r in REGIONS_DATA]

def generate_regions():
    path = os.path.join(DATA_DIR, "regions_maroc.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["code_ville","nom_ville_standard","province","region_admin","zone_geo","population","code_postal"])
        for r in REGIONS_DATA:
            w.writerow(r)
    print(f"[OK] regions_maroc.csv — {len(REGIONS_DATA)} lignes")

# =============================================================================
# 2. PRODUITS MEXORA (JSON — avec problèmes intentionnels)
# =============================================================================
def generate_produits():
    categories = {
        "Electronique": {
            "sous_categories": ["Smartphones", "Laptops", "Tablettes", "Accessoires", "Audio"],
            "marques": ["Apple", "Samsung", "Xiaomi", "Lenovo", "HP", "Sony", "JBL", "Huawei"],
            "fournisseurs": ["Apple MENA", "Samsung Maroc", "Xiaomi Distribution", "Tech Import SARL"],
            "prix_range": (299, 18999),
        },
        "Mode": {
            "sous_categories": ["Vêtements Homme", "Vêtements Femme", "Chaussures", "Accessoires Mode", "Montres"],
            "marques": ["Zara", "H&M", "Nike", "Adidas", "Lacoste", "Casio", "Swatch"],
            "fournisseurs": ["Fashion Import MA", "TextilePlus Tanger", "Mode Express"],
            "prix_range": (49, 2999),
        },
        "Alimentation": {
            "sous_categories": ["Épicerie", "Boissons", "Conserves", "Snacks", "Bio"],
            "marques": ["Dari", "Lesieur", "Centrale Danone", "Nestlé", "Knorr", "Al Badia"],
            "fournisseurs": ["Marjane Distribution", "Aswak Assalam", "BIM Maroc"],
            "prix_range": (5, 299),
        },
    }

    noms_produits = {
        "Electronique": {
            "Smartphones": ["iPhone 16 Pro 256Go", "Samsung Galaxy S24 Ultra", "Xiaomi 14 Pro", "iPhone 15 128Go", "Samsung Galaxy A55", "Xiaomi Redmi Note 13"],
            "Laptops": ["MacBook Air M3", "Lenovo ThinkPad X1", "HP Pavilion 15", "MacBook Pro 14 M3", "Lenovo IdeaPad 3"],
            "Tablettes": ["iPad Air M2", "Samsung Galaxy Tab S9", "Xiaomi Pad 6"],
            "Accessoires": ["AirPods Pro 2", "Chargeur USB-C 65W", "Coque iPhone 16", "Câble HDMI 2m", "Souris Logitech MX"],
            "Audio": ["JBL Flip 6", "Sony WH-1000XM5", "AirPods Max", "JBL Charge 5"],
        },
        "Mode": {
            "Vêtements Homme": ["Polo Lacoste Classic", "T-shirt Nike Dri-FIT", "Jean Slim Zara", "Veste Adidas Originals"],
            "Vêtements Femme": ["Robe H&M Summer", "Blazer Zara Femme", "Jupe Nike Sportswear", "Pull Lacoste V-neck"],
            "Chaussures": ["Nike Air Max 90", "Adidas Stan Smith", "Nike Air Force 1", "Adidas Ultraboost"],
            "Accessoires Mode": ["Ceinture Lacoste Cuir", "Sac Zara Bandoulière", "Écharpe H&M Laine"],
            "Montres": ["Casio G-Shock GA-2100", "Swatch Originals", "Casio Vintage A168"],
        },
        "Alimentation": {
            "Épicerie": ["Huile Lesieur 5L", "Sucre Enmer 2kg", "Farine Dari 10kg", "Riz Basmati 5kg"],
            "Boissons": ["Pack Eau Sidi Ali 6x1.5L", "Jus Valencia Orange 1L", "Café Dubois 250g"],
            "Conserves": ["Sardines Raïbi 10x125g", "Tomate Concentrée Aicha", "Olives Cartier 400g"],
            "Snacks": ["Biscuits Bimo Tagger", "Chips Lay's Nature 150g", "Chocolat Nestlé 100g"],
            "Bio": ["Miel Atlas Bio 500g", "Huile Argan Bio 250ml", "Thé Vert Bio Marrakech"],
        },
    }

    produits = []
    pid = 1
    casing_options = {
        "Electronique": ["Electronique", "electronique", "ELECTRONIQUE", "Électronique"],
        "Mode": ["Mode", "mode", "MODE", "mode "],
        "Alimentation": ["Alimentation", "alimentation", "ALIMENTATION", "Alimentation "],
    }

    for cat, info in categories.items():
        for sous_cat, noms in noms_produits[cat].items():
            for nom in noms:
                # Intentional: inconsistent category casing
                cat_display = random.choice(casing_options[cat])
                marque = random.choice(info["marques"])
                fournisseur = random.choice(info["fournisseurs"])
                prix = round(random.uniform(*info["prix_range"]), 2)

                # Intentional: some products have null prix_catalogue
                if random.random() < 0.05:
                    prix = None

                # Intentional: some products are inactive
                actif = True
                if random.random() < 0.08:
                    actif = False

                date_creation = f"20{random.randint(20,24)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"

                produits.append({
                    "id_produit": f"P{pid:03d}",
                    "nom": nom,
                    "categorie": cat_display,
                    "sous_categorie": sous_cat,
                    "marque": marque,
                    "fournisseur": fournisseur,
                    "prix_catalogue": prix,
                    "origine_pays": random.choice(["Maroc", "USA", "Chine", "France", "Corée du Sud", "Japon"]),
                    "date_creation": date_creation,
                    "actif": actif,
                })
                pid += 1

    path = os.path.join(DATA_DIR, "produits_mexora.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"produits": produits}, f, ensure_ascii=False, indent=2)
    print(f"[OK] produits_mexora.json — {len(produits)} produits")
    return [p["id_produit"] for p in produits]

# =============================================================================
# 3. CLIENTS MEXORA (CSV — avec problèmes intentionnels)
# =============================================================================
def generate_clients():
    prenoms_h = ["Youssef","Mohammed","Ahmed","Amine","Omar","Hamza","Karim","Rachid","Mehdi","Samir",
                 "Hassan","Khalid","Abdel","Brahim","Nabil","Reda","Adil","Zakaria","Ilyas","Soufiane"]
    prenoms_f = ["Fatima","Aicha","Meryem","Salma","Nadia","Houda","Khadija","Sara","Imane","Loubna",
                 "Zineb","Ghita","Amina","Hajar","Sanaa","Wiam","Noura","Laila","Samira","Hanane"]
    noms = ["Bennani","Alaoui","Idrissi","El Amrani","Tazi","Berrada","Fassi","Chraibi","Lahlou","Squalli",
            "Bouzid","Hajji","Mansouri","Ziani","Moussaoui","Kettani","Naciri","Benkirane","Ouazzani","Filali",
            "Sabri","El Khoury","Rahmani","Chaoui","Guessous","Tahiri","Mernissi","Benslimane","Regragui","Hakimi"]
    canaux = ["Google Ads", "Facebook", "Instagram", "Bouche-à-oreille", "Email Marketing", "TikTok", "Référencement"]

    # City variants (intentional inconsistency)
    city_variants = {
        "Tanger": ["Tanger", "tanger", "TNG", "TANGER", "Tnja", "tange", "Tangier"],
        "Casablanca": ["Casablanca", "casablanca", "CASA", "Casa", "CAS", "Dar el Beida"],
        "Rabat": ["Rabat", "rabat", "RBT", "RABAT"],
        "Fès": ["Fès", "Fes", "fes", "FES", "Fez"],
        "Marrakech": ["Marrakech", "marrakech", "MRK", "MARRAKECH", "Marrakesh"],
        "Agadir": ["Agadir", "agadir", "AGD", "AGADIR"],
        "Oujda": ["Oujda", "oujda", "OUJ", "OUJDA"],
        "Meknès": ["Meknès", "Meknes", "meknes", "MEK"],
        "Tétouan": ["Tétouan", "Tetouan", "tetouan", "TET"],
        "Kénitra": ["Kénitra", "Kenitra", "kenitra", "KNT"],
        "Salé": ["Salé", "Sale", "sale", "SLA"],
        "Nador": ["Nador", "nador", "NAD"],
        "Mohammedia": ["Mohammedia", "mohammedia", "MOH"],
        "El Jadida": ["El Jadida", "el jadida", "ELJ"],
        "Béni Mellal": ["Béni Mellal", "Beni Mellal", "BNM"],
    }

    # Gender variants (intentional inconsistency)
    sexe_variants_m = ["m", "M", "1", "Homme", "homme", "male", "h", "H"]
    sexe_variants_f = ["f", "F", "0", "Femme", "femme", "female"]

    clients = []
    nb_clients = 5000
    emails_used = []

    for i in range(1, nb_clients + 1):
        is_male = random.random() < 0.5
        prenom = random.choice(prenoms_h if is_male else prenoms_f)
        nom = random.choice(noms)
        sexe = random.choice(sexe_variants_m if is_male else sexe_variants_f)

        city_key = random.choice(list(city_variants.keys()))
        ville = random.choice(city_variants[city_key])

        # Generate email
        email_base = f"{prenom.lower()}.{nom.lower().replace(' ', '')}".replace("é","e").replace("è","e").replace("ê","e").replace("â","a").replace("î","i")
        email = f"{email_base}{random.randint(1,999)}@{random.choice(['gmail.com','yahoo.fr','hotmail.com','outlook.com','email.ma'])}"

        # Intentional: some malformed emails
        if random.random() < 0.03:
            email = random.choice([
                f"{email_base}{random.randint(1,99)}gmail.com",  # missing @
                f"{email_base}{random.randint(1,99)}@",          # missing domain
                f"{email_base}{random.randint(1,99)}@com",       # invalid domain
                f"@gmail.com",                                    # missing local part
            ])

        # Birth date
        year = random.randint(1940, 2008)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        date_naissance = f"{year}-{month:02d}-{day:02d}"

        # Intentional: some impossible birth dates
        if random.random() < 0.02:
            date_naissance = random.choice([
                f"2015-{random.randint(1,12):02d}-{random.randint(1,28):02d}",  # too young
                f"1890-{random.randint(1,12):02d}-{random.randint(1,28):02d}",  # too old
                f"2030-01-15",  # future date
            ])

        date_inscription = f"20{random.randint(20,25)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        canal = random.choice(canaux)
        tel = f"06{random.randint(10000000, 99999999)}"

        clients.append([f"C{i:04d}", nom, prenom, email, date_naissance, sexe,
                        ville, tel, date_inscription, canal])
        emails_used.append(email)

    # Intentional: Add ~150 duplicate clients (same email, different id_client)
    for i in range(nb_clients + 1, nb_clients + 151):
        dup_idx = random.randint(0, nb_clients - 1)
        orig = clients[dup_idx]
        new_client = [f"C{i:04d}", orig[1], orig[2], orig[3], orig[4],
                      random.choice(sexe_variants_m + sexe_variants_f),
                      orig[6], orig[7],
                      f"20{random.randint(20,25)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                      orig[9]]
        clients.append(new_client)

    random.shuffle(clients)

    path = os.path.join(DATA_DIR, "clients_mexora.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id_client","nom","prenom","email","date_naissance","sexe",
                     "ville","telephone","date_inscription","canal_acquisition"])
        w.writerows(clients)
    print(f"[OK] clients_mexora.csv — {len(clients)} lignes (dont ~150 doublons email)")
    return [c[0] for c in clients]

# =============================================================================
# 4. COMMANDES MEXORA (CSV — 50 000 lignes avec problèmes intentionnels)
# =============================================================================
def generate_commandes(product_ids, client_ids):
    city_variants = {
        "Tanger": ["Tanger", "tanger", "TNG", "TANGER", "Tnja", "tange"],
        "Casablanca": ["Casablanca", "casablanca", "CASA", "Casa", "CAS"],
        "Rabat": ["Rabat", "rabat", "RBT", "RABAT"],
        "Fès": ["Fès", "Fes", "fes", "FES"],
        "Marrakech": ["Marrakech", "marrakech", "MRK", "MARRAKECH"],
        "Agadir": ["Agadir", "agadir", "AGD"],
        "Oujda": ["Oujda", "oujda", "OUJ"],
        "Meknès": ["Meknès", "Meknes", "meknes"],
        "Tétouan": ["Tétouan", "Tetouan", "tetouan"],
        "Kénitra": ["Kénitra", "Kenitra", "kenitra"],
        "Salé": ["Salé", "Sale", "sale"],
        "Nador": ["Nador", "nador"],
        "Mohammedia": ["Mohammedia", "mohammedia"],
        "El Jadida": ["El Jadida", "el jadida"],
    }
    all_city_variants = []
    for variants in city_variants.values():
        all_city_variants.extend(variants)

    statuts = ["livré", "livré", "livré", "livré", "livré",  # ~50% livré
               "en_cours", "en_cours",
               "annulé",
               "retourné",
               "OK", "KO", "DONE", "livre", "LIVRE", "annule", "retourne"]

    modes_paiement = ["Carte bancaire", "Virement", "Cash à la livraison", "PayPal", "Apple Pay"]

    livreur_ids = [f"L{i:03d}" for i in range(1, 51)]  # 50 livreurs

    nb_commandes = 48500  # Base, then add duplicates to reach ~50000
    commandes = []

    start_date = datetime(2022, 1, 1)
    end_date = datetime(2025, 6, 30)
    date_range_days = (end_date - start_date).days

    for i in range(1, nb_commandes + 1):
        id_cmd = f"CMD{i:06d}"
        id_client = random.choice(client_ids)
        id_produit = random.choice(product_ids)

        # Random date
        cmd_date = start_date + timedelta(days=random.randint(0, date_range_days))

        # Intentional: mixed date formats
        fmt_choice = random.random()
        if fmt_choice < 0.4:
            date_str = cmd_date.strftime("%Y-%m-%d")       # 2024-11-15
        elif fmt_choice < 0.7:
            date_str = cmd_date.strftime("%d/%m/%Y")        # 15/11/2024
        elif fmt_choice < 0.9:
            date_str = cmd_date.strftime("%b %d %Y")        # Nov 15 2024
        else:
            date_str = cmd_date.strftime("%d-%m-%Y")        # 15-11-2024

        # Quantity
        quantite = random.randint(1, 10)
        # Intentional: some negative quantities
        if random.random() < 0.01:
            quantite = -random.randint(1, 5)

        # Price
        prix = round(random.uniform(10, 15000), 2)
        # Intentional: some zero prices (test orders)
        if random.random() < 0.015:
            prix = 0.0

        statut = random.choice(statuts)
        ville = random.choice(all_city_variants)
        mode = random.choice(modes_paiement)

        # Livreur — intentional: 7% missing
        if random.random() < 0.07:
            id_livreur = ""
        else:
            id_livreur = random.choice(livreur_ids)

        # Delivery date (2-7 days after order)
        livraison_date = cmd_date + timedelta(days=random.randint(1, 10))
        date_livraison = livraison_date.strftime("%Y-%m-%d")

        commandes.append([id_cmd, id_client, id_produit, date_str, quantite, prix,
                          statut, ville, mode, id_livreur, date_livraison])

    # Intentional: Add ~1500 duplicates (~3%)
    for _ in range(1500):
        dup = random.choice(commandes[:nb_commandes])
        commandes.append(list(dup))

    random.shuffle(commandes)

    path = os.path.join(DATA_DIR, "commandes_mexora.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id_commande","id_client","id_produit","date_commande","quantite",
                     "prix_unitaire","statut","ville_livraison","mode_paiement",
                     "id_livreur","date_livraison"])
        w.writerows(commandes)
    print(f"[OK] commandes_mexora.csv — {len(commandes)} lignes (dont ~1500 doublons)")

# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("GÉNÉRATION DES DONNÉES MEXORA")
    print("=" * 50)
    generate_regions()
    product_ids = generate_produits()
    client_ids = generate_clients()
    generate_commandes(product_ids, client_ids)
    print("=" * 50)
    print("TERMINÉ — Tous les fichiers sont dans data/")
