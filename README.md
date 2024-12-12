#Service_des_utilisateurs
Application de Gestion des Utilisateurs avec Flask et RabbitMQ


## Fonctionnalités principales

### Ajouter un utilisateur :

### POST /utilisateurs

```http
POST /utilisateurs
```
```json
{
  "nom": "Doe",
  "prenom": "John",
  "email": "john.doe@example.com"
}
```


#### Récupérer un utilisateur par ID :

```http
GET /utilisateurs/<id>
```

####Vérifier la validité d'un utilisateur :

```http
GET /valid-user/<id_utilisateur>
```

##Emprunts

####Vérifier les retards :

```http
GET /verifier_retards
```

###Pénalités

####Ajouter une pénalité :

```http
POST /penalites
```

```json
{
  "utilisateur_id": 1,
  "montant": 10.50
}
```

###Payer une pénalité :

```http
POST /penalite/pay
```

```json
{
  "id_penalite": 1
}
```


