from telegram import Update
from telegram.ext import ContextTypes
from utils.db import get_user, create_user, get_balance
from utils.ui import (
    bet_keyboard, roulette_keyboard, mines_setup_keyboard,
    blackjack_keyboard, back_keyboard
)

async def _ensure_user(update, context):
    user = update.effective_user
    if not get_user(user.id):
        create_user(user.id, user.username or "", user.first_name)

async def slots_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _ensure_user(update, context)
    balance = get_balance(update.effective_user.id)
    await update.message.reply_text(
        f"🎰 *SLOT MACHINE*\n\n💰 Solde: `${balance:.2f} USDT`\n\nChoisis ta mise:",
        parse_mode="Markdown",
        reply_markup=bet_keyboard("slots")
    )

async def blackjack_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _ensure_user(update, context)
    balance = get_balance(update.effective_user.id)
    await update.message.reply_text(
        f"🃏 *BLACKJACK*\n\n💰 Solde: `${balance:.2f} USDT`\n\nChoisis ta mise:",
        parse_mode="Markdown",
        reply_markup=bet_keyboard("blackjack")
    )

async def dice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _ensure_user(update, context)
    balance = get_balance(update.effective_user.id)
    await update.message.reply_text(
        f"🎲 *DÉS*\n\n💰 Solde: `${balance:.2f} USDT`\n\nChoisis ta mise:",
        parse_mode="Markdown",
        reply_markup=bet_keyboard("dice")
    )

async def roulette_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _ensure_user(update, context)
    balance = get_balance(update.effective_user.id)
    await update.message.reply_text(
        f"🎡 *ROULETTE*\n\n💰 Solde: `${balance:.2f} USDT`\n\nChoisis ta mise:",
        parse_mode="Markdown",
        reply_markup=bet_keyboard("roulette")
    )

async def mines_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _ensure_user(update, context)
    balance = get_balance(update.effective_user.id)
    await update.message.reply_text(
        f"💣 *MINES*\n\n💰 Solde: `${balance:.2f} USDT`\n\nChoisis ta mise:",
        parse_mode="Markdown",
        reply_markup=bet_keyboard("mines")
    )

async def coinflip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _ensure_user(update, context)
    balance = get_balance(update.effective_user.id)
    await update.message.reply_text(
        f"🪙 *COIN FLIP*\n\n💰 Solde: `${balance:.2f} USDT`\n\nChoisis ta mise:",
        parse_mode="Markdown",
        reply_markup=bet_keyboard("coinflip")
    )
