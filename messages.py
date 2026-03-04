"""
Gère tous les messages texte libres envoyés par le joueur:
- Saisie de mise personnalisée
- Enregistrement adresse wallet source (pour auto-détection dépôts)
- Numéro de roulette personnalisé
- Montant de retrait
"""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from utils.db import get_balance, get_user, create_user, save_deposit_address
from handlers.callbacks import start_game
from config import MIN_BET, MAX_BET, MIN_WITHDRAW

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()

    if not get_user(user.id):
        create_user(user.id, user.username or "", user.first_name)

    # ══════════════════════════════════════════
    #  1. MISE PERSONNALISÉE
    # ══════════════════════════════════════════
    if "awaiting_bet_game" in context.user_data:
        game = context.user_data.pop("awaiting_bet_game")
        
        try:
            bet = float(text.replace(",", "."))
        except ValueError:
            await update.message.reply_text(
                "❌ Montant invalide. Entre un nombre comme `5` ou `12.50`",
                parse_mode="Markdown"
            )
            context.user_data["awaiting_bet_game"] = game  # Remet en attente
            return

        balance = get_balance(user.id)

        if bet < MIN_BET:
            await update.message.reply_text(
                f"❌ Mise minimum: `${MIN_BET} USDT`",
                parse_mode="Markdown"
            )
            context.user_data["awaiting_bet_game"] = game
            return

        if bet > MAX_BET:
            await update.message.reply_text(
                f"❌ Mise maximum: `${MAX_BET} USDT`",
                parse_mode="Markdown"
            )
            context.user_data["awaiting_bet_game"] = game
            return

        if balance < bet:
            await update.message.reply_text(
                f"❌ *Solde insuffisant!*\n\n"
                f"💰 Ton solde: `${balance:.2f}`\n"
                f"💸 Ta mise: `${bet:.2f}`\n\n"
                f"Dépose des fonds avec /deposit",
                parse_mode="Markdown"
            )
            return

        # Confirme la mise et lance le jeu
        msg = await update.message.reply_text(
            f"✅ Mise de `${bet:.2f} USDT` confirmée!\n⏳ Lancement...",
            parse_mode="Markdown"
        )
        
        # Crée un faux "query" object pour réutiliser start_game
        class FakeQuery:
            def __init__(self, message):
                self.message = message
            async def edit_message_text(self, text, **kwargs):
                await self.message.edit_text(text, **kwargs)
            async def answer(self):
                pass
        
        fake_query = FakeQuery(msg)
        await start_game(fake_query, context, user.id, game, bet)
        return

    # ══════════════════════════════════════════
    #  2. NUMÉRO ROULETTE PERSONNALISÉ
    # ══════════════════════════════════════════
    if context.user_data.get("awaiting_roulette_number"):
        context.user_data.pop("awaiting_roulette_number")
        bet = context.user_data.pop("roulette_bet", 0)

        try:
            number = int(text)
            if not (0 <= number <= 36):
                raise ValueError
        except ValueError:
            await update.message.reply_text(
                "❌ Entre un numéro entre *0* et *36*",
                parse_mode="Markdown"
            )
            context.user_data["awaiting_roulette_number"] = True
            context.user_data["roulette_bet"] = bet
            return

        from utils.db import update_balance, record_game, clear_game_state
        from games.other_games import spin_roulette, roulette_win, format_roulette_result

        update_balance(user.id, -bet)
        spin = spin_roulette()
        result = roulette_win(spin, f"num_{number}", bet)

        if result["win"]:
            update_balance(user.id, bet + result["profit"])

        record_game(user.id, "roulette", bet, f"{spin['number']}_{spin['color']}", result["profit"])
        clear_game_state(user.id)

        balance = get_balance(user.id)
        msg = format_roulette_result(spin, result, f"Numéro {number}", bet, balance)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Rejouer", callback_data="game_roulette"),
             InlineKeyboardButton("🔙 Menu", callback_data="menu")]
        ])
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=keyboard)
        return

    # ══════════════════════════════════════════
    #  3. ENREGISTREMENT ADRESSE WALLET SOURCE
    #     (Pour auto-détection des dépôts)
    # ══════════════════════════════════════════
    if context.user_data.get("awaiting_wallet_address"):
        currency = context.user_data.pop("awaiting_wallet_address")
        address = text.strip()

        # Validation basique de l'adresse
        valid = False
        if currency == "TON" and (address.startswith("UQ") or address.startswith("EQ")) and len(address) > 40:
            valid = True
        elif currency == "USDT" and address.startswith("T") and len(address) == 34:
            valid = True

        if not valid:
            await update.message.reply_text(
                f"❌ Adresse {currency} invalide.\n"
                f"{'Format TON: UQ... ou EQ... (48 caractères)' if currency == 'TON' else 'Format USDT TRC20: T... (34 caractères)'}\n\n"
                f"Réessaie:",
                parse_mode="Markdown"
            )
            context.user_data["awaiting_wallet_address"] = currency
            return

        save_deposit_address(user.id, address)

        await update.message.reply_text(
            f"✅ *Adresse {currency} enregistrée!*\n\n"
            f"`{address}`\n\n"
            f"Maintenant quand tu envoies des fonds depuis cette adresse, "
            f"ton solde sera crédité *automatiquement* en moins de 30 secondes! 🚀\n\n"
            f"💡 Tu peux aussi mettre ton ID `{user.id}` en commentaire/memo lors du transfert.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💰 Voir mon wallet", callback_data="wallet")
            ]])
        )
        return

    # ══════════════════════════════════════════
    #  4. MONTANT DE RETRAIT
    # ══════════════════════════════════════════
    if context.user_data.get("awaiting_withdraw_amount"):
        context.user_data.pop("awaiting_withdraw_amount")

        try:
            amount = float(text.replace(",", "."))
        except ValueError:
            await update.message.reply_text("❌ Montant invalide.")
            return

        balance = get_balance(user.id)

        if amount < MIN_WITHDRAW:
            await update.message.reply_text(
                f"❌ Minimum de retrait: `${MIN_WITHDRAW} USDT`",
                parse_mode="Markdown"
            )
            return

        if amount > balance:
            await update.message.reply_text(
                f"❌ Solde insuffisant!\n💰 Disponible: `${balance:.2f}`",
                parse_mode="Markdown"
            )
            return

        context.user_data["withdraw_amount"] = amount
        context.user_data["awaiting_withdraw_address"] = True

        await update.message.reply_text(
            f"💸 Retrait de `${amount:.2f} USDT`\n\nEntre ton adresse de destination (TRC20):",
            parse_mode="Markdown"
        )
        return

    if context.user_data.get("awaiting_withdraw_address"):
        context.user_data.pop("awaiting_withdraw_address")
        address = text.strip()
        amount = context.user_data.pop("withdraw_amount", 0)

        if not (address.startswith("T") and len(address) == 34):
            await update.message.reply_text("❌ Adresse USDT TRC20 invalide.")
            return

        from utils.db import create_transaction
        create_transaction(user.id, "withdraw", amount, "USDT", address)

        from config import ADMIN_IDS
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"💸 *Demande de retrait*\n\n"
                         f"👤 User: `{user.id}` (@{user.username or 'N/A'})\n"
                         f"💰 Montant: `${amount:.2f} USDT`\n"
                         f"📤 Adresse: `{address}`",
                    parse_mode="Markdown"
                )
            except:
                pass

        await update.message.reply_text(
            f"✅ *Demande de retrait envoyée!*\n\n"
            f"💰 Montant: `${amount:.2f} USDT`\n"
            f"📤 Vers: `{address}`\n\n"
            f"⏳ Délai: 1-24h\nTon solde sera débité après traitement.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Menu", callback_data="menu")
            ]])
        )
        return

    # ══════════════════════════════════════════
    #  5. MESSAGE INCONNU → GUIDE
    # ══════════════════════════════════════════
    await update.message.reply_text(
        "🎰 Utilise les boutons ou tape /menu pour jouer!",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📋 Ouvrir le menu", callback_data="menu")
        ]])
    )
