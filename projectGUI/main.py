from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Outil d'analyse et de gestion d'articles")
        self.setGeometry(100, 100, 800, 600)

        # Création des onglets
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Ajouter les sections
        self.tabs.addTab(self.create_analysis_tab(), "Analyse de site")
        self.tabs.addTab(self.create_article_tab(), "Création d'articles")
        self.tabs.addTab(self.create_ftp_tab(), "Transfert FTP")

    def create_analysis_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Section : Analyse de site"))
        tab.setLayout(layout)
        return tab

    def create_article_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Section : Création d'articles"))
        tab.setLayout(layout)
        return tab

    def create_ftp_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Section : Transfert FTP"))
        tab.setLayout(layout)
        return tab

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
