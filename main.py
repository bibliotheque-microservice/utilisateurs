import json
import threading
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from rabbitMQ.rabbitmq import init_rabbitmq
import os
import re

# Initialisation de l'application Flask
app = Flask(__name__)

# Chargement des variables d'environnement depuis .env
required_env_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")

app.config.from_mapping(
    SQLALCHEMY_DATABASE_URI=f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

# Initialisation de SQLAlchemy
db = SQLAlchemy(app)

# Modèles
class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    date_creation = db.Column(db.Date, default=db.func.current_date())
    emprunts = db.relationship('Emprunt', backref='utilisateur', lazy=True)

class Penalite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255))
    date_penalite = db.Column(db.Date, default=db.func.current_date())

# Initialisation de la base de données
@app.before_first_request
def init_db():
    try:
        with app.app_context():
            db.create_all()  # Créer les tables si elles n'existent pas
    except Exception as e:
        app.logger.error(f"Database initialization failed: {e}")
        raise e

# Routes API
@app.route('/utilisateurs', methods=['POST'])
def ajouter_utilisateur():
    data = request.json
    if not data.get('nom') or not data.get('prenom') or not data.get('email'):
        return jsonify({"message": "Nom, prénom et email sont requis."}), 400
    
    if not validate_email(data['email']):
        return jsonify({"message": "Email invalide."}), 400

    nouvel_utilisateur = Utilisateur(
        nom=data['nom'], 
        prenom=data['prenom'], 
        email=data['email']
    )
    db.session.add(nouvel_utilisateur)
    db.session.commit()
    return jsonify({"message": "Utilisateur ajouté avec succès."})

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

@app.route('/utilisateurs/<int:id>', methods=['GET'])
def get_utilisateur(id):
    utilisateur = Utilisateur.query.get_or_404(id)
    return jsonify({
        "id": utilisateur.id,
        "nom": utilisateur.nom,
        "prenom": utilisateur.prenom,
        "email": utilisateur.email,
        "date_creation": utilisateur.date_creation
    })

@app.route('/penalites', methods=['POST'])
def ajouter_penalite():
    data = request.json
    nouvelle_penalite = Penalite(
        utilisateur_id=data['utilisateur_id'], 
        montant=data['montant'], 
        description=data['description']
    )
    db.session.add(nouvelle_penalite)
    db.session.commit()
    return jsonify({"message": "Pénalité ajoutée avec succès."})

# Lancer l'application Flask et RabbitMQ
if __name__ == '__main__':
    threading.Thread(target=init_rabbitmq, daemon=True).start()  # Lancer RabbitMQ dans un thread
    app.run(debug=True)
