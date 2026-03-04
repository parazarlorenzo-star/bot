from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.db import get_user, create_user, get_balance, create_transaction
from utils.ui import back_keyboard
from config import TON_WALLET_ADDRESS, USDT_WALLET_ADDRESS, MIN_DEPOSIT, MIN_WITHDRAW

def wallet_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Déposer TON",   callback_data="deposit_TON"),
            InlineKeyboardButton("➕ Déposer USDT",  callback_data="deposit_USDT"),
        ],
        [
            InlineKeyboardButton("🔗 Lier mon adresse", callback_data="register_address"),
        ],
        [
            InlineKeyboardButton("➖ Retirer",       callback_data="withdraw_start"),
        ],
        [
            InlineKeyboardButton("🔙 Menu",          callback_data="menu"),
        ]
    ])

async def wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = get_user(user.id)

    if not db_user:
        create_user(user.id, user.username or "", user.first_name)
        db_user = get_user(user.id)

    linked = db_user["deposit_address"] if db_user["deposit_address"] else "Non liée"
    linked_display = f"`{linked[:20]}...`" if len(str(linked)) > 20 else f"`{linked}`"

    text = f"""
💼 *Mon Wallet*

╔══════════════════════════════╗
║  💰 Solde: `${db_user['balance']:.2f} USDT`         ║
╠══════════════════════════════╣
║  📈 Total misé: `${db_user['total_wagered']:.2f}`     ║
║  🏆 Total gagné: `${db_user['total_won']:.2f}`     ║
║  🎮 Parties: `{db_user['games_played']}`              ║
╚══════════════════════════════╝

*Adresses de dépôt du casino:*
🔷 TON: `{TON_WALLET_ADDRESS}`
💵 USDT (TRC20): `{USDT_WALLET_ADDRESS}`

*Ton adresse source liée:* {linked_display}
🤖 Les dépôts depuis cette adresse sont crédités *automatiquement!*

💡 *Astuce:* Tu peux aussi mettre ton ID `{user.id}` en commentaire lors du virement.
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=wallet_keyboard())

async def deposit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    currency = context.args[0].upper() if context.args else "USDT"
    addr = TON_WALLET_ADDRESS if currency == "TON" else USDT_WALLET_ADDRESS
    network = "TON" if currency == "TON" else "TRC20 (Tron)"
    memo_instruction = (
        "Dans le champ *Commentaire*, écris ton ID: `" + str(user.id) + "`"
        if currency == "TON" else
        "Dans le champ *Memo/Tag*, écris ton ID: `" + str(user.id) + "`"
    )

    text = f"""
➕ *Dépôt {currency}*

Adresse de dépôt:
`{addr}`

🔑 *TRÈS IMPORTANT — Ton ID unique:*
`{user.id}`

{memo_instruction}

⚠️ *Sans le memo, ton dépôt ne sera PAS crédité automatiquement!*

📋 *Résumé:*
• Réseau: `{network}`
• Minimum: `${MIN_DEPOSIT} USDT`
• Délai: ⚡ 30 secondes à 5 minutes
• Créditement: 🤖 Automatique dès confirmation

Après envoi, reste sur Telegram — tu recevras une notification automatique! ✅
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=back_keyboard())

async def withdraw_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    balance = get_balance(user.id)
    
    text = f"""
➖ *Retrait*

💰 Solde disponible: `${balance:.2f} USDT`
📉 Minimum de retrait: `${MIN_WITHDRAW} USDT`

Pour retirer, envoie:
`/retirer <montant> <adresse_wallet>`

Exemple:
`/retirer 10 TAdresseWalletIci`

⏳ Délai de traitement: 1-24h
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=back_keyboard())
