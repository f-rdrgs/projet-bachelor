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