# Lyon Lawyers Public Data Project

## Introduction

Ce projet contient :

- Un script **python** permettant de scraper les données publiques du site du **Barrau de Lyon**
- Une application ElectronJS
- Afficher les données des avocats
- Ajouter de nouveaux avocats
- Modifier les informations existantes
- Supprimer des entrées

Le défi de ce projet consiste à utiliser MongoDB comme base de données. Pour l’application desktop cross-platform, la solution retenue est ElectronJS avec Vue.js intégré. L’utilisation de Claude.ai permet d’accélérer le développement de l’application.

## Installation et mise en place

### Import de la base de données

Le dossier ``lawyer_ddb`` contient la base de données à importer dans **MongoDB**.

Utiliser la commande suivante :
``mongostore <chemin-vers-le-dosser>``

### Installation de l'application

1. Ouvrez un terminal dans le dossier
``lawyer_app``
2. Installer les dépendances :
``npm install``
3. Lancez l'application en mode développement :
``npm run dev``

## Technologies utilisées

- **Python** - scraping des données
- **MongoDB** - stockage des données
- **ElectronJS** - interface desktop
- Node.js / npm - gestion des dépendances

## Description du traitement mis en oeuvre

Dans un premier temps, j’ai développé un script en Python afin de réaliser l’extraction automatisée des informations présentes sur le site du Barreau de Lyon.

Le script commence par ouvrir le navigateur et afficher la liste des avocats. Étant donné que la pagination limite l’affichage à douze avocats par page, le programme récupère l’attribut href du bouton « Suivant », qui permet de naviguer vers la page suivante. Cette valeur est ensuite stockée dans une variable nommée nextButton.

Ensuite, le script parcourt successivement chaque page de résultats afin de collecter les données présentes sur les fiches individuelles. Les informations extraites sont stockées dans une variable data.

A chaque répétition, une vérification est effectuée pour s’assurer que la variable nextButton contient bien un lien valide. Si ce lien est absent, la boucle de navigation s’interrompt automatiquement. Une fois l’ensemble des données collectées, le script génère un fichier de sortie dans lequel les informations contenues dans data sont enregistrées.

## Problème rencontés lors ud scraping et solutions apportées

### 1. Identification des coordonnées des avocats

#### Problèmes :

Les informations de contact (téléphone, email, fax, site web) n’étaient pas directement identifiables, car le site ne les distingue pas clairement dans la structure HTML.

#### Solution :

- Le téléphone et l’email sont repérables via la classe CSS de la div
correspondante.
- Le fax et l’URL du site web sont identifiés via les icônes Font Awesome : l’icône print correspond au fax et l’icône pin correspond à l’URL du site.

### 2. Gestion du changement de page (pagination)

#### Problème

Après avoir parcouru toutes les fiches d’avocats d’une page, le script devait passer à la page suivante. Le site maintient le bouton « suivant » visible même sur la dernière page, ce qui peut entraîner une boucle infinie.

#### Solution

- L’URL du bouton « suivant » est stockée dans une variable nextButton.
- Après avoir parcouru toutes les fiches de la page, le script vérifie si nextButton contient un lien valide.
- Si la variable est vide (None), la boucle s’arrête automatiquement. Sinon, le script passe à la page suivante : à jour nextButton avec le nouveau lien.

## Développement de l’application ElectronJS

Après avoir importé les données dans la collection lawyer_ddb de MongoDB, j’ai commencé le développement de l’application desktop cross-platform avec ElectronJS.

### Modules et outils utilisés :

- Vue Router : gestion de la navigation entre composants
- Mongoose : interaction avec MongoDB
- Valibot : ajout de validateurs pour les formulaires.

### Étapes de développement

#### 1. Création des handlers backend :

- Lister les avocats (10 par page)
- Supprimer un avocat
- Modifier un avocat
- Créer un nouvel avocat
- Récupérer un avocat par 

#### 2. Création du premier composant Vue :

- Interface pour afficher la liste des avocats
- Bloc de pagination
- Partie visuelle générée avec l’aide de Claude.ai
- Intégration dynamique des données issues de MongoDB

#### 3. Adaptation des fonctions générées par Claude.ai :

- Modification des fonctions de suppression et de modification pour correspondre à la structure et aux technologies du projet.

#### 4. Création d’un composant pour le détail de l’avocat :

- Affichage complet des informations d’un avocat.
- Boutons de modification et de suppression inspirés du design de la liste des avocats
- Intégration dynamique avec la base de données

Cette approche a permis de séparer clairement le backend et l’interface, tout
en garantissant une interaction fluide et dynamique avec la base de données
MongoDB.

### Difficultés rencontrées et solutions

#### 1. Désynchronisation des champs après suppression d’un avocat

- Problème : Après la suppression d’un avocat, les champs des formulaires de création et de modification ainsi que la barre de recherche ne prenaient plus en compte les saisies de l’utilisateur. Le problème disparaissait uniquement après ouverture de DevTools ou changement de taille de la fenêtre.
- Analyse : Le problème survient uniquement après utilisation de la fonction confirm() de Windows.
Solution : Remplacement de confirm() par une modale interne intégrée à l’application, ce qui rétablit la synchronisation des champs.

#### 2. Erreur lors de la modification d’un avocat

- Problème : lors de l’appel au handler updateLawyer(id, data) une erreur indiquait qu’un objet ne pouvait pas être cloné.
- Analyse : ElectronJS nécessite des objets simples, tandis que les objets reactive() de Vue.js contiennent des structures complexes.
- Solution : conversion de l’objet en string puis reconversion en objet simple avant l’envoi au handler.

#### 3. Mise en place de la pagination

- Problème : difficulté à trouver une solution de pagination dans Mongoose
- Analyse :initialement conseillé par Claude.ai d’utiliser le plugin mongoose-paginate-v2. Après vérification, il existe une méthode native de pagination Mongoose.
- Solution : après comparaison, décision d’utiliser la pagination native pour plus de simplicité et d’efficacité, bien que le plugin ait été testé.

### Bilan et enseignements du projet

Ce projet m’a permis de découvrir et de mettre en pratique plusieurs
compétences techniques et méthodologiques :

- Développement d’applications desktop cross-platform avec ElectronJS
- Utilisation d’une base de données NoSQL (MongoDB)
- Interaction avec la base de données via Mongoose
- Développement backend avec NodeJS
- Utilisation de Claude.ai pour accélérer le développement, notamment pour la partie visuelle et pour résoudre certaines difficultés techniques.

## Perspectives d’améliorations :

- Séparation complète de l’application ElectronJS et du backend via Spring REST
- Ajout de cases à cocher pour permettre la suppression multiple d’avocats
- Mise en place de filtres avancés, au-delà d’une simple barre de recherche (par exemple : tri par date, filtrage des avocats par rapport à leurs coordonnées)
