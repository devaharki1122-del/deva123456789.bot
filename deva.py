import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

FORCE_CHANNELS = [
    "@chanaly_boot",
    "@dwri_yar",
    "@Sayko_channel"
]

users = set()

# 🔒 Check Join
async def check_join(bot, user_id):
    for ch in FORCE_CHANNELS:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# 🏠 Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.add(user_id)

    if not await check_join(context.bot, user_id):
        buttons = [
            [InlineKeyboardButton("🔗 Join 1", url="https://t.me/chanaly_boot")],
            [InlineKeyboardButton("🔗 Join 2", url="https://t.me/dwri_yar")],
            [InlineKeyboardButton("🔗 Join 3", url="https://t.me/Sayko_channel")],
            [InlineKeyboardButton("✅ Check", callback_data="check")]
        ]

        await update.message.reply_text("🔒 Join first:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    buttons = [
        [InlineKeyboardButton("📥 Download", callback_data="download")],
        [InlineKeyboardButton("🤖 AI", callback_data="ai")],
        [InlineKeyboardButton("👑 Owner Panel", callback_data="owner")]
    ]

    await update.message.reply_text("✨ Main Menu", reply_markup=InlineKeyboardMarkup(buttons))

# 🔘 Buttons
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id

    if q.data == "check":
        if await check_join(context.bot, user_id):
            await q.edit_message_text("✅ Joined!")
        else:
            await q.edit_message_text("❌ Not joined")

    elif q.data == "download":
        context.user_data["mode"] = "download"
        await q.edit_message_text("📥 Send link")

    elif q.data == "ai":
        context.user_data["mode"] = "ai"
        await q.edit_message_text("🤖 Ask anything")

    elif q.data == "owner":
        if user_id != ADMIN_ID:
            await q.edit_message_text("❌ Not Owner")
            return

        buttons = [
            [InlineKeyboardButton("📊 Users", callback_data="stats")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")]
        ]

        await q.edit_message_text("👑 Owner Panel", reply_markup=InlineKeyboardMarkup(buttons))

    elif q.data == "stats":
        await q.edit_message_text(f"👥 Users: {len(users)}")

    elif q.data == "broadcast":
        context.user_data["mode"] = "broadcast"
        await q.edit_message_text("📢 Send message")

# 📩 Messages
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    mode = context.user_data.get("mode")

    if mode == "broadcast" and user_id == ADMIN_ID:
        for uid in users:
            try:
                await context.bot.send_message(uid, text)
            except:
                pass
        await update.message.reply_text("📢 Sent")

# 🚀 Run
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

app.run_polling()