# Prototype de Chatbot avec Rasa

## Installation

```bash
pip install -r requirements.txt
```
et téléchargement du modèle

```bash
python3.10 -m spacy download fr_core_news_md
```

Afin de faire fonctionner le composant Duckling, il est nécessaire d'avoir une installation fonctionnelle de Docker et si souhaité pull en avance l'image `rasa/duckling`

## Préparation du Chatbot

Afin de pouvoir faire usage du Chatbot, il est nécessaire d'entrainer le modèle au préalable

```bash
rasa train --fixed-model-name my_rasa_model
```

## Utilisation

En se trouvant dans le dossier `test_reservation`

Il faut exécuter les commandes suivantes dans un terminal chacun :
```bash
rasa run --enable-api --port 5005  --cors '*' -m models/my_rasa_model.tar.gz
rasa run actions
docker run --name duckling -p 8000:8000 rasa/duckling 
```