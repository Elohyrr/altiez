"""
Module d automatisation - VERSION BLACKLIST FIXED
Vérifie les MOTS ENTIERS dans la blacklist (pas sous-chaînes)
"""

import time
import re
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from .utils import wait_and_click, print_success, print_error, print_info, is_color_green
from .constants import SELECTORS, BLACKLIST_WORDS, GREEN_COLORS


def normalize_quotes(text):
    if not text:
        return text
    text = text.replace(chr(8220), chr(34))
    text = text.replace(chr(8221), chr(34))
    text = text.replace(chr(171), chr(34))
    text = text.replace(chr(187), chr(34))
    text = text.replace(chr(8216), chr(39))
    text = text.replace(chr(8217), chr(39))
    return text


def clean_text(text):
    if not text:
        return text
    text = text.strip()
    text = normalize_quotes(text)
    text = text.strip(chr(34)).strip(chr(39))
    text = text.rstrip(".").rstrip("!").rstrip("?").rstrip(",").rstrip(";").rstrip(":")
    return text.strip()


def texts_match(text1, text2):
    if not text1 or not text2:
        return False
    normalized1 = normalize_quotes(text1.strip())
    normalized2 = normalize_quotes(text2.strip())
    if normalized1 == normalized2:
        return True
    if clean_text(text1) == clean_text(text2):
        return True
    return False


def get_text_variants(text):
    variants = []
    variants.append(text)
    normalized = normalize_quotes(text)
    if normalized != text:
        variants.append(normalized)
    cleaned = clean_text(text)
    if cleaned != text:
        variants.append(cleaned)
    text_no_punct = text.rstrip(".").rstrip("!").rstrip("?").rstrip(",")
    if text_no_punct != text:
        variants.append(text_no_punct)
    if chr(34) not in text and cleaned:
        variants.append(f"{chr(34)}{cleaned}{chr(34)}")
    no_quotes = text.replace(chr(34), "").replace(chr(39), "")
    if no_quotes:
        variants.append(no_quotes)
        cleaned_no_quotes = clean_text(no_quotes)
        if cleaned_no_quotes:
            variants.append(cleaned_no_quotes)
    return [v for v in dict.fromkeys(variants) if v]


def is_blacklisted(text):
    """Vérifie si le texte contient un mot blacklisté (MOT ENTIER uniquement)"""
    if not text:
        return False

    text_lower = text.lower()

    for word in BLACKLIST_WORDS:
        word_lower = word.lower()

        # Si blacklist word contient des espaces, chercher la phrase exacte
        if " " in word_lower:
            if word_lower in text_lower:
                return True
        else:
            # Vérifier MOT ENTIER avec word boundaries
            # Utiliser regex pour éviter "right" dans "trustworthy"
            pattern = r"\b" + re.escape(word_lower) + r"\b"
            if re.search(pattern, text_lower):
                return True

    return False


def login(page, username, password):
    try:
        print_info("Connexion...")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        email_field = page.locator(
            'input[type="email"], input[name="email"], input[placeholder*="mail"]'
        ).first
        email_field.wait_for(state="visible", timeout=5000)
        email_field.click()
        time.sleep(0.3)
        email_field.fill(username)
        time.sleep(0.5)
        password_field = page.locator('input[type="password"]').first
        password_field.wait_for(state="visible", timeout=5000)
        password_field.click()
        time.sleep(0.3)
        password_field.fill(password)
        time.sleep(0.5)
        connect_button_selectors = [
            'button:has-text("Se connecter")',
            'button:has-text("Connexion")',
            'button:has-text("Login")',
            'button[type="submit"]',
        ]
        clicked = False
        for selector in connect_button_selectors:
            try:
                button = page.locator(selector).first
                button.wait_for(state="visible", timeout=2000)
                button.click()
                clicked = True
                print_info(f"Connexion via: {selector}")
                break
            except PlaywrightTimeout:
                continue
        if not clicked:
            print_error("Bouton de connexion non trouvé")
            return False
        time.sleep(3)
        print_success("Connexion réussie")
        return True
    except Exception as e:
        print_error(f"Échec connexion: {e}")
        return False


def detect_exercise_type(page):
    print_info("Mode: Détection par question")
    return "mixed"


