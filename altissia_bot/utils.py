"""
Utilitaires et helpers
"""

import os
from dotenv import load_dotenv
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout


def load_config():
    """Charge la configuration depuis .env"""
    load_dotenv()

    config = {
        "username": os.getenv("ALTISSIA_USERNAME"),
        "password": os.getenv("ALTISSIA_PASSWORD"),
        "url": os.getenv("ALTISSIA_URL", "https://www.altissia.com"),
    }

    if not config["username"] or not config["password"]:
        raise ValueError(
            "Erreur: ALTISSIA_USERNAME et ALTISSIA_PASSWORD doivent être "
            "définis dans le fichier .env\n"
            "Copiez .env.example vers .env et remplissez vos identifiants."
        )

    return config


def wait_and_click(page: Page, selector: str, timeout: int = 5000) -> bool:
    """
    Attend qu'un élément soit visible et clique dessus

    Returns: True si succès, False sinon
    """
    try:
        page.wait_for_selector(selector, timeout=timeout, state="visible")
        page.click(selector)
        return True
    except PlaywrightTimeout:
        return False


def print_header(text: str):
    """Affiche un en-tête"""
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text: str):
    """Affiche un message de succès"""
    print(f"✓ {text}")


def print_error(text: str):
    """Affiche un message d'erreur"""
    print(f"✗ {text}")


def print_info(text: str):
    """Affiche un message d'information"""
    print(f"ℹ {text}")
