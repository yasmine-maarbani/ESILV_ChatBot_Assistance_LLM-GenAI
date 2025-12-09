import os
from pathlib import Path
from typing import Iterable, List

import requests
from .parse_html import parse_html_folder


DEFAULT_BASE_URL = "https://www.esilv.fr"
DEFAULT_PAGES = [
    "/formations/",
    "/admissions/",
    "/entreprises/",
]


def fetch_page(url: str, timeout: int = 10) -> str:
    """Télécharge le contenu HTML brut d'une page."""
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def save_raw_html(content: str, output_path: Path) -> None:
    """Enregistre le contenu HTML dans un fichier."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def scrape_esilv_pages(
    base_url: str = DEFAULT_BASE_URL,
    pages: Iterable[str] = DEFAULT_PAGES,
    output_dir: Path | str = Path("data/raw/esilv_html"),
) -> List[Path]:
    """
    Télécharge une liste de pages ESILV et les sauvegarde dans data/raw/esilv_html.

    Returns
    -------
    List[Path] : liste des chemins des fichiers HTML sauvegardés.
    """
    output_dir = Path(output_dir)
    downloaded_files: List[Path] = []

    for rel_path in pages:
        url = base_url.rstrip("/") + rel_path
        safe_name = rel_path.strip("/").replace("/", "_") or "index"
        out_file = output_dir / f"{safe_name}.html"

        print(f"[scraper_esilv] Fetch {url} -> {out_file}")
        html = fetch_page(url)
        save_raw_html(html, out_file)
        downloaded_files.append(out_file)

    return downloaded_files


if __name__ == "__main__":

    # TODO: change to definitive path from config
    raw_html_dir = Path("data/raw/test_scraper_html")
    parsed_text_dir = Path("data/docs")

    print("[1] Téléchargement des pages HTML…")
    downloaded = scrape_esilv_pages(
        pages=DEFAULT_PAGES,
        output_dir=raw_html_dir,
    )
    print(f"   -> {len(downloaded)} pages téléchargées")
    for f in downloaded:
        print(f"     - {f}")

    print("\n[2] Extraction du texte depuis les fichiers HTML…")
    extracted = parse_html_folder(
        input_dir=raw_html_dir,
        output_dir=parsed_text_dir,
    )
    print(f"   -> {len(extracted)} fichiers texte générés")
    for f in extracted:
        print(f"     - {f}")


