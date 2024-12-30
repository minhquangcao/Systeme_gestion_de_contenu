import requests
from bs4 import BeautifulSoup
import cssutils
import json
import os
from datetime import datetime
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

IMPORTANT_TAGS = {"header", "main", "article", "section", "div", "h1", "h2", "h3", "p", "img", "ul", "ol", "li", 
                  "a", "span", "strong", "em", "blockquote", "code", "pre", "table", "tr", "th", "td", "form", 
                  "input", "button", "select", "textarea", "label", "nav", "footer", "aside", "figure", "figcaption"
                  , "video", "audio", "iframe", "canvas", "svg", "path", "circle", "rect", "polygon", "polyline",
                  "ellipse", "line", "g", "defs", "symbol", "use", "text", "tspan", "textPath", "clipPath", "mask",
                  "pattern", "linearGradient", "radialGradient", "stop", "a", "title", "desc", "metadata", "defs",
                  "style", "template"}

def fetch_global_styles(soup, base_url):
    """
    Récupère les styles globaux d'une page HTML (balises <style> et fichiers CSS liés),
    avec gestion des erreurs et optimisation des téléchargements.
    """
    styles = ""

    # Étape 1 : Récupérer les styles dans les balises <style>
    for style_tag in soup.find_all("style"):
        styles += style_tag.string or ""

    # Étape 2 : Identifier les fichiers CSS liés
    css_links = {
        urljoin(base_url, link_tag.get("href"))
        for link_tag in soup.find_all("link", rel="stylesheet")
        if link_tag.get("href")
    }

    # Étape 3 : Télécharger les fichiers CSS en parallèle
    def fetch_stylesheet(url):
        """Télécharge un fichier CSS avec gestion des erreurs et limite de taille."""
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            if len(response.text) > 500000:  # Limiter la taille des CSS à 500 Ko
                print(f"Fichier CSS trop volumineux ignoré : {url}")
                return ""
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération de {url}: {e}")
            return ""

    with ThreadPoolExecutor(max_workers=5) as executor:
        css_contents = executor.map(fetch_stylesheet, css_links)

    # Étape 4 : Ajouter les contenus CSS récupérés
    for content in css_contents:
        styles += content

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

def get_minimal_structure_with_styles(element, css_rules, seen_tags, parent_styles=None, tag_counters=None, max_occurrences=5):
    """
    Retourne une structure simplifiée et stylée d'un élément en évitant les doublons
    et limite le nombre d'instances incluses pour chaque type de balise.
    """
    # Initialiser le compteur pour les balises si nécessaire
    if tag_counters is None:
        tag_counters = {}

    # Vérifier si la balise est importante
    if element.name not in IMPORTANT_TAGS:
        return None  # Ignorer les balises non importantes

    # Initialiser ou incrémenter le compteur pour cette balise
    if element.name not in tag_counters:
        tag_counters[element.name] = 0
    tag_counters[element.name] += 1

    # Vérifier si la limite pour cette balise est atteinte
    if tag_counters[element.name] > max_occurrences:
        return None

    # Récupérer les styles complets pour l'élément
    parent_styles = parent_styles or {}
    element_styles = get_complete_styles(element, css_rules, parent_styles)

    # Ajouter la balise et ses styles au résultat
    structure = {
        "tag": element.name,
        "styles": element_styles,
        "children": []
    }

    # Parcourir les enfants directs
    for child in element.find_all(recursive=False):
        child_structure = get_minimal_structure_with_styles(
            child, css_rules, seen_tags, element_styles, tag_counters, max_occurrences
        )
        if child_structure:
            structure["children"].append(child_structure)

    # Si pas d'enfants pertinents, supprimer le champ "children"
    if not structure["children"]:
        structure.pop("children", None)

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
        tag_counters = {}
# Extraire la structure minimale avec une limite d'occurrences par balise
        minimal_structure = get_minimal_structure_with_styles(
            root_element, css_rules, seen_tags, tag_counters=tag_counters, max_occurrences=5
        )

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
        output_dir = "frontend/templates"
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
