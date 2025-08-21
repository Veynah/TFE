#!/home/groot/venv/googleScripts/bin/python3

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import logging
from datetime import datetime, timedelta
import hashlib

# Configuration du logger
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configuration
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = "privata"
BACKUP_DIRECTORY = "private"
PARENT_FOLDER_ID = "private"
HASH_VERIFICATION_FILE = os.path.join(BACKUP_DIRECTORY, "hash_verification.txt")

# Authentification
logging.info("Authentification en cours...")
try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=credentials)
    logging.info("Authentification réussie.")
except Exception as e:
    logging.error(f"Erreur lors de l'authentification : {e}")
    exit()

# Fonction pour lister tous les fichiers et dossiers d'un dossier parent, y compris les sous-dossiers
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
                fields="files(id, name, mimeType, md5Checksum, createdTime)",
                orderBy="name",
            )
            .execute()
        )
        items = results.get("files", [])
        logging.info(f"{len(items)} élément(s) trouvé(s).")
        return items
    except Exception as e:
        logging.error(f"Erreur lors du listing des éléments : {e}")
        return []

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

        # Vérification de l'intégrité du fichier téléchargé
        local_md5 = calculate_md5(file_path)
        verification_status = "ERREUR"
        if server_md5 and local_md5:
            if server_md5 == local_md5:
                verification_status = "OK"
            logging.info(f"Vérification du fichier {file_name} : {verification_status}")
        else:
            logging.error(f"Impossible de vérifier l'intégrité du fichier {file_name}.")

        # Écriture du résultat dans le fichier de vérification
        with open(HASH_VERIFICATION_FILE, "a") as verification_file:
            verification_file.write(f"{file_name}: {verification_status}\n")

    except Exception as e:
        logging.error(f"Erreur lors du téléchargement du fichier {file_name} : {e}")

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

# Processus principal pour vérifier et télécharger les fichiers manquants
def download_backups(parent_folder_id, local_path):
    logging.info("Début du processus de vérification et téléchargement des fichiers...")
    cutoff_date = datetime.now() - timedelta(days=21)
    items = list_all_files(parent_folder_id)

    # Parcourir les dossiers en premier
    for item in items:
        item_name = item["name"]
        item_id = item["id"]
        mime_type = item["mimeType"]

        if mime_type == "application/vnd.google-apps.folder":
            # Si c'est un dossier, créer un répertoire local et lister les fichiers dans ce dossier
            local_subdir_path = os.path.join(local_path, item_name)
            os.makedirs(local_subdir_path, exist_ok=True)
            logging.debug(f"Répertoire trouvé sur Drive: {item_name} (ID: {item_id})")
            download_backups(
                item_id, local_subdir_path
            )  # Appel récursif pour les sous-dossiers

    # Maintenant, traiter les fichiers
    for item in items:
        item_name = item["name"]
        item_id = item["id"]
        mime_type = item["mimeType"]
        item_md5 = item.get("md5Checksum")
        created_time = datetime.strptime(item["createdTime"], "%Y-%m-%dT%H:%M:%S.%fZ")

        if mime_type != "application/vnd.google-apps.folder":
            if created_time < cutoff_date:
                logging.info(
                    f"Fichier {item_name} ignoré car il est plus vieux que 21 jours."
                )
                continue

            # Si c'est un fichier, vérifier s'il existe déjà dans le sous-répertoire correspondant
            local_files = os.listdir(local_path)
            logging.debug(f"Fichier trouvé sur Drive: {item_name}")
            if item_name not in local_files:
                logging.info(f"Fichier manquant trouvé : {item_name}")
                download_file(item_id, item_name, local_path, item_md5)

# Liste les répertoires et fichiers locaux
def list_local_files(local_path):
    logging.info(
        f"Listing des fichiers et dossiers locaux dans le répertoire {local_path}"
    )
    for root, dirs, files in os.walk(local_path):
        logging.debug(f"Dossier: {root}")
        for dir_name in dirs:
            logging.debug(f"Sous-dossier: {dir_name}")
        for file_name in files:
            logging.debug(f"Fichier: {file_name}")

# Démarrer le processus de vérification et téléchargement des fichiers
download_backups(PARENT_FOLDER_ID, BACKUP_DIRECTORY)
list_local_files(BACKUP_DIRECTORY)


