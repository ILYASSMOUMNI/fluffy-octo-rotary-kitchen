# fluffy-octo-rotary-kitchen
Par Ismail Khdem
just a test by zakaria

## Fonctionnalités Principales

### 1. Gestion des utilisateurs
- Inscription et gestion des profils (chefs, amateurs, blogueurs)
- Création et modification de profils
- Authentification sécurisée avec rôles et permissions

### 2. Gestion des recettes
- Ajout, modification et suppression des recettes
- Organisation des recettes par catégories (plats, desserts, etc.)
- Gestion des ingrédients et portions

### 3. Recherche et filtrage
- Recherche de recettes par nom, ingrédients, catégorie, temps de préparation
- Filtres avancés pour les préférences alimentaires (végétarien, sans gluten...)
- Accès aux recettes favorites et populaires

### 4. Partage et interaction
- Système de commentaires et notes sur les recettes
- Partage de recettes sur les réseaux sociaux
- Export des recettes en PDF ou Excel

### 5. Module IA (Facultatif)
- Suggestions de recettes basées sur les ingrédients disponibles
- Analyse des préférences culinaires et recommandations personnalisées
- Reconnaissance d'images pour identifier les ingrédients d'une photo
- Chatbot interactif pour proposer des recettes selon les envies du moment

## Spécifications des fonctionnalités

Chaque fonctionnalité comprend :
- Création, modification et suppression des profils
- Informations personnelles :
  - Nom, prénom
  - Date de naissance
  - Adresse
  - Contact
- Détails professionnels :
  - Poste
  - Date d'embauche
  - Numéro de contrat
  - Service
- Historique professionnel :
  - Promotions
  - Formations
- Gestion des accès :
  - Différents niveaux (administrateur, technicien, clients)
  - Traçabilité des actions utilisateurs
- Rapports personnalisés sur les réparations





// pour la base de données 
CREATE TABLE utilisateurs (
    id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    date_naissance DATE,
    adresse VARCHAR(255),
    contact VARCHAR(100),
    poste VARCHAR(50),
    date_embauche DATE,
    numero_contrat VARCHAR(50),
    service VARCHAR(50),
    niveau_acces ENUM('administrateur', 'technicien', 'client') NOT NULL,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE historique_professionnel (
    id_historique INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT,
    type_evenement ENUM('promotion', 'formation') NOT NULL,
    description TEXT,
    date_evenement DATE,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(id_utilisateur) ON DELETE CASCADE
);


CREATE TABLE recettes (
    id_recette INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT,
    titre VARCHAR(100) NOT NULL,
    description TEXT,
    categorie ENUM('entrée', 'plat', 'dessert', 'boisson', 'autre') NOT NULL,
    temps_preparation INT COMMENT 'Durée en minutes',
    portions INT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(id_utilisateur) ON DELETE SET NULL
);

CREATE TABLE ingredients (
    id_ingredient INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE
);
CREATE TABLE recette_ingredients (
    id_recette_ingredient INT AUTO_INCREMENT PRIMARY KEY,
    id_recette INT,
    id_ingredient INT,
    quantite VARCHAR(50),
    FOREIGN KEY (id_recette) REFERENCES recettes(id_recette) ON DELETE CASCADE,
    FOREIGN KEY (id_ingredient) REFERENCES ingredients(id_ingredient) ON DELETE CASCADE
);
CREATE TABLE commentaires (
    id_commentaire INT AUTO_INCREMENT PRIMARY KEY,
    id_recette INT,
    id_utilisateur INT,
    note TINYINT CHECK (note BETWEEN 1 AND 5),
    commentaire TEXT,
    date_commentaire TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_recette) REFERENCES recettes(id_recette) ON DELETE CASCADE,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(id_utilisateur) ON DELETE SET NULL
);
CREATE TABLE favoris (
    id_favori INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT,
    id_recette INT,
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(id_utilisateur) ON DELETE CASCADE,
    FOREIGN KEY (id_recette) REFERENCES recettes(id_recette) ON DELETE CASCADE
);
CREATE TABLE partages (
    id_partage INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT,
    id_recette INT,
    plateforme VARCHAR(50),
    date_partage TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(id_utilisateur) ON DELETE SET NULL,
    FOREIGN KEY (id_recette) REFERENCES recettes(id_recette) ON DELETE CASCADE
);
CREATE TABLE tracabilite_actions (
    id_action INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT,
    action VARCHAR(255) NOT NULL,
    date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(id_utilisateur) ON DELETE SET NULL
);

CREATE TABLE rapports_personnalises (
    id_rapport INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT,
    titre VARCHAR(100) NOT NULL,
    contenu TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(id_utilisateur) ON DELETE SET NULL
);

