import random

# ══════════════════════════════════════════
#  ROULETTE
# ══════════════════════════════════════════

ROULETTE_REDS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

def spin_roulette() -> dict:
    number = random.randint(0, 36)
    color = "green" if number == 0 else ("red" if number in ROULETTE_REDS else "black")
    return {"number": number, "color": color}

def roulette_win(spin: dict, bet_type: str, bet: float) -> dict:
    n = spin["number"]
    c = spin["color"]
    
    result = {"win": False, "multiplier": 0, "profit": -bet}
    
    if bet_type == "red" and c == "red":
        result = {"win": True, "multiplier": 2, "profit": bet}
    elif bet_type == "black" and c == "black":
        result = {"win": True, "multiplier": 2, "profit": bet}
    elif bet_type == "zero" and n == 0:
        result = {"win": True, "multiplier": 35, "profit": bet * 35}
    elif bet_type == "1-12" and 1 <= n <= 12:
        result = {"win": True, "multiplier": 3, "profit": bet * 2}
    elif bet_type == "13-24" and 13 <= n <= 24:
        result = {"win": True, "multiplier": 3, "profit": bet * 2}
    elif bet_type == "25-36" and 25 <= n <= 36:
        result = {"win": True, "multiplier": 3, "profit": bet * 2}
    elif bet_type == "even" and n != 0 and n % 2 == 0:
        result = {"win": True, "multiplier": 2, "profit": bet}
    elif bet_type == "odd" and n % 2 == 1:
        result = {"win": True, "multiplier": 2, "profit": bet}
    elif bet_type.startswith("num_") and str(n) == bet_type[4:]:
        result = {"win": True, "multiplier": 36, "profit": bet * 35}
    
    return result

def format_roulette_result(spin: dict, result: dict, bet_type: str, bet: float, balance: float) -> str:
    n = spin["number"]
    c = spin["color"]
    color_emoji = {"red": "🔴", "black": "⚫", "green": "🟢"}.get(c, "⚪")
    
    BET_NAMES = {
        "red": "Rouge", "black": "Noir", "zero": "Zéro",
        "1-12": "1-12", "13-24": "13-24", "25-36": "25-36",
        "even": "Pair", "odd": "Impair",
    }
    bet_name = BET_NAMES.get(bet_type, bet_type.replace("num_", "Numéro "))
    
    msg = f"""
🎡 *ROULETTE*

La bille tombe sur...

╔═══════════════╗
║  {color_emoji} *{n}*  ║
╚═══════════════╝

🎯 Ton pari: *{bet_name}*
"""
    if result["win"]:
        msg += f"🎉 *GAGNÉ! x{result['multiplier']}*\n📈 Gain: *+${result['profit']:.2f} USDT*"
    else:
        msg += f"❌ *PERDU!*\n📉 Perdu: *-${bet:.2f} USDT*"
    
    msg += f"\n💼 Solde: `${balance:.2f}`"
    return msg

# ══════════════════════════════════════════
#  DICE
# ══════════════════════════════════════════

def roll_dice(prediction: str, bet: float) -> dict:
    """
    prediction: 'high' (4-6), 'low' (1-3), 'exact_X'
    """
    roll = random.randint(1, 6)
    win = False
    multiplier = 0
    
    if prediction == "high" and roll >= 4:
        win, multiplier = True, 2
    elif prediction == "low" and roll <= 3:
        win, multiplier = True, 2
    elif prediction.startswith("exact_") and str(roll) == prediction[6:]:
        win, multiplier = True, 6
    
    profit = bet * (multiplier - 1) if win else -bet
    
    return {
        "roll": roll,
        "prediction": prediction,
        "win": win,
        "multiplier": multiplier,
        "profit": profit,
    }

DICE_EMOJIS = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣"}

