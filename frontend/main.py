import streamlit as st
from PIL import Image
import sys
import os
import logging
import json
import platform
from dotenv import load_dotenv
import base64
load_dotenv()
FILE_CONFIG = "frontend/config/config.json"

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from backend.ftp_transfer import FTPClient
from backend.analyseGenerateTemplate import WebScraper

# Configuration de la page
st.set_page_config(
    page_title="Outil GUI Analyse Génération et de Transfert automatique articles web",
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
st.markdown('<div class="main-title">🌐 Outil Gestion d\'Articles</div>', unsafe_allow_html=True)

# Menu de navigation dans la barre latérale
st.sidebar.title("📂 Menu de Navigation")
menu = st.sidebar.radio(
    "Choisissez une section :",
    ["Analyser la structure d'un Site Web", "Créez votre structure de l'Article", "Remplissez votre Article", "Transfert FTP","Informations"]
)


# **Analyse de site web**
if menu == "Analyser la structure d'un Site Web":
    st.header("🌐 Analyser la structure d'un Site Web")
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
elif menu == "Créez votre structure de l'Article":
    st.header("🗂️ Définir la Structure de l'Article par Défault")
    st.markdown("Choisissez d'utiliser une structure classique ou créez votre propre organisation.")

    # Choix entre structure par défaut ou personnalisée
    structure_mode = st.radio("Mode de définition de la structure :",
                               ["Utiliser la structure classique", "Créer une structure personnalisée"])

    # -------------------------
    # Mode par défaut
    # -------------------------
    if structure_mode == "Utiliser la structure classique":
        st.subheader("Structure classique")
        st.markdown("Sélectionnez les sections classiques et personnalisez leur style et formatage. Une prévisualisation est affichée pour chaque section.")

        # Sections classiques avec options de sélection
        default_sections = {
            "Titre": True,
            "Résumé/Abstract": True,
            "Introduction": True,
            "Matériels et Méthodes": False,
            "Résultats": True,
            "Discussion": False,
            "Conclusion": True,
            "Références": False,
            "Annexes": False
        }
        selected_sections = {}
        for section, default in default_sections.items():
            selected_sections[section] = st.checkbox(f"Afficher la section **{section}**", value=default)

        # Pour chaque section sélectionnée, possibilité d'ajouter des options de style, de formatage et d'indiquer l'inclusion d'un média
        default_section_configs = {}
        for section, selected in selected_sections.items():
            if selected:
                st.markdown(f"##### Options pour la section **{section}**")
                col1, col2 = st.columns(2)
                with col1:
                    font = st.selectbox(f"Police pour {section} :", ["Arial", "Helvetica", "Times New Roman", "Courier New"],
                                        key=f"default_font_{section}")
                    font_size = st.slider(f"Taille du texte pour {section} :", 10, 50, 16, key=f"default_font_size_{section}")
                    alignment = st.selectbox(f"Alignement pour {section} :", ["left", "center", "right"],
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

                # Option pour indiquer l'inclusion d'un média
                include_media = st.checkbox("Inclure un média (image, vidéo ou PDF) ?", key=f"include_media_{section}")
                media_type = None
                if include_media:
                    media_type = st.selectbox("Type de média :", ["Image", "Vidéo", "PDF"], key=f"media_type_{section}")

                # Prévisualisation d'exemple
                sample_text = f"Ceci est un exemple de contenu pour la section {section}."
                if bold:
                    sample_text = f"<b>{sample_text}</b>"
                if italic:
                    sample_text = f"<i>{sample_text}</i>"
                if underline:
                    sample_text = f"<u>{sample_text}</u>"
                if strikethrough:
                    sample_text = f"<s>{sample_text}</s>"

                # Enregistrement de la configuration (on enregistre le type de média s'il est sélectionné)
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
                    },
                    "media": {"included": include_media, "type": media_type} if include_media else None
                }
                style_str = (
                    f"font-family: {font}; "
                    f"font-size: {font_size}px; "
                    f"color: {text_color}; "
                    f"background-color: {background_color}; "
                    f"text-align: {alignment}; "
                    "padding: 10px; margin-bottom: 10px; border-radius: 5px;"
                )
                st.markdown(f"<h{min(2,6)} style='margin-bottom:5px'>{section}</h{min(2,6)}>", unsafe_allow_html=True)
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

            st.markdown("#### Indiquer l'inclusion d'un média (image, vidéo ou PDF)")
            include_media = st.checkbox("Inclure un média ?", key="custom_include_media")
            media_type = None
            if include_media:
                media_type = st.selectbox("Type de média :", ["Image", "Vidéo", "PDF"], key="custom_media_type")

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
                        },
                        "media": {"included": include_media, "type": media_type} if include_media else None
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
                if sec.get("media"):
                    section_html += f"<p><em>Média à inclure : {sec['media']['type']}</em></p>"
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
elif menu == "Remplissez votre Article":
    st.header("📝 Création d'Articles")
    st.markdown("Ici, vous pouvez créer et éditer votre article en remplissant tous les champs requis.")

    # Choix du mode de création de l'article
    creation_mode = st.radio("Sélectionnez le mode de création :",
                              ["Utiliser une structure que vous avez créée", "Utiliser une structure extraite d'un site web"])

    # Dossier de sauvegarde des articles générés
    output_folder = "generated_articles"
    if not os.path.exists(output_folder):
        st.write(f"Log : Création du dossier {output_folder}")
        os.makedirs(output_folder)

    # ---------------------------
    # Mode : Utiliser une structure que vous avez créée
    # ---------------------------
    if creation_mode == "Utiliser une structure que vous avez créée":
        st.subheader("Création d'article via la structure que vous avez créée")
        try:
            with open("article_structure.json", "r", encoding="utf-8") as file:
                structure_file = json.load(file)
            st.write("Fichier JSON chargé avec succès :", structure_file)
        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier JSON : {e}")
            structure_file = None

        if structure_file is not None:
            try:
                structure_data = structure_file
                mode = structure_data.get("mode")
                if mode not in ["default", "custom"]:
                    st.error("Le fichier chargé ne correspond pas à une structure d'article valide.")
                else:
                    st.markdown("### Remplissez le contenu pour chaque section")
                    article_contents = {}
                    allowed_types = ["png", "jpg", "jpeg", "gif", "mp4", "mov", "pdf"]
                    # Mode DEFAULT : sections stockées dans un dictionnaire
                    if mode == "default":
                        sections = structure_data.get("sections", {})
                        for section, conf in sections.items():
                            if conf.get("active"):
                                # Option pour afficher le titre dans le HTML final
                                include_title = st.checkbox(f"Afficher le titre '{section}' dans le HTML ?", value=True, key=f"title_{section}")
                                st.markdown(f"**Section : {section}**")
                                content = st.text_area(f"Contenu pour la section '{section}'",
                                                        key=f"content_default_{section}", height=150)
                                # Affichage dans l'interface de la config du média
                                if conf.get("media"):
                                    st.markdown(f"Média attaché dans la structure : **{conf.get('media')}**")
                                # Widget d'upload
                                media_uploaded = st.file_uploader(
                                    f"Uploader un média pour la section '{section}' (optionnel)",
                                    type=allowed_types,
                                    key=f"media_default_{section}"
                                )
                                # Vérification du type en fonction du JSON (si défini)
                                expected_type = None
                                if isinstance(conf.get("media"), dict):
                                    expected_type = conf.get("media").get("type")
                                if media_uploaded is not None:
                                    ext = media_uploaded.name.split('.')[-1].lower()
                                    if expected_type:
                                        if expected_type.lower() == "image":
                                            valid_extensions = ["png", "jpg", "jpeg", "gif"]
                                        elif expected_type.lower() == "vidéo":
                                            valid_extensions = ["mp4", "mov"]
                                        elif expected_type.lower() == "pdf":
                                            valid_extensions = ["pdf"]
                                        else:
                                            valid_extensions = allowed_types
                                        if ext not in valid_extensions:
                                            st.error(f"Le type de média uploadé ne correspond pas à la section '{section}' (attendu: {expected_type}, fourni: {ext}).")
                                            media_uploaded = None
                                # Si aucun fichier n'est uploadé, on garde le média défini dans la structure (s'il existe)
                                media = media_uploaded if media_uploaded is not None else conf.get("media")
                                article_contents[section] = {
                                    "content": content,
                                    "style": conf.get("style", {}),
                                    "formatting": conf.get("style", {}).get("formatting", {}),
                                    "media": media,
                                    "include_title": include_title
                                }
                    # Mode CUSTOM : sections stockées dans une liste
                    else:
                        sections = structure_data.get("sections", [])
                        for idx, sec in enumerate(sections):
                            section_title = sec.get("name", f"Section {idx+1}")
                            include_title = st.checkbox(f"Afficher le titre '{section_title}' dans le HTML ?", value=True, key=f"title_custom_{idx}")
                            st.markdown(f"**Section : {section_title}**")
                            content = st.text_area(f"Contenu pour la section '{section_title}'",
                                                   key=f"content_custom_{idx}", height=150)
                            if sec.get("media"):
                                st.markdown(f"Média attaché dans la structure : **{sec.get('media')}**")
                            media_uploaded = st.file_uploader(
                                f"Uploader un média pour la section '{section_title}' (optionnel)",
                                type=allowed_types,
                                key=f"media_custom_{idx}"
                            )
                            expected_type = None
                            if isinstance(sec.get("media"), dict):
                                expected_type = sec.get("media").get("type")
                            if media_uploaded is not None:
                                ext = media_uploaded.name.split('.')[-1].lower()
                                if expected_type:
                                    if expected_type.lower() == "image":
                                        valid_extensions = ["png", "jpg", "jpeg", "gif"]
                                    elif expected_type.lower() == "vidéo":
                                        valid_extensions = ["mp4", "mov"]
                                    elif expected_type.lower() == "pdf":
                                        valid_extensions = ["pdf"]
                                    else:
                                        valid_extensions = allowed_types
                                    if ext not in valid_extensions:
                                        st.error(f"Le type de média uploadé ne correspond pas à la section '{section_title}' (attendu: {expected_type}, fourni: {ext}).")
                                        media_uploaded = None
                            media = media_uploaded if media_uploaded is not None else sec.get("media")
                            article_contents[idx] = {
                                "name": section_title,
                                "content": content,
                                "style": sec.get("style", {}),
                                "formatting": sec.get("formatting", {}),
                                "media": media,
                                "include_title": include_title
                            }
                    # Bouton de génération de l'article
                    if st.button("Générer l'article (structure d'article)"):
                        # Vérifier que tous les champs obligatoires sont remplis
                        if mode == "default":
                            missing = [sec for sec, data in article_contents.items() if data["content"].strip() == ""]
                        else:
                            missing = [data["name"] for data in article_contents.values() if data["content"].strip() == ""]
                        if missing:
                            st.error(f"Les champs suivants sont manquants : {', '.join(missing)}")
                        else:
                            final_article_html = ""

                            # Fonction pour sauvegarder le fichier uploadé dans un dossier spécifique et retourner le chemin
                            def save_media_file(media_obj, allowed_types, destination_folder="./generated_articles/uploaded_media"):
                                if not hasattr(media_obj, "read"):
                                    return None
                                media_obj.seek(0)
                                ext = media_obj.name.split('.')[-1].lower() if hasattr(media_obj, "name") else ""
                                if ext not in allowed_types:
                                    st.error(f"Fichier non autorisé : .{ext} n'est pas accepté.")
                                    return None
                                if not os.path.exists(destination_folder):
                                    os.makedirs(destination_folder)
                                # On utilise le nom d'origine pour le fichier (vous pouvez ajouter un timestamp pour éviter les collisions)
                    
                                file_path = os.path.join(destination_folder, media_obj.name)
                                try:
                                    with open(file_path, "wb") as f:
                                        media_obj.seek(0)
                                        f.write(media_obj.read())
                                    if os.path.exists(file_path):
                                        st.write(f"Log : Fichier '{media_obj.name}' sauvegardé dans '{destination_folder}'.")
                                        return file_path
                                    else:
                                        st.error("Erreur lors de la sauvegarde du fichier.")
                                        return None
                                except Exception as e:
                                    st.error(f"Erreur lors de la sauvegarde du fichier : {e}")
                                    return None

                            # Fonction pour générer le HTML à partir du chemin du fichier
                            def generate_media_html(media_obj):
                                # Si c'est un fichier uploadé, on le sauvegarde et on récupère son chemin
                                if hasattr(media_obj, "read"):
                                    file_path = save_media_file(media_obj, allowed_types)
                                    if not file_path:
                                        return "<p>Erreur lors de la sauvegarde du fichier.</p>"
                                    ext = file_path.split('.')[-1].lower()
                                # Si c'est déjà un chemin (string)
                                elif isinstance(media_obj, str):
                                    file_path = media_obj
                                    ext = file_path.split('.')[-1].lower()
                                else:
                                    return ""
                                
                                
                                 # Nom de fichier seulement (ex : "MTV.pdf")
                                filename = os.path.basename(file_path)

                                # Depuis le dossier ./generated_articles, le chemin RELATIF vers uploaded_media est :
                                # "./uploaded_media/<filename>"
                                # (car physically : ./generated_articles/uploaded_media/<filename>)
                                relative_path_for_html = f"./uploaded_media/{filename}"

                                if ext in ["png", "jpg", "jpeg", "gif"]:
                                    return f"<img src='{relative_path_for_html}' style='max-width:100%;'/>"
                                elif ext == "pdf":
                                    return f"<embed src='{relative_path_for_html}' width='100%' height='600px' type='application/pdf' />"
                                else:
                                    return "<p>Type de fichier non supporté.</p>"
                                
                                

                            # Assemblage du HTML final selon le mode
                            if mode == "default":
                                for section, data in article_contents.items():
                                    style = data.get("style", {})
                                    formatting = data.get("formatting", {})
                                    font = style.get("font", "Arial")
                                    font_size = style.get("font_size", 16)
                                    alignment = style.get("alignment", "left")
                                    text_color = style.get("text_color", "#000000")
                                    background_color = style.get("background_color", "#ffffff")
                                    style_str = (
                                        f"font-family: {font}; "
                                        f"font-size: {font_size}px; "
                                        f"color: {text_color}; "
                                        f"background-color: {background_color}; "
                                        f"text-align: {alignment}; "
                                        "padding: 10px; margin-bottom: 10px; border-radius: 5px;"
                                    )
                                    content = data["content"]
                                    if formatting.get("bold"):
                                        content = f"<b>{content}</b>"
                                    if formatting.get("italic"):
                                        content = f"<i>{content}</i>"
                                    if formatting.get("underline"):
                                        content = f"<u>{content}</u>"
                                    if formatting.get("strikethrough"):
                                        content = f"<s>{content}</s>"
                                    section_html = ""
                                    if data.get("include_title", True):
                                        section_html += f"<h2>{section}</h2>"
                                    section_html += f"<div style='{style_str}'>{content}</div>"
                                    media = data.get("media")
                                    if media:
                                        section_html += generate_media_html(media)
                                    final_article_html += section_html
                            else:  # mode custom
                                for idx, data in article_contents.items():
                                    style = data.get("style", {})
                                    formatting = data.get("formatting", {})
                                    font = style.get("font", "Arial")
                                    font_size = style.get("font_size", 16)
                                    alignment = style.get("alignment", "left")
                                    text_color = style.get("text_color", "#000000")
                                    background_color = style.get("background_color", "#ffffff")
                                    style_str = (
                                        f"font-family: {font}; "
                                        f"font-size: {font_size}px; "
                                        f"color: {text_color}; "
                                        f"background-color: {background_color}; "
                                        f"text-align: {alignment}; "
                                        "padding: 10px; margin-bottom: 10px; border-radius: 5px;"
                                    )
                                    content = data["content"]
                                    if formatting.get("bold"):
                                        content = f"<b>{content}</b>"
                                    if formatting.get("italic"):
                                        content = f"<i>{content}</i>"
                                    if formatting.get("underline"):
                                        content = f"<u>{content}</u>"
                                    if formatting.get("strikethrough"):
                                        content = f"<s>{content}</s>"
                                    section_html = ""
                                    if data.get("include_title", True):
                                        section_html += f"<h2>{data.get('name', f'Section {idx+1}')}</h2>"
                                    section_html += f"<div style='{style_str}'>{content}</div>"
                                    media = data.get("media")
                                    if media:
                                        section_html += generate_media_html(media)
                                    final_article_html += section_html

                            st.markdown("### Prévisualisation de l'article final")
                            st.markdown(final_article_html, unsafe_allow_html=True)
                            if not final_article_html.strip():
                                st.error("Erreur : L'article généré est vide !")
                            else:
                                st.write("Log : Article généré avec succès.")
                                download_filename = "final_article_default.html" if mode == "default" else "final_article_custom.html"
                                try:
                                    st.download_button(
                                        label="Télécharger le fichier",
                                        data=final_article_html.encode("utf-8"),
                                        file_name=download_filename,
                                        mime="text/html"
                                    )
                                    st.success("Téléchargement prêt !")
                                except Exception as e:
                                    st.error(f"Erreur lors du téléchargement : {e}")
                                    st.write(f"Log : Exception - {e}")
                                output_filename = "final_article_default.html" if mode == "default" else "final_article_custom.html"
                                output_path = os.path.join(output_folder, output_filename)
                                try:
                                    with open(output_path, "w", encoding="utf-8") as f:
                                        f.write(final_article_html)
                                    st.success(f"Article final enregistré dans '{output_path}'.")
                                except Exception as e:
                                    st.error(f"Erreur lors de l'enregistrement : {e}")
                                    st.write(f"Log : Exception - {e}")
            except Exception as e:
                st.error(f"Erreur lors du chargement du fichier JSON : {e}")
                st.write(f"Log : Exception lors du chargement du JSON - {e}")
        else:
            st.info("Veuillez charger votre fichier JSON de structure d'article.")

    # ---------------------------
    # Mode : Utiliser la structure d'analyse
    # ---------------------------
    else:
        st.subheader("Création d'article via une structure extraite d'un site web")
        st.write("pas encore implémenté")

