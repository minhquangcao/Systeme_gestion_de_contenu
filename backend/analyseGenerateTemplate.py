import requests
from bs4 import BeautifulSoup
import cssutils
import json
import os
from datetime import datetime
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor


class WebScraper:
    IMPORTANT_TAGS = {
        "header", "main", "article", "section", "div", "h1", "h2", "h3", "p", "img", "ul", "ol", "li",
        "a", "span", "strong", "em", "blockquote", "code", "pre", "table", "tr", "th", "td", "form",
        "input", "button", "select", "textarea", "label", "footer", "aside", "figure", "figcaption",
        "video", "audio", "iframe", "canvas", "svg", "path", "circle", "rect", "polygon", "polyline",
        "ellipse", "line", "g", "defs", "symbol", "use", "text", "tspan", "textPath", "clipPath", "mask",
        "pattern", "linearGradient", "radialGradient", "stop", "title", "desc", "metadata", "defs",
        "style", "template"
    }

    def __init__(self, url):
        self.url = url
        self.base_url = "/".join(url.split("/")[:-1])
        self.soup = None
        self.css_rules = {}

    def fetch_page(self):
        """Télécharge la page HTML."""
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête HTTP : {e}")

    def fetch_global_styles(self):
        """Récupère les styles globaux (CSS) de la page."""
        styles = ""
        # Balises <style>
        for style_tag in self.soup.find_all("style"):
            styles += style_tag.string or ""

        # Liens CSS
        css_links = {
            urljoin(self.base_url, link_tag.get("href"))
            for link_tag in self.soup.find_all("link", rel="stylesheet")
            if link_tag.get("href")
        }

        # Télécharger les fichiers CSS
        def fetch_stylesheet(url):
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                if len(response.text) > 500000:
                    print(f"Fichier CSS trop volumineux ignoré : {url}")
                    return ""
                return response.text
            except requests.exceptions.RequestException as e:
                print(f"Erreur lors de la récupération de {url}: {e}")
                return ""

        with ThreadPoolExecutor(max_workers=5) as executor:
            css_contents = executor.map(fetch_stylesheet, css_links)

        for content in css_contents:
            styles += content

        return styles

    def parse_global_styles(self, styles):
        """Analyse les styles CSS globaux."""
        parser = cssutils.CSSParser()
        try:
            stylesheet = parser.parseString(styles)
            for rule in stylesheet:
                if rule.type == rule.STYLE_RULE:
                    self.css_rules[rule.selectorText] = {
                        prop.name: prop.value for prop in rule.style
                    }
        except Exception as e:
            print(f"Erreur lors de l'analyse des styles CSS : {e}")

    def get_structure_with_styles(self, element, parent_styles=None, tag_counters=None, max_occurrences=5):
        """Retourne une structure minimaliste avec styles."""
        if not element.name in self.IMPORTANT_TAGS:
            return None

        if tag_counters is None:
            tag_counters = {}

        tag_counters[element.name] = tag_counters.get(element.name, 0) + 1
        if tag_counters[element.name] > max_occurrences:
            return None

        parent_styles = parent_styles or {}
        global_styles = self.match_global_styles(element)
        inline_styles = self.get_inline_styles(element)

        combined_styles = {**parent_styles, **global_styles, **inline_styles}
        structure = {"tag": element.name, "styles": combined_styles, "children": []}

        for child in element.find_all(recursive=False):
            child_structure = self.get_structure_with_styles(child, combined_styles, tag_counters, max_occurrences)
            if child_structure:
                structure["children"].append(child_structure)

        if not structure["children"]:
            structure.pop("children", None)

        return structure

    def match_global_styles(self, element):
        """Associe les styles globaux à un élément."""
        matched_styles = {}
        tag_name = element.name
        if tag_name in self.css_rules:
            matched_styles.update(self.css_rules[tag_name])

        if element.has_attr("class"):
            for cls in element["class"]:
                class_selector = f".{cls}"
                if class_selector in self.css_rules:
                    matched_styles.update(self.css_rules[class_selector])

        if element.has_attr("id"):
            id_selector = f"#{element['id']}"
            if id_selector in self.css_rules:
                matched_styles.update(self.css_rules[id_selector])

        return matched_styles

    def get_inline_styles(self, element):
        """Extrait les styles inline."""
        inline_styles = {}
        if element.has_attr("style"):
            for style in element["style"].split(";"):
                if ":" in style:
                    key, value = style.split(":", 1)
                    inline_styles[key.strip()] = value.strip()
        return inline_styles

    def extract_and_save(self, output_dir="frontend/templates"):
        """Extrait la structure et sauvegarde dans un fichier JSON."""
        if not self.soup:
            print("La page n'a pas été téléchargée.")
            return

        styles = self.fetch_global_styles()
        self.parse_global_styles(styles)

        root_element = self.soup.find("main") or self.soup.body
        if not root_element:
            print("Aucun élément <main> ou <body> trouvé.")
            return

        structure = self.get_structure_with_styles(root_element)

        if structure:
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filepath = os.path.join(output_dir, f"structure_{timestamp}.json")
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(structure, file, indent=4, ensure_ascii=False)
            print(f"Structure sauvegardée dans {filepath}")
        else:
            print("Aucune structure extraite.")


# Exemple d'utilisation
if __name__ == "__main__":
    url = "https://www.zooplus.fr/magazine/poisson/plantes-daquarium/cryptocoryne"
    scraper = WebScraper(url)
    scraper.fetch_page()
    scraper.extract_and_save()
