import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QFormLayout,
    QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Outil d'Analyse et de Gestion d'Articles")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet(self.get_stylesheet())  # Appliquer un style moderne

        # Création des onglets
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Ajouter les sections
        self.tabs.addTab(self.create_analysis_tab(), "Analyse de Site")
        self.tabs.addTab(self.create_article_tab(), "Création d'Articles")
        self.tabs.addTab(self.create_ftp_tab(), "Transfert FTP")

    def create_analysis_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Titre
        layout.addWidget(self.create_title("Analyse de Site"))

        # Champ URL
        form = QFormLayout()
        self.url_input = QLineEdit()
        form.addRow("Entrez l'URL du site :", self.url_input)
        layout.addLayout(form)

        # Bouton d'analyse
        analyze_button = QPushButton("Analyser")
        analyze_button.clicked.connect(self.analyze_site)
        layout.addWidget(analyze_button, alignment=Qt.AlignRight)

        tab.setLayout(layout)
        return tab

    def create_article_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Titre
        layout.addWidget(self.create_title("Création d'Articles"))

        # Formulaire
        form = QFormLayout()
        self.title_input = QLineEdit()
        self.intro_input = QTextEdit()
        self.body_input = QTextEdit()
        self.author_name_input = QLineEdit()
        self.author_photo_button = QPushButton("Importer une Photo")
        self.author_photo_button.clicked.connect(self.load_author_photo)

        form.addRow("Titre :", self.title_input)
        form.addRow("Introduction :", self.intro_input)
        form.addRow("Corps de l'article :", self.body_input)
        form.addRow("Nom de l'Auteur :", self.author_name_input)
        form.addRow("Photo de l'Auteur :", self.author_photo_button)
        layout.addLayout(form)

        # Bouton d'enregistrement
        submit_button = QPushButton("Enregistrer l'Article")
        submit_button.clicked.connect(self.save_article)
        layout.addWidget(submit_button, alignment=Qt.AlignRight)

        tab.setLayout(layout)
        return tab

    def create_ftp_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Titre
        layout.addWidget(self.create_title("Transfert FTP"))

        # Formulaire FTP
        form = QFormLayout()
        self.ftp_ip_input = QLineEdit()
        self.ftp_username_input = QLineEdit()
        self.ftp_password_input = QLineEdit()
        self.ftp_password_input.setEchoMode(QLineEdit.Password)

        form.addRow("Adresse IP/URL :", self.ftp_ip_input)
        form.addRow("Identifiant :", self.ftp_username_input)
        form.addRow("Mot de Passe :", self.ftp_password_input)
        layout.addLayout(form)

        # Bouton de transfert
        transfer_button = QPushButton("Transférer")
        transfer_button.clicked.connect(self.transfer_files)
        layout.addWidget(transfer_button, alignment=Qt.AlignRight)

        tab.setLayout(layout)
        return tab

    def create_title(self, text):
        title = QLabel(text)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        return title

    def analyze_site(self):
        url = self.url_input.text()
        if not url:
            self.show_alert("Erreur", "Veuillez entrer une URL valide.")
        else:
            print(f"Analyse du site : {url}")  # Remplacer par la logique réelle

    def load_author_photo(self):
        photo_path, _ = QFileDialog.getOpenFileName(self, "Choisir une Photo", "", "Images (*.png *.jpg *.jpeg)")
        if photo_path:
            print(f"Photo sélectionnée : {photo_path}")

    def save_article(self):
        if not self.title_input.text() or not self.body_input.toPlainText():
            self.show_alert("Erreur", "Veuillez remplir tous les champs obligatoires.")
        else:
            print("Article sauvegardé avec succès.")  # Remplacer par la logique réelle

    def transfer_files(self):
        ip = self.ftp_ip_input.text()
        username = self.ftp_username_input.text()
        password = self.ftp_password_input.text()
        if not ip or not username or not password:
            self.show_alert("Erreur", "Tous les champs FTP sont obligatoires.")
        else:
            print(f"Connexion FTP : {ip}, {username}")  # Remplacer par la logique réelle

    def show_alert(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def get_stylesheet(self):
        return """
        QMainWindow {
            background-color: #f4f4f4;
        }
        QPushButton {
            background-color: #0078d7;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #005a9e;
        }
        QLineEdit, QTextEdit {
            border: 1px solid #ccc;
            padding: 5px;
            border-radius: 3px;
        }
        QLabel {
            color: #333;
        }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
