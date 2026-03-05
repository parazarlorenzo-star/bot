import random, asyncio
from telegram import Update
from telegram.ext import ContextTypes
from database import get_balance, add_balance, remove_balance

# In-memory game sessions
GAMES = {}

SUITS  = ["♠", "♥", "♦", "♣"]
RANKS  = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]

SUIT_EMOJI = {"♠": "♠️", "♥": "♥️", "♦": "♦️", "♣": "♣️"}

def deal():
    return (random.choice(RANKS), random.choice(SUITS))

def value(hand):
    total = 0
    aces  = 0
    for r, s in hand:
        if r in ["J","Q","K"]:
            total += 10
        elif r == "A":
            total += 11
            aces  += 1
        else:
            total += int(r)
    while total > 21 and aces:
        total -= 10
        aces  -= 1
    return total

def fmt_hand(hand, hide=False):
    cards = []
    for i, (r, s) in enumerate(hand):
        if i == 1 and hide:
            cards.append("🂠")
        else:
            cards.append(f"[{r}{SUIT_EMOJI[s]}]")
    return "  ".join(cards)

async def cmd_blackjack(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    name = update.effective_user.first_name

    if uid in GAMES:
        return await update.message.reply_text("⚠️ You already have a game running! Use /hit or /stand.")

    try:
        bet = int(ctx.args[0])
        assert bet > 0
    except:
        return await update.message.reply_text("❌ Usage: /blackjack <bet>")

    bal = get_balance(uid)
    if bal < bet:
        return await update.message.reply_text(f"❌ Not enough chips. Balance: *{bal:,}*", parse_mode="Markdown")

    remove_balance(uid, bet)

    player = [deal(), deal()]
    dealer = [deal(), deal()]

    GAMES[uid] = {"bet": bet, "player": player, "dealer": dealer}

    # Send card flip animation using dice emoji 🎴
    await update.message.reply_text("🃏 *Dealing cards...*", parse_mode="Markdown")
    await asyncio.sleep(0.5)

    # Player card 1
    d1 = await update.message.reply_dice(emoji="🎰")
    await asyncio.sleep(0.8)
    # Player card 2
    d2 = await update.message.reply_dice(emoji="🎰")
    await asyncio.sleep(1.5)

    pval = value(player)
    await update.message.reply_text(
        f"🃏 *Blackjack*\n\n"
        f"🏠 *Dealer:* {fmt_hand(dealer, hide=True)}  *(one card hidden)*\n\n"
        f"👤 *Your Hand:* {fmt_hand(player)}\n"
        f"Value: *{pval}*\n\n"
        f"💰 Bet: *{bet:,} chips*\n\n"
        f"👊 /hit — Draw a card\n"
        f"🛑 /stand — Hold your hand",
        parse_mode="Markdown"
    )

    if pval == 21:
        await _resolve(update, uid, blackjack=True)

async def cmd_hit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in GAMES:
        return await update.message.reply_text("❌ No active game. Start with /blackjack <bet>")

    game = GAMES[uid]

    # Card flip animation
    await update.message.reply_text("🃏 Drawing a card...")
    flip = await update.message.reply_dice(emoji="🎰")
    await asyncio.sleep(1.5)

    new_card = deal()
    game["player"].append(new_card)
    pval = value(game["player"])

    await update.message.reply_text(
        f"🃏 *Your Hand:* {fmt_hand(game['player'])}\n"
        f"Value: *{pval}*",
        parse_mode="Markdown"
    )

    if pval > 21:
        new_bal = get_balance(uid)
        del GAMES[uid]
        await update.message.reply_text(
            f"💥 *BUST!* You went over 21.\n\n"
            f"❌ Lost *{game['bet']:,} chips*.\n"
            f"Balance: *{new_bal:,} chips*",
            parse_mode="Markdown"
        )
    elif pval == 21:
        await _resolve(update, uid)
    else:
        await update.message.reply_text("👊 /hit — Draw again\n🛑 /stand — Hold")

async def cmd_stand(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in GAMES:
        return await update.message.reply_text("❌ No active game. Start with /blackjack <bet>")
    await _resolve(update, uid)

async def _resolve(update, uid, blackjack=False):
    game   = GAMES[uid]
    player = game["player"]
    dealer = game["dealer"]
    bet    = game["bet"]

    await update.message.reply_text("🏠 *Dealer reveals their hand...*", parse_mode="Markdown")

    # Dealer card reveal animation
    flip = await update.message.reply_dice(emoji="🎰")
    await asyncio.sleep(1.5)

    while value(dealer) < 17:
        await update.message.reply_text("🏠 Dealer draws...")
        await update.message.reply_dice(emoji="🎰")
        await asyncio.sleep(1.5)
        dealer.append(deal())

    pval = value(player)
    dval = value(dealer)

    dealer_txt = fmt_hand(dealer)
    player_txt = fmt_hand(player)

    if blackjack or pval == 21 and dval != 21:
        win = int(bet * 1.5)
        add_balance(uid, bet + win)
        new_bal = get_balance(uid)
        result = (
            f"🃏 *BLACKJACK!* 🎉\n\n"
            f"🏠 Dealer: {dealer_txt} (*{dval}*)\n"
            f"👤 You:    {player_txt} (*{pval}*)\n\n"
            f"✅ Won *+{win:,} chips* (1.5x)!\n"
            f"Balance: *{new_bal:,} chips*"
        )
    elif dval > 21 or pval > dval:
        add_balance(uid, bet * 2)
        new_bal = get_balance(uid)
        result = (
            f"🃏 *You WIN!* 🎉\n\n"
            f"🏠 Dealer: {dealer_txt} (*{dval}*)\n"
            f"👤 You:    {player_txt} (*{pval}*)\n\n"
            f"✅ Won *+{bet:,} chips*!\n"
            f"Balance: *{new_bal:,} chips*"
        )
    elif pval == dval:
        add_balance(uid, bet)
        new_bal = get_balance(uid)
        result = (
            f"🃏 *PUSH — Tie!* 🤝\n\n"
            f"🏠 Dealer: {dealer_txt} (*{dval}*)\n"
            f"👤 You:    {player_txt} (*{pval}*)\n\n"
            f"↩️ Bet returned.\n"
            f"Balance: *{new_bal:,} chips*"
        )
    else:
        new_bal = get_balance(uid)
        result = (
            f"🃏 *You Lost* 😢\n\n"
            f"🏠 Dealer: {dealer_txt} (*{dval}*)\n"
            f"👤 You:    {player_txt} (*{pval}*)\n\n"
            f"❌ Lost *{bet:,} chips*.\n"
            f"Balance: *{new_bal:,} chips*"
        )

    del GAMES[uid]
    await update.message.reply_text(result, parse_mode="Markdown")
