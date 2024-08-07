# Base de données

[toc]

## Prérequis

- Docker
- Postgres (Pour se connecter manuellement)
- libpq-dev
- python3.10-dev

## Schéma 
![Schéma base de données](./documentation/db.png)

## Usage 

### Démarrage simple 
Depuis le dossier racine projet: 

Démarrer la base de données
>docker compose up

Se connecter à la base de données
>psql -h 0.0.0.0 -p 3401 -U admin -d chatbot-rasa

Après avoir démarré la base de données, il faut lui fournir des données. Pour se faire, des fichiers `.csv` doivent être ajoutés dans le dossier `/data` en suivant le template fourni. Par défaut des fichiers sont déjà présent et ne nécessitent que d'être modifiés.
Une fois les fichiers ajoutés, il suffit d'exécuter le script python `data_insert.py`. Si les fichiers ne sont pas supprimés ou ajoutés, les intents spécifés sont déjà correctement configurés dans le script et ne nécessitent aucune modification.

Arrêter la base de données
>docker compose down

### Rebuild

Recréer l'image si la base de données à changé
>docker compose build --no-cache db

Supprimer le volume associé
>docker volume rm projet_chatbot_volume

Vider une table et reset son incrément (Après connection à la DB)
>TRUNCATE TABLE [table] RESTART IDENTITY CASCADE;

## Sources

[Tutoriel de mise en place de la DB](https://1kevinson.com/how-to-create-a-postgres-database-in-docker/)