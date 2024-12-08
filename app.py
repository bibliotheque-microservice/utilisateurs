from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
import psycopg2
import pika
import json

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Récupérer les variables d'environnement
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')  # Default 'rabbitmq' if not specified
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'admin')

# Vérification des variables d'environnement
missing_env_vars = [
    var for var in [DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT, RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD]
    if not var
]
if missing_env_vars:
    raise ValueError(f"Les variables d'environnement suivantes sont manquantes : {missing_env_vars}")

# Route pour la page d'accueil
@app.route('/')
def home():
    return "Bienvenue sur l'application de gestion des utilisateurs"

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
        cursor.execute('SELECT * FROM penalites WHERE id_penalite = %s', (penalite_id,))
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
    connection = None
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()

        channel.queue_declare(queue='paiements_queue')

        message = {"id_penalite": penalite_id}
        channel.basic_publish(exchange='', routing_key='paiements_queue', body=json.dumps(message))
        app.logger.info(f"Message envoyé : {message}")
    except Exception as e:
        app.logger.error(f"Erreur lors de l'envoi du message RabbitMQ : {str(e)}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
