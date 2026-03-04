from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.db import get_stats, get_all_users, update_balance, set_balance
from config import ADMIN_IDS

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ Accès refusé.")
        return
    
    stats = get_stats()
    
    text = f"""
🔐 *PANEL ADMIN*

📊 *Statistiques:*
👥 Utilisateurs: `{stats['total_users']}`
💰 Total misé: `${stats['total_wagered']:.2f} USDT`
🏦 Total en caisse: `${stats['total_balance']:.2f} USDT`
🎮 Parties aujourd'hui: `{stats['games_today']}`

*Commandes admin:*
`/addbalance <user_id> <montant>` — Ajouter du solde
`/setbalance <user_id> <montant>` — Définir le solde
`/broadcast <message>` — Message à tous
`/userinfo <user_id>` — Info utilisateur
`/ban <user_id>` — Bannir un joueur
"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Stats complètes", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 Liste joueurs", callback_data="admin_users")],
        [InlineKeyboardButton("💰 Dépôts en attente", callback_data="admin_deposits")],
    ])
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def add_balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    try:
        target_id = int(context.args[0])
        amount = float(context.args[1])
        update_balance(target_id, amount)
        await update.message.reply_text(f"✅ `+${amount}` ajouté à l'utilisateur `{target_id}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Erreur: {e}\nUsage: /addbalance <user_id> <montant>")
