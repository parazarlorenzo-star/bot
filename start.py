from telegram import Update
from telegram.ext import ContextTypes
from utils.db import get_user, create_user, get_balance
from utils.ui import main_menu_keyboard, welcome_message
from config import WELCOME_BONUS

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = get_user(user.id)
    
    if not db_user:
        create_user(user.id, user.username or "", user.first_name, WELCOME_BONUS)
        balance = WELCOME_BONUS
        is_new = True
    else:
        balance = db_user["balance"]
        is_new = False
    
    text = welcome_message(user.first_name, balance)
    
    if is_new and WELCOME_BONUS > 0:
        text = f"🎁 *Bonus de bienvenue: ${WELCOME_BONUS} USDT offerts!*\n\n" + text
    
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    balance = get_balance(user.id)
    
    await update.message.reply_text(
        welcome_message(user.first_name, balance),
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
