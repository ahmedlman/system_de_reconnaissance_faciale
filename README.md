# 🎓 Gestion de la Présence des Élèves avec Détection de Visage par Caméra

> 📅 Projet de Fin d'Études – Année Universitaire 2024/2025  
> 🏢 Réalisé chez Kernel SI (Kernel Solutions and Innovation) – Hammam-Lif  
> 👨‍💻 Réalisé par : Ahmed  
> 🎯 Encadré par : [Nom de l'encadrant académique / industriel]

---

## 📝 Description du Projet

Ce projet vise à développer un système de gestion de la présence des élèves basé sur la reconnaissance faciale en temps réel via caméra. Il a pour but d’automatiser le suivi de présence en milieu scolaire, en réduisant les tâches administratives, en augmentant la précision des données de présence et en renforçant la transparence.

---

## 🚀 Fonctionnalités Principales

- 🔐 Authentification des utilisateurs avec gestion des rôles (Admin, Enseignant, Étudiant)
- 📷 Détection et reconnaissance faciale en temps réel avec caméra
- ⏰ Reconnaissance limitée à une plage horaire définie
- 🧠 Modèle CNN intégré pour l’entraînement et la reconnaissance
- 🗓️ Suivi de présence journalier avec statistiques (présents, absents)
- 🧑‍🏫 Gestion des enseignants et des étudiants avec photos et informations complètes
- 📊 Tableau de bord interactif avec indicateurs clés
- 🛠️ Interface graphique moderne et responsive construite avec [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

---

## 🧰 Technologies Utilisées

| Technologie     | Usage                                      |
|----------------|--------------------------------------------|
| Python          | Langage principal de développement         |
| OpenCV          | Capture vidéo et traitement d'image        |
| TensorFlow      | Modèle CNN MobileNetV2 pour la reconnaissance faciale |
| Mediapipe       | Détection des visages (optionnelle/alternative) |
| CustomTkinter   | Création de l'interface utilisateur moderne |
| MySQL           | Stockage des utilisateurs, présences, rôles |
| threading       | Pour le traitement parallèle (vidéo, UI, etc.) |

---

## 🗂️ Structure du Projet

```plaintext
📁 assets/ # Images, icônes, GIFs, etc.
📁 dataset/ # Données d’entraînement pour le modèle
📁 models/ # Modèles enregistrés (CNN, encodings, etc.)
📁 photo/ # Photos des élèves/enseignants
📁 Diagrammes/ # Modèles de base de données (MySQL Workbench)
📁 venv/ # Environnement virtuel Python

📄 capture_faces.py # Capture d’images de visages
📄 face_recog.py # Détection et reconnaissance faciale en temps réel
📄 config.py # Paramètres de configuration
📄 database.py # Connexion à la base de données
📄 login.py, sign_up.py # Authentification des utilisateurs
📄 student.py # Gestion des étudiants
📄 teacher.py # Gestion des enseignants
📄 classe.py, classes.svg # Gestion des classes et visualisation
📄 home.py, main.py # Interface principale et navigation
📄 seance.py # Gestion des séances / plages horaires
📄 settings.py # Paramètres de l’application
📄 shape_predictor_68_face_landmarks.dat(.bz2) # Modèle Dlib de détection des points du visage
📄 haarcascade_frontalface_default.xml # Classifieur Haar pour la détection des visages
📄 face_encodings.pickle # Données encodées pour la reconnaissance
📄 database.sql # Script SQL de création de base de données
📄 diagram star.mwb # Modèle de base de données (MySQL Workbench)
## ⚙️ Installation

### Prérequis

- Python 3.9 ou version supérieure
- MySQL Server (avec table `users`, `students`, `teachers`, `attendance`, etc.)
- Caméra intégrée ou externe
- Virtualenv recommandé

### Étapes

```bash
git clone https://github.com/votre-utilisateur/pfe-face-attendance.git
cd pfe-face-attendance
pip install -r requirements.txt
