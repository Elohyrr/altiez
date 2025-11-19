#!/usr/bin/env python3
"""
Bot d'automatisation Altissia
Script principal pour lancer et gérer les exercices
"""
import sys
import time
from playwright.sync_api import sync_playwright
from .utils import load_config, print_header, print_success, print_error, print_info
from .automations import (
    login,
    get_available_exercises,
    select_exercise,
    solve_exercise,
    navigate_to_unit,
)


def display_menu(exercises: list) -> int:
    """
    Affiche le menu de sélection d'exercice

    Args:
        exercises: Liste des exercices disponibles

    Returns:
        int: ID de l'exercice sélectionné
    """
    print_header("📚 EXERCICES DISPONIBLES")

    if not exercises:
        print_error("Aucun exercice trouvé")
        print_info("Assurez-vous d'être sur la bonne page d'unité")
        return 0

    for exercise in exercises:
        print(f"  {exercise['id']}. {exercise['title']}")

    print("\n" + "-" * 60)

    while True:
        try:
            choice = input(f"\n👉 Choisissez un exercice (1-{len(exercises)}) ou 0 pour quitter : ")
            choice_int = int(choice)

            if choice_int == 0:
                print_info("Au revoir !")
                return 0

            if 1 <= choice_int <= len(exercises):
                return choice_int
            else:
                print_error(f"Veuillez entrer un nombre entre 1 et {len(exercises)}")
        except ValueError:
            print_error("Veuillez entrer un nombre valide")
        except KeyboardInterrupt:
            print("\n")
            print_info("Interruption par l'utilisateur")
            return 0


def run_bot_interactive(headless: bool = False, unit_url: str = None):
    """
    Lance le bot en mode interactif

    Args:
        headless: Lancer le navigateur en mode headless
        unit_url: URL de l'unité à ouvrir (optionnel)
    """
    # Chargement de la configuration
    try:
        config = load_config()
    except ValueError as e:
        print_error(str(e))
        return

    print_header("🤖 BOT ALTISSIA - AUTOMATISATION D'EXERCICES")
    print_info(f"Utilisateur : {config['username']}")
    print_info(f"URL : {config['url']}")

    with sync_playwright() as p:
        # Lancement du navigateur
        print_info("Démarrage du navigateur...")
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",  # Masque l'automatisation
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="fr-FR",
            timezone_id="Europe/Paris",
            extra_http_headers={
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            },
        )

        # Masquer les traces d'automatisation
        page = context.new_page()
        page.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
        )

        try:
            # Navigation vers Altissia
            print_info(f"Accès à {config['url']}...")
            page.goto(config["url"])
            time.sleep(2)

            # Connexion
            if not login(page, config["username"], config["password"]):
                print_error("Échec de connexion")
                return

            # Navigation vers l'unité (si URL fournie)
            if unit_url:
                if not navigate_to_unit(page, unit_url):
                    print_error("Impossible d'accéder à l'unité")

            # Pause pour permettre la navigation manuelle
            print_info("Naviguez manuellement vers votre exercice...")
            print_info(
                "Appuyez sur Entrée une fois sur la page de l'exercice (là où vous voyez les questions)..."
            )
            input()

            # Vérifier si on est déjà dans un exercice
            time.sleep(1)
            try:
                page.wait_for_selector("input.c-iJOJc", timeout=3000, state="visible")
                print_success("Exercice détecté !")
                print("")
                print("=" * 60)
                print("📖 FONCTIONNEMENT DU BOT :")
                print("  Phase 1 : Collecte toutes les réponses (sans remplir)")
                print("  Phase 2 : Vous retournez au début manuellement")
                print("  Phase 3 : Le bot remplit tout automatiquement")
                print("=" * 60)
                print("")

                # Boucle principale
                while True:
                    # Résoudre l'exercice directement
                    print_header("🎯 RÉSOLUTION AUTOMATIQUE")
                    questions_solved = solve_exercise(page)

                    print_success(f"🎉 Exercice terminé ! {questions_solved} questions résolues")

                    # Demander si on continue
                    print("\n" + "-" * 60)
                    continue_choice = input("\n👉 Faire un autre exercice ? (o/n) : ").lower()

                    if continue_choice != "o":
                        print_info("Au revoir !")
                        break

                    # Retour pour un nouvel exercice
                    print_info("Naviguez vers le prochain exercice...")
                    input("Appuyez sur Entrée quand vous êtes prêt...")
                    time.sleep(1)

                    # Vérifier qu'on est bien dans un exercice
                    try:
                        page.wait_for_selector("input.c-iJOJc", timeout=3000, state="visible")
                    except Exception:
                        print_error("Pas d'exercice détecté sur cette page")
                        break

            except Exception:
                print_error("Aucun exercice détecté sur cette page")
                print_info(
                    "Assurez-vous d'être sur la page d'un exercice (là où vous voyez les questions)"
                )
                return

        except KeyboardInterrupt:
            print("\n")
            print_info("Interruption par l'utilisateur")
        except Exception as e:
            print_error(f"Erreur inattendue : {e}")
            import traceback

            traceback.print_exc()
        finally:
            # Fermeture propre
            print_info("Fermeture du navigateur...")
            browser.close()


def run_bot_auto(exercise_number: int = 1, headless: bool = True, unit_url: str = None):
    """
    Lance le bot en mode automatique (sans interaction)

    Args:
        exercise_number: Numéro de l'exercice à résoudre
        headless: Lancer le navigateur en mode headless
        unit_url: URL de l'unité
    """
    try:
        config = load_config()
    except ValueError as e:
        print_error(str(e))
        return

    print_header("🤖 BOT ALTISSIA - MODE AUTOMATIQUE")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="fr-FR",
            timezone_id="Europe/Paris",
            extra_http_headers={
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            },
        )

        page = context.new_page()
        page.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
        )

        try:
            page.goto(config["url"])
            time.sleep(2)

            if not login(page, config["username"], config["password"]):
                return

            if unit_url:
                navigate_to_unit(page, unit_url)

            exercises = get_available_exercises(page)

            if not select_exercise(page, exercise_number, exercises):
                return

            questions_solved = solve_exercise(page)
            print_success(f"✅ Terminé ! {questions_solved} questions résolues")

        except Exception as e:
            print_error(f"Erreur : {e}")
        finally:
            browser.close()


def main():
    """Point d'entrée principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Bot d'automatisation Altissia",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python main.py                           # Mode interactif
  python main.py --headless                # Mode interactif headless
  python main.py --auto --exercise 1       # Mode automatique
  python main.py --unit-url <URL>          # Avec URL d'unité spécifique
        """,
    )

    parser.add_argument(
        "--auto", action="store_true", help="Mode automatique (résout l'exercice sans interaction)"
    )

    parser.add_argument(
        "--exercise", type=int, default=1, help="Numéro de l'exercice en mode auto (défaut: 1)"
    )

    parser.add_argument(
        "--headless", action="store_true", help="Lance le navigateur en mode headless (invisible)"
    )

    parser.add_argument("--unit-url", type=str, help="URL de l'unité Altissia")

    args = parser.parse_args()

    try:
        if args.auto:
            run_bot_auto(
                exercise_number=args.exercise, headless=args.headless, unit_url=args.unit_url
            )
        else:
            run_bot_interactive(headless=args.headless, unit_url=args.unit_url)
    except KeyboardInterrupt:
        print("\n")
        print_info("Programme interrompu")
        sys.exit(0)


if __name__ == "__main__":
    main()
