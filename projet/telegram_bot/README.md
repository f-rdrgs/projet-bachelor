# Bot Telegram

## Prérequis

- Docker
- Python3.6+

## Utilisation

Le script associé au bot peut être lancé à la fois avec un simple 
>python main.py

Ou en utilisant docker compose
>docker compose -f telegram-docker-compose.yml up -d

Afin de pouvoir utiliser le bot il est nécessaire de créer un bot Telegram en suivant [le tutoriel suivant](https://core.telegram.org/bots/tutorial) et d'ensuite fournir la clé d'api dans un fichier `.env-api` dans le dossier courant `/telegram_bot` à créer dans le format suivant:
```
TELEGRAM_API_KEY=<CLÉ API>
```
