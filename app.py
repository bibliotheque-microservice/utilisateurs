import json
import threading
import logging
import os
import pika
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import pika
from dotenv import load_dotenv
import logging



# Charger les variables d'environnement
load_dotenv()

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# Récupérer les variables d'environnement
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq-users')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'admin')


# Vérification des variables d'environnement
missing_env_vars = [
    var for var in [DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT, RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD]
    if not var
]
if missing_env_vars:
    raise ValueError(f"Les variables d'environnement suivantes sont manquantes : {missing_env_vars}")

# Modèles SQLAlchemy
class Utilisateur(db.Model):
    __tablename__ = 'utilisateurs'  # Spécifier le nom de la table
    id_utilisateur = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    statut = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.Date, default=db.func.current_date())
    emprunts = db.relationship('Emprunt', backref='utilisateur', lazy=True)

class Penalite(db.Model):
    __tablename__ = 'penalites'  # Spécifier le nom de la table
    id_penalite = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_utilisateur'), nullable=False)  # Correction de la référence à la table 'utilisateurs'
    montant = db.Column(db.Numeric(10, 2), nullable=False)

class Emprunt(db.Model):
    __tablename__ = 'emprunts'  # Spécifier le nom de la table
    id_emprunt = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_utilisateur'), nullable=False)  # Correction de la référence à la table 'utilisateurs'
    livre_id = db.Column(db.Integer, nullable=False)
    date_emprunt = db.Column(db.DateTime, default=datetime.utcnow)
    date_retour_prevu = db.Column(db.DateTime, nullable=False)
    date_retour_effectif = db.Column(db.DateTime, nullable=True)


# Initialisation de la base de données
with app.app_context():
    db.create_all()

connection = None
channel = None

# Fonction pour initialiser RabbitMQ
def init_rabbitmq():
    global connection, channel
    try:
        app.logger.info("Initialisation de RabbitMQ...")
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD),
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='paiements_queue', durable=True)
        app.logger.info("RabbitMQ initialisé avec succès.")
    except Exception as e:
        app.logger.error(f"Erreur lors de l'initialisation de RabbitMQ : {str(e)}")
        connection, channel = None, None

