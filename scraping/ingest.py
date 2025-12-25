from pathlib import Path
from typing import List

from scraper import scrape_esilv_pages
from parse_html import parse_html_folder


def ingest_esilv_site(
    raw_html_dir: Path | str = Path("data/raw/esilv_html"),
    parsed_text_dir: Path | str = Path("data/processed/esilv_text"),
) -> List[Path]:

    print("[scraping/ingest] Scraping ESILV website pages...")
    scrape_esilv_pages(output_dir=raw_html_dir)

    print("[scraping/ingest] Text extraction from HTML...")
    out_files = parse_html_folder(raw_html_dir, parsed_text_dir)

    print(f"[scraping/ingest] {len(out_files)} text files generated.")
    return out_files
