from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

# Bot tokeningizni kiriting
TOKEN = "7922057081:AAGi7X77AbRM-8y38kppr300PxpbJEvlCqo"

# Botni ishga tushirish
app = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("Salom! Bot ishlamoqda! 😊")

app.add_handler(CommandHandler("start", start))
app.run_polling()
