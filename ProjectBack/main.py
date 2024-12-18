import requests
from bs4 import BeautifulSoup
import json

# Balises importantes pour lesquelles on extrait la structure et les styles
IMPORTANT_TAGS = {"header", "main", "article", "section", "div", "h1", "h2", "h3", "p", "img", "ul", "ol", "li"}

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

        # Fonction pour extraire les styles pertinents
        def get_computed_styles(element):
            styles = {}
            
            # Récupération des styles inlines
            if element.has_attr("style"):
                inline_styles = element["style"].split(";")
                for style in inline_styles:
                    if ":" in style:
                        key, value = style.split(":", 1)
                        styles[key.strip()] = value.strip()

            # Filtrage des styles pertinents
            filtered_styles = {
                "color": styles.get("color"),
                "font-size": styles.get("font-size"),
                "font-family": styles.get("font-family"),
                "font-weight": styles.get("font-weight"),
                "font-style": styles.get("font-style"),
                "background-color": styles.get("background-color"),
                "text-align": styles.get("text-align")
            }

            # Suppression des entrées non définies
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
                    # Supprimer les doublons (exemple : <div><div><div>)
                    if len(structure["children"]) == 0 or structure["children"][-1]["tag"] != child_structure["tag"]:
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
