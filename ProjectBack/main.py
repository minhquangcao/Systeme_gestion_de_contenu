import requests
from bs4 import BeautifulSoup
import cssutils
import json

# Balises importantes pour lesquelles on extrait la structure et les styles
IMPORTANT_TAGS = {"header", "main", "article", "section", "div", "h1", "h2", "h3", "p", "img", "ul", "ol", "li"}

def fetch_global_styles(soup, base_url):
    """
    Récupère tous les styles globaux (internes et externes) de la page.
    """
    styles = ""

    # Récupérer les styles dans les balises <style>
    for style_tag in soup.find_all("style"):
        styles += style_tag.string or ""

    # Récupérer les fichiers CSS liés
    for link_tag in soup.find_all("link", rel="stylesheet"):
        href = link_tag.get("href")
        if href:
            # Résoudre l'URL absolue
            stylesheet_url = href if href.startswith("http") else f"{base_url}/{href}"
            try:
                response = requests.get(stylesheet_url)
                response.raise_for_status()
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
    stylesheet = parser.parseString(styles)

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

def extract_structure_and_styles(url):
    """
    Récupère la structure simplifiée et les styles pertinents d'une page web.
    """
    try:
        # Récupération de la page web
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text

        # Analyse HTML avec BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        base_url = "/".join(url.split("/")[:-1])  # Base URL pour les fichiers CSS relatifs

        # Récupérer les styles globaux
        global_styles = fetch_global_styles(soup, base_url)
        css_rules = parse_global_styles(global_styles)

        # Fonction pour extraire les styles pertinents
        def get_computed_styles(element):
            inline_styles = {}
            
            # Récupération des styles inline
            if element.has_attr("style"):
                for style in element["style"].split(";"):
                    if ":" in style:
                        key, value = style.split(":", 1)
                        inline_styles[key.strip()] = value.strip()

            # Récupération des styles globaux
            global_styles = match_global_styles(element, css_rules)

            # Fusion des styles inline et globaux
            combined_styles = {**global_styles, **inline_styles}

            # Filtrage des styles pertinents
            filtered_styles = {
                "color": combined_styles.get("color"),
                "font-size": combined_styles.get("font-size"),
                "font-family": combined_styles.get("font-family"),
                "font-weight": combined_styles.get("font-weight"),
                "font-style": combined_styles.get("font-style"),
                "background-color": combined_styles.get("background-color"),
                "text-align": combined_styles.get("text-align")
            }

            return {k: v for k, v in filtered_styles.items() if v}

        # Fonction récursive pour construire la hiérarchie avec styles
        def parse_element_with_styles(element):
            if element.name not in IMPORTANT_TAGS:
                return None  # Ignorer les balises non importantes

            # Construction de la structure avec styles
            structure = {
                "tag": element.name,
                "styles": get_computed_styles(element),
                "children": []
            }

            # Ajouter les enfants pour les balises importantes
            for child in element.find_all(recursive=False):
                child_structure = parse_element_with_styles(child)
                if child_structure:
                    structure["children"].append(child_structure)

            # Si pas d'enfants pertinents, supprimer le champ "children"
            if not structure["children"]:
                structure.pop("children", None)

            return structure

        # Démarrer à partir de la balise <main> ou <body>
        root_element = soup.find("main") or soup.body
        if not root_element:
            print("La page ne contient pas de balise <main> ou <body>.")
            return None

        # Analyse de la structure avec styles
        styled_structure = parse_element_with_styles(root_element)

        # Conversion en JSON
        json_structure = json.dumps(styled_structure, indent=4, ensure_ascii=False)
        return json_structure

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête HTTP : {e}")
        return None
    except Exception as e:
        print(f"Erreur : {e}")
        return None


if __name__ == "__main__":
    # URL de la page à scraper
    url = input("Entrez l'URL de la page à scraper : ")
    result = extract_structure_and_styles(url)
    if result:
        print("Structure avec styles en JSON :")
        print(result)

        # Sauvegarde dans un fichier JSON
        with open("styled_structure.json", "w", encoding="utf-8") as file:
            file.write(result)
        print("La structure avec styles a été sauvegardée dans 'styled_structure.json'.")
