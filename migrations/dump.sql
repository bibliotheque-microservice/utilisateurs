-- Table des utilisateurs
CREATE TABLE utilisateurs (
    id_utilisateur SERIAL PRIMARY KEY,           -- Identifiant unique de l'utilisateur
    nom VARCHAR(100) NOT NULL,                   -- Nom de l'utilisateur
    prenom VARCHAR(100) NOT NULL,                -- Prénom de l'utilisateur
    email VARCHAR(255) UNIQUE NOT NULL,          -- Adresse email de l'utilisateur
    mot_de_passe VARCHAR(255) NOT NULL,          -- Mot de passe (hashé)
    statut VARCHAR(20) DEFAULT 'actif',          -- Statut de l'utilisateur (actif, suspendu, etc.)
    created_at TIMESTAMP DEFAULT NOW(),          -- Date de création
    updated_at TIMESTAMP DEFAULT NOW(),          -- Date de mise à jour
    deleted_at TIMESTAMP NULL                    -- Soft delete (date de suppression ou NULL)
);

-- Table des rôles des utilisateurs (si vous voulez gérer les rôles d'accès)
CREATE TABLE roles (
    id_role SERIAL PRIMARY KEY,                  -- Identifiant unique du rôle
    nom_role VARCHAR(50) NOT NULL,               -- Nom du rôle (par exemple, admin, utilisateur)
    created_at TIMESTAMP DEFAULT NOW(),          -- Date de création
    updated_at TIMESTAMP DEFAULT NOW()           -- Date de mise à jour
);

-- Table pour lier les utilisateurs et leurs rôles
CREATE TABLE utilisateur_roles (
    utilisateur_id INT NOT NULL,                 -- ID de l'utilisateur
    role_id INT NOT NULL,                         -- ID du rôle
    created_at TIMESTAMP DEFAULT NOW(),          -- Date de création
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs (id_utilisateur) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles (id_role) ON DELETE CASCADE,
    PRIMARY KEY (utilisateur_id, role_id)        -- La relation est unique pour chaque utilisateur et rôle
);

-- Table des historiques de connexion (si vous voulez suivre les connexions des utilisateurs)
CREATE TABLE historiques_connexion (
    id_connexion SERIAL PRIMARY KEY,             -- Identifiant unique
    utilisateur_id INT NOT NULL,                 -- ID de l'utilisateur
    adresse_ip VARCHAR(45) NOT NULL,             -- Adresse IP de la connexion
    date_connexion TIMESTAMP DEFAULT NOW(),      -- Date de connexion
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs (id_utilisateur) ON DELETE CASCADE
);

-- Table des mots de passe oubliés (si vous gérez la réinitialisation des mots de passe)
CREATE TABLE mots_de_passe_oublies (
    id_mdp_oublie SERIAL PRIMARY KEY,            -- Identifiant unique
    utilisateur_id INT NOT NULL,                 -- ID de l'utilisateur
    token VARCHAR(255) NOT NULL,                  -- Token pour la réinitialisation
    date_creation TIMESTAMP DEFAULT NOW(),       -- Date de création du token
    date_expiration TIMESTAMP NOT NULL,          -- Date d'expiration du token
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs (id_utilisateur) ON DELETE CASCADE
);

-- Insertion d'exemples d'utilisateurs
INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe)
VALUES
('Doe', 'John', 'john.doe@example.com', 'hashed_password_1'),
('Smith', 'Jane', 'jane.smith@example.com', 'hashed_password_2');

-- Insertion de rôles
INSERT INTO roles (nom_role)
VALUES
('admin'),
('utilisateur');

-- Liaison des utilisateurs aux rôles
INSERT INTO utilisateur_roles (utilisateur_id, role_id)
VALUES
(1, 1),  -- John Doe est admin
(2, 2);  -- Jane Smith est un utilisateur
