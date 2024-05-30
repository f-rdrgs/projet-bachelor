import datetime
from fastapi import FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import asyncio
import httpx
import os

app = FastAPI()

class Communicate_Rasa(BaseModel):
    sender:str
    message:str

class Test_rasa_nlu(BaseModel):
    text:str

origins = [
    "http://0.0.0.0",
    "http://0.0.0.0:5500",
    "http://localhost:5500",
    "http://localhost",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from configparser import ConfigParser

# https://www.postgresqltutorial.com/postgresql-python/connect/
def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config



from sqlalchemy import Column, ForeignKey, Time, create_engine, select
from sqlalchemy.engine import URL

config = load_config()

url = URL.create(
    drivername="postgresql",
    username=config["user"],
    host=config["host"],
    database=config["database"],
    password=config["password"],
    port=config["port"]
)

engine = create_engine(url)



# https://coderpad.io/blog/development/sqlalchemy-with-postgresql/
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, VARCHAR,Enum

import enum

Base = declarative_base()


class Jours_Semaine(enum.Enum):
    lundi = 0
    mardi = 1
    mercredi = 2
    jeudi = 3
    vendredi = 4
    samedi = 5
    dimanche = 6

class Ressource(Base):
    __tablename__ = 'ressource'

    label = Column(VARCHAR(),primary_key=True)
    description = Column(Text(),nullable=True)

class Jour_Horaire(Base):
    __tablename__ = 'jour_horaire'

    id = Column(Integer(),primary_key=True,autoincrement="auto")
    jour = Column(Enum(Jours_Semaine),nullable=False)
    debut = Column(Time(),nullable=False)
    fin = Column(Time(),nullable=False)
    temps_reservation = Column(Time(),nullable=False)
    label = Column(VARCHAR(),ForeignKey('ressource.label'),nullable=True)

from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

def seconds_to_hour_min_sec(seconds:int)-> tuple[int,int,int]:
    hour = seconds / 3600

@app.get("/get-jours-semaine/{ressource_label}")
async def get_jours_semaine(ressource_label:str):
    query = session.query(Jour_Horaire.jour).where(Jour_Horaire.label.like(ressource_label)).distinct().all()
    query_result = []
    if query.__len__() > 0:
       query_result = [Jours_Semaine(jour[0]).value for jour in query]
    # query_result = jsonable_encoder(query)
    # print(query)
    return JSONResponse(content=query_result,status_code=status.HTTP_200_OK)


@app.get("/get-horaires/{ressource_label}")
async def get_horaires_for_ressource(ressource_label: str):
    query = session.query(Jour_Horaire).where(Jour_Horaire.label.like(ressource_label)).all()
    query_result = jsonable_encoder(query)
    print(query_result)
    return JSONResponse(content=query_result,status_code=status.HTTP_200_OK)

@app.get("/get-horaires/{jour_semaine}/{ressource_label}")
async def get_horaires_for_ressource(jour_semaine:str,ressource_label: str):
    try:
        decoupage = datetime.time(minute=30)
        print(decoupage.__str__())
        query = session.query(Jour_Horaire).where(Jour_Horaire.label.like(ressource_label)).where(Jour_Horaire.jour == Jours_Semaine[jour_semaine]).all()
        query_result = jsonable_encoder(query)
        print(query_result)

        total_sec_calc = lambda hour,minute,second: (hour*3600 + minute*60 + second)

        
        final_schedule = []
        for schedule in query_result:
            print(f"Schedule {schedule}")
            debut = datetime.datetime.strptime(schedule['debut'], '%H:%M:%S').time()
            debut_delta = datetime.timedelta(seconds=total_sec_calc(debut.hour,debut.minute,debut.second))
            fin = datetime.datetime.strptime(schedule['fin'], '%H:%M:%S').time()
            fin_delta = datetime.timedelta(seconds=total_sec_calc(fin.hour,fin.minute,fin.second))
            print(f"Debut {debut}")
            print(f"Fin {fin}")


            decoupage_delta = datetime.timedelta(seconds=total_sec_calc(decoupage.hour,decoupage.minute,decoupage.second))

            slot_count = (fin_delta.total_seconds()-debut_delta.total_seconds()) / decoupage_delta.total_seconds()

            print(f"Number of slots : {slot_count}")
            new_schedule = [str(debut_delta+(decoupage_delta*offset)) for offset in range(int(slot_count))]
            final_schedule += new_schedule


        return JSONResponse(content={"horaire_heures":final_schedule,"horaire":query_result},status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



@app.get("/get-ressources")
async def get_ressources():
    query = session.query(Ressource).all()
    return JSONResponse(content=jsonable_encoder(query),status_code=status.HTTP_200_OK)

@app.post("/test-nlu")
async def test_nlu_rasa(data:Test_rasa_nlu):
    headers = {"Content-Type": "application/json"}
    print(data.model_dump_json())
    async with httpx.AsyncClient() as client:
        response = await client.post('http://rasa-core:5005/model/parse',data=data.model_dump_json(),headers=headers)    
        return JSONResponse(content=response.json(),status_code=status.HTTP_200_OK)

@app.post("/communicate-rasa")
async def talk_to_rasa(data:Communicate_Rasa):
    headers = {"Content-Type": "application/json"}
    print(data.model_dump_json())
    async with httpx.AsyncClient() as client:
        response = await client.post('http://rasa-core:5005/webhooks/rest/webhook',data=data.model_dump_json(),headers=headers)    
        return JSONResponse(content=response.json(),status_code=status.HTTP_200_OK)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0" , port=5500, log_level="info",reload = True,workers=4,reload_dirs=["/app"],reload_excludes=["/app/.venv"])