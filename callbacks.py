import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from utils.db import (
    get_balance, update_balance, record_game,
    save_game_state, get_game_state, clear_game_state, get_user, create_user
)
from utils.ui import (
    main_menu_keyboard, bet_keyboard, wallet_keyboard, back_keyboard,
    roulette_keyboard, mines_setup_keyboard, mines_grid_keyboard,
    blackjack_keyboard, welcome_message
)
from games.slots import spin_slots, format_slots_result
from games.blackjack import (
    new_game as bj_new, hit as bj_hit, stand as bj_stand,
    double_down as bj_double, surrender as bj_surrender,
    calculate_profit as bj_profit, format_blackjack_state,
    can_double, can_split, is_blackjack
)
from games.other_games import (
    spin_roulette, roulette_win, format_roulette_result,
    roll_dice, format_dice_result,
    flip_coin, format_coinflip_result,
    new_mines_game, reveal_tile, cashout_mines, mines_profit,
    get_mines_multiplier
)
from config import MIN_BET, MAX_BET

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    data = query.data
    
    # Ensure user exists
    if not get_user(user.id):
        create_user(user.id, user.username or "", user.first_name)
    
    # ── Menu & Navigation ─────────────────────────────────────────────────────
    
    if data == "menu":
        balance = get_balance(user.id)
        await query.edit_message_text(
            welcome_message(user.first_name, balance),
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        return
    
    if data == "withdraw_start":
        balance = get_balance(user.id)
        if balance < 0.01:
            await query.edit_message_text(
                "❌ Ton solde est vide. Dépose des fonds d'abord!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💰 Déposer", callback_data="wallet")]])
            )
            return
        context.user_data["awaiting_withdraw_amount"] = True
        await query.edit_message_text(
            f"➖ *Retrait*\n\n💰 Solde dispo: `${balance:.2f} USDT`\n\nEntre le montant à retirer:",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )
        return

    if data == "register_address":
        await query.edit_message_text(
            "🔗 *Lier ton adresse source*\n\n"
            "Envoie ton adresse TON *ou* USDT TRC20 depuis laquelle tu vas déposer.\n\n"
            "Cela permet la *détection automatique* de tes dépôts!\n\n"
            "Choisis la devise:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔷 Adresse TON", callback_data="link_TON"),
                 InlineKeyboardButton("💵 Adresse USDT", callback_data="link_USDT")],
                [InlineKeyboardButton("🔙 Retour", callback_data="wallet")]
            ])
        )
        return

    if data.startswith("link_"):
        currency = data[5:]
        context.user_data["awaiting_wallet_address"] = currency
        format_hint = "UQ... ou EQ... (48 caractères)" if currency == "TON" else "T... (34 caractères)"
        await query.edit_message_text(
            f"🔷 *Lier adresse {currency}*\n\nFormat: `{format_hint}`\n\nEnvoie ton adresse:",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )
        return

    if data == "wallet":
        db_user = get_user(user.id)
        if not db_user:
            create_user(user.id, user.username or "", user.first_name)
            db_user = get_user(user.id)
        from config import TON_WALLET_ADDRESS, USDT_WALLET_ADDRESS
        from handlers.wallet import wallet_keyboard
        linked = db_user["deposit_address"] if db_user["deposit_address"] else "Non liée"
        linked_display = f"`{linked[:20]}...`" if len(str(linked)) > 20 else f"`{linked}`"
        text = f"""
💼 *Mon Wallet*

╔══════════════════════════════╗
║  💰 Solde: `${db_user['balance']:.2f} USDT`         ║
╠══════════════════════════════╣
║  📈 Total misé: `${db_user['total_wagered']:.2f}`     ║
║  🏆 Total gagné: `${db_user['total_won']:.2f}`     ║
╚══════════════════════════════╝

🔷 TON: `{TON_WALLET_ADDRESS}`
💵 USDT: `{USDT_WALLET_ADDRESS}`

*Adresse source liée:* {linked_display}
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=wallet_keyboard())
        return

    if data == "stats":
        db_user = get_user(user.id)
        text = f"""
📊 *Mes Statistiques*

👤 {user.first_name}
🆔 ID: `{user.id}`

