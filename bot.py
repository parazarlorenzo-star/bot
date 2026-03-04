import logging
import asyncio
import os
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters
)
from handlers.start import start_handler, menu_handler
from handlers.wallet import wallet_handler, deposit_handler, withdraw_handler
from handlers.games import (
    slots_handler, blackjack_handler, dice_handler,
    roulette_handler, mines_handler, coinflip_handler
)
from handlers.admin import admin_handler, add_balance_cmd
from handlers.callbacks import button_callback
from handlers.custom_bet import handle_custom_bet_message
from utils.deposit_watcher import deposit_watcher
from config import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


async def post_init(application):
    """Lance le deposit watcher après démarrage du bot"""
    asyncio.create_task(deposit_watcher(application.bot))
    logger.info("👀 Deposit watcher lancé en arrière-plan")


def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # ── Commandes ──────────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start",       start_handler))
    app.add_handler(CommandHandler("menu",        menu_handler))
    app.add_handler(CommandHandler("wallet",      wallet_handler))
    app.add_handler(CommandHandler("deposit",     deposit_handler))
    app.add_handler(CommandHandler("withdraw",    withdraw_handler))
    app.add_handler(CommandHandler("slots",       slots_handler))
    app.add_handler(CommandHandler("blackjack",   blackjack_handler))
    app.add_handler(CommandHandler("dice",        dice_handler))
    app.add_handler(CommandHandler("roulette",    roulette_handler))
    app.add_handler(CommandHandler("mines",       mines_handler))
    app.add_handler(CommandHandler("coinflip",    coinflip_handler))
    app.add_handler(CommandHandler("admin",       admin_handler))
    app.add_handler(CommandHandler("addbalance",  add_balance_cmd))

    # ── Boutons inline ─────────────────────────────────────────────────────────
    app.add_handler(CallbackQueryHandler(button_callback))

    # ── Messages texte (mises perso + numéro roulette) ─────────────────────────
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_custom_bet_message
    ))

    logger.info("🎰 Casino Bot démarré!")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
