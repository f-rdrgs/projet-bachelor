FROM python:3.10

WORKDIR /app

COPY ./requirements.txt ./server.py database.ini /app/

RUN pip install -r requirements.txt

CMD [ "python3.10","./server.py" ]

