#!/bin/bash

# Script d'installation rapide pour le bot Altissia

echo "🤖 Installation du Bot Altissia"
echo "================================"
echo ""

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    echo "   Installez Python 3 puis relancez ce script"
    exit 1
fi

echo "✅ Python 3 détecté"
echo ""

# Vérifier que pip est installé
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip n'est pas installé"
    echo "   Installez pip puis relancez ce script"
    exit 1
fi

echo "✅ pip détecté"
echo ""

# Installation des dépendances Python
echo "📦 Installation des dépendances Python..."
pip3 install -r requirements.txt || pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'installation des dépendances"
    exit 1
fi

echo "✅ Dépendances Python installées"
echo ""

# Installation de Chromium pour Playwright
echo "🌐 Installation de Chromium pour Playwright..."
playwright install chromium

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'installation de Chromium"
    exit 1
fi

echo "✅ Chromium installé"
echo ""

# Création du fichier .env s'il n'existe pas
if [ ! -f .env ]; then
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "✅ Fichier .env créé"
    echo ""
    echo "⚠️  IMPORTANT : Éditez le fichier .env et ajoutez vos identifiants Altissia"
    echo "   Ouvrez .env et remplacez :"
    echo "   - ALTISSIA_USERNAME=votre_email@example.com"
    echo "   - ALTISSIA_PASSWORD=votre_mot_de_passe"
else
    echo "ℹ️  Fichier .env existant (non modifié)"
fi

echo ""

# Rendre main.py exécutable
chmod +x main.py
echo "✅ main.py rendu exécutable"
echo ""

echo "================================"
echo "🎉 Installation terminée !"
echo "================================"
echo ""
echo "Prochaines étapes :"
echo "1. Éditez le fichier .env avec vos identifiants"
echo "2. Lancez le bot avec : python main.py"
echo ""
echo "Pour plus d'aide : consultez QUICKSTART.md ou README.md"
echo ""