def detect_question_type(page):
    try:
        time.sleep(0.5)
        input_count = page.locator(f'{SELECTORS["input_field"]}:visible').count()
        if input_count > 0:
            return "text"
        true_btn = page.locator(
            'button:has-text("true"):visible, button:has-text("True"):visible'
        ).count()
        false_btn = page.locator(
            'button:has-text("false"):visible, button:has-text("False"):visible'
        ).count()
        if true_btn > 0 and false_btn > 0:
            return "truefalse"
        order_indicators = [
            "text=Put the elements in the right order",
            "text=Mettez les éléments dans le bon ordre",
            "text=Sélectionnez le premier élément",
        ]
        for indicator in order_indicators:
            try:
                count = page.locator(indicator).count()
                if count > 0:
                    return "order"
            except Exception:
                pass
        all_clickable = page.locator(
            'button:visible, [role="button"]:visible, div[class*="button"]:visible'
        ).all()
        choice_count = sum(1 for elem in all_clickable if is_valid_choice_element(elem))
        if choice_count >= 2:
            return "choice"
        return "unknown"
    except Exception as e:
        print_error(f"Erreur détection: {e}")
        return "unknown"


def is_valid_choice_element(elem):
    try:
        text = elem.inner_text().strip()
        if not text or is_blacklisted(text):
            return False
        if len(text) > 200:
            return False
        return True
    except Exception:
        return False


def collect_all_answers(page, exercise_type, max_questions=100):
    print_info("PHASE 1: Collecte des réponses")
    answers_db = []
    for q_num in range(1, max_questions + 1):
        try:
            try:
                retry_visible = page.locator(
                    'button:has-text("Réessayer"), button:has-text("Ressayer")'
                ).count()
                continuer_visible = page.locator('button:has-text("Continuer")').count()
                if retry_visible > 0 and continuer_visible == 0:
                    print_info("Bouton Réessayer détecté - Fin")
                    break
            except Exception:
                pass
            question_type = detect_question_type(page)
            if question_type == "unknown":
                print_info("Plus de questions")
                break
            print_info(f"--- Question {q_num} ({question_type.upper()}) ---")
            if not wait_and_click(page, SELECTORS["validate_button"], timeout=3000):
                print_info("Plus de bouton Valider")
                break

            time.sleep(2.5)

            correct_answers = []
            if question_type == "text":
                correct_answers = find_text_answers(page)
            elif question_type == "choice":
                correct_answers = find_choice_answers(page)
            elif question_type == "truefalse":
                correct_answers = detect_truefalse_answer(page)
            elif question_type == "order":
                correct_answers = find_order_answer(page)
            correct_answers = filter_blacklist(correct_answers)
            if not correct_answers:
                print_error(f"Aucune réponse pour Q{q_num}")
                correct_answers = find_any_correct_elements(page)
                correct_answers = filter_blacklist(correct_answers)
                if not correct_answers:
                    manual = input("Entrez manuellement (ou skip): ").strip()
                    if manual.lower() == "skip":
                        break
                    elif manual:
                        correct_answers = [manual]
                    else:
                        break
            answers_db.append(
                {"question_num": q_num, "type": question_type, "answers": correct_answers}
            )
            print_success(f"Réponse: {correct_answers}")
            if not wait_and_click(page, SELECTORS["continue_button"], timeout=3000):
                print_info("Dernière question")
                break
            time.sleep(0.5)
        except Exception as e:
            print_error(f"Erreur Q{q_num}: {e}")
            break
    print_success(f"{len(answers_db)} questions collectées!")
    return answers_db


def filter_blacklist(answers):
    """Filtre avec vérification MOT ENTIER"""
    if not answers:
        return []
    filtered = []
    for answer in answers:
        if not is_blacklisted(answer):
            filtered.append(answer)
        else:
            print_info(f"  Ignoré (blacklist): {answer}")
    return filtered


def find_text_answers(page):
    results = []
    try:
        correct_elements = page.locator(SELECTORS["correct_answer"]).all()
        for elem in correct_elements:
            text = elem.inner_text().strip()
            if text:
                results.append(text)
                print_info(f"  Texte correct: {text}")
    except Exception:
        pass
    if not results:
        results = find_green_text_elements(page)
    return results


def find_green_text_elements(page):
    results = []
    try:
        spans = page.locator("span:visible, div:visible").all()[:30]
        for span in spans:
            try:
                text = span.inner_text().strip()
                if not text or len(text) > 200:
                    continue
                color = span.evaluate("el => window.getComputedStyle(el).color")
                classes = span.get_attribute("class") or ""
                # Utilisation de la nouvelle fonction
                is_green = is_color_green(str(color)) or "correct" in classes.lower()

                if is_green:
                    results.append(text)
                    print_info(f"  Texte vert: {text}")
            except Exception:
                continue
    except Exception:
        pass
    return results


