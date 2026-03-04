import random
import json

DECK = []
for suit in ["S", "H", "D", "C"]:
    for value in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]:
        DECK.append(f"{value}{suit}")

def create_deck(num_decks=6):
    deck = DECK * num_decks
    random.shuffle(deck)
    return deck

def card_value(card: str) -> int:
    v = card[:-1]
    if v in ["J", "Q", "K"]:
        return 10
    if v == "A":
        return 11
    return int(v)

def hand_value(hand: list) -> int:
    total = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c[:-1] == "A")
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def is_blackjack(hand: list) -> bool:
    return len(hand) == 2 and hand_value(hand) == 21

def can_double(hand: list) -> bool:
    return len(hand) == 2

def can_split(hand: list) -> bool:
    return len(hand) == 2 and card_value(hand[0]) == card_value(hand[1])

def dealer_should_hit(hand: list) -> bool:
    return hand_value(hand) < 17

def new_game(bet: float) -> dict:
    deck = create_deck()
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]
    return {
        "player": player,
        "dealer": dealer,
        "deck": deck,
        "bet": bet,
        "status": "playing",
        "doubled": False,
    }

def hit(state: dict) -> dict:
    state["player"].append(state["deck"].pop())
    if hand_value(state["player"]) > 21:
        state["status"] = "bust"
    return state

def stand(state: dict) -> dict:
    # Dealer plays
    while dealer_should_hit(state["dealer"]):
        state["dealer"].append(state["deck"].pop())
    
    player_v = hand_value(state["player"])
    dealer_v = hand_value(state["dealer"])
    
    if dealer_v > 21 or player_v > dealer_v:
        state["status"] = "player_win"
    elif player_v < dealer_v:
        state["status"] = "dealer_win"
    else:
        state["status"] = "push"
    return state

def double_down(state: dict) -> dict:
    state["bet"] *= 2
    state["doubled"] = True
    state["player"].append(state["deck"].pop())
    if hand_value(state["player"]) > 21:
        state["status"] = "bust"
    else:
        state = stand(state)
    return state

def surrender(state: dict) -> dict:
    state["status"] = "surrender"
    return state

def calculate_profit(state: dict) -> float:
    bet = state["bet"]
    status = state["status"]
    
    if status == "player_win":
        if is_blackjack(state["player"]) and not state["doubled"]:
            return bet * 1.5  # Blackjack pays 3:2
        return bet
    elif status == "push":
        return 0
    elif status == "surrender":
        return -bet / 2
    else:  # bust, dealer_win
        return -bet

def format_hand(hand: list, hide_second=False) -> str:
    suits = {"S": "♠️", "H": "♥️", "D": "♦️", "C": "♣️"}
    result = ""
    for i, card in enumerate(hand):
        if hide_second and i == 1:
            result += "🂠 "
        else:
            value, suit = card[:-1], card[-1]
            result += f"{value}{suits.get(suit, suit)} "
    return result.strip()

def format_blackjack_state(state: dict, show_dealer=False) -> str:
    player_v = hand_value(state["player"])
    
    if show_dealer:
        dealer_v = hand_value(state["dealer"])
        dealer_display = format_hand(state["dealer"])
        dealer_score = f"({dealer_v})"
    else:
        dealer_display = format_hand(state["dealer"], hide_second=True)
        dealer_score = f"({card_value(state['dealer'][0])}+?)"
    
    player_display = format_hand(state["player"])
    
    status_map = {
        "player_win": "🏆 GAGNÉ!",
        "dealer_win": "❌ PERDU!",
        "bust": "💥 BUST!",
        "push": "🤝 ÉGALITÉ",
        "surrender": "🏳️ ABANDONNÉ",
        "playing": "🃏 Ton tour...",
    }
    
    msg = f"""
🃏 *BLACKJACK*

🏦 Croupier: {dealer_display} {dealer_score}

👤 Toi: {player_display} *({player_v})*

💰 Mise: `${state['bet']:.2f} USDT`
"""
    
    if state["status"] != "playing":
        profit = calculate_profit(state)
        msg += f"\n{status_map.get(state['status'], '')}"
        if profit > 0:
            msg += f"\n📈 Gain: *+${profit:.2f}*"
        elif profit < 0:
            msg += f"\n📉 Perdu: *${profit:.2f}*"
        else:
            msg += f"\n↩️ Mise remboursée"
    
    return msg
