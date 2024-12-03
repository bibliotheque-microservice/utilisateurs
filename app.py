from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

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

# Cron job pour vérifier les emprunts en retard (exécuté quotidiennement)
@app.route('/verifier_retards', methods=['GET'])
def verifier_retards():
    today = datetime.today().date()
    emprunts_en_retard = Emprunt.query.filter(Emprunt.est_retard == False, Emprunt.date_retour < today).all()

    for emprunt in emprunts_en_retard:
        # Si l'emprunt est en retard, on marque comme "retard" et on ajoute une pénalité
        emprunt.est_retard = True
        db.session.commit()

        # Vérification de la pénalité existante ou création d'une nouvelle pénalité
        penalite_existante = Penalite.query.filter_by(utilisateur_id=emprunt.utilisateur_id).order_by(Penalite.date_penalite.desc()).first()
        
        if penalite_existante:
            # Ajout d'une nouvelle ligne de pénalité si le retard est plus d'un jour
            if penalite_existante.date_penalite < today:
                nouvelle_penalite = Penalite(
                    utilisateur_id=emprunt.utilisateur_id,
                    montant=5.00,  # Exemple de montant pour la pénalité, à adapter
                    description=f"Retard pour l'emprunt du livre {emprunt.livre_id}.",
                    date_penalite=today
                )
                db.session.add(nouvelle_penalite)
                db.session.commit()
        else:
            # Créer une pénalité si aucune n'existe encore
            nouvelle_penalite = Penalite(
                utilisateur_id=emprunt.utilisateur_id,
                montant=5.00,  # Exemple de montant pour la pénalité, à adapter
                description=f"Retard pour l'emprunt du livre {emprunt.livre_id}.",
                date_penalite=today
            )
            db.session.add(nouvelle_penalite)
            db.session.commit()

    return jsonify({"message": "Retards vérifiés et pénalités créées."})

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

if __name__ == '__main__':
    app.run(debug=True)
