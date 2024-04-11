import requests
import os
import numpy as np
# Training example from https://towardsdatascience.com/building-a-conversational-chatbot-for-slack-using-rasa-and-python-part-1-bca5cc75d32f#bypass 
# from rasa_nlu.training_data import load_data
# from rasa_nlu.config import RasaNLUModelConfig
# from rasa_nlu.model import Trainer
# from rasa_nlu import config

# # loading the nlu training samples
# training_data = load_data("nlu.md")

# # trainer to educate our pipeline
# trainer = Trainer(config.load("config.yml"))

# # train the model!
# interpreter = trainer.train(training_data)

# # store it for future use
# model_directory = trainer.persist("./models/nlu", fixed_model_name="current")


def send_message_to_rasa(message):
    url = 'http://localhost:5005/webhooks/rest/webhook' # Assuming Rasa server is running locally on port 5005
    data = {'sender': 'user','message': message}
    response = requests.post(url, json=data,headers={
        'Content-Type': 'application/json'
    })
    return response.json()

# https://rasa.com/docs/rasa/training-data-format/#lookup-tables
# https://rasa.com/docs/rasa/nlu-training-data/#entities-roles-and-groups
# D'abord lancer le serveur
# rasa run --enable-api --port 5005  --cors '*' -m models/my_rasa_model.tar.gz
# Ensuite lancer le serveur d'actions custom
# rasa run actions
# rasa train --fixed-model-name my_rasa_model
# model FR à avoir 
# python3.10 -m spacy download fr_core_news_md 
# Pour run serveur duckling 
# docker run --name duckling_reserv -p 8000:8000 rasa/duckling 
# ou 
# docker start duckling_reserv -a 
# Renseigner sur Forms pour créer un patterne de conversation qui nécessite de récupérer une quantité d'informations avant de passer à la suite
# https://rasa.com/docs/rasa/forms/#defining-a-form 

# Intéressant example fourni dans le rapport de recherche officiel de Rasa
# https://arxiv.org/pdf/2402.12234.pdf
# Seulement disponible avec Rasa Pro mais peut-être intéressant à mentionner ?

# À noter que les dates en format dd.mm.yyyy ne marchent pas et doivent être traitées en dd/mm/yyyy
if __name__ == "__main__":
    stop_convo = False
    while(not stop_convo):
        user_input = input("Entrez \"stop\" pour arrêter\nVotre message ->")
        print(f"input: {user_input}")
        if(user_input== "stop"):
            stop_convo= True
        if( not stop_convo):
            responses = send_message_to_rasa(user_input)
            print("Rasa's response ->", responses) 
            for response in responses:
                if response["text"] == "Au revoir":
                    stop_convo = True
