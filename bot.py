import logging
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = "8535807539:AAFxJV3X3SAKqu08d1irGHEv9mLs1Rv5sII"
# Simplified database: {user_id: {"xp": 0, "level": 1}}
user_data = {}

# --- ADMIN COMMANDS ---

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await context.bot.unban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"👢 {user.first_name} has been kicked.")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"🚫 {user.first_name} has been permanently banned.")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        permissions = ChatPermissions(can_send_messages=False)
        await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions)
        await update.message.reply_text(f"🔇 {user.first_name} is now muted.")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        permissions = ChatPermissions(can_send_messages=True, can_send_polls=True, can_send_other_messages=True)
        await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions)
        await update.message.reply_text(f"🔊 {user.first_name} can speak again.")

# --- CAPTCHA & JOIN LOGIC ---

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        # Mute them until they pass captcha
        await context.bot.restrict_chat_member(update.effective_chat.id, member.id, ChatPermissions(can_send_messages=False))
        
        keyboard = [[InlineKeyboardButton("✅ I am Human", callback_data=f"verify_{member.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Welcome {member.mention_html()}! Click below to talk.", reply_markup=reply_markup, parse_mode='HTML')

async def captcha_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id_to_verify = int(query.data.split("_")[1])
    
    if query.from_user.id == user_id_to_verify:
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id_to_verify, ChatPermissions(can_send_messages=True))
        await query.answer("Verified! You can now chat.")
        await query.edit_message_text("✅ Verification successful.")
    else:
        await query.answer("This button isn't for you!", show_alert=True)

# --- LEVELS & PROFILE ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "level": 1}
    
    user_data[user_id]["xp"] += 10 # 10 XP per message
    
    # Level up every 100 XP
    if user_data[user_id]["xp"] >= user_data[user_id]["level"] * 100:
        user_data[user_id]["level"] += 1
        await update.message.reply_text(f"🎉 Congrats {update.effective_user.first_name}! You reached Level {user_data[user_id]['level']}!")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = user_data.get(user_id, {"xp": 0, "level": 1})
    await update.message.reply_text(f"👤 PROFILE: {update.effective_user.first_name}\n⭐ Level: {stats['level']}\n📊 XP: {stats['xp']}")

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 Web Dashboard: [Coming Soon]\nManage your settings here: https://your-website.com")

# --- MAIN ---

if __name__ == "__main__":
    app = Application.builder().token(8535807539:AAFxJV3X3SAKqu08d1irGHEv9mLs1Rv5sII).build()

    # Handlers
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("level", profile)) # Reuse profile for level
    app.add_handler(CommandHandler("dashboard", dashboard))
    
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(CallbackQueryHandler(captcha_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Bot is running 24/7 (Local test)...")

    app.run_polling()
