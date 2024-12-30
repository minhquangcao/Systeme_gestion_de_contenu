from ftplib import FTP_TLS
import os
import socket
FTP_HOST = "localhost"
FTP_USER = "ftpuser"
FTP_PASSWORD = "test123"


def connect_to_ftp(host, user, password):
    """
    Connecte au serveur FTP avec les informations fournies.
    """
    try:
        ftp = FTP_TLS(host)
        ftp.auth()
        ftp.login(user=user, passwd=password)
        ftp.prot_p()  # Activer la protection des données
        ftp.set_pasv(True)  # Activer le mode passif
        ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # Gérer la session TLS
        ftp.set_debuglevel(2)  # Activer les logs de débogage
        print(f"Connexion réussie au serveur FTP : {host}")
        return ftp
    except Exception as e:
        print(f"Erreur lors de la connexion au serveur FTP : {e}")
        return None

def transfer_file(ftp, local_file, remote_directory):
    """
    Transfère un fichier local vers un répertoire spécifique sur le serveur FTP.
    Si le répertoire distant n'existe pas, il est créé.
    """
    try:
        # Naviguer vers le répertoire distant ou le créer
        try:
            ftp.cwd(remote_directory)
        except Exception:
            print(f"Répertoire distant non trouvé. Création de : {remote_directory}")
            ftp.mkd(remote_directory)
            ftp.cwd(remote_directory)

        # Transférer le fichier
        with open(local_file, "rb") as file:
            ftp.storbinary(f"STOR {os.path.basename(local_file)}", file)
        print(f"Transfert réussi : {local_file} vers {remote_directory}")

    except Exception as e:
        print(f"Erreur lors du transfert de {local_file} : {e}")

def transfer_files_to_ftp(host, user, password, files_and_directories):
    """
    Transfère plusieurs fichiers vers leurs répertoires appropriés sur le serveur FTP.
    """
    ftp = connect_to_ftp(host, user, password)
    if not ftp:
        return

    for local_file, remote_directory in files_and_directories.items():
        if os.path.exists(local_file):
            transfer_file(ftp, local_file, remote_directory)
        else:
            print(f"Fichier local non trouvé : {local_file}")

    ftp.quit()
    print("Déconnexion du serveur FTP.")

if __name__ == "__main__":
    # Étape 1 : Prendre les informations de connexion
    ftp_host = FTP_HOST
    ftp_user = FTP_USER
    ftp_password = FTP_PASSWORD

    # Étape 2 : Fichiers à transférer et leurs répertoires distants
    files_and_directories = {
        "test.txt": "/test"     # Article HTML généré
    }

    # Étape 3 : Transférer les fichiers
    transfer_files_to_ftp(ftp_host, ftp_user, ftp_password, files_and_directories)