def find_choice_answers(page):
    results = []
    try:
        print_info("  Recherche choix verts...")
        all_elements = page.locator("*:visible").all()
        for i, elem in enumerate(all_elements):
            if i > 150:
                break
            try:
                text = elem.inner_text().strip()
                if not text or len(text) == 0 or len(text) > 100:
                    continue
                if is_blacklisted(text):
                    continue
                styles = elem.evaluate(
                    """el => {
                    const s = window.getComputedStyle(el);
                    return {
                        borderColor: s.borderColor,
                        backgroundColor: s.backgroundColor,
                        color: s.color
                    };
                }"""
                )
                classes = elem.get_attribute("class") or ""

                # Vérification avec is_color_green
                is_green = (
                    is_color_green(str(styles["color"]))
                    or is_color_green(str(styles["backgroundColor"]))
                    or is_color_green(str(styles["borderColor"]))
                    or "correct" in classes.lower()
                    or "success" in classes.lower()
                    or "iscorrect-true" in classes.lower()
                )

                if is_green:
                    if text not in results:
                        is_duplicate = False
                        for existing in results:
                            if text in existing or existing in text:
                                is_duplicate = True
                                break
                        if not is_duplicate:
                            results.append(text)
                            print_success(f"  ✓ VERT: {text}")
            except Exception:
                continue
        print_info(f"  Total verts: {len(results)}")
    except Exception as e:
        print_error(f"Erreur find_choice_answers: {e}")
    return results


def find_order_answer(page):
    results = []
    try:
        print_info("  Recherche phrase verte ORDER...")
        all_elements = page.locator("span:visible, div:visible, p:visible").all()
        green_sentence = None
        for elem in all_elements[:100]:
            try:
                text = elem.inner_text().strip()
                if not text or is_blacklisted(text):
                    continue
                color = elem.evaluate("el => window.getComputedStyle(el).color")
                classes = elem.get_attribute("class") or ""

                # Utilisation de la nouvelle fonction
                is_green = is_color_green(str(color)) or "correct" in classes.lower()

                if is_green and len(text) > 10:
                    green_sentence = text
                    print_info(f"  Phrase verte: {green_sentence}")
                    break
            except Exception:
                continue
        if green_sentence:
            words = green_sentence.split()
            cleaned_words = []
            for word in words:
                word = word.strip()
                if word:
                    cleaned_words.append(word)
            results = cleaned_words
            print_info(f"  Mots extraits: {results}")
    except Exception as e:
        print_error(f"Erreur find_order_answer: {e}")
    return results


def find_any_correct_elements(page):
    results = []
    try:
        selectors = ['[class*="correct"]', '[class*="success"]', '[class*="isCorrect-true"]']
        for selector in selectors:
            try:
                elements = page.locator(selector).all()[:10]
                for elem in elements:
                    text = elem.inner_text().strip()
                    if text and len(text) < 100 and text not in results:
                        results.append(text)
            except Exception:
                continue
    except Exception:
        pass
    return results


def detect_truefalse_answer(page):
    try:
        incorrect = page.locator("text=Incorrect, text=Wrong").count()
        if incorrect > 0:
            return ["false"]
        correct = page.locator("text=Correct, text=Right").count()
        if correct > 0:
            return ["true"]
        return ["true"]
    except Exception:
        return ["true"]


def fill_all_answers(page, answers_db):
    print_info("PHASE 2: Remplissage automatique")
    filled_count = 0
    for qa in answers_db:
        try:
            q_num = qa["question_num"]
            q_type = qa["type"]
            answers = qa["answers"]
            print_info(f"Q{q_num} ({q_type}): {answers}")
            time.sleep(1)
            if q_type == "text":
                success = fill_text_question(page, answers)
            elif q_type == "choice":
                success = fill_choice_question(page, answers)
            elif q_type == "truefalse":
                success = fill_truefalse_question(page, answers)
            elif q_type == "order":
                success = fill_order_question(page, answers)
            else:
                success = False
            if not success:
                print_error(f"Échec Q{q_num}")
                break
            filled_count += 1
            time.sleep(0.5)
        except Exception as e:
            print_error(f"Erreur Q{qa['question_num']}: {e}")
            break
    return filled_count


