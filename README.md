task : notifications d'admin  

session , !!!


sudo apt update
sudo apt install python3-pip python3-dev libpq-dev postgresql-client

pip3 install -r requirements.txt

important changes :

- added pending recipes page
- added recipe status page for amateur users
- check profile nav bar
- fixed some redirection in dahsboard page
- chef can approve or reject a recipe added by other users
- chef can delete or edit any recipes
- chef's recipes are auto approved
- 

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
