# API Rasa chatbot

## Prérequis

>Docker

## Utilisation

Pour lancer le serveur
>docker compose -f api-docker-compose.yml up

Pour recompiler en cas de changement de `server.py`
>docker compose -f api/api-docker-compose.yml build --no-cache api
