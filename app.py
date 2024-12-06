from dotenv import load_dotenv
load_dotenv()  # Charger les variables d'environnement depuis le fichier .env
import os
from flask import Flask, request, jsonify
import psycopg2
import pika
import json

app = Flask(__name__)

# Récupérer les variables d'environnement
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
PORT = os.getenv('PORT')
DB_PORT = os.getenv('DB_PORT')

# Route pour payer une pénalité
@app.route('/penalite/pay', methods=['POST'])
def pay_penalite():
    print("Requête reçue : ", request.data)  # Log le corps brut reçu
    try:
        data = request.json  # Tente de parser le JSON
        print("Données parsées : ", data)  # Log les données parsées
        penalite_id = data.get('id_penalite')  # Extraire le penalite_id du corps de la requête
    except Exception as e:
        print("Erreur de parsing JSON : ", str(e))
        return jsonify({"error": "Données JSON invalides"}), 400
    if not penalite_id:
        return jsonify({"error": "id_penalite manquant dans la requête"}), 400

    # Vérifier si la pénalité existe
    conn = psycopg2.connect(
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASSWORD, 
        host=DB_HOST, 
        port=DB_PORT
    )
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM penalites WHERE id_penalite = %s', (penalite_id,))
        penalite = cursor.fetchone()

        if not penalite:
            return jsonify({"error": "Pénalité non trouvée"}), 404

        # Mettre à jour la pénalité comme payée
        cursor.execute(''' 
            UPDATE penalites
            SET paye = TRUE, date_paiement = NOW()
            WHERE id_penalite = %s;
        ''', (penalite_id,))
        conn.commit()
    finally:
        conn.close()

    # Envoyer un message RabbitMQ
    send_payment_notification(penalite_id)

    return jsonify({"message": "Pénalité payée avec succès et notification envoyée"}), 200

# Fonction pour envoyer un message RabbitMQ après paiement
def send_payment_notification(penalite_id):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='paiements_queue')

        message = {"id_penalite": penalite_id}
        channel.basic_publish(exchange='', routing_key='paiements_queue', body=json.dumps(message))
        print(f"Message envoyé: {message}")
    finally:
        connection.close()

if __name__ == "__main__":
    app.run(debug=True)