# **Transfert FTP**
if menu == "Transfert FTP":
    st.header("📤 Transfert FTP")
    st.markdown("Entrez les informations nécessaires pour transférer vos fichiers.")

    ftp_ip = st.text_input("Adresse du serveur FTP :", placeholder="ftp.exemple.com")
    ftp_user = st.text_input("Nom d'utilisateur FTP :", placeholder="Utilisateur")
    ftp_password = st.text_input("Mot de passe FTP :", type="password")
    ftp_directory = st.text_input("Répertoire FTP :", placeholder="")

    if st.button("Se connecter"):
        if not ftp_ip or not ftp_user or not ftp_password:
            st.error("❌ Veuillez remplir tous les champs.")
        else:
            try:
                with open(FILE_CONFIG, "r", encoding="utf-8") as f:
                    data = json.load(f)

                data["USERNAME_FTP"] = ftp_user
                data["PASSWORD_FTP"] = ftp_password
                data["SERVEUR_FTP"] = ftp_ip
                data["DIRECTORY_URL"] = f"htdocs/{ftp_directory}" if ftp_directory else "test"

                with open(FILE_CONFIG, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)

                st.success("✅ Configuration enregistrée !")
            except Exception as e:
                st.error(f"❌ Une erreur est survenue : {e}")

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