╔══════════════════════════════╗
║  💰 Solde: `${db_user['balance']:.2f}`              ║
║  📈 Total misé: `${db_user['total_wagered']:.2f}`   ║
║  🏆 Total gagné: `${db_user['total_won']:.2f}`   ║
║  🎮 Parties: `{db_user['games_played']}`            ║
╚══════════════════════════════╝
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard())
        return

    if data == "help":
        text = """
ℹ️ *Aide & Commandes*

🎰 `/slots` — Machine à sous
🃏 `/blackjack` — Blackjack
🎲 `/dice` — Dés
🎡 `/roulette` — Roulette
💣 `/mines` — Mines
🪙 `/coinflip` — Pile ou face

💰 `/wallet` — Mon portefeuille
➕ `/deposit TON` ou `/deposit USDT`
➖ `/withdraw` — Retirer

📞 Support: @AdminUsername
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard())
        return

    # ── Game selection from menu ───────────────────────────────────────────────
    
    if data.startswith("game_"):
        game = data[5:]
        balance = get_balance(user.id)
        game_names = {
            "slots": "🎰 SLOT MACHINE",
            "blackjack": "🃏 BLACKJACK",
            "dice": "🎲 DÉS",
            "roulette": "🎡 ROULETTE",
            "mines": "💣 MINES",
            "coinflip": "🪙 COIN FLIP",
        }
        await query.edit_message_text(
            f"{game_names.get(game, game)}\n\n💰 Solde: `${balance:.2f} USDT`\n\nChoisis ta mise:",
            parse_mode="Markdown",
            reply_markup=bet_keyboard(game)
        )
        return
    
    # ── Deposit ────────────────────────────────────────────────────────────────
    
    if data.startswith("deposit_"):
        currency = data[8:]
        from config import TON_WALLET_ADDRESS, USDT_WALLET_ADDRESS
        addr = TON_WALLET_ADDRESS if currency == "TON" else USDT_WALLET_ADDRESS
        network = "TON" if currency == "TON" else "TRC20 (Tron)"
        memo_field = "Commentaire" if currency == "TON" else "Memo/Tag"
        text = f"""
➕ *Dépôt {currency}*

Adresse:
`{addr}`

🔑 *Ton ID à mettre dans le champ {memo_field}:*
`{user.id}`

⚡ Créditement automatique en 30s–5min
⚠️ Sans memo = dépôt non détecté!

