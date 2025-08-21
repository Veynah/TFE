#!/home/groot/venv/googleScripts/bin/python3

import os
import re
from datetime import datetime, timedelta, date

# Répertoires pour les sauvegardes hebdomadaires et annuelles
BACKUP_DIRECTORY = "private"
WEEKLY_BACKUP_DIR = "private"
YEARLY_BACKUP_DIR = "private"

# Durée de rétention des fichiers (en jours)
RETENTION_DAYS = 8

"""
Script de gestion des sauvegardes.

Ce script gère automatiquement les fichiers de sauvegarde en appliquant
les règles suivantes :
1. Organisation des Sauvegardes Hebdomadaires.
2. Organisation des Sauvegardes Annuelles.
3. Suppression des Sauvegardes Obsolètes.

Le script supprime les fichiers plus anciens que 8 jours et déplace les
fichiers hebdomadaires et annuels vers des répertoires spécifiques.
"""


# Fonction pour extraire la date à partir du nom de fichier
def extract_date_from_filename(filename):
    date_pattern = r"\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD
    match = re.search(date_pattern, filename)
    if match:
        return datetime.strptime(match.group(), "%Y-%m-%d")
    return None


# Fonction pour traiter les fichiers dans un sous-répertoire donné
def process_subdirectory(subdirectory):
    cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
    last_monday = datetime.now() - timedelta(days=datetime.now().weekday() + 7)

    for filename in sorted(os.listdir(subdirectory)):
        file_path = os.path.join(subdirectory, filename)
        file_date = extract_date_from_filename(filename)

        if not file_date:
            continue

        # Vérification pour le fichier du lundi dernier
        if file_date.date() == last_monday.date():
            dest_path = os.path.join(
                WEEKLY_BACKUP_DIR, os.path.basename(subdirectory), filename
            )
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # Vérification si le fichier existe déjà
            if os.path.exists(dest_path):
                print(f"Le fichier hebdomadaire {dest_path} existe déjà, aucun déplacement nécessaire.")
            else:
                os.rename(file_path, dest_path)
                print(f"Déplacé {file_path} vers {dest_path}")

        # Vérification pour les fichiers annuels
        elif file_date.date() == date(file_date.year, 12, 31):
            dest_path = os.path.join(
                YEARLY_BACKUP_DIR, os.path.basename(subdirectory), filename
            )
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # Vérification si le fichier existe déjà
            if os.path.exists(dest_path):
                print(f"Le fichier annuel {dest_path} existe déjà, aucun déplacement nécessaire.")
            else:
                os.rename(file_path, dest_path)
                print(f"Déplacé {file_path} vers {dest_path}")

        # Suppression des fichiers obsolètes
        elif file_date < cutoff_date:
            os.remove(file_path)
            print(f"Supprimé {file_path}")


# Fonction principale pour traiter tous les sous-répertoires
def process_files(directory):
    for subdirectory in os.listdir(directory):
        subdirectory_path = os.path.join(directory, subdirectory)
        if os.path.isdir(subdirectory_path) and subdirectory not in [
            "backups_hebdo",
            "backups_annuelles",
        ]:
            process_subdirectory(subdirectory_path)


# Fonction pour ne garder que la sauvegarde du dernier lundi
def keep_latest_monday_backup(directory):
    for subdirectory in os.listdir(directory):
        subdirectory_path = os.path.join(directory, subdirectory)
        if os.path.isdir(subdirectory_path):
            monday_files = []
            for filename in os.listdir(subdirectory_path):
                file_path = os.path.join(subdirectory_path, filename)
                file_date = extract_date_from_filename(filename)
                
                # Vérification si le fichier correspond à un lundi
                if file_date and file_date.weekday() == 0:
                    monday_files.append((file_date, file_path))
            
            # Tri des fichiers du plus récent au plus ancien
            monday_files.sort(reverse=True, key=lambda x: x[0])
            
            # Garder seulement le dernier lundi
            for _, file_to_remove in monday_files[1:]:
                os.remove(file_to_remove)
                print(f"Supprimé l'ancien backup du lundi: {file_to_remove}")


# Exécuter la fonction
process_files(BACKUP_DIRECTORY)
keep_latest_monday_backup(WEEKLY_BACKUP_DIR)
