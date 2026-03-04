"""
Gestion des mises personnalisées saisies au clavier.
Le joueur tape son montant après avoir choisi "Montant perso".
"""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.db import get_balance, get_user, create_user
from utils.ui import bet_keyboard, back_keyboard
from config import MIN_BET, MAX_BET


async def handle_custom_bet_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Intercepte les messages texte quand le joueur est en train de saisir
    une mise personnalisée (contexte stocké dans context.user_data).
    """
    user = update.effective_user

    # ── Mise personnalisée ────────────────────────────────────────────────────
    if context.user_data.get("awaiting_bet_game"):
        game = context.user_data.pop("awaiting_bet_game")
        text = update.message.text.strip().replace(",", ".")

        try:
            bet = float(text)
        except ValueError:
            await update.message.reply_text(
                "❌ *Montant invalide.* Entre un nombre, ex: `5.50`",
                parse_mode="Markdown",
                reply_markup=bet_keyboard(game)
            )
            context.user_data["awaiting_bet_game"] = game
            return

        balance = get_balance(user.id)

        if bet < MIN_BET:
            await update.message.reply_text(
                f"❌ Mise trop basse! Minimum: `${MIN_BET} USDT`",
                parse_mode="Markdown",
                reply_markup=bet_keyboard(game)
            )
            context.user_data["awaiting_bet_game"] = game
            return

        if bet > MAX_BET:
            await update.message.reply_text(
                f"❌ Mise trop haute! Maximum: `${MAX_BET} USDT`",
                parse_mode="Markdown",
                reply_markup=bet_keyboard(game)
            )
            context.user_data["awaiting_bet_game"] = game
            return

        if bet > balance:
            await update.message.reply_text(
                f"❌ Solde insuffisant!\n💰 Solde: `${balance:.2f}`\n💸 Mise: `${bet:.2f}`",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Déposer", callback_data="wallet")],
                    [InlineKeyboardButton("🔙 Menu", callback_data="menu")],
                ])
            )
            return

        # Lance le jeu avec la mise saisie
        # On envoie un faux callback pour réutiliser le système existant
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✅ Miser ${bet:.2f}", callback_data=f"bet_{game}_{bet}"),
             InlineKeyboardButton("✏️ Changer", callback_data=f"game_{game}")]
        ])
        await update.message.reply_text(
            f"🎮 *{game.upper()}*\n\n💰 Mise confirmée: `${bet:.2f} USDT`\n\nClique pour lancer!",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return

    # ── Numéro roulette ────────────────────────────────────────────────────────
    if context.user_data.get("awaiting_roulette_number"):
        context.user_data.pop("awaiting_roulette_number")
        bet = context.user_data.pop("roulette_bet", 0)
        text = update.message.text.strip()

        try:
            number = int(text)
            assert 0 <= number <= 36
        except (ValueError, AssertionError):
            await update.message.reply_text(
                "❌ Numéro invalide. Entre un nombre entre *0* et *36*.",
                parse_mode="Markdown",
            )
            return

        # Simule le callback de la roulette avec ce numéro
        from utils.db import get_game_state, clear_game_state, update_balance, record_game
        from games.other_games import spin_roulette, roulette_win, format_roulette_result
        import json

        # Récupère la mise depuis le game state
        state_row = get_game_state(user.id)
        if state_row and state_row["game"] == "roulette_bet":
            state_data = json.loads(state_row["state"])
            bet = state_data["bet"]

        update_balance(user.id, -bet)
        spin   = spin_roulette()
        result = roulette_win(spin, f"num_{number}", bet)

        if result["win"]:
            update_balance(user.id, bet + result["profit"])

        record_game(user.id, "roulette", bet, f"{spin['number']}_{spin['color']}", result["profit"])
        clear_game_state(user.id)

        balance = get_balance(user.id)
        msg     = format_roulette_result(spin, result, f"num_{number}", bet, balance)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Rejouer", callback_data="game_roulette"),
             InlineKeyboardButton("🔙 Menu",    callback_data="menu")]
        ])
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=keyboard)
        return