def format_dice_result(result: dict, bet: float, balance: float) -> str:
    die = DICE_EMOJIS.get(result["roll"], str(result["roll"]))
    pred_names = {
        "high": "Haut (4-6)", "low": "Bas (1-3)",
    }
    for i in range(1, 7):
        pred_names[f"exact_{i}"] = f"Exact {DICE_EMOJIS[i]}"
    
    pred = pred_names.get(result["prediction"], result["prediction"])
    
    msg = f"""
🎲 *DÉS*

╔═════════╗
║   {die}   ║
╚═════════╝

🎯 Pari: *{pred}*
"""
    if result["win"]:
        msg += f"✅ *GAGNÉ! x{result['multiplier']}*\n📈 *+${result['profit']:.2f} USDT*"
    else:
        msg += f"❌ *PERDU!*\n📉 *-${bet:.2f} USDT*"
    
    msg += f"\n💼 Solde: `${balance:.2f}`"
    return msg

# ══════════════════════════════════════════
#  COIN FLIP
# ══════════════════════════════════════════

def flip_coin(choice: str, bet: float) -> dict:
    result = random.choice(["heads", "tails"])
    win = result == choice
    profit = bet if win else -bet
    return {"result": result, "choice": choice, "win": win, "profit": profit}

def format_coinflip_result(result: dict, bet: float, balance: float) -> str:
    emoji = "🦅" if result["result"] == "heads" else "🌊"
    choice_emoji = "🦅" if result["choice"] == "heads" else "🌊"
    choice_name = "Face" if result["choice"] == "heads" else "Pile"
    result_name = "Face" if result["result"] == "heads" else "Pile"
    
    return f"""
🪙 *COIN FLIP*

La pièce tourne...

╔═══════════════╗
║     {emoji} *{result_name}*     ║
╚═══════════════╝

🎯 Ton choix: {choice_emoji} *{choice_name}*

{"🎉 *GAGNÉ! x2*\n📈 *+${:.2f} USDT*".format(result['profit']) if result['win'] else f"❌ *PERDU!*\n📉 *-${bet:.2f} USDT*"}
💼 Solde: `${balance:.2f}`
"""

# ══════════════════════════════════════════
#  MINES
# ══════════════════════════════════════════

def new_mines_game(bet: float, num_mines: int) -> dict:
    positions = list(range(25))
    mines = random.sample(positions, num_mines)
    return {
        "bet": bet,
        "num_mines": num_mines,
        "mines": mines,
        "revealed": [],
        "status": "playing",
        "step": 0,
    }

MINES_MULTIPLIERS = {
    1:  [1.04, 1.09, 1.15, 1.22, 1.30, 1.40, 1.52, 1.68, 1.88, 2.14, 2.50, 3.00, 3.75, 5.00, 7.50],
    3:  [1.12, 1.28, 1.50, 1.80, 2.20, 2.75, 3.55, 4.75, 6.60, 9.50, 14.5, 24.0, 45.0, 100.0, 300.0],
    5:  [1.22, 1.55, 2.00, 2.65, 3.60, 5.00, 7.20, 10.8, 16.8, 27.5, 47.5, 88.0, 180.0, 420.0, 1200.0],
    10: [1.55, 2.50, 4.20, 7.50, 14.0, 28.0, 60.0, 140.0, 370.0, 1200.0, 4500.0, 20000.0, 100000.0, 600000.0, 3000000.0],
}

def get_mines_multiplier(num_mines: int, steps: int) -> float:
    mults = MINES_MULTIPLIERS.get(num_mines, MINES_MULTIPLIERS[1])
    idx = min(steps - 1, len(mults) - 1)
    return mults[idx] if steps > 0 else 1.0

def reveal_tile(state: dict, position: int) -> dict:
    if position in state["mines"]:
        state["status"] = "exploded"
    else:
        state["revealed"].append(position)
        state["step"] += 1
        if len(state["revealed"]) == 25 - state["num_mines"]:
            state["status"] = "completed"
    return state

def cashout_mines(state: dict) -> dict:
    state["status"] = "cashed_out"
    return state

def mines_profit(state: dict) -> float:
    if state["status"] == "exploded":
        return -state["bet"]
    mult = get_mines_multiplier(state["num_mines"], state["step"])
    return state["bet"] * mult - state["bet"]
