import base64
import os
import re
import dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import requests

# Code réalisé à l'aide de la vidéo suivante :  How To Create A Telegram Bot In Python For Beginners (2023 Tutorial) - Indently
# https://www.youtube.com/watch?v=vZtm1wuA2yc

async def start_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bonjour! Je suis un bot de réservation. Que souhaitez-vous faire ?\neg. \"Je voudrais réserver un terrain de Pétanque, je voudrais réserver, quel est l'horaire de tennis, ...\"")

async def get_base64_document(uuid_file:str):
    if os.path.exists(f'./tmp/{uuid_file}.ics'):
        with open(f'./tmp/{uuid_file}.ics','rb') as f:
            return f.read()

async def handle_message(update:Update, context:ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    id_user = update.message.chat.id
    # headers = {"Content-Type": "application/json"}
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
    file = [elem["text"] for elem in response_json if elem["text"].startswith("[FILE]")]
    file_ics = ""
    if len(response_json) > 0:
        response_array = [str(resp["text"]).replace('[br]','\n').replace('[tab]','  ') for resp in response_json if not resp["text"].startswith("[FILE]")]
    

    # [OPTION][0][TITLE][option1][OPTIONS][(Un choix 1,1)(Un choix 2,2)(Un choix 3,3)][OPTION][1][TITLE][option2][OPTIONS][(Un choix 1,4)(Un choix 2,5)(Un choix 3,6)]
    for resp in response_array:
        if resp.startswith("[OPTION]"):
            options = resp.split("[OPTION]")[1:]
            regex_title = "\[TITLE\]\[(.*?)\]"
            regex_options = "\[OPTIONS]\[(.*?)\]"
            regex_single_opt = "\((.*?)\,"
            regex_single_opt_index = "\,(.*?)\)"

            titles = [re.search(regex_title,option).group(1) for option in options]
            options_choice = [re.search(regex_options,option)[1] for option in options]
            single_options = [re.findall(regex_single_opt,option) for option in options_choice]
            single_options_index = [re.findall(regex_single_opt_index,option)  for option in options_choice]

            resp = ""
            for index, title in enumerate(titles):
                resp+=f"{title}:\n"
                for ind_opt, opt in enumerate(single_options[index]):
                    resp+=f"\n\t{single_options_index[index][ind_opt]}. {opt}"
                resp+="\n\n"
            resp +="Veuillez choisir une option par question"
        regex_link = r'\[LINK\]\[(https://[^\]]+)\]'
        if re.findall(regex_link,resp):        
            resp = resp.replace("[","").replace("]","").replace("LINK","")
        await update.message.reply_text(resp,parse_mode="")
    if file:
        file_ics = f"{file[0].removeprefix('[FILE]')}"
    
        
        response = requests.get(f"http://api:5500/get-ics-file/{file_ics}")
        response.raise_for_status()
        response_json = response.json()
        if response.status_code == 200:
            try:
                b64File = str(response_json["file_base64"])[8:-1]
                print(f"FILE: {b64File}")
                binary_file = base64.b64decode(b64File)
                print(binary_file)
                with open(file=f'./tmp/{file_ics}.ics',mode='wb') as f:
                    f.write(binary_file)
                await update.message.reply_document(caption="Fichier ICS de l'événement",document=open(f'./tmp/{file_ics}.ics','rb')) 
                if os.path.exists(f'./tmp/{file_ics}.ics'):
                    os.remove(f'./tmp/{file_ics}.ics')   
            except Exception as e:
                print(f"Error while generating ICS: {e}")
                await update.message.reply_text('Erreur lors de la génération du fichier ics pour l\'événement')



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