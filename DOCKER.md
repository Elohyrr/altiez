# 🐳 Docker Setup - Solution Définitive

## 🎯 Pourquoi Docker ?

Le bot Altiez dépend de Playwright et Chromium, qui utilisent les bibliothèques TLS système (OpenSSL/NSS). Sur certaines distributions Ubuntu/Debian, des incompatibilités SSL peuvent empêcher la connexion à Altissia.

**Docker résout ce problème définitivement** en figeant l'environnement complet :
- ✅ OS Ubuntu stable
- ✅ OpenSSL compatible
- ✅ Chromium fonctionnel
- ✅ Certificats valides
- ✅ Même comportement sur toutes les machines

---

## 📦 Prérequis

### Linux (Ubuntu/Debian/LMDE)

```bash
# Installer Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER

# Redémarrer la session ou exécuter
newgrp docker
```

### Vérification

```bash
docker --version
docker-compose --version
```

---

## 🚀 Installation & Lancement

### Méthode 1 : Docker Compose (recommandé)

**1. Configuration**

Copier le fichier d'environnement :

```bash
cp .env.example .env
```

Éditer `.env` avec vos identifiants :

```env
ALTISSIA_USERNAME=your_email@example.com
ALTISSIA_PASSWORD=your_password
ALTISSIA_URL=https://www.altissia.com/
```

**2. Autoriser l'affichage X11**

```bash
xhost +local:root
```

**3. Lancer le bot**

```bash
docker-compose run --rm altiez
```

Le navigateur s'ouvrira sur votre écran et vous pourrez interagir avec le terminal.

**4. Arrêter le bot**

```bash
# Ctrl+C dans le terminal
# Le container sera automatiquement supprimé grâce à --rm
```

---

### Méthode 2 : Docker manuel

**1. Build de l'image**

```bash
docker build -t altiez:latest .
```

**2. Lancer le container**

```bash
# Autoriser X11
xhost +local:root

# Lancer avec UI
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -e ALTISSIA_USERNAME="your_email@example.com" \
  -e ALTISSIA_PASSWORD="your_password" \
  -e ALTISSIA_URL="https://www.altissia.com/" \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/scan_results:/app/scan_results \
  -v $(pwd)/html_snapshots:/app/html_snapshots \
  --device /dev/dri \
  --shm-size=2g \
  --network host \
  altiez:latest
```

---

## 🎮 Modes d'utilisation

### Mode normal (UI visible)

```bash
docker-compose run --rm altiez
```

### Mode headless (pas d'UI)

```bash
docker-compose run --rm altiez python run.py --headless
```

### Mode analyse

```bash
docker-compose run --rm altiez python run.py --analyze
```

### Mode scan

```bash
docker-compose run --rm altiez python run.py --scan
```

---

## 🔧 Configuration avancée

### Wayland (au lieu de X11)

Si vous utilisez Wayland, la configuration X11 ne marchera pas directement. Deux solutions :

**Option A : Passer en session Xorg**

Déconnectez-vous et sélectionnez "Ubuntu on Xorg" à la connexion.

**Option B : VNC dans Docker** (solution universelle)

Créer `Dockerfile.vnc` :

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

# Installer VNC
RUN apt-get update && apt-get install -y \
    x11vnc \
    xvfb \
    fluxbox \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Script de démarrage VNC
RUN echo '#!/bin/bash\n\
Xvfb :99 -screen 0 1280x720x16 &\n\
export DISPLAY=:99\n\
fluxbox &\n\
x11vnc -display :99 -forever -nopw -rfbport 5900 &\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "run.py"]
```

Lancer :

```bash
docker build -f Dockerfile.vnc -t altiez-vnc .

docker run -it --rm \
  -p 5900:5900 \
  -e ALTISSIA_USERNAME="your@email.com" \
  -e ALTISSIA_PASSWORD="password" \
  -e ALTISSIA_URL="https://www.altissia.com/" \
  --shm-size=2g \
  altiez-vnc
```

Connectez-vous avec un client VNC (Remmina, TigerVNC...) sur `localhost:5900`.

---

## 🧪 Debug

### Le navigateur ne s'affiche pas

**Cause** : Problème X11

**Solution** :

```bash
# Vérifier DISPLAY
echo $DISPLAY

# Réautoriser X11
xhost +local:root

# Vérifier que le container accède à X11
docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix altiez:latest env | grep DISPLAY
```

### Erreur "Cannot open display"

**Cause** : Variable DISPLAY non définie ou X11 non autorisé

**Solution** :

```bash
export DISPLAY=:0
xhost +local:root
```

### Erreur SSL/TLS malgré Docker

**Ne devrait JAMAIS arriver** car l'image Playwright officielle embarque tout ce qui est nécessaire.

Si ça arrive quand même :

1. Vérifier que vous utilisez bien l'image `mcr.microsoft.com/playwright/python:v1.42.0-jammy`
2. Rebuild sans cache : `docker-compose build --no-cache`
3. Vérifier votre connexion réseau (proxy/firewall)

### Container trop lent

**Cause** : Manque de ressources

**Solution** : Augmenter la RAM allouée à Docker (dans Docker Desktop ou via daemon.json)

---

## 📁 Volumes persistants

Les données suivantes sont sauvegardées sur l'hôte :

- `./config/` → Sessions et cookies
- `./scan_results/` → Résultats des scans
- `./html_snapshots/` → Captures HTML

Elles sont partagées entre les exécutions du container.

---

## 🧹 Nettoyage

### Supprimer les containers arrêtés

```bash
docker-compose down
```

### Supprimer l'image

```bash
docker rmi altiez:latest
```

### Nettoyage complet Docker

```bash
docker system prune -a
```

---

## ✅ Avantages de la solution Docker

| Problème | Solution native | Solution Docker |
|----------|----------------|-----------------|
| SSL cassé sur Ubuntu | ❌ Impossible à fiabiliser | ✅ Résolu définitivement |
| OpenSSL incompatible | ❌ Peut casser le système | ✅ Environnement isolé |
| Chromium manquant | ❌ Installation manuelle | ✅ Déjà installé |
| Certificats expirés | ❌ Mise à jour système | ✅ Toujours à jour |
| "Chez moi ça marche" | ❌ Environnements différents | ✅ Identique partout |

---

## 🚫 Ce qu'il NE FAUT PLUS faire

❌ `apt install chromium-browser`
❌ Réparer OpenSSL manuellement
❌ Réinstaller Python/Playwright en local
❌ Bidouiller les certificats système
❌ Croire qu'un `apt update` va sauver une machine éclatée

➡️ **Docker règle TOUT ça**

---

## 💡 Tips

### Raccourci shell

Ajouter à `~/.bashrc` :

```bash
alias altiez='cd /path/to/altiez && xhost +local:root && docker-compose up'
```

### Rebuild rapide après modification du code

```bash
docker-compose up --build
```

### Exécuter des commandes dans le container

```bash
docker-compose run altiez bash
```

---

## 🆘 Support

Si Docker ne fonctionne pas :

1. Vérifier les prérequis (Docker installé, user dans groupe docker)
2. Vérifier X11 (variable DISPLAY, xhost)
3. Tester avec l'image de base :

```bash
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  mcr.microsoft.com/playwright/python:v1.42.0-jammy \
  python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(headless=False); b.close()"
```

Si ça marche → le problème vient du code
Si ça marche pas → problème de config Docker/X11

---

**Made with 🐳 for reliable automation**
