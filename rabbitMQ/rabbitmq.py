import pika
import json
import logging

# Configurer le logging
logging.basicConfig(level=logging.INFO)

def init_rabbitmq():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        # Déclaration des exchanges
        channel.exchange_declare(exchange='emprunts_exchange', exchange_type='direct', durable=True)
        channel.exchange_declare(exchange='penality_exchange', exchange_type='direct', durable=True)

        # Déclaration des queues
        channel.queue_declare(queue='emprunts_created_queue', durable=True)
        channel.queue_declare(queue='emprunts_finished_queue', durable=True)
        channel.queue_declare(queue='user_penalties_queue', durable=True)

        # Lier les queues aux exchanges avec les routing keys appropriées
        channel.queue_bind(exchange='emprunts_exchange', queue='emprunts_created_queue', routing_key='emprunts.v1.created')
        channel.queue_bind(exchange='emprunts_exchange', queue='emprunts_finished_queue', routing_key='emprunts.v1.finished')
        channel.queue_bind(exchange='penality_exchange', queue='user_penalties_queue', routing_key='user.v1.penalities.new')
        channel.queue_bind(exchange='penality_exchange', queue='user_penalties_queue', routing_key='user.v1.penalities.paid')

        logging.info("Exchange et queues déclarés et liés avec succès.")

        return channel, connection
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation de RabbitMQ : {e}")
        raise

def publish_message(channel, exchange_name, routing_key, message):
    try:
        message_json = json.dumps(message)
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=message_json,
            properties=pika.BasicProperties(
                delivery_mode=2,  # message persistant
            )
        )
        logging.info(f"Message envoyé à {exchange_name} avec routing key {routing_key}: {message}")
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi du message : {e}")

def callback_penalties(ch, method, properties, body):
    try:
        message = json.loads(body)
        if method.routing_key == 'user.v1.penalities.new':
            logging.info(f"Message reçu sur 'user.v1.penalities.new' : {message}")
            # Traitement de la pénalité
            # Ajouter la pénalité à la base de données (exemple)
            # db.session.add(penalite)
            # db.session.commit()
        elif method.routing_key == 'user.v1.penalities.paid':
            logging.info(f"Message reçu sur 'user.v1.penalities.paid' : {message}")
        else:
            logging.warning(f"Message non géré avec Routing Key {method.routing_key}")
    except Exception as e:
        logging.error(f"Erreur lors du traitement du message de pénalité : {e}")

def callback_emprunts(ch, method, properties, body):
    try:
        message = json.loads(body)
        if method.routing_key == 'emprunts.v1.finished':
            logging.info(f"Message reçu sur 'emprunts.v1.finished' : {message}")
            # Traitement de l'emprunt terminé
        else:
            logging.warning(f"Message non géré avec Routing Key {method.routing_key}")
    except Exception as e:
        logging.error(f"Erreur lors du traitement du message d'emprunt : {e}")

def start_consuming(channel):
    try:
        channel.basic_consume(queue='user_penalties_queue', on_message_callback=callback_penalties, auto_ack=True)
        channel.basic_consume(queue='emprunts_finished_queue', on_message_callback=callback_emprunts, auto_ack=True)
        logging.info("En attente de messages...")
        channel.start_consuming()
    except Exception as e:
        logging.error(f"Erreur lors de la consommation des messages : {e}")

# Exécution de l'initialisation et de la consommation des messages
channel, connection = init_rabbitmq()
start_consuming(channel)
