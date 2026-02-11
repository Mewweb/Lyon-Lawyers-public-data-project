# Lyon Lawyers Public Data Project
## Introduction
Ce projet contient : 
- Un script **python** permettant de scraper les données publiques du site du **Barrau de Lyon**
- Une application ElectronJS
    - Afficher les données des avocats
    - Ajouter de nouveaux avocats
    - Modifier les informations existantes
    - Supprimer des entrées

L'objectifs du projet est de collecter, stocker et manipuler facilement ces données via une interface graphique

## Installation et mise en place
### Import de la base de données
Le dossier ``lawyer_ddb`` contient la base de données à importer dans **MongoDB**.

Utiliser la commande suivante :
``mongostore <chemin-vers-le-dosser>``
### Installation de l'application
1. Ouvrez un terminal dans le dossier ``lawyer_app``
2. Installer les dépendances : 
``npm install``
3. Lancez l'application en mode développement :
``npm run dev``

## Technologies utilisées
- **Python** - scraping des données
- **MongoDB** - stockage des données
- **ElectronJS** - interface desktop
- Node.js / npm - gestion des dépendances