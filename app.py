from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3308/bibliotheque'
db = SQLAlchemy(app)

# Modèles
class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    date_creation = db.Column(db.Date, default=db.func.current_date())

class Penalite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255))
    date_penalite = db.Column(db.Date, default=db.func.current_date())

# Routes
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
    with app.app_context():  # Créer un contexte d'application pour exécuter db.create_all()
        db.create_all()
    app.run(debug=True)
