import os
from dotenv import load_dotenv

load_dotenv()

# ══════════════════════════════════════════
#  🔑 CONFIGURATION — REMPLACE CES VALEURS
# ══════════════════════════════════════════

BOT_TOKEN = os.getenv("BOT_TOKEN", "8673116882:AAGS8jXfEZpkUpWhLRi1xQivvgDW32dBjmU")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "8585602420").split(",")))

# TON Wallet (pour recevoir les dépôts)
TON_WALLET_ADDRESS = os.getenv("TON_WALLET", "UQBTBzKX1VTuJg86OZFAZmT20M_YHiqyTdKH5_emMvjJe8-P")
USDT_WALLET_ADDRESS = os.getenv("USDT_WALLET", "0xFF9969AEDd9F3B5BE6c70fd137C283cf04b65b82")

# Base de données
DB_PATH = "data/casino.db"

# Limites du casino
MIN_BET = 0.1          # Mise minimum en USDT
MAX_BET = 1000.0       # Mise maximum en USDT
MIN_DEPOSIT = 1.0      # Dépôt minimum
MIN_WITHDRAW = 5.0     # Retrait minimum

# House edge (avantage du casino %)
HOUSE_EDGE = 0.03      # 3%

# Bonus bienvenue
WELCOME_BONUS = 0.0    # Mettre ex: 5.0 pour 5 USDT offerts

# Symboles Slot Machine
SLOT_SYMBOLS = {
    "🍒": {"weight": 30, "multiplier": 2},
    "🍋": {"weight": 25, "multiplier": 3},
    "🍊": {"weight": 20, "multiplier": 4},
    "🍇": {"weight": 15, "multiplier": 5},
    "💎": {"weight": 7,  "multiplier": 10},
    "7️⃣": {"weight": 3,  "multiplier": 20},
}

# Multiplicateurs Mines
MINES_MULTIPLIERS = {
    1:  {1: 1.08, 2: 1.17, 3: 1.28, 4: 1.40, 5: 1.54},
    3:  {1: 1.24, 2: 1.55, 3: 1.95, 4: 2.50, 5: 3.27},
    5:  {1: 1.45, 2: 2.12, 3: 3.18, 4: 4.93, 5: 7.93},
    10: {1: 2.0,  2: 4.0,  3: 8.5,  4: 18.0, 5: 42.0},
}
