# Rasa Chatbot

## Prérequis

>Docker
>Python

## Usage

Lancer le bot 
>docker compose -f rasa-docker-compose.yml up

Recompiler l'image si des changements ont été effectués
>docker compose -f rasa-docker-compose.yml build --no-cache 

Pour vérifier si bot est valide
>rasa data validate -d domain

Afin de rendre le bot le plus modulable selon les données utilisées, un script `fill_data.py` est présent qui va générer certains intents fortements liés aux ressources disponibles dans `/db/data/*.csv`. Si davantage d'intents doivent être ajoutés, il suffit de les spécifier dans `fill_data.py` et d'ajouter les textes qui précèdent ou font suite aux données fournies dans `/data_filling`.