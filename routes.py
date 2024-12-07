from flask import Blueprint, request, jsonify
from app import db
from app.models import Utilisateur, Penalite, Emprunt
from datetime import datetime

# Création du Blueprint pour les routes
routes = Blueprint('routes', __name__)

# Route pour ajouter un utilisateur
@routes.route('/utilisateurs', methods=['POST'])
def ajouter_utilisateur():
    data = request.json
    try:
        nouvel_utilisateur = Utilisateur(
            nom=data['nom'], 
            prenom=data['prenom'], 
            email=data['email']
        )
        db.session.add(nouvel_utilisateur)
        db.session.commit()
        return jsonify({"message": "Utilisateur ajouté avec succès."}), 201
    except Exception as e:
        return jsonify({"message": f"Erreur : {str(e)}"}), 400

# Route pour récupérer un utilisateur par ID
@routes.route('/utilisateurs/<int:id>', methods=['GET'])
def get_utilisateur(id):
    utilisateur = Utilisateur.query.get_or_404(id)
    return jsonify({
        "id": utilisateur.id,
        "nom": utilisateur.nom,
        "prenom": utilisateur.prenom,
        "email": utilisateur.email,
        "date_creation": utilisateur.date_creation
    })

# Route pour ajouter une pénalité
@routes.route('/penalites', methods=['POST'])
def ajouter_penalite():
    data = request.json
    try:
        nouvelle_penalite = Penalite(
            utilisateur_id=data['utilisateur_id'], 
            montant=data['montant'], 
            description=data['description']
        )
        db.session.add(nouvelle_penalite)
        db.session.commit()
        return jsonify({"message": "Pénalité ajoutée avec succès."}), 201
    except Exception as e:
        return jsonify({"message": f"Erreur : {str(e)}"}), 400

# Route pour vérifier les emprunts en retard
@routes.route('/verifier_retards', methods=['GET'])
def verifier_retards():
    today = datetime.today().date()
    emprunts_en_retard = Emprunt.query.filter(Emprunt.est_retard == False, Emprunt.date_retour < today).all()

    for emprunt in emprunts_en_retard:
        emprunt.est_retard = True
        db.session.commit()

        penalite_existante = Penalite.query.filter_by(utilisateur_id=emprunt.utilisateur_id).order_by(Penalite.date_penalite.desc()).first()
        
        if penalite_existante:
            if penalite_existante.date_penalite < today:
                nouvelle_penalite = Penalite(
                    utilisateur_id=emprunt.utilisateur_id,
                    montant=5.00,  # Exemple de montant pour la pénalité
                    description=f"Retard pour l'emprunt du livre {emprunt.livre_id}.",
                    date_penalite=today
                )
                db.session.add(nouvelle_penalite)
                db.session.commit()
        else:
            nouvelle_penalite = Penalite(
                utilisateur_id=emprunt.utilisateur_id,
                montant=5.00,
                description=f"Retard pour l'emprunt du livre {emprunt.livre_id}.",
                date_penalite=today
            )
            db.session.add(nouvelle_penalite)
            db.session.commit()

    return jsonify({"message": "Retards vérifiés et pénalités créées."}), 200

# **Nouvelle route** pour vérifier si un utilisateur est bloqué
@routes.route('/check_blocked/<int:user_id>', methods=['GET'])
def check_blocked(user_id):
    penalty_count = Penalite.query.filter_by(utilisateur_id=user_id, status='unpaid').count()

    if penalty_count > 10:  # Remplace 10 par la limite choisie
        return jsonify({"blocked": True, "message": "User is blocked due to too many penalties"}), 200
    return jsonify({"blocked": False, "message": "User is not blocked"}), 200
