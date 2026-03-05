import asyncio, random
from telegram import Update
from telegram.ext import ContextTypes
from database import get_balance, add_balance, remove_balance

async def cmd_dice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    name = update.effective_user.first_name
    try:
        bet = int(ctx.args[0])
        assert bet > 0
    except:
        return await update.message.reply_text("❌ Usage: /dice <bet>")

    bal = get_balance(uid)
    if bal < bet:
        return await update.message.reply_text(f"❌ Not enough chips. Balance: *{bal:,}*", parse_mode="Markdown")

    remove_balance(uid, bet)

    await update.message.reply_text("🎲 *You roll first!*", parse_mode="Markdown")

    # Player's real dice roll (Telegram native 🎲)
    player_dice = await update.message.reply_dice(emoji="🎲")
    player_val  = player_dice.dice.value
    await asyncio.sleep(3)

    await update.message.reply_text("🎲 *Casino rolls...*", parse_mode="Markdown")

    # Casino's real dice roll
    casino_dice = await update.message.reply_dice(emoji="🎲")
    casino_val  = casino_dice.dice.value
    await asyncio.sleep(3)

    if player_val > casino_val:
        add_balance(uid, bet * 2)
        new_bal = get_balance(uid)
        await update.message.reply_text(
            f"🎲 *Dice Result*\n\n"
            f"👤 You: *{player_val}*\n"
            f"🏠 Casino: *{casino_val}*\n\n"
            f"🎉 You WIN! *+{bet:,} chips*!\n"
            f"Balance: *{new_bal:,} chips*",
            parse_mode="Markdown"
        )
    elif player_val == casino_val:
        add_balance(uid, bet)
        new_bal = get_balance(uid)
        await update.message.reply_text(
            f"🎲 *Dice Result*\n\n"
            f"👤 You: *{player_val}*\n"
            f"🏠 Casino: *{casino_val}*\n\n"
            f"🤝 TIE — Bet returned.\n"
            f"Balance: *{new_bal:,} chips*",
            parse_mode="Markdown"
        )
    else:
        new_bal = get_balance(uid)
        await update.message.reply_text(
            f"🎲 *Dice Result*\n\n"
            f"👤 You: *{player_val}*\n"
            f"🏠 Casino: *{casino_val}*\n\n"
            f"😢 Casino wins. Lost *{bet:,} chips*.\n"
            f"Balance: *{new_bal:,} chips*",
            parse_mode="Markdown"
        )
