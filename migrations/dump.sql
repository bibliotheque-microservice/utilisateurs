-- Création de la table des utilisateurs
CREATE TABLE utilisateurs (
    id_utilisateur SERIAL PRIMARY KEY,           -- Identifiant unique de l'utilisateur (auto-incrément)
    nom VARCHAR(100) NOT NULL,                   -- Nom de l'utilisateur
    prenom VARCHAR(100) NOT NULL,                -- Prénom de l'utilisateur
    email VARCHAR(255) UNIQUE NOT NULL,          -- Adresse email unique et obligatoire
    mot_de_passe VARCHAR(255) NOT NULL,          -- Mot de passe hashé (pour sécurité)
    statut VARCHAR(20) DEFAULT 'actif',          -- Statut : actif par défaut, peut être suspendu, supprimé, etc.
    created_at TIMESTAMP DEFAULT NOW(),          -- Date de création de l'utilisateur (timestamp par défaut)
    updated_at TIMESTAMP DEFAULT NOW(),          -- Date de mise à jour (timestamp, mis à jour via triggers ou manuellement)
    deleted_at TIMESTAMP NULL                    -- Soft delete : la suppression logique avec une date, sinon NULL
);

-- Création de la table des rôles
CREATE TABLE roles (
    id_role SERIAL PRIMARY KEY,                  -- Identifiant unique du rôle
    nom_role VARCHAR(50) NOT NULL,               -- Nom du rôle, par exemple 'admin' ou 'utilisateur'
    created_at TIMESTAMP DEFAULT NOW(),          -- Date de création du rôle
    updated_at TIMESTAMP DEFAULT NOW()           -- Date de mise à jour du rôle
);

-- Table de liaison entre utilisateurs et rôles (relation N-N)
CREATE TABLE utilisateur_roles (
    utilisateur_id INT NOT NULL,                 -- ID de l'utilisateur (clé étrangère vers `utilisateurs`)
    role_id INT NOT NULL,                        -- ID du rôle (clé étrangère vers `roles`)
    created_at TIMESTAMP DEFAULT NOW(),          -- Date de création de cette liaison
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs (id_utilisateur) ON DELETE CASCADE, -- Supprime la relation si l'utilisateur est supprimé
    FOREIGN KEY (role_id) REFERENCES roles (id_role) ON DELETE CASCADE,                      -- Supprime la relation si le rôle est supprimé
    PRIMARY KEY (utilisateur_id, role_id)        -- Empêche les doublons : une même liaison ne peut exister qu'une seule fois
);

-- Table pour suivre les historiques de connexion des utilisateurs
CREATE TABLE historiques_connexion (
    id_connexion SERIAL PRIMARY KEY,             -- Identifiant unique pour chaque connexion
    utilisateur_id INT NOT NULL,                 -- ID de l'utilisateur (clé étrangère vers `utilisateurs`)
    adresse_ip VARCHAR(45) NOT NULL,             -- Adresse IP utilisée lors de la connexion
    date_connexion TIMESTAMP DEFAULT NOW(),      -- Date et heure de la connexion
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs (id_utilisateur) ON DELETE CASCADE -- Si l'utilisateur est supprimé, les historiques le sont aussi
);

-- Table pour gérer les réinitialisations de mots de passe
CREATE TABLE mots_de_passe_oublies (
    id_mdp_oublie SERIAL PRIMARY KEY,            -- Identifiant unique pour chaque demande
    utilisateur_id INT NOT NULL,                 -- ID de l'utilisateur ayant demandé une réinitialisation
    token VARCHAR(255) NOT NULL,                 -- Token généré pour valider la demande
    date_creation TIMESTAMP DEFAULT NOW(),       -- Date de création du token
    date_expiration TIMESTAMP NOT NULL,          -- Date d'expiration du token (limite de validité)
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs (id_utilisateur) ON DELETE CASCADE -- Suppression si l'utilisateur est supprimé
);

-- Insertion d'exemples d'utilisateurs
INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe)
VALUES
('Doe', 'John', 'john.doe@example.com', 'hashed_password_1'), -- Exemple : un utilisateur fictif nommé John Doe
('Smith', 'Jane', 'jane.smith@example.com', 'hashed_password_2'); -- Exemple : une utilisatrice fictive nommée Jane Smith

-- Insertion d'exemples de rôles
INSERT INTO roles (nom_role)
VALUES
('admin'),        -- Rôle administrateur
('utilisateur');  -- Rôle utilisateur standard

-- Liaison des utilisateurs aux rôles
INSERT INTO utilisateur_roles (utilisateur_id, role_id)
VALUES
(1, 1),  -- John Doe est administrateur
(2, 2);  -- Jane Smith est une utilisatrice standard

-- Création de la table des emprunts (gestion des livres empruntés par les utilisateurs)
CREATE TABLE emprunts (
    id_emprunt SERIAL PRIMARY KEY,               -- Identifiant unique pour chaque emprunt
    utilisateur_id INT NOT NULL,                 -- ID de l'utilisateur emprunteur
    livre_id INT NOT NULL,                       -- ID du livre emprunté
    date_emprunt DATE NOT NULL,                  -- Date à laquelle l'emprunt a été fait
    date_retour_prevu DATE NOT NULL,             -- Date limite pour rendre le livre
    date_retour_effectif DATE,                   -- Date réelle du retour (peut être NULL si pas encore rendu)
    statut VARCHAR(50) DEFAULT 'en_cours',       -- Statut de l'emprunt : en_cours, rendu, retard
    date_creation TIMESTAMP DEFAULT NOW(),       -- Date de création de l'emprunt
    UNIQUE(utilisateur_id, livre_id, date_retour_effectif) -- Empêche un utilisateur de réemprunter un même livre sans l'avoir rendu
);

-- Création de la table des pénalités (frais imposés pour des retards ou dommages)
CREATE TABLE penalites (
    id_penalite SERIAL PRIMARY KEY,              -- Identifiant unique pour chaque pénalité
    utilisateur_id INT NOT NULL,                 -- ID de l'utilisateur sanctionné
    emprunt_id INT NOT NULL,                     -- ID de l'emprunt concerné
    montant DECIMAL(10, 2) NOT NULL,             -- Montant de la pénalité
    paye BOOLEAN DEFAULT FALSE,                  -- Statut de paiement (non payé par défaut)
    date_calcul TIMESTAMP DEFAULT NOW(),         -- Date à laquelle la pénalité a été calculée
    date_paiement TIMESTAMP,                     -- Date à laquelle la pénalité a été payée
    FOREIGN KEY (emprunt_id) REFERENCES emprunts (id_emprunt) ON DELETE CASCADE -- Si l'emprunt est supprimé, la pénalité l'est aussi
);
