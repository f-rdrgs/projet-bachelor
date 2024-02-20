import requests
import os

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
# Pour train
# rasa train --fixed-model-name my_rasa_model
if __name__ == "__main__":
    user_input = input("Your input -> ")
    response = send_message_to_rasa(user_input)
    print("Rasa's response ->", response)