import time
import requests
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from collections import deque


BASE_DOMAIN = "esilv.fr"
BASE_URL = "https://www.esilv.fr/"

def init_robots_parser():
    url = "https://www.esilv.fr/robots.txt"

    try:
        resp = requests.get(url, timeout=5)
        status = resp.status_code
        #print("robots.txt status =", status)

        rp = RobotFileParser()
        rp.parse(resp.text.splitlines())
        return rp

    except requests.RequestException as e:
        print("Erreur lors de la récupération de robots.txt :", e)
        return None

def is_internal_url(url):
    parsed = urlparse(url)
    # garde les sous-domaines éventuels de esilv.fr
    return parsed.netloc.endswith(BASE_DOMAIN) or parsed.netloc == ""

def normalize_url(url, base=BASE_URL):
    # résout les liens relatifs + enlève le fragment (#...)
    abs_url = urljoin(base, url)
    abs_url, _ = urldefrag(abs_url)
    # optionnel : enlever trailing slash cohérent
    if abs_url.endswith("/"):
        abs_url = abs_url[:-1]
    return abs_url

def discover_all_urls(base_url=BASE_URL, delay=0.5, max_pages=None, user_agent="ESILV-crawler/1.0"):
    rp = init_robots_parser()
    

    to_visit = deque([base_url])
    seen = set()
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})

    while to_visit:
        url = to_visit.popleft()

        # Limite optionnelle de sécurité
        if max_pages is not None and len(seen) >= max_pages:
            break

        if url in seen:
            continue
        seen.add(url)

        # Respect robots.txt
        if not rp.can_fetch(user_agent, url):
            continue

        try:
            resp = session.get(url, timeout=10)
        except requests.RequestException:
            continue

        # On ne suit que le HTML
        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # Récupérer tous les liens <a href="...">
        for a in soup.find_all("a", href=True):
            href = a["href"]
            new_url = normalize_url(href, base=resp.url)

            if not is_internal_url(new_url):
                continue

            # Là encore, respecter robots.txt avant d'ajouter
            if new_url not in seen and rp.can_fetch(user_agent, new_url):
                to_visit.append(new_url)

        # Politeness
        time.sleep(delay)

    return list(seen)
