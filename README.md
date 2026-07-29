# SyncMPV

Un clone minimal de [Syncplay](https://syncplay.pl) avec un lecteur **MPV
intégré directement dans la fenêtre** (pas de fenêtre externe à lancer à
côté) — via `libmpv` / `python-mpv`.

## Architecture

- `server.py` : serveur central (asyncio). Gère des "salons" (rooms) et
  rediffuse l'état de lecture (lecture/pause, position, fichier) à tous
  les clients connectés à un même salon.
- `client.py` : client PyQt5. La fenêtre vidéo est un `mpv.MPV` intégré
  (rendu directement dans un `QFrame`, via son `winId()`), avec un
  panneau latéral pour la connexion, la liste des utilisateurs et le chat.

## Installation

### 1. Dépendance système : libmpv

```bash
# Debian / Ubuntu
sudo apt install libmpv2   # ou libmpv-dev / libmpv1 selon la version de la distro

# Arch
sudo pacman -S mpv

# macOS (Homebrew)
brew install mpv
```

### 2. Dépendances Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

### Démarrer le serveur (sur une machine accessible par tous, ou en local pour tester)

```bash
python3 server.py --host 0.0.0.0 --port 8999
```

Si le serveur est exposé sur internet (par ex. via un service de DNS
dynamique comme No-IP), il est fortement recommandé d'ajouter un mot
de passe pour éviter que n'importe qui puisse rejoindre votre salon :

```bash
python3 server.py --host 0.0.0.0 --port 8999 --password votremotdepasse
```

Chaque client devra alors renseigner le même mot de passe dans le
champ correspondant du panneau de connexion.

### Démarrer un client

```bash
python3 client.py
```

Dans la fenêtre :
1. Renseigner l'hôte/port du serveur, un nom de salon (identique pour
   tout le monde) et un pseudo, puis cliquer sur **Se connecter**.
2. Cliquer sur **Ouvrir un fichier…** pour choisir une vidéo locale
   (chaque participant doit avoir le même fichier sur son disque —
   comme avec Syncplay, seul l'état de lecture est synchronisé, pas le
   flux vidéo lui-même).
3. Lecture, pause et déplacement dans la vidéo sont automatiquement
   répercutés chez tous les autres participants du salon.

## Comment fonctionne la synchronisation

- Chaque client envoie son état (pause/position/fichier) au serveur
  quand un événement local se produit (pause, seek) ou toutes les
  `STATE_SEND_INTERVAL` secondes (3s par défaut, réglable dans
  `client.py`).
- Le serveur retient le dernier état connu du salon et le redonne à
  tout nouveau client qui rejoint, puis rediffuse chaque mise à jour
  aux autres.
- Un client qui reçoit un état distant ne resynchronise sa position
  que si l'écart dépasse `SEEK_THRESHOLD` (1s par défaut), pour éviter
  les micro-saccades.
- Un court délai (`IGNORE_ECHO_WINDOW`) évite qu'un client renvoie
  immédiatement l'état qu'il vient de recevoir, ce qui provoquerait des
  boucles inutiles.

## Limites connues / pistes d'amélioration

- Pas de compensation fine de latence réseau (ping/pong basique déjà
  présent côté protocole, mais pas encore exploité pour corriger la
  position exacte).
- Pas de gestion de "playlist" partagée, uniquement un fichier à la fois.
- Pas de chiffrement/authentification : à utiliser sur un réseau de
  confiance (VPN, LAN) ou à mettre derrière un reverse proxy TLS pour
  un usage sur Internet ouvert.
- Le chat et la liste d'utilisateurs sont volontairement basiques.

Toutes ces pistes sont faciles à ajouter dans `server.py` /
`client.py` si besoin — dites-moi ce que vous voulez approfondir en
premier.
