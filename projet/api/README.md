# API Rasa chatbot

## Prérequis

>Docker
>Python3.6+

## Utilisation

Pour lancer le serveur
>docker compose -f api-docker-compose.yml up

Pour recompiler en cas de changement de `server.py`
>docker compose -f api/api-docker-compose.yml build --no-cache api



Afin de faire fonctionner le système d'ajout d'événements à un calendrier google, il faut d'abord suivre le tutoriel [ci-présent](https://developers.google.com/calendar/api/quickstart/python) afin de créer un projet permettant d'utiliser l'API Google Calendar puis ajouter le fichier `credentials.json` dans le dossier courant de l'API.

Ensuite, créer un environnement virtuel (optionnel) .venv et installer les packages décrits dans `requirements.txt`

Une fois cela fait, exécuter le script suivant:

>python google_cal.py


Si tout se passe bien le message suivant apparaîtra une fois connecté :

``Vous êtes bien connecté ou l'êtes à présent.``
