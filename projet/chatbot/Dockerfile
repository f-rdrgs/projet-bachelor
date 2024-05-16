FROM python:3.10

WORKDIR '/app'

COPY ./actions ./data ./tests ./*.yml ./requirements.txt /app/

RUN pip install -r requirements.txt && python3.10 -m spacy download fr_core_news_md