"""
Utilitaires et helpers
"""

import os
import logging
import re
from dotenv import load_dotenv
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),  # Console
        logging.FileHandler("altissia_bot.log", mode="a", encoding="utf-8"),  # Fichier
    ],
)
logger = logging.getLogger("altissia_bot")


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


def is_color_green(color_string: str) -> bool:
    """
    Vérifie si une chaîne de couleur (rgb ou rgba) est "verte".
    Analyse les composantes RGB.
    Le vert est dominant si G > R et G > B, avec un seuil minimum.
    """
    if not color_string:
        return False

    # Extraction des nombres
    match = re.search(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", color_string)
    if not match:
        return False

    try:
        r, g, b = map(int, match.groups())

        # Critères pour considérer une couleur comme verte :
        # 1. Le vert doit être dominant
        # 2. Le vert doit avoir une intensité minimale
        # 3. La différence entre vert et les autres doit être significative

        # Cas spécifiques très clairs (vert pur, vert lime)
        if g > 100 and r < 100 and b < 100:
            return True

        # Cas plus nuancés (ex: rgb(34, 197, 94))
        if g > r + 20 and g > b + 20 and g > 100:
            return True

        # Verts très clairs (backgrounds)
        # ex: rgb(233, 251, 241) -> R=233, G=251, B=241
        if g >= r and g >= b and g > 200:
            # Si c'est très clair, on vérifie juste que c'est pas rouge ou bleu
            # Mais attention au blanc (255, 255, 255)
            if r > 240 and b > 240 and g > 240:
                return False  # Blanc
            return True

        return False
    except ValueError:
        return False


def print_header(text: str):
    """Affiche un en-tête"""
    logger.info("=" * 60)
    logger.info(f"  {text}")
    logger.info("=" * 60)


def print_success(text: str):
    """Affiche un message de succès"""
    logger.info(f"✓ {text}")


def print_error(text: str):
    """Affiche un message d'erreur"""
    logger.error(f"✗ {text}")


def print_info(text: str):
    """Affiche un message d'information"""
    logger.info(f"ℹ {text}")


"""
Utilitaires et helpers
"""
