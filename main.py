from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = 8597525857:AAGmQPuasuLbIwSBHa2cLjzS-8aYAXkkJAc

waiting_users = []
active_pairs = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await update.message.reply_text(
        "👋 Привет! Это анонимный чат.\n"
        "Нажми /next чтобы найти собеседника!"
    )


async def next_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # если уже в паре — удалить
    if user_id in active_pairs:
        pair = active_pairs[user_id]
        del active_pairs[pair]
        del active_pairs[user_id]

    if waiting_users and waiting_users[0] != user_id:
        partner_id = waiting_users.pop(0)

        active_pairs[user_id] = partner_id
        active_pairs[partner_id] = user_id

        await context.bot.send_message(partner_id, "🔗 Найден новый собеседник!")
        await update.message.reply_text("🔗 Найден новый собеседник!")
    else:
        if user_id not in waiting_users:
            waiting_users.append(user_id)
        await update.message.reply_text("⏳ Ожидание собеседника...")


async def relay_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in active_pairs:
        await update.message.reply_text("❗ Нажми /next чтобы найти собеседника")
        return

    partner_id = active_pairs[user_id]
    await context.bot.send_message(partner_id, update.message.text)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", next_partner))
    app.add_handler(MessageHandler(filters.TEXT, relay_message))

    app.run_polling()
