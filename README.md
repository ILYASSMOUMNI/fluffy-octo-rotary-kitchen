# fluffy-octo-rotary-kitchen
hadi for google auth
pip install social-auth-app-django

READ THIS
zakaria was here
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
run this before starting the project
pip install django-widget-tweaks

note:
i removed all the files and added mine here
configure your mysql database here in fluffy-octo-rotary-kitchen\cooking_platform\settings.py
exactly here:
DATABASES = {
'default': {
'ENGINE': 'django.db.backends.mysql',
'NAME': 'cooking_db',
'USER': 'root',
'PASSWORD': 'root',
'HOST': 'localhost',
'PORT': '3306',
}
}
and create it in mysql and run the migration using :
python manage.py makemigrations
python manage.py migrate
ps:some functionality are still not working and still in developement espicially in the add recipe and edit also note the you have to chose a chef as a role to be able to see the full functionality's of the recipe "add,edit..."
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

some recipe data 3la wed test dyal suggestion

INSERT INTO recipes_ingredient (id, name, quantity) VALUES
-- Pancake ingredients
(1, 'All-purpose flour', '1 1/2 cups'),
(2, 'Baking powder', '3 1/2 tsp'),
(3, 'Salt', '1 tsp'),
(4, 'Sugar', '1 tbsp'),
(5, 'Milk', '1 1/4 cups'),
(6, 'Egg', '1 large'),
(7, 'Butter', '3 tbsp, melted'),

-- Carbonara ingredients
(8, 'Spaghetti', '400g'),
(9, 'Pancetta', '200g'),
(10, 'Eggs', '4 large'),
(11, 'Pecorino Romano', '50g'),
(12, 'Parmesan', '50g'),
(13, 'Black pepper', 'to taste'),
(14, 'Salt', 'to taste'),

-- Cookie ingredients
(15, 'All-purpose flour', '2 1/4 cups'),
(16, 'Baking soda', '1 tsp'),
(17, 'Salt', '1 tsp'),
(18, 'Butter', '1 cup, softened'),
(19, 'Granulated sugar', '3/4 cup'),
(20, 'Brown sugar', '3/4 cup'),
(21, 'Eggs', '2 large'),
(22, 'Vanilla extract', '2 tsp'),
(23, 'Chocolate chips', '2 cups');

-- Insert recipes
INSERT INTO recipes_recipe (id, title, description, servings, instructions, category_id, created_by_id) VALUES
(1, 'Classic Pancakes', 'Fluffy, golden pancakes perfect for a weekend breakfast', 4, 
'1. Sift together dry ingredients\n2. Make a well and add wet ingredients\n3. Mix until just combined\n4. Heat griddle to medium-high\n5. Pour 1/4 cup batter per pancake\n6. Flip when bubbles form on top\n7. Cook until golden brown', 
1, 1),

(2, 'Spaghetti Carbonara', 'Creamy Italian pasta dish with eggs, cheese, and pancetta', 2,
'1. Cook pasta in boiling salted water\n2. Fry pancetta until crispy\n3. Whisk eggs with grated cheeses\n4. Drain pasta, reserve some water\n5. Quickly mix hot pasta with egg mixture\n6. Add pancetta and pepper\n7. Adjust consistency with pasta water',
3, 1),

(3, 'Chocolate Chip Cookies', 'Classic chewy cookies with melty chocolate chips', 24,
'1. Preheat oven to 375°F (190°C)\n2. Combine flour, baking soda, and salt\n3. Cream butter and sugars until light\n4. Beat in eggs and vanilla\n5. Gradually add dry ingredients\n6. Stir in chocolate chips\n7. Drop by rounded tablespoon onto baking sheets\n8. Bake for 9-11 minutes',
4, 1);

-- Create many-to-many relationships between recipes and ingredients
INSERT INTO recipes_recipe_ingredients (id, recipe_id, ingredient_id) VALUES
-- Pancake ingredients
(1, 1, 1),
(2, 1, 2),
(3, 1, 3),
(4, 1, 4),
(5, 1, 5),
(6, 1, 6),
(7, 1, 7),

-- Carbonara ingredients
(8, 2, 8),
(9, 2, 9),
(10, 2, 10),
(11, 2, 11),
(12, 2, 12),
(13, 2, 13),
(14, 2, 14),

-- Cookie ingredients
(15, 3, 15),
(16, 3, 16),
(17, 3, 17),
(18, 3, 18),
(19, 3, 19),
(20, 3, 20),
(21, 3, 21),
(22, 3, 22),
(23, 3, 23);
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
