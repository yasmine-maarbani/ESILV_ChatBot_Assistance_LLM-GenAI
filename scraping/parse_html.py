from pathlib import Path
from typing import List

from bs4 import BeautifulSoup


def extract_main_text(html: str) -> str:
    """
    Extrait le texte principal d'une page HTML.
    Version simple : enlève scripts, styles, nav, footer, puis récupère le <body>.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Supprimer les balises non textuelles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Optionnel : supprimer les nav/footer
    for tag in soup.find_all(["nav", "footer"]):
        tag.decompose()

    body = soup.body or soup
    text = body.get_text(separator="\n")
    # Nettoyage simple
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def parse_html_file(path: Path) -> str:
    """Lit un fichier HTML et renvoie le texte principal extrait."""
    html = path.read_text(encoding="utf-8")
    return extract_main_text(html)


def parse_html_folder(input_dir: Path | str, output_dir: Path | str) -> List[Path]:
    """
    Parcourt un dossier de fichiers HTML et écrit les versions texte dans output_dir.
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_files: List[Path] = []

    for html_path in input_dir.glob("*.html"):
        text = parse_html_file(html_path)
        out_path = output_dir / (html_path.stem + ".txt")
        out_path.write_text(text, encoding="utf-8")
        output_files.append(out_path)

    return output_files
