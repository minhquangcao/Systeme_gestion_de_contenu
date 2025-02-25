import ftplib
import os
import time
import streamlit as st
import json

FILE_CONFIG = "frontend/config/config.json"
class ExplicitFTPTLS(ftplib.FTP_TLS):
    """Explicit FTPS, with shared TLS session"""

    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(
                conn,
                server_hostname=self.host,
                session=self.sock.session
            )
        return conn, size


class FTPClient:
    """Gestion complète des connexions et transferts FTPS."""

    def __init__(self):
        with open(FILE_CONFIG, "r", encoding="utf-8") as f:
            data = json.load(f)  # Charger les données JSON

        self.host = data["SERVEUR_FTP"]
        self.user = data["USERNAME_FTP"]
        self.password = data["PASSWORD_FTP"]
        self.remote_directory = data["DIRECTORY_URL"]
        self.ftp = None

    def connect(self):
        """Connexion au serveur FTP avec FTPS."""
        try:
            self.ftp = ExplicitFTPTLS(self.host)
            self.ftp.auth()  # Initialiser l'authentification TLS
            self.ftp.login(user=self.user, passwd=self.password)
            self.ftp.prot_p()  # Activer la protection des connexions de données
            self.ftp.set_pasv(True)  # Activer le mode passif
            print(f"Connexion réussie au serveur FTP : {self.host}")
        except Exception as e:
            print(f"Erreur lors de la connexion au serveur FTP : {e}")
            self.ftp = None

    def progress_callback(self, block):
        """Callback pour afficher la progression du transfert."""
        self.pbar.update(len(block))  # Mettre à jour la barre de progression

    def transfer_file(self, local_file):
        """Transfère un fichier local vers un répertoire distant avec suivi de la progression."""
        if not self.ftp:
            print("Pas de connexion FTP active.")
            return

        try:
            # Naviguer vers le répertoire distant ou le créer
            try:
                self.ftp.cwd(self.remote_directory)
            except ftplib.error_perm:
                print(f"Répertoire distant non trouvé. Création de : {self.remote_directory}")
                self.ftp.mkd(self.remote_directory)
                self.ftp.cwd(self.remote_directory)

            # Obtenir la taille du fichier local pour la barre de progression
            file_size = os.path.getsize(local_file)

            with st.spinner(text="📤 Transfert en cours...",show_time=True):
                time.sleep(5)
                # Ouvrir le fichier local à transférer
                with open(local_file, "rb") as file:
                    self.ftp.storbinary(f"STOR {os.path.basename(local_file)}", file)

                    # Vérification de la réussite du transfert en listant le fichier sur le serveur
                    files = self.ftp.nlst()  # Récupérer la liste des fichiers sur le serveur
                    if os.path.basename(local_file) in files:
                        st.success(f"✅ Transfert réussi : {local_file}")
                    else:
                        st.error(f"❌ Le transfert a échoué : {local_file} n'est pas présent sur le serveur.")

        except Exception as e:
            print(f"Erreur lors du transfert de {local_file} : {e}")

    def transfer_files(self, files):
        """Transfère plusieurs fichiers vers leurs répertoires appropriés avec suivi de la progression."""
        if not self.ftp:
            print("Pas de connexion FTP active.")
            return

        for local_file in files:
            if os.path.exists(local_file):
                self.transfer_file(local_file)
            else:
                st.error(f"Fichier local non trouvé : {local_file}")

    def disconnect(self):
        """Déconnecte du serveur FTP."""
        if self.ftp:
            try:
                self.ftp.quit()
                print("Déconnexion du serveur FTP.")
            except Exception as e:
                print(f"Erreur lors de la déconnexion : {e}")
