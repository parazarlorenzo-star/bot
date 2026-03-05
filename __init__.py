from telegram import Update
from telegram.ext import ContextTypes
from database import get_balance, add_balance, remove_balance, set_balance
from config import ADMIN_USERNAME

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    bal  = get_balance(update.effective_user.id)
    await update.message.reply_text(
        f"🎰 Welcome to the Casino, *{name}*!\n\n"
        f"💰 Starting balance: *{bal:,} chips*\n\n"
        "📋 *Commands:*\n"
        "/balance — Check balance\n"
        "/deposit <amount> — Deposit chips\n"
        "/withdraw <amount> — Withdraw chips\n\n"
        "🎮 *Games:*\n"
        "/coinflip <bet> — Coin flip\n"
        "/blackjack <bet> — Blackjack\n"
        "/dice <bet> — Dice roll\n"
        "/roulette <bet> <red|black|green|0-36> — Roulette\n"
        "/bowling <bet> <normal|double|crazy> <1|2> — Bowling\n"
        "/dart <bet> <normal|double|crazy> <1|2> — Darts\n"
        "/basketball <bet> <normal|double|crazy> <1|2> — Basketball\n"
        "/football <bet> <normal|double|crazy> <1|2> — Football",
        parse_mode="Markdown"
    )

async def balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    name = update.effective_user.first_name
    bal  = get_balance(uid)
    await update.message.reply_text(
        f"💰 *{name}'s Balance*\n\n🪙 *{bal:,} chips*",
        parse_mode="Markdown"
    )

async def deposit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        amount = int(ctx.args[0])
        assert amount > 0
    except:
        return await update.message.reply_text("❌ Usage: /deposit <amount>")
    add_balance(uid, amount)
    bal = get_balance(uid)
    await update.message.reply_text(
        f"✅ *Deposit Successful*\n\n"
        f"Deposited: *+{amount:,} chips* 🪙\n"
        f"New balance: *{bal:,} chips*",
        parse_mode="Markdown"
    )

async def withdraw(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        amount = int(ctx.args[0])
        assert amount > 0
    except:
        return await update.message.reply_text("❌ Usage: /withdraw <amount>")
    success = remove_balance(uid, amount)
    if not success:
        bal = get_balance(uid)
        return await update.message.reply_text(
            f"❌ Insufficient funds.\nYour balance: *{bal:,} chips*",
            parse_mode="Markdown"
        )
    bal = get_balance(uid)
    await update.message.reply_text(
        f"✅ *Withdrawal Successful*\n\n"
        f"Withdrew: *{amount:,} chips* 🪙\n"
        f"Remaining: *{bal:,} chips*",
        parse_mode="Markdown"
    )

async def addbal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Admins only.")
    try:
        target_id = int(ctx.args[0])
        amount    = int(ctx.args[1])
    except:
        return await update.message.reply_text("❌ Usage: /addbal <user_id> <amount>")
    add_balance(target_id, amount)
    bal = get_balance(target_id)
    await update.message.reply_text(
        f"👑 Added *{amount:,} chips* to user `{target_id}`\nNew balance: *{bal:,} chips*",
        parse_mode="Markdown"
    )

async def removebal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Admins only.")
    try:
        target_id = int(ctx.args[0])
        amount    = int(ctx.args[1])
    except:
        return await update.message.reply_text("❌ Usage: /removebal <user_id> <amount>")
    remove_balance(target_id, amount)
    bal = get_balance(target_id)
    await update.message.reply_text(
        f"👑 Removed *{amount:,} chips* from user `{target_id}`\nNew balance: *{bal:,} chips*",
        parse_mode="Markdown"
    )

async def resetbal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Admins only.")
    try:
        target_id = int(ctx.args[0])
    except:
        return await update.message.reply_text("❌ Usage: /resetbal <user_id>")
    set_balance(target_id, 1000)
    await update.message.reply_text(
        f"👑 Reset user `{target_id}` balance to *1,000 chips*.",
        parse_mode="Markdown"
    )
