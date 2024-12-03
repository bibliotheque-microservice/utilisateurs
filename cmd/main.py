import json
import threading
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from rabbitmq import init_rabbitmq  # Importer la logique RabbitMQ

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3308/bibliotheque'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
with app.app_context():
    db.create_all()

# Routes API
@app.route('/utilisateurs', methods=['POST'])
def ajouter_utilisateur():
    data = request.json
    nouvel_utilisateur = Utilisateur(
        nom=data['nom'], 
        prenom=data['prenom'], 
        email=data['email']
    )
    db.session.add(nouvel_utilisateur)
    db.session.commit()
    return jsonify({"message": "Utilisateur ajouté avec succès."})

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
