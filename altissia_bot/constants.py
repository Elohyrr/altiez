"""
Constantes, sélecteurs et listes de mots pour le bot Altissia.
"""

SELECTORS = {
    "input_field": 'input.c-iJOJc, input[type="text"]',
    "validate_button": 'button:has-text("Valider")',
    "correct_answer": "span.c-gUxMKR-bkfbUO-isCorrect-true",
    "continue_button": 'button.c-jUtMbh, button.c-lfgsZH:has-text("Continuer")',
    "retry_button": 'button:has-text("Réessayer"), button:has-text("Ressayer")',
}

BLACKLIST_WORDS = [
    "Incorrect",
    "Correct",
    "Wrong",
    "Faux",
    "Vrai",
    "Error",
    "Success",
    "Valider",
    "Continuer",
    "Revenir",
    "Ressayer",
    "Réessayer",
    "Pause",
    "Play",
    "Mute",
    "Skip",
    "Select the right answer",
    "Choose",
    "Click",
    "Put the elements in the right order",
    "Sélectionnez le premier élément",
    "Listen to",
    "Max is writing",
    "Accueil",
    "Toutes les leçons",
    "Actualités",
]

# Liste des variantes de vert utilisées par Altissia (pour référence)
GREEN_COLORS = [
    "rgb(26, 179, 92)",
    "rgb(233, 251, 241)",
    "rgb(34, 197, 94)",
    "rgb(22, 163, 74)",
    "rgb(16, 185, 129)",
    "rgb(5, 150, 105)",
    "rgb(0, 128, 0)",
    "rgb(0, 255, 0)",
    "rgb(76, 175, 80)",
    "rgb(46, 125, 50)",
    "rgb(67, 160, 71)",
    "rgb(102, 187, 106)",
    "rgb(139, 195, 74)",
    "rgb(156, 204, 101)",
    "rgb(200, 230, 201)",
    "rgb(165, 214, 167)",
]
