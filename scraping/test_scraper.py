import os
import sys
from pathlib import Path
# --- Import du scraper ---
from .scraper import scrape_esilv_pages
from .parse_html import parse_html_folder


def main():
    print("\n=== Test du Scraper ESILV (bas-niveau) ===\n")

    # On teste sur une petite partie du site
    test_pages = [
        "/formations/",
        "/admissions/",
    ]

    raw_html_dir = Path("data/raw/test_scraper_html")
    parsed_text_dir = Path("data/docs")

    print("[1] Téléchargement des pages HTML…")
    downloaded = scrape_esilv_pages(
        pages=test_pages,
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

    print("\n[3] Aperçu du contenu (premières lignes) :\n")
    for txt_file in extracted:
        print(f"--- {txt_file.name} ---")
        content = txt_file.read_text(encoding="utf-8").splitlines()
        for line in content[:10]:  # On affiche les 10 premières lignes
            print("  ", line)
        print()

    print("=== Test terminé ===\n")


if __name__ == "__main__":
    main()
