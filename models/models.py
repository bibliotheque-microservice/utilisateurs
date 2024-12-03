from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Modèle Utilisateur
class Utilisateur(db.Model):
    __tablename__ = 'utilisateurs'
    
    id_utilisateur = db.Column(db.Integer, primary_key=True)         # Identifiant unique
    nom = db.Column(db.String(100), nullable=False)                   # Nom
    prenom = db.Column(db.String(100), nullable=False)                # Prénom
    email = db.Column(db.String(255), unique=True, nullable=False)    # Email
    mot_de_passe = db.Column(db.String(255), nullable=False)          # Mot de passe (hashé)
    statut = db.Column(db.String(20), default='actif')                # Statut (actif, suspendu, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)      # Date de création
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Date de mise à jour
    deleted_at = db.Column(db.DateTime, nullable=True)                # Soft delete (date de suppression)
    
    # Champs pour gérer les emprunts et les pénalités
    solde_penalites = db.Column(db.Float, default=0.0)                # Solde des pénalités
    emprunts_en_retard = db.Column(db.Boolean, default=False)         # Indiquer si l'utilisateur a des emprunts en retard

    # Lien avec les rôles
    roles = db.relationship('Role', secondary='utilisateur_roles', back_populates='utilisateurs')

    # Relation avec les emprunts
    emprunts = db.relationship('Emprunt', backref='utilisateur', lazy=True)
    
    # Relation avec les pénalités
    penalites = db.relationship('Penalite', backref='utilisateur', lazy=True)

    def __repr__(self):
        return f'<Utilisateur {self.nom} {self.prenom}>'

    # Méthode pour mettre à jour le solde des pénalités
    def update_solde_penalites(self):
        total_penalites = sum([penalite.montant for penalite in self.penalites if penalite.date_paiement is None])
        self.solde_penalites = total_penalites
        db.session.commit()

# Modèle Rôle
class Role(db.Model):
    __tablename__ = 'roles'
    
    id_role = db.Column(db.Integer, primary_key=True)                # Identifiant unique du rôle
    nom_role = db.Column(db.String(50), nullable=False)              # Nom du rôle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)      # Date de création
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Date de mise à jour

    # Lien avec les utilisateurs
    utilisateurs = db.relationship('Utilisateur', secondary='utilisateur_roles', back_populates='roles')

    def __repr__(self):
        return f'<Role {self.nom_role}>'

# Table de liaison Utilisateur-Rôle
class UtilisateurRole(db.Model):
    __tablename__ = 'utilisateur_roles'

    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_utilisateur', ondelete='CASCADE'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id_role', ondelete='CASCADE'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)      # Date de création

# Modèle Emprunt
class Emprunt(db.Model):
    __tablename__ = 'emprunts'
    
    id_emprunt = db.Column(db.Integer, primary_key=True)              # Identifiant unique de l'emprunt
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_utilisateur', ondelete='CASCADE'))
    livre_id = db.Column(db.Integer, nullable=False)                   # Identifiant du livre emprunté
    date_emprunt = db.Column(db.DateTime, default=datetime.utcnow)     # Date de l'emprunt
    date_retour_prevu = db.Column(db.DateTime, nullable=False)        # Date de retour prévue
    date_retour_effectif = db.Column(db.DateTime, nullable=True)      # Date de retour effectif (si retourné)
    
    utilisateur = db.relationship('Utilisateur', backref=db.backref('emprunts', lazy=True))

    def __repr__(self):
        return f'<Emprunt {self.id_emprunt}>'

# Modèle Penalite
class Penalite(db.Model):
    __tablename__ = 'penalites'
    
    id_penalite = db.Column(db.Integer, primary_key=True)            # Identifiant unique de la pénalité
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_utilisateur', ondelete='CASCADE'), nullable=False)
    montant = db.Column(db.Float, nullable=False)                     # Montant de la pénalité
    date_paiement = db.Column(db.DateTime, nullable=True)             # Date de paiement de la pénalité
    
    utilisateur = db.relationship('Utilisateur', backref=db.backref('penalites', lazy=True))

    def __repr__(self):
        return f'<Penalite {self.id_penalite}>'

# Modèle Historique de Connexion
class HistoriqueConnexion(db.Model):
    __tablename__ = 'historiques_connexion'
    
    id_connexion = db.Column(db.Integer, primary_key=True)           # Identifiant unique
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_utilisateur', ondelete='CASCADE'), nullable=False)  # ID de l'utilisateur
    adresse_ip = db.Column(db.String(45), nullable=False)             # Adresse IP de la connexion
    date_connexion = db.Column(db.DateTime, default=datetime.utcnow)  # Date de connexion

    utilisateur = db.relationship('Utilisateur', backref='connexions')

    def __repr__(self):
        return f'<Connexion de {self.utilisateur.nom} {self.utilisateur.prenom} à {self.date_connexion}>'

# Modèle pour le mot de passe oublié (gestion de la réinitialisation)
class MotDePasseOublie(db.Model):
    __tablename__ = 'mots_de_passe_oublies'
    
    id_mdp_oublie = db.Column(db.Integer, primary_key=True)            # Identifiant unique
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_utilisateur', ondelete='CASCADE'), nullable=False)  # ID de l'utilisateur
    token = db.Column(db.String(255), nullable=False)                   # Token pour la réinitialisation
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)     # Date de création du token
    date_expiration = db.Column(db.DateTime, nullable=False)            # Date d'expiration du token

    utilisateur = db.relationship('Utilisateur', backref='mots_de_passe_oublies')

    def __repr__(self):
        return f'<Token de réinitialisation pour {self.utilisateur.nom} {self.utilisateur.prenom}>'

