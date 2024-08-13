import requests
from bs4 import BeautifulSoup
import whois
from urllib.parse import urljoin, urlparse
import re

def get_page_text(url):
    """Récupère et parse le contenu HTML de la page spécifiée."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération de {url}: {e}")
        return None

def get_all_links(base_url, soup):
    """Extrait tous les liens internes d'une page web."""
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.add(full_url)
    return links

def extract_contact_info(soup):
    """Extrait les informations de contact d'une page web."""
    contact_info = {}
    contact_patterns = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone': r'\+?\d[\d -]{8,}\d',
        'address': r'\d{1,5}\s\w+(\s\w+){1,5},?\s\w+(\s\w+){1,3}'
    }
    
    text = soup.get_text()
    for key, pattern in contact_patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            contact_info[key] = list(set(matches))
    
    return contact_info

def get_hosting_info(domain):
    """Récupère les informations d'hébergement d'un domaine."""
    try:
        response = requests.get(f"https://www.whois.com/whois/{domain}", timeout=10)
        response.raise_for_status()
        start = response.text.find("Name Server") + len("Name Server")
        end = response.text.find("</pre>", start)
        return response.text[start:end].strip() if start != -1 else "Information non disponible"
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération des informations d'hébergement: {e}")
        return "Erreur"

def get_whois_info(domain):
    """Récupère les informations WHOIS d'un domaine."""
    try:
        domain_info = whois.whois(domain)
        return {
            'Domain Name': domain_info.domain_name,
            'Registrar': domain_info.registrar,
            'Creation Date': domain_info.creation_date,
            'Expiration Date': domain_info.expiration_date,
            'Name Servers': domain_info.name_servers,
            'Owner': domain_info.org,
            'Email': domain_info.emails
        }
    except Exception as e:
        print(f"Erreur lors de la récupération des informations WHOIS: {e}")
        return {}

def scrape_website(base_url):
    """Scrape un site web pour extraire les liens internes et les informations de contact."""
    visited_urls = set()
    urls_to_visit = {base_url}

    while urls_to_visit:
        url = urls_to_visit.pop()
        if url in visited_urls:
            continue
        visited_urls.add(url)
        print(f"[+] URL visitée : {url}")

        soup = get_page_text(url)
        if soup:
            contact_info = extract_contact_info(soup)
            if contact_info:
                if 'email' in contact_info:
                    print(f"[+] Emails trouvés : {contact_info['email']}")
                if 'phone' in contact_info:
                    print(f"[+] Téléphones trouvés : {contact_info['phone']}")
                if 'address' in contact_info:
                    print(f"[+] Adresses trouvées : {contact_info['address']}")

            links = get_all_links(base_url, soup)
            urls_to_visit.update(links - visited_urls)

if __name__ == "__main__":
    site_url = input("Entrez l'URL du site web (ex : https://example.com) : ")
    domain = urlparse(site_url).netloc

    print("\n[INFO] Informations WHOIS:")
    whois_info = get_whois_info(domain)
    for key, value in whois_info.items():
        print(f"{key}: {value}")

    print("\n[INFO] Informations sur l'hébergement:")
    hosting_info = get_hosting_info(domain)
    print(f"Nom de l'hébergeur: {hosting_info}")

    print("\n[INFO] Scraping du site web:")
    scrape_website(site_url)
    print("\n[INFO] Scraping terminé.")

    input("Appuyez sur Entrer pour quitter.")
