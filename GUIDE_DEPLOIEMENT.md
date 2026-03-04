# 🎰 Casino Bot Telegram — Guide de déploiement

## Structure du projet
```
casino-bot/
├── bot.py              ← Point d'entrée principal
├── config.py           ← Configuration (modifie ici)
├── requirements.txt    ← Dépendances Python
├── .env.example        ← Template de configuration
├── Procfile            ← Pour Railway/Render
├── handlers/
│   ├── start.py        ← /start et /menu
│   ├── wallet.py       ← /wallet, /deposit, /withdraw
│   ├── games.py        ← Commandes des jeux
│   ├── admin.py        ← Panel admin
│   └── callbacks.py    ← Tous les boutons inline
├── games/
│   ├── slots.py        ← Machine à sous
│   ├── blackjack.py    ← Blackjack
│   └── other_games.py  ← Roulette, Dés, Mines, CoinFlip
└── utils/
    ├── db.py           ← Base de données SQLite
    └── ui.py           ← Claviers et messages
```

---

## ✅ ÉTAPE 1 — Créer ton bot Telegram

1. Ouvre Telegram et cherche **@BotFather**
2. Envoie `/newbot`
3. Donne un nom (ex: "Mon Casino")
4. Donne un username (ex: "monCasinoBot" — doit finir par "bot")
5. **Copie le TOKEN** qu'il te donne (format: `1234567890:AAFxxx...`)

---

## ✅ ÉTAPE 2 — Configurer le fichier .env

1. Copie `.env.example` et renomme-le `.env`
2. Remplis toutes les valeurs:

```env
BOT_TOKEN=TON_TOKEN_ICI
ADMIN_IDS=TON_ID_TELEGRAM
TON_WALLET=TON_ADRESSE_TON
USDT_WALLET=TON_ADRESSE_USDT
```

**Comment trouver ton ID Telegram?**
→ Va sur @userinfobot et envoie `/start`

---

## ✅ ÉTAPE 3 — Déploiement GRATUIT sur Railway

Railway te permet de faire tourner ton bot 24h/24 gratuitement.

### 3.1 — Prépare ton code sur GitHub
1. Crée un compte sur [github.com](https://github.com)
2. Crée un **nouveau repository** (clique sur "New")
3. Upload tous les fichiers du dossier `casino-bot/`
4. **NE METS PAS le fichier `.env`** sur GitHub (il contient tes secrets!)

### 3.2 — Déploie sur Railway
1. Va sur [railway.app](https://railway.app) et connecte ton GitHub
2. Clique **"New Project"** → **"Deploy from GitHub repo"**
3. Sélectionne ton repository
4. Railway va détecter automatiquement Python

### 3.3 — Configure les variables d'environnement
Dans Railway, va dans ton projet → **"Variables"** et ajoute:

| Clé | Valeur |
|-----|--------|
| `BOT_TOKEN` | Ton token BotFather |
| `ADMIN_IDS` | Ton ID Telegram |
| `TON_WALLET` | Ton adresse TON |
| `USDT_WALLET` | Ton adresse USDT |

### 3.4 — Lancer le bot
1. Va dans **"Settings"** → **"Start Command"**: `python bot.py`
2. Clique **"Deploy"**
3. Regarde les logs — tu dois voir: `🎰 Casino Bot started!`

---

## ✅ ÉTAPE 4 — Configurer les commandes du bot

Dans **@BotFather**, envoie `/setcommands` puis sélectionne ton bot et colle:

```
start - 🎰 Ouvrir le casino
menu - 📋 Menu principal
wallet - 💰 Mon portefeuille
deposit - ➕ Déposer des fonds
withdraw - ➖ Retirer des fonds
slots - 🎰 Machine à sous
blackjack - 🃏 Blackjack
dice - 🎲 Dés
roulette - 🎡 Roulette
mines - 💣 Mines
coinflip - 🪙 Pile ou face
admin - 🔐 Panel admin
```

---

## ✅ ÉTAPE 5 — Gestion des dépôts (manuel)

Pour l'instant, les dépôts sont **manuels**. Quand un joueur dépose:

1. Il t'envoie le hash de sa transaction
2. Vérifie sur [tonviewer.com](https://tonviewer.com) ou [tronscan.org](https://tronscan.org)
3. Ajoute le solde manuellement via la commande admin:

```
/addbalance 123456789 10.0
```
(Remplace 123456789 par l'ID du joueur et 10.0 par le montant)

---

## 🔧 Commandes Admin

| Commande | Description |
|----------|-------------|
| `/admin` | Panel admin principal |
| `/addbalance <id> <montant>` | Ajouter du solde |
| `/setbalance <id> <montant>` | Définir le solde |

---

## ⚙️ Personnalisation dans config.py

```python
MIN_BET = 0.1          # Mise minimum
MAX_BET = 1000.0       # Mise maximum
MIN_DEPOSIT = 1.0      # Dépôt minimum
WELCOME_BONUS = 5.0    # Bonus bienvenue (mettre 0 pour désactiver)
HOUSE_EDGE = 0.03      # Avantage casino (3%)
```

---

## ❓ Problèmes fréquents

**Bot ne répond pas?**
→ Vérifie les logs Railway, le BOT_TOKEN est sûrement incorrect

**Erreur "Unauthorized"?**
→ Ton token est invalide, recrée-le via @BotFather

**Erreur de module?**
→ Vérifie que requirements.txt est bien dans le repo GitHub

---

## 📞 Structure des jeux

| Jeu | Méthode | Multiplicateur |
|-----|---------|---------------|
| 🎰 Slots | Aléatoire | x2 à x20 |
| 🃏 Blackjack | Standard | x1.5 (BJ), x1 (win) |
| 🎲 Dés | Choix | x2 (H/L), x6 (exact) |
| 🎡 Roulette | Choix | x2 à x35 |
| 💣 Mines | Progression | x1.04 → x1,200,000 |
| 🪙 Coin Flip | 50/50 | x2 |
