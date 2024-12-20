import json
from tkinter import Tk, filedialog


# Liste des balises importantes
IMPORTANT_TAGS = {"header", "main", "article", "section", "div", "h1", "h2", "h3", "p", "img", "ul", "ol", "li"}

def generate_html_from_json(data):
    """
    Génère un article HTML basé sur la structure JSON uniquement.
    """
    def parse_element(element, depth=0):
        """
        Analyse récursivement une balise du JSON pour produire le HTML correspondant.
        """
        tag = element.get("tag", "div")
        styles = element.get("styles", {})
        children = element.get("children", [])
        style_attr = " ".join(f"{k}: {v};" for k, v in styles.items())
        indent = "  " * depth

        # Si la balise n'est pas importante, on l'ignore
        if tag not in IMPORTANT_TAGS:
            return ""

        # Générer l'ouverture de la balise avec les styles
        html = f'{indent}<{tag} style="{style_attr}">'

        # Simuler du contenu fictif si nécessaire
        if tag in {"h1", "h2", "h3"}:
            html += f"Titre fictif ({tag.upper()})"
        elif tag == "p":
            html += f"Paragraphe fictif de test ({tag.upper()})."
        elif tag == "img":
            html += f'<img src="https://via.placeholder.com/800x400" alt="Image fictive" style="{style_attr}"/>'
        elif tag == "ul":
            html += f"<li>Élément de liste fictif 1</li><li>Élément de liste fictif 2</li>"

        # Ajouter les enfants récursivement
        for child in children:
            html += "\n" + parse_element(child, depth + 1)

        # Fermer la balise si ce n'est pas une balise auto-fermante
        if tag not in ["img", "br", "hr", "input"]:
            html += f'\n{indent}</{tag}>'

        return html

    # Génération du HTML complet avec les balises et styles depuis JSON
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Article généré depuis JSON</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                line-height: 1.6;
                background-color: #f9f9f9;
            }}
            article {{
                max-width: 800px;
                margin: auto;
                padding: 20px;
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            h1, h2 {{
                color: #333;
            }}
            img {{
                max-width: 100%;
                height: auto;
                margin: 10px 0;
            }}
            ul {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 5px;
            }}
        </style>
    </head>
    <body>
        <article>
        {parse_element(data)}
        </article>
    </body>
    </html>
    """


def select_json_file():
    """Permet à l'utilisateur de sélectionner un fichier JSON."""
    Tk().withdraw()  # Masquer la fenêtre principale
    file_path = filedialog.askopenfilename(
        title="Sélectionnez un fichier JSON",
        filetypes=[("Fichiers JSON", "*.json")]
    )
    return file_path


# Étape 1 : Sélectionner un fichier JSON
print("Veuillez sélectionner un fichier JSON.")
json_file_path = select_json_file()

if not json_file_path:
    print("Aucun fichier sélectionné. Fin du programme.")
else:
    # Étape 2 : Charger le fichier JSON
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    # Étape 3 : Générer le HTML basé uniquement sur JSON
    html_content = generate_html_from_json(data)

    # Étape 4 : Sauvegarder le HTML généré
    output_file_path = json_file_path.replace(".json", ".html")
    with open(output_file_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

    print(f"Fichier HTML généré avec succès : {output_file_path}")
