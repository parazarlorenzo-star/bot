import random
from config import SLOT_SYMBOLS

def spin_slots(bet: float) -> dict:
    """Spin the slot machine and return result"""
    symbols = list(SLOT_SYMBOLS.keys())
    weights = [SLOT_SYMBOLS[s]["weight"] for s in symbols]
    
    # Spin 3 reels
    reels = random.choices(symbols, weights=weights, k=3)
    
    result = {
        "reels": reels,
        "display": f"{reels[0]} | {reels[1]} | {reels[2]}",
        "win": False,
        "multiplier": 0,
        "profit": -bet,
    }
    
    # Check win conditions
    if reels[0] == reels[1] == reels[2]:
        # Triple match
        mult = SLOT_SYMBOLS[reels[0]]["multiplier"]
        result["win"] = True
        result["multiplier"] = mult
        result["profit"] = bet * mult - bet
        result["win_type"] = f"TRIPLE {reels[0]}"
    elif reels[0] == reels[1] or reels[1] == reels[2]:
        # Double match - small win
        matched = reels[0] if reels[0] == reels[1] else reels[1]
        mult = max(1.0, SLOT_SYMBOLS[matched]["multiplier"] * 0.3)
        result["win"] = True
        result["multiplier"] = round(mult, 2)
        result["profit"] = bet * mult - bet
        result["win_type"] = f"PAIRE {matched}"
    
    return result

def format_slots_result(result: dict, bet: float, new_balance: float) -> str:
    display = result["display"]
    
    if result["win"]:
        profit = result["profit"]
        emoji = "🎉" if result["multiplier"] >= 5 else "✅"
        return f"""
🎰 *SLOT MACHINE* 🎰

┌─────────────────────┐
│  {display}  │
└─────────────────────┘

{emoji} *{result.get('win_type', 'WIN')}!*
💰 Multiplicateur: *x{result['multiplier']}*
📈 Gain: *+${profit:.2f} USDT*
💼 Solde: `${new_balance:.2f}`
"""
    else:
        return f"""
🎰 *SLOT MACHINE* 🎰

┌─────────────────────┐
│  {display}  │
└─────────────────────┘

❌ *Pas de chance cette fois!*
📉 Perdu: *-${bet:.2f} USDT*
💼 Solde: `${new_balance:.2f}`
"""
