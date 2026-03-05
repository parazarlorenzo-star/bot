import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers import economy, coinflip, blackjack, dice_game, roulette, bowling, dart, basketball, football

logging.basicConfig(level=logging.INFO)

import os
TOKEN = os.environ["8673116882:AAGS8jXfEZpkUpWhLRi1xQivvgDW32dBjmU"]

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Economy
    app.add_handler(CommandHandler("start",    economy.start))
    app.add_handler(CommandHandler("balance",  economy.balance))
    app.add_handler(CommandHandler("deposit",  economy.deposit))
    app.add_handler(CommandHandler("withdraw", economy.withdraw))
    app.add_handler(CommandHandler("addbal",   economy.addbal))
    app.add_handler(CommandHandler("removebal",economy.removebal))
    app.add_handler(CommandHandler("resetbal", economy.resetbal))

    # Games
    app.add_handler(CommandHandler("coinflip",   coinflip.cmd_coinflip))
    app.add_handler(CommandHandler("blackjack",  blackjack.cmd_blackjack))
    app.add_handler(CommandHandler("hit",        blackjack.cmd_hit))
    app.add_handler(CommandHandler("stand",      blackjack.cmd_stand))
    app.add_handler(CommandHandler("dice",       dice_game.cmd_dice))
    app.add_handler(CommandHandler("roulette",   roulette.cmd_roulette))
    app.add_handler(CommandHandler("bowling",    bowling.cmd_bowling))
    app.add_handler(CommandHandler("dart",       dart.cmd_dart))
    app.add_handler(CommandHandler("basketball", basketball.cmd_basketball))
    app.add_handler(CommandHandler("football",   football.cmd_football))

    print("🎰 Casino Bot is running on Telegram!")
    app.run_polling()

if __name__ == "__main__":
    main()
