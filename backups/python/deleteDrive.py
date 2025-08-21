#!/home/groot/venv/googleScripts/bin/python3

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from datetime import datetime, timedelta
import io
import hashlib
import logging
import os
import json

# Configuration du logger
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configuration
SCOPES = ["https://www.googleapis.com/auth/drive"]
TOKEN_PATH = "private"
BACKUP_DIRECTORY = "private"
PARENT_FOLDER_ID = "private"
HASH_VERIFICATION_FILE = "hash_verification.txt"

# Charger les credentials
logging.info("Chargement des credentials...")
try:
    with open(TOKEN_PATH, "r") as token_file:
        token_info = json.load(token_file)
    credentials = Credentials.from_authorized_user_info(token_info, SCOPES)
    service = build("drive", "v3", credentials=credentials)
    logging.info("Authentification réussie.")
except Exception as e:
    logging.error(f"Erreur lors de l'authentification : {e}")
    exit()


# Fonction pour lister tous les fichiers et dossiers d'un dossier parent
def list_all_files(parent_folder_id):
    logging.info(
        f"Listing des fichiers et dossiers dans le dossier parent ID: {parent_folder_id}"
    )
    try:
        results = (
            service.files()
            .list(
                q=f"'{parent_folder_id}' in parents",
                spaces="drive",
                fields="files(id, name, mimeType, createdTime, md5Checksum)",
                orderBy="createdTime desc",
            )
            .execute()
        )
        items = results.get("files", [])
        logging.info(f"{len(items)} élément(s) trouvé(s).")
        return items
    except Exception as e:
        logging.error(f"Erreur lors du listing des éléments : {e}")
        return []


# Fonction pour supprimer un fichier sur Google Drive
def delete_file(file_id, file_name):
    logging.info(f"Suppression du fichier ID: {file_id}, Nom: {file_name}")
    try:
        #service.files().update(fileId=file_id, body={"trashed": True}).execute()
        service.files().delete(fileId=file_id).execute()
        logging.info(f"Fichier {file_name} mis dans la corbeille avec succès.")
        with open("poubelle.txt", "a") as poubelle_file:
            poubelle_file.write(f"{file_name}\n")
    except Exception as e:
        logging.error(f"Erreur lors de la suppression du fichier {file_name} : {e}")


# Fonction pour calculer le hachage MD5 d'un fichier
def calculate_md5(file_path):
    md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception as e:
        logging.error(f"Erreur lors du calcul du hachage MD5 pour {file_path} : {e}")
        return None


# Fonction pour télécharger un fichier
def download_file(file_id, file_name, local_directory, server_md5):
    logging.info(
        f"Début du téléchargement pour le fichier ID: {file_id}, Nom: {file_name}"
    )
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            logging.info(f"Téléchargement {int(status.progress() * 100)}% complet.")
        file_path = os.path.join(local_directory, file_name)
        with open(file_path, "wb") as f:
            f.write(fh.getbuffer())
        logging.info(f"Fichier téléchargé et enregistré à {file_path}")

        local_md5 = calculate_md5(file_path)
        verification_status = "ERREUR"
        if server_md5 and local_md5:
            if server_md5 == local_md5:
                verification_status = "OK"
            logging.info(f"Vérification du fichier {file_name} : {verification_status}")
        else:
            logging.error(f"Impossible de vérifier l'intégrité du fichier {file_name}.")

        with open(HASH_VERIFICATION_FILE, "a") as verification_file:
            verification_file.write(f"{file_name}: {verification_status}\n")

    except Exception as e:
        logging.error(f"Erreur lors du téléchargement du fichier {file_name} : {e}")


# Fonction pour trier et conserver les 2 fichiers les plus récents
def keep_two_most_recent_files(files):
    logging.info("Conservation des deux fichiers les plus récents...")
    files.sort(key=lambda x: x["createdTime"], reverse=True)
    to_delete = files[2:]
    for file in to_delete:
        delete_file(file["id"], file["name"])


# Processus principal pour vérifier et télécharger les fichiers manquants
def download_backups(parent_folder_id, local_path):
    logging.info("Début du processus de vérification et téléchargement des fichiers...")
    cutoff_date = datetime.now() - timedelta(days=8)
    items = list_all_files(parent_folder_id)

    folders = [
        item
        for item in items
        if item["mimeType"] == "application/vnd.google-apps.folder"
    ]
    files = [
        item
        for item in items
        if item["mimeType"] != "application/vnd.google-apps.folder"
    ]

    # Process folders first
    for folder in folders:
        local_subdir_path = os.path.join(local_path, folder["name"])
        os.makedirs(local_subdir_path, exist_ok=True)
        download_backups(folder["id"], local_subdir_path)

    # Process files

    # Téléchargement des fichiers manquants et non plus vieux de 8 jours
    for file in files:
        file_name = file["name"]
        file_id = file["id"]
        file_md5 = file.get("md5Checksum")
        created_time = datetime.strptime(file["createdTime"], "%Y-%m-%dT%H:%M:%S.%fZ")

        if created_time < cutoff_date:
            logging.info(
                f"Fichier {file_name} ignoré car il est plus vieux que 8 jours."
            )
            continue

        if file_name not in os.listdir(local_path):
            logging.info(f"Fichier manquant trouvé : {file_name}")
            download_file(file_id, file_name, local_path, file_md5)

    # Ensuite, on conserve seulement les 2 fichiers les plus récents (sans toucher aux dossiers)
    keep_two_most_recent_files(files)


# Exécuter le script
download_backups(PARENT_FOLDER_ID, BACKUP_DIRECTORY)

