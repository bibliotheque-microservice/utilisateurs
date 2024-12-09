# Utilisation de l'image de base Python
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /usr/src/app

# Copier le fichier des dépendances (ex: requirements.txt)
COPY requirements.txt .

# Mettre à jour pip et installer les dépendances Python sans garder le cache
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers de l'application dans le conteneur
COPY . .

# Définir la variable d'environnement Flask
ENV FLASK_APP=app.py  

# Exposer le port 5000 pour Flask
EXPOSE 5000

# Commande pour exécuter l'application Flask
CMD ["flask", "run", "--host=0.0.0.0"]
