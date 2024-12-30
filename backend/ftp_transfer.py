import ftplib
import os

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
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
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

    def transfer_file(self, local_file, remote_directory):
        """Transfère un fichier local vers un répertoire distant."""
        if not self.ftp:
            print("Pas de connexion FTP active.")
            return

        try:
            # Naviguer vers le répertoire distant ou le créer
            try:
                self.ftp.cwd(remote_directory)
            except ftplib.error_perm:
                print(f"Répertoire distant non trouvé. Création de : {remote_directory}")
                self.ftp.mkd(remote_directory)
                self.ftp.cwd(remote_directory)

            # Transférer le fichier
            with open(local_file, "rb") as file:
                self.ftp.storbinary(f"STOR {os.path.basename(local_file)}", file)
                print(f"Transfert réussi : {local_file} vers {remote_directory}")
        except Exception as e:
            print(f"Erreur lors du transfert de {local_file} : {e}")

    def transfer_files(self, files_and_directories):
        """Transfère plusieurs fichiers vers leurs répertoires appropriés."""
        if not self.ftp:
            print("Pas de connexion FTP active.")
            return

        for local_file, remote_directory in files_and_directories.items():
            if os.path.exists(local_file):
                self.transfer_file(local_file, remote_directory)
            else:
                print(f"Fichier local non trouvé : {local_file}")

    def disconnect(self):
        """Déconnecte du serveur FTP."""
        if self.ftp:
            try:
                self.ftp.quit()
                print("Déconnexion du serveur FTP.")
            except Exception as e:
                print(f"Erreur lors de la déconnexion : {e}")

if __name__ == "__main__":
    # Informations de connexion
    FTP_HOST = "localhost"
    FTP_USER = "ftpuser"
    FTP_PASSWORD = "test123"

    # Fichiers à transférer et leurs répertoires distants
    files_and_directories = {
        "test.txt": "/test"  # Exemple de fichier à transférer
    }

    # Initialisation et transfert
    ftp_client = FTPClient(FTP_HOST, FTP_USER, FTP_PASSWORD)
    ftp_client.connect()
    ftp_client.transfer_files(files_and_directories)
    ftp_client.disconnect()
