import os
import dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import requests

# Code réalisé à l'aide de la vidéo suivante :  How To Create A Telegram Bot In Python For Beginners (2023 Tutorial) - Indently
# https://www.youtube.com/watch?v=vZtm1wuA2yc

async def start_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bonjour! Je suis un bot de réservation. Que souhaitez-vous faire ?\neg. \"Je voudrais réserver un terrain de Pétanque, je voudrais réserver, ...\"")

async def handle_message(update:Update, context:ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    id_user = update.message.chat.id
    headers = {"Content-Type": "application/json"}
    data = {
        "message":text,
        "sender": str(id_user)
    }
    print(data)
    response = requests.post("http://api:5500/communicate-rasa",json={
        "message": str(text),
        "sender": str(id_user)
    })
    response.raise_for_status()
    response_array = []
    response_json = response.json()
    print(f"Rasa response: {response_json}")
    if len(response_json) > 0:
        response_array = [resp["text"] for resp in response_json]
    
    for resp in response_array:
        await update.message.reply_text(resp)


async def error(update:Update, context:ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


if __name__ == "__main__":
    dotenv.load_dotenv(dotenv_path="./.env-api")
    TOKEN = os.getenv('TELEGRAM_API_KEY')
    dotenv.load_dotenv(dotenv_path="./.env-api")
    print(os.getenv('BOT_USERNAME'))
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()

    app.add_handler(CommandHandler('start',start_command))

    app.add_handler(MessageHandler(filters.TEXT,handle_message))
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=1)