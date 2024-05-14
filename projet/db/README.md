# Base de données


## Prérequis

- Docker
- Postgres (Pour se connecter manuellement)

## Schéma 
![Schéma base de données](./documentation/db.png)

## Usage 

Démarrer la base de données
>docker compose up

Se connecter à la base de données
>psql -h 0.0.0.0 -p 3401 -U admin -d chatbot-rasa

Arrêter la base de données
>docker compose down