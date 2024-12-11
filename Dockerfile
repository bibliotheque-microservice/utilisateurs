FROM python:3.10-slim

WORKDIR /usr/src/app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copier les fichiers de l'application
COPY . .

# Définir la variable FLASK_APP pour Flask
ENV FLASK_APP=main.py

# Exposer le port Flask
EXPOSE 5000

# Lancer Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