def fill_text_question(page, answers):
    try:
        page.wait_for_selector(SELECTORS["input_field"], timeout=3000, state="visible")
        input_fields = page.locator(SELECTORS["input_field"]).all()
        min_count = min(len(input_fields), len(answers))
        for i in range(min_count):
            answer = answers[i].strip()
            input_fields[i].click()
            time.sleep(0.2)
            input_fields[i].fill(answer)
            time.sleep(0.2)
        if not wait_and_click(page, SELECTORS["validate_button"], timeout=3000):
            return False
        time.sleep(0.5)
        wait_and_click(page, SELECTORS["continue_button"], timeout=3000)
        time.sleep(0.5)
        print_success("Rempli")
        return True
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def fill_choice_question(page, answers):
    try:
        clicked = 0
        for answer_text in answers:
            variants = get_text_variants(answer_text)
            print_info(f"  Recherche: {answer_text}")
            button_found = False

            for variant in variants:
                if button_found:
                    break
                try:
                    button = page.locator("div.c-cFbiKG").filter(has_text=variant).first
                    button.wait_for(state="visible", timeout=500)
                    button.click()
                    button_found = True
                    clicked += 1
                    time.sleep(0.4)
                    print_success(f"  ✓ Cliqué: {variant}")
                    break
                except PlaywrightTimeout:
                    pass

            if not button_found:
                for variant in variants:
                    if button_found:
                        break
                    # Fallback selectors using safe filter()
                    try:
                        elem = (
                            page.locator("button, [role='button']").filter(has_text=variant).first
                        )
                        elem.wait_for(state="visible", timeout=500)
                        elem.click()
                        button_found = True
                        clicked += 1
                        time.sleep(0.4)
                        print_success(f"  ✓ Cliqué (fallback): {variant}")
                        break
                    except PlaywrightTimeout:
                        pass

            if not button_found:
                for variant in variants:
                    if button_found:
                        break
                    try:
                        elem = page.locator("*:visible").filter(has_text=variant).first
                        elem.wait_for(state="visible", timeout=500)
                        elem.click()
                        button_found = True
                        clicked += 1
                        time.sleep(0.4)
                        print_success(f"  ✓ Cliqué (dernier recours): {variant}")
                        break
                    except PlaywrightTimeout:
                        pass

            if not button_found:
                print_error(f"  ✗ Non trouvé: {answer_text}")

        if clicked == 0:
            return False

        time.sleep(0.5)
        if not wait_and_click(page, SELECTORS["validate_button"], timeout=3000):
            return False
        time.sleep(0.5)
        wait_and_click(page, SELECTORS["continue_button"], timeout=3000)
        time.sleep(0.5)
        print_success("Rempli")
        return True
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def fill_truefalse_question(page, answers):
    try:
        answer = clean_text(answers[0]).lower()
        if answer not in ["true", "false"]:
            return False
        try:
            button = page.locator(f'button:has-text("{answer}")').first
            button.wait_for(state="visible", timeout=1000)
            button.click()
            time.sleep(0.3)
            print_success(f"  {answer.upper()}")
        except PlaywrightTimeout:
            pass
        if not wait_and_click(page, SELECTORS["validate_button"], timeout=3000):
            return False
        time.sleep(0.5)
        wait_and_click(page, SELECTORS["continue_button"], timeout=3000)
        time.sleep(0.5)
        print_success("Rempli")
        return True
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def fill_order_question(page, answers):
    try:
        print_info("  Remplissage ORDER...")
        print_info(f"  Ordre: {answers}")
        for word in answers:
            variants = get_text_variants(word)
            print_info(f"  Cherche: {word}")
            clicked = False
            for variant in variants:
                if clicked:
                    break
                try:
                    # Prefer exact match first if possible, or robust filter
                    # Using filter(has_text=...) is robust against special chars
                    btn = page.locator("button:visible").filter(has_text=variant).first
                    btn.wait_for(state="visible", timeout=500)
                    btn.click()
                    clicked = True
                    time.sleep(0.4)
                    print_success(f"  Cliqué: {word}")
                except PlaywrightTimeout:
                    continue
            if not clicked:
                print_info(f"  Fallback: {word}")
                try:
                    all_buttons = page.locator("button:visible").all()
                    for btn in all_buttons:
                        try:
                            btn_text = btn.inner_text().strip()
                            for variant in variants:
                                if texts_match(btn_text, variant):
                                    btn.click()
                                    clicked = True
                                    time.sleep(0.4)
                                    print_success(f"  Cliqué (fallback): {word}")
                                    break
                            if clicked:
                                break
                        except Exception:
                            continue
                except Exception:
                    pass
            if not clicked:
                print_error(f"  Non trouvé: {word}")
                return False
        time.sleep(0.5)
        if not wait_and_click(page, SELECTORS["validate_button"], timeout=3000):
            return False
        time.sleep(0.5)
        wait_and_click(page, SELECTORS["continue_button"], timeout=3000)
        time.sleep(0.5)
        print_success("Ordre rempli")
        return True
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def check_retry_button(page, click=False):
    try:
        selectors = ['button:has-text("Réessayer")', 'button:has-text("Ressayer")']
        for selector in selectors:
            try:
                retry_btn = page.locator(selector).first
                retry_btn.wait_for(state="visible", timeout=2000)
                if click:
                    print_info("Clic Réessayer...")
                    retry_btn.click()
                    time.sleep(2)
                    print_success("Retour au début")
                return True
            except PlaywrightTimeout:
                continue
        return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False
