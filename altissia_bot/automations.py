"""
Module d'automatisation pour les exercices Altissia
"""

import time
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
from .utils import (
    wait_and_click,
    print_success,
    print_error,
    print_info,
    print_progress,
)


# Sélecteurs HTML Altissia
SELECTORS = {
    "input_field": "input.c-iJOJc",
    "validate_button": 'button:has-text("Valider")',
    "correct_answer": "span.c-gUxMKR-bkfbUO-isCorrect-true",
    "continue_button": 'button.c-jUtMbh, button.c-lfgsZH:has-text("Continuer")',
}


def login(page: Page, username: str, password: str) -> bool:
    """
    Connexion à la plateforme Altissia

    Args:
        page: Page Playwright
        username: Nom d'utilisateur
        password: Mot de passe

    Returns:
        bool: True si connexion réussie, False sinon
    """
    try:
        print_info("Connexion à Altissia...")

        # Attendre que la page soit complètement chargée
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Remplir le champ email/username de façon plus naturelle
        email_field = page.locator(
            'input[type="email"], input[name="email"], input[name="username"]'
        ).first
        email_field.click()
        time.sleep(0.3)
        email_field.fill(username)
        time.sleep(0.5)

        # Remplir le champ password de façon plus naturelle
        password_field = page.locator('input[type="password"], input[name="password"]').first
        password_field.click()
        time.sleep(0.3)
        password_field.fill(password)
        time.sleep(0.5)

        # Cliquer sur le bouton de connexion
        page.click(
            'button[type="submit"], button:has-text("Connexion"), button:has-text("Login"), button:has-text("Se connecter")'
        )

        # Attendre que la connexion se fasse
        print_info("Tentative de connexion...")
        time.sleep(3)

        print_success("Connexion réussie")
        return True
    except Exception as e:
        print_error(f"Échec de la connexion : {e}")
        return False


def get_available_exercises(page: Page) -> list:
    """
    Récupère la liste des exercices disponibles dans l'unité

    Args:
        page: Page Playwright

    Returns:
        list: Liste des exercices (titre, sélecteur)
    """
    # Cette fonction devra être adaptée selon la structure HTML réelle
    # d'Altissia pour lister les exercices
    print_info("Récupération des exercices disponibles...")

    exercises = []
    try:
        # Exemple : chercher tous les liens/boutons d'exercices
        # À adapter selon la vraie structure
        exercise_elements = page.locator(
            '[data-exercise], .exercise-item, a[href*="exercise"]'
        ).all()

        for idx, element in enumerate(exercise_elements, 1):
            title = element.inner_text() or f"Exercice {idx}"
            exercises.append({"id": idx, "title": title.strip(), "element": element})

        if not exercises:
            print_info("Aucun exercice trouvé (structure HTML à vérifier)")
    except Exception as e:
        print_error(f"Erreur lors de la récupération des exercices : {e}")

    return exercises


def select_exercise(page: Page, exercise_id: int, exercises: list) -> bool:
    """
    Sélectionne et lance un exercice

    Args:
        page: Page Playwright
        exercise_id: ID de l'exercice à lancer
        exercises: Liste des exercices disponibles

    Returns:
        bool: True si l'exercice a été lancé, False sinon
    """
    try:
        if not exercises or exercise_id > len(exercises):
            print_error(f"Exercice {exercise_id} introuvable")
            return False

        exercise = exercises[exercise_id - 1]
        print_info(f"Lancement de l'exercice : {exercise['title']}")

        exercise["element"].click()
        time.sleep(1)

        print_success("Exercice ouvert")
        return True
    except Exception as e:
        print_error(f"Erreur lors de l'ouverture de l'exercice : {e}")
        return False


def collect_answer(page: Page, question_number: int):
    """
    Collecte la réponse d'une question sans la remplir
    Gère les questions à réponse simple ou multiple (plusieurs trous)

    Logique :
    1. Clique sur Valider sans répondre → révèle la réponse
    2. Récupère TOUTES les bonnes réponses (peut y en avoir plusieurs)
    3. Clique Continuer (pour passer à la suivante)

    Args:
        page: Page Playwright
        question_number: Numéro de la question

    Returns:
        list: Liste des réponses correctes ou None si échec
    """
    try:
        print_info(f"Collecte de la réponse {question_number}...")

        # Étape 1 : Cliquer sur Valider sans répondre pour révéler la réponse
        if not wait_and_click(page, SELECTORS["validate_button"], timeout=3000):
            print_error("Bouton Valider introuvable")
            return None

        time.sleep(0.5)

        # Étape 2 : Récupérer TOUTES les bonnes réponses (peut y en avoir plusieurs)
        try:
            page.wait_for_selector(SELECTORS["correct_answer"], timeout=3000, state="visible")
            correct_answers_elements = page.locator(SELECTORS["correct_answer"]).all()

            correct_answers = []
            for element in correct_answers_elements:
                text = element.inner_text().strip()
                if text:
                    correct_answers.append(text)

            if not correct_answers:
                print_error("Aucune réponse correcte trouvée")
                return None

            # Affichage
            if len(correct_answers) == 1:
                print_success(f"Réponse {question_number} : '{correct_answers[0]}'")
            else:
                print_success(
                    f"Réponse {question_number} : {correct_answers} ({len(correct_answers)} trous)"
                )

        except Exception as e:
            print_error(f"Erreur lors de la récupération des réponses : {e}")
            return None

        # Étape 3 : Cliquer sur Continuer (ne pas remplir le champ)
        if not wait_and_click(page, SELECTORS["continue_button"], timeout=3000):
            print_info("Bouton Continuer introuvable (dernière question ?)")
            return correct_answers  # Dernière question

        time.sleep(0.5)

        return correct_answers

    except Exception as e:
        print_error(f"Erreur lors de la collecte : {e}")
        return None


