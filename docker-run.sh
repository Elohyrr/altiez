#!/bin/bash
# Script de démarrage rapide pour Altiez avec Docker
# Usage: ./docker-run.sh

set -e

echo "🐳 Altiez Docker - Démarrage rapide"
echo ""

# Vérifier que .env existe
if [ ! -f .env ]; then
    echo "❌ Fichier .env non trouvé!"
    echo "📝 Création depuis .env.example..."
    cp .env.example .env
    echo "✅ Fichier .env créé"
    echo ""
    echo "⚠️  IMPORTANT: Éditez .env avec vos identifiants avant de continuer"
    echo "   nano .env"
    echo ""
    exit 1
fi

# Autoriser X11
echo "🖥️  Autorisation X11..."
xhost +local:root 2>/dev/null || {
    echo "⚠️  Impossible d'autoriser X11 (xhost non trouvé ou pas de serveur X)"
    echo "   Le navigateur ne s'affichera peut-être pas"
}

echo ""
echo "🚀 Lancement du container..."
echo ""

# Lancer docker-compose en mode interactif
docker-compose run --rm altiez
