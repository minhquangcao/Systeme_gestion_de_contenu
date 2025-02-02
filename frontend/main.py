import streamlit as st
from PIL import Image
from backend.ftp_transfer import FTPClient
from backend.analyseGenerateTemplate import WebScraper
import sys
import os
import logging
import json

# Ajouter le chemin racine du projet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
    ["Accueil", "Analyse de Site", "Structure de l'Article", "Création d'Articles", "Transfert FTP", "Informations"]
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
                # Exemple d'utilisation de la classe WebScraper
                scraper = WebScraper(url)
                logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                logging.info(f"Début de l'analyse pour l'URL : {url}")
                scraper.fetch_page()
                logging.info("Page HTML récupérée avec succès.")
                scraper.extract_and_save()
                logging.info("Modèles d'articles extraits")
                st.success("✅ Analyse terminée. Les modèles d'articles ont été extraits.")

# =========================
# **Structure de l'Article**
# =========================
elif menu == "Structure de l'Article":
    st.header("🗂️ Définir la Structure de l'Article")
    st.markdown("Choisissez d'utiliser une structure par défaut ou créez votre propre organisation.")

    # Choix entre structure par défaut ou personnalisée
    structure_mode = st.radio("Mode de définition de la structure :", 
                               ["Utiliser la structure par défaut", "Créer une structure personnalisée"])

    # -------------------------
    # Mode par défaut
    # -------------------------
    if structure_mode == "Utiliser la structure par défaut":
        st.subheader("Structure par défaut")
        st.markdown("Sélectionnez les sections classiques et personnalisez leur style et formatage. Une prévisualisation est affichée pour chaque section.")

        # Sections classiques avec options de sélection
        default_sections = {
            "Titre": True,
            "Résumé/Abstract": True,
            "Introduction": True,
            "Matériels et Méthodes": True,
            "Résultats": True,
            "Discussion": True,
            "Conclusion": True,
            "Références": True,
            "Annexes": False
        }
        selected_sections = {}
        for section, default in default_sections.items():
            selected_sections[section] = st.checkbox(f"Afficher la section **{section}**", value=default)

        # Pour chaque section sélectionnée, possibilité d'ajouter des options de style et de formatage
        default_section_configs = {}
        for section, selected in selected_sections.items():
            if selected:
                st.markdown(f"##### Options pour la section **{section}**")
                col1, col2 = st.columns(2)
                with col1:
                    font = st.selectbox(f"Police pour {section} :", 
                                        ["Arial", "Helvetica", "Times New Roman", "Courier New"],
                                        key=f"default_font_{section}")
                    font_size = st.slider(f"Taille du texte pour {section} :", 10, 50, 16, key=f"default_font_size_{section}")
                    alignment = st.selectbox(f"Alignement pour {section} :", 
                                             ["left", "center", "right"],
                                             key=f"default_align_{section}")
                with col2:
                    text_color = st.color_picker(f"Couleur du texte pour {section} :", "#000000", key=f"default_text_color_{section}")
                    background_color = st.color_picker(f"Couleur de fond pour {section} :", "#ffffff", key=f"default_bg_color_{section}")
                    # Options de formatage
                    col_format = st.columns(4)
                    bold = col_format[0].checkbox("Gras", value=False, key=f"default_bold_{section}")
                    italic = col_format[1].checkbox("Italique", value=False, key=f"default_italic_{section}")
                    underline = col_format[2].checkbox("Souligné", value=False, key=f"default_underline_{section}")
                    strikethrough = col_format[3].checkbox("Barré", value=False, key=f"default_strike_{section}")

                # On utilise un texte d'exemple pour la prévisualisation
                sample_text = f"Ceci est un exemple de contenu pour la section {section}."
                # Application du formatage sur le texte d'exemple
                if bold:
                    sample_text = f"<b>{sample_text}</b>"
                if italic:
                    sample_text = f"<i>{sample_text}</i>"
                if underline:
                    sample_text = f"<u>{sample_text}</u>"
                if strikethrough:
                    sample_text = f"<s>{sample_text}</s>"

                # Stocker la configuration
                default_section_configs[section] = {
                    "active": True,
                    "style": {
                        "font": font,
                        "font_size": font_size,
                        "alignment": alignment,
                        "text_color": text_color,
                        "background_color": background_color,
                        "formatting": {
                            "bold": bold,
                            "italic": italic,
                            "underline": underline,
                            "strikethrough": strikethrough
                        }
                    }
                }
                # Prévisualisation de la section
                style_str = (
                    f"font-family: {font}; "
                    f"font-size: {font_size}px; "
                    f"color: {text_color}; "
                    f"background-color: {background_color}; "
                    f"text-align: {alignment}; "
                    "padding: 10px; margin-bottom: 10px; border-radius: 5px;"
                )
                st.markdown(f"<h{min(2, 6)} style='margin-bottom:5px'>{section}</h{min(2, 6)}>", unsafe_allow_html=True)
                st.markdown(f"<div style='{style_str}'>{sample_text}</div>", unsafe_allow_html=True)

        # Bouton d'enregistrement pour la structure par défaut
        if st.button("Enregistrer la structure par défaut"):
            structure_config = {
                "mode": "default",
                "sections": default_section_configs
            }
            try:
                with open("article_structure.json", "w") as f:
                    json.dump(structure_config, f, indent=4)
                st.success("Structure par défaut et styles enregistrés avec succès.")
            except Exception as e:
                st.error(f"Erreur lors de l'enregistrement : {e}")

    # -------------------------
    # Mode personnalisé
    # -------------------------
    else:
        st.subheader("Structure personnalisée")
        # Initialisation de la liste des sections personnalisées dans la session
        if "custom_sections" not in st.session_state:
            st.session_state.custom_sections = []

        st.markdown("### Ajouter une nouvelle section avec options avancées")
        with st.form(key="add_custom_section_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                section_name = st.text_input("Nom de la section")
            with col2:
                section_level = st.number_input("Niveau hiérarchique (1 = principal, 2 = sous-section, etc.)", 
                                                min_value=1, max_value=5, value=1, step=1)
            
            st.markdown("#### Contenu de la section")
            section_content = st.text_area("Saisissez le contenu (Markdown ou HTML est supporté)", height=150)
            
            st.markdown("#### Options de formatage")
            col_format1, col_format2 = st.columns(2)
            with col_format1:
                bold = st.checkbox("Gras (Bold)")
                italic = st.checkbox("Italique (Italic)")
            with col_format2:
                underline = st.checkbox("Souligné (Underline)")
                strikethrough = st.checkbox("Barré (Strikethrough)")
            
            st.markdown("#### Personnalisation du style")
            col_style1, col_style2, col_style3 = st.columns(3)
            with col_style1:
                font = st.selectbox("Police", ["Arial", "Helvetica", "Times New Roman", "Courier New"])
                font_size = st.slider("Taille du texte", min_value=10, max_value=50, value=16)
            with col_style2:
                text_color = st.color_picker("Couleur du texte", "#000000")
                background_color = st.color_picker("Couleur de fond", "#ffffff")
            with col_style3:
                alignment = st.selectbox("Alignement", ["left", "center", "right"])
            
            submitted = st.form_submit_button("Ajouter la section")
            if submitted:
                if section_name.strip() == "":
                    st.error("Veuillez saisir un nom pour la section.")
                else:
                    new_section = {
                        "name": section_name,
                        "level": int(section_level),
                        "content": section_content,
                        "formatting": {
                            "bold": bold,
                            "italic": italic,
                            "underline": underline,
                            "strikethrough": strikethrough
                        },
                        "style": {
                            "font": font,
                            "font_size": font_size,
                            "text_color": text_color,
                            "background_color": background_color,
                            "alignment": alignment
                        }
                    }
                    st.session_state.custom_sections.append(new_section)
                    st.success(f"La section **{section_name}** a été ajoutée avec succès.")

        # Affichage et prévisualisation de l'article personnalisé
        if st.session_state.custom_sections:
            st.markdown("### 📑 Sections ajoutées")
            for idx, sec in enumerate(st.session_state.custom_sections):
                st.markdown(f"**{sec['name']}** (Niveau {sec['level']})")
                with st.expander("Voir les détails"):
                    st.json(sec, expanded=True)

            st.markdown("### 👀 Prévisualisation de l'article personnalisé")
            preview_html = ""
            for sec in st.session_state.custom_sections:
                style = sec["style"]
                formatting = sec["formatting"]
                style_str = (
                    f"font-family: {style['font']}; "
                    f"font-size: {style['font_size']}px; "
                    f"color: {style['text_color']}; "
                    f"background-color: {style['background_color']}; "
                    f"text-align: {style['alignment']}; "
                    "padding: 10px; margin-bottom: 10px; border-radius: 5px;"
                )
                content = sec["content"]
                if formatting["bold"]:
                    content = f"<b>{content}</b>"
                if formatting["italic"]:
                    content = f"<i>{content}</i>"
                if formatting["underline"]:
                    content = f"<u>{content}</u>"
                if formatting["strikethrough"]:
                    content = f"<s>{content}</s>"

                header_tag = f"h{min(sec['level'], 6)}"
                section_html = f"<{header_tag}>{sec['name']}</{header_tag}>"
                section_html += f"<div style='{style_str}'>{content}</div>"
                preview_html += section_html
            st.markdown(preview_html, unsafe_allow_html=True)

            if st.button("Enregistrer la structure personnalisée"):
                structure_config = {
                    "mode": "custom",
                    "sections": st.session_state.custom_sections
                }
                try:
                    with open("article_structure.json", "w") as f:
                        json.dump(structure_config, f, indent=4)
                    st.success("Structure personnalisée et styles enregistrés avec succès.")
                except Exception as e:
                    st.error(f"Erreur lors de l'enregistrement : {e}")

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
                ftp_client = FTPClient(ftp_ip, ftp_user, ftp_password)
                ftp_client.connect()
                # Exemple de fichier à transférer, adapter selon vos besoins
                files_and_directories = {
                    "backend/test.txt": "test"
                }
                ftp_client.transfer_files(files_and_directories)
                ftp_client.disconnect()
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

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("© 2024 Outil Pro de Gestion d'Articles")
