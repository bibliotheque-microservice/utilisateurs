from app import db
from app.models import Utilisateur
import logging

def handle_create_user(message):
    """Handler pour créer un nouvel utilisateur."""
    try:
        # Assurez-vous que le message contient les bonnes informations
        utilisateur = Utilisateur(
            nom=message['nom'],
            prenom=message['prenom'],
            email=message['email']
        )
        db.session.add(utilisateur)
        db.session.commit()
        logging.info(f"Utilisateur créé : {message['nom']} {message['prenom']}")
    except Exception as e:
        logging.error(f"Erreur lors de la création de l'utilisateur : {e}")

def handle_update_user(message):
    """Handler pour mettre à jour un utilisateur existant."""
    try:
        utilisateur = Utilisateur.query.get(message['id'])
        if utilisateur:
            utilisateur.nom = message.get('nom', utilisateur.nom)
            utilisateur.prenom = message.get('prenom', utilisateur.prenom)
            utilisateur.email = message.get('email', utilisateur.email)
            db.session.commit()
            logging.info(f"Utilisateur mis à jour : {utilisateur.id}")
        else:
            logging.warning(f"Utilisateur {message['id']} non trouvé.")
    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour de l'utilisateur : {e}")

def handle_delete_user(message):
    """Handler pour supprimer un utilisateur."""
    try:
        utilisateur = Utilisateur.query.get(message['id'])
        if utilisateur:
            db.session.delete(utilisateur)
            db.session.commit()
            logging.info(f"Utilisateur supprimé : {utilisateur.id}")
        else:
            logging.warning(f"Utilisateur {message['id']} non trouvé.")
    except Exception as e:
        logging.error(f"Erreur lors de la suppression de l'utilisateur : {e}")
