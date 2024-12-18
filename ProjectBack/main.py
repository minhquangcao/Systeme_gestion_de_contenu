import requests
from bs4 import BeautifulSoup
import cssutils
import json
import os
from datetime import datetime

IMPORTANT_TAGS = {"header", "main", "article", "section", "div", "h1", "h2", "h3", "p", "img", "ul", "ol", "li"}

def fetch_global_styles(soup, base_url):
    """
    Récupère les styles globaux de la page, en tenant compte des erreurs et de la taille des CSS.
    """
    styles = ""

    # Récupérer les styles dans les balises <style>
    for style_tag in soup.find_all("style"):
        styles += style_tag.string or ""

    # Récupérer les fichiers CSS liés
    for link_tag in soup.find_all("link", rel="stylesheet"):
        href = link_tag.get("href")
        if href:
            stylesheet_url = href if href.startswith("http") else f"{base_url}/{href}"
            try:
                response = requests.get(stylesheet_url, timeout=5)  # Timeout pour éviter les blocages
                response.raise_for_status()
                if len(response.text) > 500000:  # Limiter la taille des CSS traités (500 Ko ici)
                    print(f"Fichier CSS trop volumineux ignoré : {stylesheet_url}")
                    continue
                styles += response.text
            except requests.exceptions.RequestException as e:
                print(f"Erreur lors de la récupération de {stylesheet_url}: {e}")

    return styles

def parse_global_styles(styles):
    """
    Analyse les styles CSS globaux et retourne un dictionnaire associant les sélecteurs à leurs styles.
    """
    css_rules = {}
    parser = cssutils.CSSParser()
    try:
        stylesheet = parser.parseString(styles)
    except Exception as e:
        print(f"Erreur lors de l'analyse des styles CSS : {e}")
        return {}

    for rule in stylesheet:
        if rule.type == rule.STYLE_RULE:
            css_rules[rule.selectorText] = {prop.name: prop.value for prop in rule.style}

    return css_rules

def match_global_styles(element, css_rules):
    """
    Associe les styles globaux à un élément en fonction de ses classes, ID et balises.
    """
    matched_styles = {}

    # Associer les styles par balise
    tag_name = element.name
    if tag_name in css_rules:
        matched_styles.update(css_rules[tag_name])

    # Associer les styles par classe
    if element.has_attr("class"):
        for cls in element["class"]:
            class_selector = f".{cls}"
            if class_selector in css_rules:
                matched_styles.update(css_rules[class_selector])

    # Associer les styles par ID
    if element.has_attr("id"):
        id_selector = f"#{element['id']}"
        if id_selector in css_rules:
            matched_styles.update(css_rules[id_selector])

    return matched_styles

def get_complete_styles(element, css_rules, parent_styles):
    """
    Combine les styles globaux, inline et hérités pour un élément.
    """
    # Récupérer les styles globaux et inline
    global_styles = match_global_styles(element, css_rules)
    inline_styles = {}
    if element.has_attr("style"):
        for style in element["style"].split(";"):
            if ":" in style:
                key, value = style.split(":", 1)
                inline_styles[key.strip()] = value.strip()

    # Fusionner les styles
    combined_styles = {**parent_styles, **global_styles, **inline_styles}

    return combined_styles  # Garder tous les styles disponibles

def get_minimal_structure_with_styles(element, css_rules, seen_tags, parent_styles=None):
    """
    Retourne une structure simplifiée et stylée d'un élément en évitant les doublons
    et sans inclure de contenu textuel.
    """
    if element.name not in IMPORTANT_TAGS or element.name in seen_tags:
        return None  # Ignorer les balises déjà vues ou non importantes

    parent_styles = parent_styles or {}
    
    # Récupérer les styles complets pour l'élément
    element_styles = get_complete_styles(element, css_rules, parent_styles)

    # Ajouter la balise et ses styles au résultat
    structure = {
        "tag": element.name,
        "styles": element_styles,
        "children": []
    }

    # Parcourir les enfants directs
    for child in element.find_all(recursive=False):
        child_structure = get_minimal_structure_with_styles(child, css_rules, seen_tags, element_styles)
        if child_structure:
            structure["children"].append(child_structure)

    # Si pas d'enfants pertinents, supprimer le champ "children"
    if not structure["children"]:
        structure.pop("children", None)

    # Marquer la balise comme vue
    seen_tags.add(element.name)

    return structure

def extract_structure_and_styles(url):
    """
    Récupère la structure simplifiée et les styles pertinents d'une page web.
    """
    try:
        # Récupération de la page web
        response = requests.get(url, timeout=10)  # Timeout pour éviter les blocages
        response.raise_for_status()
        html_content = response.text

        # Analyse HTML avec BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        base_url = "/".join(url.split("/")[:-1])

        # Récupérer les styles globaux
        global_styles = fetch_global_styles(soup, base_url)
        css_rules = parse_global_styles(global_styles)

        # Démarrer à partir de la balise <main> ou <body>
        root_element = soup.find("main") or soup.body
        if not root_element:
            print("La page ne contient pas de balise <main> ou <body>.")
            return None

        # Initialiser l'ensemble des balises vues
        seen_tags = set()

        # Extraire la structure minimale
        minimal_structure = get_minimal_structure_with_styles(root_element, css_rules, seen_tags)

        # Conversion en JSON
        return json.dumps(minimal_structure, indent=4, ensure_ascii=False)

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête HTTP : {e}")
        return None
    except Exception as e:
        print(f"Erreur : {e}")
        return None

if __name__ == "__main__":
    url = input("Entrez l'URL de la page à scraper : ")
    result = extract_structure_and_styles(url)
    if result:
        print("Structure avec styles minimalistes en JSON :")
        print(result)
        # Créer le dossier s'il n'existe pas
        output_dir = "projectGUI/templates"
        os.makedirs(output_dir, exist_ok=True)

        # Générer un nom de fichier unique basé sur la date et l'heure
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"minimal_styled_structure_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        # Sauvegarder le fichier
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(result)
        print(f"La structure a été sauvegardée dans '{filepath}'.")
        with open("minimal_styled_structure.json", "w", encoding="utf-8") as file:
            file.write(result)
        print("La structure a été sauvegardée dans 'minimal_styled_structure.json'.")
    else:
        print("Aucun fichier n'a été créé en raison d'une erreur.")