# Callback pour RabbitMQ
def rabbitmq_callback(ch, method, properties, body):
    app.logger.info(f"Message reçu : {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Consommation des messages RabbitMQ
def start_rabbitmq_consumer():
    global channel
    try:
        if channel is None or channel.is_closed:
            app.logger.warning("Le canal RabbitMQ n'est pas prêt. Réinitialisation...")
            init_rabbitmq()
        channel.basic_consume(queue='paiements_queue', on_message_callback=rabbitmq_callback)
        app.logger.info("Démarrage de la consommation RabbitMQ...")
        channel.start_consuming()
    except Exception as e:
        app.logger.error(f"Erreur lors de la consommation des messages : {str(e)}")


# Route pour la page d'accueil
@app.route('/')
def home():
    return "Bienvenue sur l'application de gestion des utilisateurs"

# Route pour ajouter un utilisateur
@app.route('/utilisateurs', methods=['POST'])
def ajouter_utilisateur():
    data = request.get_json()
    nouvel_utilisateur = Utilisateur(
        nom=data['nom'], 
        prenom=data['prenom'], 
        email=data['email']
    )
    db.session.add(nouvel_utilisateur)
    db.session.commit()
    return jsonify({"message": "Utilisateur ajouté avec succès."})

# Route pour récupérer un utilisateur par ID
@app.route('/utilisateurs/<int:id>', methods=['GET'])
def get_utilisateur(id):
    utilisateur = Utilisateur.query.get_or_404(id)
    return jsonify({
        "id": utilisateur.id_utilisateur,
        "nom": utilisateur.nom,
        "prenom": utilisateur.prenom,
        "email": utilisateur.email,
        "created_at": utilisateur.created_at
    })

# Route pour ajouter une pénalité
@app.route('/penalites', methods=['POST'])
def ajouter_penalite():
    data = request.json
    nouvelle_penalite = Penalite(
        utilisateur_id=data['utilisateur_id'], 
        montant=data['montant'], 
    )
    db.session.add(nouvelle_penalite)
    db.session.commit()
    return jsonify({"message": "Pénalité ajoutée avec succès."})

# Route pour vérifier les emprunts en retard
@app.route('/verifier_retards', methods=['GET'])
def verifier_retards():
    today = datetime.today().date()
    emprunts_en_retard = Emprunt.query.filter(Emprunt.date_retour_effectif < today).all()

    for emprunt in emprunts_en_retard:
        emprunt.est_retard = True
        db.session.commit()

        penalite_existante = Penalite.query.filter_by(utilisateur_id=emprunt.utilisateur_id).first()
        
        if penalite_existante:
                nouvelle_penalite = Penalite(
                    utilisateur_id=emprunt.utilisateur_id,
                    montant=5.00,
                )
                db.session.add(nouvelle_penalite)
                db.session.commit()
        else:
            nouvelle_penalite = Penalite(
                utilisateur_id=emprunt.utilisateur_id,
                montant=5.00,
            )
            db.session.add(nouvelle_penalite)
            db.session.commit()

    return jsonify({"message": "Retards vérifiés et pénalités créées."})

# Route pour payer une pénalité
@app.route('/penalite/pay', methods=['POST'])
def pay_penalite():
    app.logger.info("Requête reçue pour /penalite/pay")
    if not request.is_json:
        app.logger.error("Requête non JSON reçue")
        return jsonify({"error": "Données JSON invalides"}), 400

    data = request.get_json()
    penalite_id = data.get('id_penalite')

    if not penalite_id:
        app.logger.error("Champ id_penalite manquant dans la requête")
        return jsonify({"error": "id_penalite manquant dans la requête"}), 400

    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # Vérifie si la pénalité existe
        cursor.execute('SELECT * FROM penalites WHERE id_penalite = %s AND paye = FALSE', (penalite_id,))
        penalite = cursor.fetchone()

        if not penalite:
            app.logger.warning(f"Pénalité avec id {penalite_id} non trouvée")
            return jsonify({"error": "Pénalité non trouvée"}), 404

        # Met à jour la pénalité comme payée
        cursor.execute('''
            UPDATE penalites
            SET paye = TRUE, date_paiement = NOW()
            WHERE id_penalite = %s;
        ''', (penalite_id,))
        conn.commit()
        app.logger.info(f"Pénalité {penalite_id} marquée comme payée")
    except psycopg2.DatabaseError as e:
        app.logger.error(f"Erreur de base de données : {str(e)}")
        return jsonify({"error": f"Erreur de base de données: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

    # Envoie un message RabbitMQ
    send_payment_notification(penalite_id)

    return jsonify({"message": "Pénalité payée avec succès et notification envoyée"}), 200

# Fonction pour envoyer un message RabbitMQ
def send_payment_notification(penalite_id):
    app.logger.info(f"Envoi de notification RabbitMQ pour pénalité {penalite_id}")
    try:
        
        if channel is None or not channel.is_open:
            app.logger.error("Canal RabbitMQ fermé ou non initialisé. Tentative de reconnexion...")
            init_rabbitmq()
  
        message = {"id_penalite": penalite_id}
        channel.basic_publish(exchange='', routing_key='paiements_queue', body=json.dumps(message))
        app.logger.info(f"Message envoyé : {message}")
    except Exception as e:
        app.logger.error(f"Erreur lors de l'envoi du message RabbitMQ : {str(e)}")


@app.route('/valid-user/<int:id_utilisateur>', methods=['GET'])
def get_utilisateur_validity(id_utilisateur):
    utilisateur = Utilisateur.query.get(id_utilisateur)
    
    # Vérifier si l'utilisateur existe
    if not utilisateur:
        return jsonify({"message": "Utilisateur non trouvé"}), 404
    
    # Vérifier si l'utilisateur est actif
    if utilisateur.statut != 'actif':
        return jsonify({"message": "Utilisateur non actif"}), 400

    # Vérifier si les pénalités de l'utilisateur sont à moins de 30 euros
    penalites = Penalite.query.filter_by(utilisateur_id=id_utilisateur).all()
    total_penalites = sum(p.montant for p in penalites)

    if total_penalites >= 30:
        return jsonify({"valid" : False, "message": "Too much penalities"}), 200

    return jsonify({"valid" : True, "message": "Utilisateur valide"})



threading.Thread(target=start_rabbitmq_consumer, daemon=True).start()


# Lancer l'application Flask et RabbitMQ
if __name__ == '__main__':
    init_rabbitmq() 
    # Lancer RabbitMQ dans un thread séparé pour ne pas bloquer Flask
    app.run(debug=True, host='0.0.0.0', port=5000)

