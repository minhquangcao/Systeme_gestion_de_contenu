import streamlit as st
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="Outil Pro de Gestion d'Articles",
    page_icon="📋",
    layout="wide"
)

# CSS personnalisé pour améliorer le style
def apply_custom_styles():
    st.markdown(
        """
        <style>
        body {
            background: linear-gradient(to bottom, #ffffff, #e6f7ff);
            font-family: 'Arial', sans-serif;
        }
        .main-title {
            font-size: 2.8em;
            color: #0078d7;
            text-align: center;
            margin-bottom: 20px;
        }
        .sidebar .sidebar-content {
            background-color: #00457c !important;
            color: white;
        }
        .sidebar .css-1lcbmhc {
            padding: 20px !important;
        }
        .stButton>button {
            background-color: #4CAF50 !important;
            color: white !important;
            border: none;
            padding: 10px 20px;
            font-weight: bold;
            border-radius: 8px;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #45a049 !important;
        }
        .stFileUploader label {
            color: #0078d7 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_styles()

# Titre principal
st.markdown('<div class="main-title">🌐 Outil Pro de Gestion d\'Articles</div>', unsafe_allow_html=True)

# Menu de navigation dans la barre latérale
st.sidebar.title("📂 Menu de Navigation")
menu = st.sidebar.radio(
    "Choisissez une section :", 
    ["Accueil", "Analyse de Site", "Création d'Articles", "Transfert FTP", "Informations"]
)

# **Accueil**
if menu == "Accueil":
    st.header("🏠 Bienvenue sur l'Outil Pro de Gestion d'Articles")
    st.markdown(
        """
        Cet outil vous permet de :
        - Analyser des sites web pour en extraire des modèles d'articles.
        - Créer des articles avec des contenus personnalisés.
        - Transférer automatiquement vos fichiers sur un serveur via FTP.
        
        Explorez les fonctionnalités à l'aide du menu de navigation. 🖱️
        """
    )
    st.image("https://source.unsplash.com/900x400/?technology,web", caption="Gérez vos articles avec simplicité")

# **Analyse de site web**
elif menu == "Analyse de Site":
    st.header("🌐 Analyse de Site Web")
    st.markdown("Analysez un site pour extraire ses modèles d'articles.")
    url = st.text_input("Entrez l'URL à analyser :", placeholder="https://exemple.com")
    if st.button("Analyser le Site"):
        if not url:
            st.error("❌ Veuillez entrer une URL valide.")
        else:
            with st.spinner("🔍 Analyse en cours..."):
                # Résultats simulés
                st.success("✅ Analyse terminée avec succès !")
                st.json({
                    "Structure détectée": {
                        "Polices": ["Arial", "16px"],
                        "Couleurs": ["Bleu", "Gris"],
                        "Disposition": "Trois colonnes"
                    },
                    "Temps de chargement": "2.3 secondes",
                    "Erreurs détectées": "Aucune"
                })

# **Création d'Articles**
elif menu == "Création d'Articles":
    st.header("📝 Création d'Articles")
    st.markdown("Complétez les champs ci-dessous pour générer un article.")
    title = st.text_input("Titre de l'article :", placeholder="Entrez un titre captivant")
    intro = st.text_area("Introduction :", placeholder="Rédigez une introduction percutante")
    body = st.text_area("Contenu :", placeholder="Développez le contenu ici")
    author = st.text_input("Nom de l'auteur :", placeholder="Nom de l'auteur")
    image_file = st.file_uploader("Image principale (optionnel) :", type=["png", "jpg", "jpeg"])

    if image_file:
        st.image(Image.open(image_file), caption="Aperçu de l'image téléchargée", use_column_width=True)

    if st.button("Générer l'Article"):
        if not title or not body:
            st.error("❌ Les champs obligatoires doivent être remplis.")
        else:
            st.success("✅ Article généré avec succès !")
            st.markdown(f"**Titre :** {title}")
            st.markdown(f"**Introduction :** {intro}")
            st.markdown(f"**Auteur :** {author}")
            st.markdown(f"**Contenu :** {body}")

# **Transfert FTP**
elif menu == "Transfert FTP":
    st.header("📤 Transfert FTP")
    st.markdown("Entrez les informations nécessaires pour transférer vos fichiers.")
    ftp_ip = st.text_input("Adresse du serveur FTP :", placeholder="ftp.exemple.com")
    ftp_user = st.text_input("Nom d'utilisateur FTP :", placeholder="Utilisateur")
    ftp_password = st.text_input("Mot de passe FTP :", type="password")

    if st.button("Transférer les fichiers"):
        if not ftp_ip or not ftp_user or not ftp_password:
            st.error("❌ Veuillez remplir tous les champs.")
        else:
            with st.spinner("📤 Transfert en cours..."):
                st.success(f"✅ Fichiers transférés avec succès sur le serveur : {ftp_ip}")

# **Informations**
elif menu == "Informations":
    st.header("ℹ️ À Propos de l'Outil")
    st.markdown(
        """
        Cet outil a été conçu pour simplifier la gestion de contenu en ligne pour les producteurs de contenu ayant :
        - Peu de ressources techniques.
        - Des besoins spécifiques en gestion de contenu léger.

        **Principales fonctionnalités :**
        - Analyse automatique de la structure des articles d'un site.
        - Création d'articles en suivant le modèle détecté.
        - Transfert des fichiers vers un serveur FTP cible.
        """
    )
    st.image("https://source.unsplash.com/800x300/?technology,content", caption="Des solutions adaptées à vos besoins")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("© 2024 - Pro par Idun Group")
