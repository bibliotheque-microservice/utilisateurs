FROM python:3.10-slim

# Installer les dépendances nécessaires pour exécuter Flask et le script
RUN apt-get update && \
    apt-get install -y netcat-openbsd bash && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copier et installer les dépendances Python
COPY requirements.txt ./ 
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copier tous les fichiers de l'application dans le conteneur
COPY . . 

COPY .env /usr/src/app/.env

# Assurer que le script wait-for-rabbitmq.sh a les bonnes permissions
COPY wait-for-rabbitmq.sh /usr/src/app/wait-for-rabbitmq.sh
RUN chmod 755 /usr/src/app/wait-for-rabbitmq.sh

# Vérifier si main.py est bien copié
RUN ls -l /usr/src/app/main.py

# Vérification de la structure et des permissions des fichiers
RUN ls -l /usr/src/app/models
RUN ls -l /usr/src/app/models/models.py

# Définir l'application Flask et exposer le port
ENV FLASK_APP=main
EXPOSE 5000

# Lancer Flask directement sans attendre RabbitMQ
CMD echo "RabbitMQ check skipped. Flask will start directly." && flask run --host=0.0.0.0 --port=5000
