# Base de données

[toc]

## Prérequis

- Docker
- Postgres (Pour se connecter manuellement)

## Schéma 
![Schéma base de données](/documentation/db.png)

## Usage 

### Démarrage simple 
Depuis le dossier racine projet: 

Démarrer la base de données
>docker compose up

Se connecter à la base de données
>psql -h 0.0.0.0 -p 3401 -U admin -d chatbot-rasa

Arrêter la base de données
>docker compose down

### Rebuild

Recréer l'image si la base de données à changé
>docker compose build --no-cache db

Supprimer le volume associé
>docker volume rm projet_chatbot_volume

## Sources

[Tutoriel de mise en place de la DB](https://1kevinson.com/how-to-create-a-postgres-database-in-docker/)