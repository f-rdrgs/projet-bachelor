FROM python:3.10

WORKDIR /app

COPY ./requirements.txt ./main.py ./.env /app/

RUN pip install --upgrade pip setuptools wheel && pip install -r requirements.txt

CMD [ "python3.10","-u","./main.py" ]