"""
Utilitaires et helpers pour le bot Altissia
"""
import os
from dotenv import load_dotenv
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout


def load_config():
    """
    Charge la configuration depuis le fichier .env
    
    Returns:
        dict: Configuration avec username, password, url
    """
    load_dotenv()
    
    config = {
        'username': os.getenv('ALTISSIA_USERNAME'),
        'password': os.getenv('ALTISSIA_PASSWORD'),
        'url': os.getenv('ALTISSIA_URL', 'https://www.altissia.com/')
    }
    
    # Vérification des variables requises
    if not config['username'] or not config['password']:
        raise ValueError(
            "❌ Erreur : ALTISSIA_USERNAME et ALTISSIA_PASSWORD doivent être définis dans le fichier .env\n"
            "Copiez .env.example vers .env et remplissez vos identifiants."
        )
    
    return config


def wait_and_click(page: Page, selector: str, timeout: int = 5000):
    """
    Attend qu'un élément soit visible et clique dessus
    
    Args:
        page: Page Playwright
        selector: Sélecteur CSS de l'élément
        timeout: Timeout en millisecondes (défaut: 5000)
    
    Returns:
        bool: True si succès, False sinon
    """
    try:
        page.wait_for_selector(selector, timeout=timeout, state='visible')
        page.click(selector)
        return True
    except PlaywrightTimeout:
        print(f"⚠️  Timeout : élément '{selector}' non trouvé")
        return False


def get_text(page: Page, selector: str, timeout: int = 5000):
    """
    Récupère le texte d'un élément
    
    Args:
        page: Page Playwright
        selector: Sélecteur CSS de l'élément
        timeout: Timeout en millisecondes (défaut: 5000)
    
    Returns:
        str: Texte de l'élément ou None si non trouvé
    """
    try:
        page.wait_for_selector(selector, timeout=timeout, state='visible')
        return page.locator(selector).inner_text()
    except PlaywrightTimeout:
        print(f"⚠️  Timeout : élément '{selector}' non trouvé")
        return None


def fill_input(page: Page, selector: str, text: str, timeout: int = 5000):
    """
    Remplit un champ input avec du texte
    
    Args:
        page: Page Playwright
        selector: Sélecteur CSS du champ input
        text: Texte à entrer
        timeout: Timeout en millisecondes (défaut: 5000)
    
    Returns:
        bool: True si succès, False sinon
    """
    try:
        page.wait_for_selector(selector, timeout=timeout, state='visible')
        page.fill(selector, text)
        return True
    except PlaywrightTimeout:
        print(f"⚠️  Timeout : champ '{selector}' non trouvé")
        return False


def print_header(text: str):
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_success(text: str):
    """Affiche un message de succès"""
    print(f"✅ {text}")


def print_error(text: str):
    """Affiche un message d'erreur"""
    print(f"❌ {text}")


def print_info(text: str):
    """Affiche un message d'information"""
    print(f"ℹ️  {text}")


def print_progress(current: int, total: int, message: str = ""):
    """Affiche la progression"""
    print(f"📊 [{current}/{total}] {message}")
