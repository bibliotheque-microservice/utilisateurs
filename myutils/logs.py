import logging

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Fonction pour gérer les erreurs
def fail_on_error(err, msg):
    if err:
        logging.error(f"{msg}: {err}")
        raise Exception(f"{msg}: {err}")

# Exemple de fonction qui pourrait générer une erreur
def create_utilisateur(nom, email):
    try:
        # Imaginons que le code pour créer un utilisateur échoue
        raise ValueError("Impossible de se connecter à la base de données")
    except Exception as err:
        fail_on_error(err, "Erreur lors de la création de l'utilisateur")

# Appel à la fonction
create_utilisateur("John Doe", "john.doe@example.com")