Réseau: `{network}` · Minimum: $1
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard())
        return

    # ══════════════════════════════════════════
    #  BET SELECTION → START GAME
    # ══════════════════════════════════════════
    
    if data.startswith("bet_"):
        parts = data.split("_")
        game = parts[1]
        amount_str = parts[2]
        
        if amount_str == "custom":
            context.user_data["awaiting_bet_game"] = game
            await query.edit_message_text(
                f"✏️ Entre ton montant de mise (min ${MIN_BET}, max ${MAX_BET}):",
                reply_markup=back_keyboard()
            )
            return
        
        bet = float(amount_str)
        balance = get_balance(user.id)
        
        if balance < bet:
            await query.edit_message_text(
                f"❌ Solde insuffisant!\n💰 Ton solde: `${balance:.2f}`\n💸 Mise: `${bet:.2f}`",
                parse_mode="Markdown",
                reply_markup=bet_keyboard(game)
            )
            return
        
        # Start the game
        await start_game(query, context, user.id, game, bet)
        return
    
    # ══════════════════════════════════════════
    #  BLACKJACK ACTIONS
    # ══════════════════════════════════════════
    
    if data.startswith("bj_"):
        action = data[3:]
        state_row = get_game_state(user.id)
        
        if not state_row or state_row["game"] != "blackjack":
            await query.edit_message_text("❌ Pas de partie en cours.", reply_markup=back_keyboard())
            return
        
        state = json.loads(state_row["state"])
        
        if action == "hit":
            state = bj_hit(state)
        elif action == "stand":
            state = bj_stand(state)
        elif action == "double":
            # Check if player can afford double
            extra = state["bet"]
            if get_balance(user.id) >= extra:
                update_balance(user.id, -extra)
                state = bj_double(state)
            else:
                await query.answer("❌ Solde insuffisant pour doubler!", show_alert=True)
                return
        elif action == "surrender":
            state = bj_surrender(state)
        
        game_over = state["status"] != "playing"
        
        if game_over:
            profit = bj_profit(state)
            update_balance(user.id, state["bet"] + profit)  # Return bet + profit
            record_game(user.id, "blackjack", state["bet"], state["status"], profit)
            clear_game_state(user.id)
            balance = get_balance(user.id)
            
            msg = format_blackjack_state(state, show_dealer=True)
            if profit > 0:
                msg += f"\n\n📈 Gain: *+${profit:.2f}*\n💼 Solde: `${balance:.2f}`"
            elif profit < 0:
                msg += f"\n\n📉 Perdu: *${profit:.2f}*\n💼 Solde: `${balance:.2f}`"
            else:
                msg += f"\n\n↩️ Mise remboursée\n💼 Solde: `${balance:.2f}`"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Rejouer", callback_data="game_blackjack"),
                 InlineKeyboardButton("🔙 Menu", callback_data="menu")]
            ])
            await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=keyboard)
        else:
            save_game_state(user.id, "blackjack", json.dumps(state))
            msg = format_blackjack_state(state)
            await query.edit_message_text(
                msg, parse_mode="Markdown",
                reply_markup=blackjack_keyboard(can_double(state["player"]))
            )
        return
    
    # ══════════════════════════════════════════
    #  ROULETTE BET TYPE
    # ══════════════════════════════════════════
    
    if data.startswith("rou_"):
        bet_type = data[4:]
        state_row = get_game_state(user.id)
        
        if not state_row or state_row["game"] != "roulette_bet":
            await query.edit_message_text("❌ Erreur. Recommence.", reply_markup=back_keyboard())
            return
        
        state = json.loads(state_row["state"])
        bet = state["bet"]
        
        if bet_type == "number":
            context.user_data["awaiting_roulette_number"] = True
            context.user_data["roulette_bet"] = bet
            await query.edit_message_text(
                "🔢 Entre un numéro entre 0 et 36:",
                reply_markup=back_keyboard()
            )
            return
        
        # Deduct bet and spin
        update_balance(user.id, -bet)
        spin = spin_roulette()
        result = roulette_win(spin, bet_type, bet)
        
        if result["win"]:
            update_balance(user.id, bet + result["profit"])
        
        record_game(user.id, "roulette", bet, f"{spin['number']}_{spin['color']}", result["profit"])
        clear_game_state(user.id)
        
        balance = get_balance(user.id)
        msg = format_roulette_result(spin, result, bet_type, bet, balance)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Rejouer", callback_data="game_roulette"),
             InlineKeyboardButton("🔙 Menu", callback_data="menu")]
        ])
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=keyboard)
        return
    
    # ══════════════════════════════════════════
    #  MINES
    # ══════════════════════════════════════════
    
    if data.startswith("mines_setup_"):
        num_mines = int(data[12:])
        state_row = get_game_state(user.id)
        
        if not state_row or state_row["game"] != "mines_bet":
            await query.edit_message_text("❌ Erreur.", reply_markup=back_keyboard())
            return
        
        state_data = json.loads(state_row["state"])
        bet = state_data["bet"]
        
        # Deduct bet, start game
        update_balance(user.id, -bet)
        game_state = new_mines_game(bet, num_mines)
        save_game_state(user.id, "mines", json.dumps(game_state))
        
        msg = f"""
💣 *MINES* — {num_mines} bombe{'s' if num_mines > 1 else ''}

💰 Mise: `${bet:.2f}`
📍 Clique sur une case!

🟩 Case sûre = multiplicateur augmente
💣 Mine = tout perdu!
"""
        await query.edit_message_text(
            msg, parse_mode="Markdown",
            reply_markup=mines_grid_keyboard([], [])
        )
        return
    
    if data.startswith("mines_click_"):
        pos = int(data[12:])
        state_row = get_game_state(user.id)
        
        if not state_row or state_row["game"] != "mines":
            return
        
        state = json.loads(state_row["state"])
        state = reveal_tile(state, pos)
        
        if state["status"] == "exploded":
            # Game over
            record_game(user.id, "mines", state["bet"], "exploded", -state["bet"])
            clear_game_state(user.id)
            balance = get_balance(user.id)
            
            msg = f"""
💣 *BOOM! Tu as touché une mine!*

📉 Perdu: *-${state['bet']:.2f} USDT*
💼 Solde: `${balance:.2f}`
"""
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Rejouer", callback_data="game_mines"),
                 InlineKeyboardButton("🔙 Menu", callback_data="menu")]
            ])
            await query.edit_message_text(
                msg, parse_mode="Markdown",
                reply_markup=mines_grid_keyboard(state["revealed"], state["mines"], game_over=True)
            )
        else:
            save_game_state(user.id, "mines", json.dumps(state))
            mult = get_mines_multiplier(state["num_mines"], state["step"])
            current_win = state["bet"] * mult
            
            msg = f"""
💣 *MINES* — {state['num_mines']} bombe{'s' if state['num_mines'] > 1 else ''}

✅ Cases révélées: *{state['step']}*
💰 Mise: `${state['bet']:.2f}`
📈 Gain actuel: `${current_win:.2f}` (x{mult})

Continue ou encaisse!
"""
            await query.edit_message_text(
                msg, parse_mode="Markdown",
                reply_markup=mines_grid_keyboard(state["revealed"], [])
            )
        return
    
    if data == "mines_cashout":
        state_row = get_game_state(user.id)
        if not state_row or state_row["game"] != "mines":
            return
        
        state = json.loads(state_row["state"])
        state = cashout_mines(state)
        profit = mines_profit(state)
        
        update_balance(user.id, state["bet"] + profit)
        record_game(user.id, "mines", state["bet"], "cashed_out", profit)
        clear_game_state(user.id)
        
        balance = get_balance(user.id)
        mult = get_mines_multiplier(state["num_mines"], state["step"])
        
        msg = f"""
💰 *ENCAISSÉ!*

✅ Cases révélées: *{state['step']}*
📈 Multiplicateur: *x{mult}*
💵 Gain: *+${profit:.2f} USDT*
💼 Solde: `${balance:.2f}`
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Rejouer", callback_data="game_mines"),
             InlineKeyboardButton("🔙 Menu", callback_data="menu")]
        ])
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=keyboard)
        return
    
    if data in ["mines_dead", "mines_already"]:
        await query.answer("💣 Mine!" if data == "mines_dead" else "✅ Déjà révélé!", show_alert=False)
        return

    # ══════════════════════════════════════════
    #  DICE BET
    # ══════════════════════════════════════════
    
    if data.startswith("dice_"):
        prediction = data[5:]  # low, high, exact_1 ... exact_6
        await handle_dice_bet(query, user.id, prediction)
        return
    
    # ══════════════════════════════════════════
    #  COIN FLIP BET TYPE
    # ══════════════════════════════════════════
    
    if data.startswith("cf_"):
        choice = data[3:]
        state_row = get_game_state(user.id)
        
        if not state_row or state_row["game"] != "coinflip_bet":
            return
        
        state_data = json.loads(state_row["state"])
        bet = state_data["bet"]
        
        update_balance(user.id, -bet)
        result = flip_coin(choice, bet)
        
        if result["win"]:
            update_balance(user.id, bet + result["profit"])
        
        record_game(user.id, "coinflip", bet, result["result"], result["profit"])
        clear_game_state(user.id)
        
        balance = get_balance(user.id)
        msg = format_coinflip_result(result, bet, balance)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Rejouer", callback_data="game_coinflip"),
             InlineKeyboardButton("🔙 Menu", callback_data="menu")]
        ])
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=keyboard)
        return

# ══════════════════════════════════════════
#  GAME STARTER
# ══════════════════════════════════════════

async def start_game(query, context, user_id: int, game: str, bet: float):
    """Deducts bet and starts the appropriate game"""
    
    if game == "slots":
        update_balance(user_id, -bet)
        result = spin_slots(bet)
        
        if result["win"]:
            update_balance(user_id, bet + result["profit"])
        
        record_game(user_id, "slots", bet, result["display"], result["profit"])
        balance = get_balance(user_id)
        msg = format_slots_result(result, bet, balance)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Rejouer", callback_data=f"bet_slots_{bet}"),
             InlineKeyboardButton("🔙 Menu", callback_data="menu")]
        ])
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=keyboard)
    
    elif game == "blackjack":
        update_balance(user_id, -bet)
        state = bj_new(bet)
        
        # Check immediate blackjack
        if is_blackjack(state["player"]):
            state["status"] = "player_win"
            profit = bj_profit(state)
            update_balance(user_id, bet + profit)
            record_game(user_id, "blackjack", bet, "blackjack", profit)
            balance = get_balance(user_id)
            msg = format_blackjack_state(state, show_dealer=True)
            msg += f"\n\n🎉 *BLACKJACK!*\n📈 Gain: *+${profit:.2f}*\n💼 Solde: `${balance:.2f}`"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Rejouer", callback_data="game_blackjack"),
                 InlineKeyboardButton("🔙 Menu", callback_data="menu")]
            ])
            await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=keyboard)
        else:
            save_game_state(user_id, "blackjack", json.dumps(state))
            msg = format_blackjack_state(state)
            await query.edit_message_text(
                msg, parse_mode="Markdown",
                reply_markup=blackjack_keyboard(can_double(state["player"]))
            )
    
    elif game == "dice":
        # First select prediction
        save_game_state(user_id, "dice_bet", json.dumps({"bet": bet}))
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⬇️ Bas (1-3) x2", callback_data="dice_low"),
                InlineKeyboardButton("⬆️ Haut (4-6) x2", callback_data="dice_high"),
            ],
            [
                InlineKeyboardButton("1️⃣ x6", callback_data="dice_exact_1"),
                InlineKeyboardButton("2️⃣ x6", callback_data="dice_exact_2"),
                InlineKeyboardButton("3️⃣ x6", callback_data="dice_exact_3"),
            ],
            [
                InlineKeyboardButton("4️⃣ x6", callback_data="dice_exact_4"),
                InlineKeyboardButton("5️⃣ x6", callback_data="dice_exact_5"),
                InlineKeyboardButton("6️⃣ x6", callback_data="dice_exact_6"),
            ],
            [InlineKeyboardButton("🔙 Annuler", callback_data="menu")]
        ])
        await query.edit_message_text(
            f"🎲 *DÉS* — Mise: `${bet:.2f}`\n\nQue vas-tu parier?",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    elif game == "roulette":
        save_game_state(user_id, "roulette_bet", json.dumps({"bet": bet}))
        await query.edit_message_text(
            f"🎡 *ROULETTE* — Mise: `${bet:.2f}`\n\nOù mises-tu?",
            parse_mode="Markdown",
            reply_markup=roulette_keyboard()
        )
    
    elif game == "mines":
        save_game_state(user_id, "mines_bet", json.dumps({"bet": bet}))
        await query.edit_message_text(
            f"💣 *MINES* — Mise: `${bet:.2f}`\n\nCombien de bombes?",
            parse_mode="Markdown",
            reply_markup=mines_setup_keyboard()
        )
    
    elif game == "coinflip":
        save_game_state(user_id, "coinflip_bet", json.dumps({"bet": bet}))
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🦅 Face", callback_data="cf_heads"),
                InlineKeyboardButton("🌊 Pile", callback_data="cf_tails"),
            ],
            [InlineKeyboardButton("🔙 Annuler", callback_data="menu")]
        ])
        await query.edit_message_text(
            f"🪙 *COIN FLIP* — Mise: `${bet:.2f}`\n\nFace ou Pile?",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

# ── Dice bet callbacks ──────────────────────────────────────────────────────────
# These need to be added to the main button_callback router

async def handle_dice_bet(query, user_id: int, prediction: str):
    state_row = get_game_state(user_id)
    if not state_row:
        return
    
    state_data = json.loads(state_row["state"])
    bet = state_data["bet"]
    
    update_balance(user_id, -bet)
    result = roll_dice(prediction, bet)
    
    if result["win"]:
        update_balance(user_id, bet + result["profit"])
    
    record_game(user_id, "dice", bet, str(result["roll"]), result["profit"])
    clear_game_state(user_id)
    
    balance = get_balance(user_id)
    msg = format_dice_result(result, bet, balance)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Rejouer", callback_data="game_dice"),
         InlineKeyboardButton("🔙 Menu", callback_data="menu")]
    ])
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=keyboard)
