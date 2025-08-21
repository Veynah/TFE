# Projet TFE – Sécurisation et Déploiement d’un Environnement Odoo avec Monitoring

Ce dépôt contient l’ensemble des fichiers, scripts et configurations développés dans le cadre du Travail de Fin d’Études (TFE) consacré à la **sécurité des environnements de développement**.

---

## 📦 Prérequis

Avant d’utiliser ce dépôt, assurez-vous d’avoir installé et configuré les éléments suivants :

### 1. Docker & Docker Compose
- Docker >= 24.x  
- Docker Compose >= 2.x  
- Accès à un registre Docker local ou distant (configuration dans `Docker/docker`)

👉 Documentation officielle : [https://docs.docker.com](https://docs.docker.com)

### 2. Ansible
- Ansible >= 2.16  
- Accès SSH configuré pour le déploiement des rôles (voir `monitoring/The-Eye`)  

👉 Documentation officielle : [https://docs.ansible.com](https://docs.ansible.com)

### 3. Python
- Python >= 3.10  
- Pip et virtualenv pour l’exécution des scripts auxiliaires (backups, intégrité, etc.)  

👉 Documentation officielle : [https://docs.python.org/3/](https://docs.python.org/3/)

---

## 📂 Structure du dépôt

- **Docker/** → Construction et exécution des conteneurs (Odoo, PostgreSQL, Registry, Nginx).  
- **monitoring/** → Stack Prometheus + Grafana déployée via Ansible.  
- **odoo/** → Module Odoo custom pour l’export des métriques vers Prometheus.  
- **backups/** → Scripts Ansible et Python pour la gestion des sauvegardes (PostgreSQL + filestore Odoo).  
- **Scripts/** → Scripts shell pour l’audit système et le durcissement Linux.  
- **vade_mecum.pdf** → Document académique lié au projet.  

---

## 🚀 Déploiement

Le déploiement d’une instance Odoo sécurisée et monitorée est détaillé dans le **TFE** (voir `TFE.docx`).  
En résumé :  

1. Lancer le registre Docker local (`Docker/docker/docker-compose.yaml`).  
2. Construire et pousser l’image Odoo (`Docker/build`).  
3. Déployer les services applicatifs (`Docker/services`).  
4. Mettre en place le reverse proxy Nginx (`Docker/nginx`).  
5. Déployer la stack de monitoring avec Ansible (`monitoring/The-Eye`).  

---

## 🔒 Sécurité

Le projet inclut plusieurs mécanismes de sécurité :  
- Scripts shell d’audit et de durcissement (`Scripts/`)  
- Monitoring système et applicatif (Prometheus + Grafana + Alertmanager)  
- Sauvegardes automatisées avec signatures et rétention (`backups/`)  

---

## 📖 Références

Les instructions complètes, justifications de choix techniques et résultats des tests sont disponibles dans le document principal :  
- **TFE.docx** : Rapport académique complet  
- **vade_mecum.pdf** : Guide de procédures associé  

---

✍️ Auteur : *[Adam Tangiev]*  
🎓 Projet réalisé dans le cadre du Travail de Fin d’Études – [IETCPS]
