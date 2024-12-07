# Utilisation de l'image de base Python
FROM python:3.10-slim

# Installer les dépendances système nécessaires, y compris netcat-openbsd et d'autres utilitaires
RUN apt-get update && \
    apt-get install -y netcat-openbsd bash && \
    rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail dans le conteneur
WORKDIR /usr/src/app

# Copier le fichier des dépendances (ex: requirements.txt) et installer les dépendances
COPY requirements.txt ./ 
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copier le reste des fichiers de l'application dans le conteneur
COPY . .
COPY wait-for-rabbitmq.sh /usr/src/app/wait-for-rabbitmq.sh

# Vérification de la structure du répertoire et de la présence du fichier main.py
RUN echo "Vérification de la structure du répertoire et du fichier main.py..." && ls -l /usr/src/app/ && cat /usr/src/app/main.py

# Vérifier et modifier les permissions des fichiers dans le conteneur
RUN chmod -R 755 /usr/src/app
RUN chmod +x /usr/src/app/wait-for-rabbitmq.sh

# Définir la variable d'environnement Flask avec un chemin relatif
ENV FLASK_APP=main

# Exposer le port 5000 pour Flask
EXPOSE 5000

# Commande par défaut : utilisation dans docker-compose pour attendre RabbitMQ avant de démarrer Flask
CMD ["./wait-for-rabbitmq.sh", "rabbitmq:5672", "--", "flask", "run", "--host=0.0.0.0", "--port=5000"]
