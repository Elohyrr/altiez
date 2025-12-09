#!/usr/bin/env python3
"""
Bot Altissia - Version optimisée
Workflow automatique pour résoudre les exercices
"""
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from .utils import load_config, print_header, print_success, print_error, print_info
from .automations import (
    login,
    detect_exercise_type,
    collect_all_answers,
    fill_all_answers,
    check_retry_button,
)


def run_bot(headless=False):
    """Lance le bot avec le workflow optimisé"""
    try:
        config = load_config()
    except ValueError as e:
        print_error(str(e))
        return

    print_header("BOT ALTISSIA - WORKFLOW AUTOMATIQUE")

    with sync_playwright() as p:
        # Configuration navigateur
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-web-security",
            ],
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="fr-FR",
            timezone_id="Europe/Paris",
        )

        page = context.new_page()
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        try:
            # Connexion
            print_info(f"Accès à {config['url']}...")
            page.goto(config["url"], timeout=60000)
            time.sleep(2)

            # Login si nécessaire
            try:
                page.wait_for_selector('input[type="email"]', timeout=3000)
                if not login(page, config["username"], config["password"]):
                    print_error("Échec de connexion")
                    return
            except PlaywrightTimeout:
                print_info("Déjà connecté")

            # Instructions utilisateur
            print_info("Naviguez vers l'exercice que vous voulez résoudre")
            input("Appuyez sur Entrée une fois sur la page de l'exercice...")

            # WORKFLOW PRINCIPAL EN BOUCLE
            while True:
                # ÉTAPE 1: Détection du type d'exercice
                exercise_type = detect_exercise_type(page)

                if exercise_type == "unknown":
                    print_error("Aucun exercice détecté")
                    break

                print_success(f"Type détecté: {exercise_type.upper()}")

                # ÉTAPE 2-6: Collecte des réponses (valider → récupérer → continuer)
                answers_db = collect_all_answers(page, exercise_type, max_questions=100)

                if not answers_db:
                    print_error("Aucune réponse collectée")
                    break

                # ÉTAPE 7-8: Check bouton réessayer
                has_retry = check_retry_button(page, click=False)

                if has_retry:
                    print_info("Bouton 'Réessayer' détecté - Préparation au remplissage")

                    # Afficher les réponses collectées
                    print_header("RÉPONSES COLLECTÉES")
                    for i, qa in enumerate(answers_db, 1):
                        print_info(f"  Q{i} ({qa['type']}): {qa['answers']}")
                    print_info("-" * 60)

                    # Attendre 2 secondes puis cliquer
                    time.sleep(2)
                    check_retry_button(page, click=True)
                    time.sleep(1)

                    # ÉTAPE 9-11: Remplissage avec les réponses collectées
                    filled = fill_all_answers(page, answers_db)
                    print_success(
                        f"Exercice terminé! {filled}/{len(answers_db)} questions remplies"
                    )

                    # Demander si on continue
                    choice = input("\nFaire un autre exercice? (o/n): ").lower()
                    if choice != "o":
                        break

                    print_info("Naviguez vers le prochain exercice...")
                    input("Appuyez sur Entrée quand prêt...")
                else:
                    print_info("Pas de bouton 'Réessayer' - Fin de l'exercice")
                    break

        except KeyboardInterrupt:
            print_info("Interruption par l'utilisateur")
        except Exception as e:
            print_error(f"Erreur: {e}")
            import traceback

            traceback.print_exc()
        finally:
            browser.close()


def main():
    """Point d'entrée"""
    import argparse

    parser = argparse.ArgumentParser(description="Bot Altissia - Automatisation")
    parser.add_argument("--headless", action="store_true", help="Mode headless")
    args = parser.parse_args()

    try:
        run_bot(headless=args.headless)
    except KeyboardInterrupt:
        print_info("Programme interrompu")


if __name__ == "__main__":
    main()
