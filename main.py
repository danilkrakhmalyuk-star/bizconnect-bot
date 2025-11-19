from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "ТВОЙ_ТОКЕН_СЮДА"

waiting_users = []
active_pairs = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        "👋 Привет! Это анонимный чат про деньги, успех, бизнес и развитие.\n"
        "Нажми /next чтобы найти собеседника."
    )


async def next_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id

    if user in active_pairs:
        partner = active_pairs[user]
        del active_pairs[user]
        del active_pairs[partner]
        await update.message.reply_text("Вы отключены от прошлого собеседника. Ищу нового…")

    if waiting_users:
        partner = waiting_users.pop(0)
        active_pairs[user] = partner
        active_pairs[partner] = user

        await context.bot.send_message(partner, "🔗 Вы подключены! Можете общаться.")
        await update.message.reply_text("🔗 Собеседник найден! Общайтесь.")
    else:
        waiting_users.append(user)
        await update.message.reply_text("🔍 Ищу собеседника… Подожди немного.")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    if user in active_pairs:
        partner = active_pairs[user]
        del active_pairs[user]
        del active_pairs[partner]

        await context.bot.send_message(partner, "❌ Собеседник отключился.")
        await update.message.reply_text("Вы отключены.")
    else:
        await update.message.reply_text("Вы ни с кем не общаетесь.")


def allowed(message: str):
    keywords = ["деньги", "бизнес", "успех", "мотивация", "развитие", "инвестиции", "доход"]
    return any(word in message.lower() for word in keywords)


async def relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id

    if user not in active_pairs:
        await update.message.reply_text("❗ Вы не подключены к собеседнику. Напишите /next")
        return

    text = update.message.text

    if not allowed(text):
        await update.message.reply_text("⚠️ Только тема денег, бизнеса и успеха.")
        return

    partner = active_pairs[user]
    await context.bot.send_message(partner, text)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", next_partner))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, relay))

    print("Bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()