def fill_answer(page: Page, answers, question_number: int) -> bool:
    """
    Remplit une question avec la/les réponse(s) stockée(s)
    Gère les questions à réponse simple ou multiple (plusieurs trous)

    Args:
        page: Page Playwright
        answers: La réponse (str) ou les réponses (list) à remplir
        question_number: Numéro de la question

    Returns:
        bool: True si succès, False sinon
    """
    try:
        # Convertir en liste si c'est une seule réponse
        if isinstance(answers, str):
            answers = [answers]

        print_info(f"Remplissage question {question_number}...")

        # Attendre que les champs soient visibles
        page.wait_for_selector(SELECTORS["input_field"], timeout=3000, state="visible")

        # Récupérer tous les champs input
        input_fields = page.locator(SELECTORS["input_field"]).all()

        # Vérifier qu'on a le bon nombre de réponses
        if len(input_fields) != len(answers):
            print_error(
                f"Nombre de champs ({len(input_fields)}) ≠ nombre de réponses ({len(answers)})"
            )
            return False

        # Remplir chaque champ avec sa réponse correspondante
        for i, (field, answer) in enumerate(zip(input_fields, answers)):
            field.click()
            time.sleep(0.2)
            field.fill(answer)
            time.sleep(0.2)

        time.sleep(0.3)

        # Valider
        if not wait_and_click(page, SELECTORS["validate_button"], timeout=3000):
            print_error("Impossible de valider")
            return False

        time.sleep(0.5)

        # Continuer
        if not wait_and_click(page, SELECTORS["continue_button"], timeout=3000):
            print_info("Bouton Continuer introuvable (dernière question ?)")
            return True

        print_success(f"Question {question_number} remplie ✓")
        time.sleep(0.5)

        return True

    except Exception as e:
        print_error(f"Erreur lors du remplissage : {e}")
        return False


def solve_exercise(page: Page, max_questions: int = 100) -> int:
    """
    Résout un exercice complet automatiquement en 2 phases

    Phase 1 : Collecte toutes les réponses
    Phase 2 : Retour au début et remplissage automatique

    Args:
        page: Page Playwright
        max_questions: Nombre maximum de questions à traiter (sécurité)

    Returns:
        int: Nombre de questions résolues
    """
    print_info("🚀 PHASE 1 : Collecte des réponses...")
    print_info("Le bot va parcourir toutes les questions pour récupérer les réponses")

    answers = []

    for question_num in range(1, max_questions + 1):
        # Vérifier si le champ input existe encore (sinon, exercice terminé)
        try:
            page.wait_for_selector(SELECTORS["input_field"], timeout=2000, state="visible")
        except PlaywrightTimeout:
            print_info("Plus de questions à collecter")
            break

        # Collecter la réponse
        answer = collect_answer(page, question_num)
        if answer:
            answers.append(answer)
            print_progress(len(answers), "?", "réponses collectées")
        else:
            print_error(f"Échec collecte question {question_num}")
            break

        # Petite pause entre chaque question
        time.sleep(0.5)

    if not answers:
        print_error("Aucune réponse collectée")
        return 0

    print_success(f"✅ {len(answers)} questions collectées !")
    print("")
    print("=" * 60)
    print("📋 RÉPONSES COLLECTÉES :")
    for i, answer in enumerate(answers, 1):
        if isinstance(answer, list):
            if len(answer) == 1:
                print(f"  Question {i} : {answer[0]}")
            else:
                print(f"  Question {i} : {' / '.join(answer)} ({len(answer)} trous)")
        else:
            print(f"  Question {i} : {answer}")
    print("=" * 60)
    print("")

    # Phase 2 : Attendre que l'utilisateur retourne au début
    print_info("🔄 PHASE 2 : Remplissage automatique")
    print_info("Retournez MANUELLEMENT au début de l'exercice")
    print_info("(cliquez sur 'Recommencer' ou naviguez vers l'exercice)")
    input("Appuyez sur Entrée quand vous êtes prêt à remplir automatiquement...")

    # Vérifier qu'on est bien au début
    time.sleep(1)
    try:
        page.wait_for_selector(SELECTORS["input_field"], timeout=3000, state="visible")
    except PlaywrightTimeout:
        print_error("Pas de champ de réponse détecté. Assurez-vous d'être au début de l'exercice")
        return 0

    print_info("🚀 Démarrage du remplissage automatique...")

    # Remplir toutes les questions avec les réponses stockées
    questions_filled = 0
    for i, answer in enumerate(answers, 1):
        if fill_answer(page, answer, i):
            questions_filled += 1
        else:
            print_error(f"Échec remplissage question {i}")
            break

        time.sleep(0.5)

    print_success(f"✅ Exercice terminé ! {questions_filled}/{len(answers)} questions remplies")
    return questions_filled


def navigate_to_unit(page: Page, unit_url: str = None) -> bool:
    """
    Navigue vers une unité spécifique

    Args:
        page: Page Playwright
        unit_url: URL de l'unité (optionnel)

    Returns:
        bool: True si navigation réussie
    """
    try:
        if unit_url:
            print_info(f"Navigation vers : {unit_url}")
            page.goto(unit_url)
            time.sleep(1)
            return True
        else:
            print_info("Aucune URL d'unité fournie, navigation manuelle nécessaire")
            return False
    except Exception as e:
        print_error(f"Erreur de navigation : {e}")
        return False
