Application de Gestion des Utilisateurs avec Flask et RabbitMQ

Description
Cette application permet de gérer les utilisateurs. Elle utilise Flask pour l'API REST, PostgreSQL pour la base de données, et RabbitMQ pour la gestion des messages.

Fonctionnalités principales

Gestion des utilisateurs :

Ajouter un utilisateur

Consulter les informations d'un utilisateur

Vérifier la validité d'un utilisateur



Utilisation

Endpoints

Utilisateurs

Ajouter un utilisateur :

POST /utilisateurs

Payload JSON :
{
  "nom": "Doe",
  "prenom": "John",
  "email": "john.doe@example.com"
}
Récupérer un utilisateur par ID :

GET /utilisateurs/<id>

Vérifier la validité d'un utilisateur :

GET /valid-user/<id_utilisateur>

Emprunts

Vérifier les retards :

GET /verifier_retards

Pénalités

Ajouter une pénalité :

POST /penalites

Payload JSON :
{
  "utilisateur_id": 1,
  "montant": 10.50
}
Payer une pénalité :

POST /penalite/pay

Payload JSON :
{
  "id_penalite": 1
}

Journalisation

Les journaux sont configurés pour enregistrer les événements importants de l'application et de RabbitMQ.

Niveau de log : DEBUG

Logs inclus :

Initialisation de RabbitMQ

Envoi et réception de messages

Erreurs de base de données


