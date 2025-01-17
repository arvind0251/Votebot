from telegram import Update, Poll
from telegram.ext import Application, CommandHandler, PollHandler, CallbackContext

TOKEN = "YOUR_BOT_TOKEN"

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Use /vote to create a poll.")

async def create_poll(update: Update, context: CallbackContext):
    question = "Your favorite programming language?"
    options = ["Python", "JavaScript", "C++"]
    await update.message.reply_poll(question, options, is_anonymous=False)

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("vote", create_poll))

print("Bot started!")
app.run_polling()
