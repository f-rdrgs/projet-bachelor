import datetime
from zoneinfo import ZoneInfo
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

class Reservation_API(BaseModel):
    nom:str
    prenom:str
    numero_tel:str
    ressource:str
    date:datetime.date
    heure:datetime.time

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



from sqlalchemy import Column, ForeignKey, Time, create_engine, TIMESTAMP
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
from sqlalchemy import Column, Integer, Date, Text, VARCHAR,Enum, Time

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

class Reservation(Base):
    __tablename__ = 'reservation'
    id = Column(Integer(),primary_key=True,autoincrement="auto")
    nom = Column(VARCHAR(),nullable=False)
    prenom = Column(VARCHAR(),nullable=False)
    numero_tel = Column(VARCHAR(),nullable=False)
    date_reservation = Column(TIMESTAMP(),nullable=False)

class Reservations_Client_Resource(Base):
    __tablename__ = 'reservations_client_resource'
    id = Column(Integer(),primary_key=True,autoincrement="auto")
    reservation = Column(Integer(),ForeignKey('reservation.id'), nullable=False)
    resource = Column(VARCHAR(),ForeignKey('ressource.label'),nullable=False)
    date_reservation = Column(Date(),nullable=False)
    heure = Column(Time(),nullable=False)

from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

def seconds_to_hour_min_sec(seconds:int)-> tuple[int,int,int]:
    hour = seconds / 3600

# Temps stocké en UTC (2h en moins qu'en Suisse)

@app.post("/add-reservation/")
async def add_reservation(data:Reservation_API):
    
        new_reservation = Reservation(nom=data.nom,prenom=data.prenom,numero_tel=data.numero_tel,date_reservation=datetime.datetime.now(ZoneInfo('Europe/Paris')))
        print(datetime.datetime.now())
        output_reserv = Reservation()
        output_reserv_ressource = Reservations_Client_Resource()
        try:
            with Session.begin() as session:
                session.add(new_reservation)
                session.flush()
                session.refresh(new_reservation)
                output_reserv = {"id": new_reservation.id,"nom": new_reservation.nom,"prenom": new_reservation.prenom,"numero_tel": new_reservation.numero_tel,"date_reservation": new_reservation.date_reservation}
            with Session.begin() as session:
                reservation_ressource = Reservations_Client_Resource(reservation=output_reserv["id"],resource=data.ressource,date_reservation=data.date,heure=data.heure)
                session.add(reservation_ressource)
                session.flush()
                session.refresh(reservation_ressource)
                output_reserv_ressource = {"id": reservation_ressource.id,"heure": reservation_ressource.heure,"date_reservation": reservation_ressource.date_reservation,"ressource": reservation_ressource.resource,"date_reservation": reservation_ressource.date_reservation}
            return JSONResponse(content={
                    "message":"Réservation ajoutée",
                    "data":{"reservation":jsonable_encoder(output_reserv),"reservation_ressource":jsonable_encoder(output_reserv_ressource)}
                },status_code=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
        

@app.get("/get-reservations-ressources/")    
async def get_reservations_ressources():
    with Session.begin() as session:
        query = session.query(Reservations_Client_Resource).distinct().all()
        
        return JSONResponse(content=jsonable_encoder(query),status_code=status.HTTP_200_OK)

@app.get("/get-reservations-ressources/{ressource}")    
async def get_reservations_ressources(ressource:str):
    with Session.begin() as session:
        query = session.query(Reservations_Client_Resource).where(Reservations_Client_Resource.resource == ressource).distinct().all()
        
        return JSONResponse(content=jsonable_encoder(query),status_code=status.HTTP_200_OK)



@app.get("/get-jours-semaine/{ressource_label}")
async def get_jours_semaine(ressource_label:str):
    with Session.begin() as session:
        query = session.query(Jour_Horaire.jour).where(Jour_Horaire.label.like(ressource_label)).distinct().all()
        query_result = []
        if query.__len__() > 0:
            query_result = [Jours_Semaine(jour[0]).value for jour in query]
        return JSONResponse(content=query_result,status_code=status.HTTP_200_OK)


@app.get("/get-horaires/{ressource_label}")
async def get_horaires_for_ressource(ressource_label: str):
    with Session.begin() as session:
        query = session.query(Jour_Horaire).where(Jour_Horaire.label.like(ressource_label)).all()
        query_result = jsonable_encoder(query)
        print(query_result)
        return JSONResponse(content=query_result,status_code=status.HTTP_200_OK)

@app.get("/get-horaires/{jour}/{ressource_label}")
async def get_horaires_for_ressource(jour:str,ressource_label: str):

        with Session.begin() as session:
            decoupage = datetime.time(minute=30)
            jour_date = datetime.datetime.fromisoformat(jour).date()
            # Récupère les horaires d'une ressource pour un jour de la semaine donné
            query = session.query(Jour_Horaire).where(Jour_Horaire.label.like(ressource_label)).where(Jour_Horaire.jour == Jours_Semaine(jour_date.weekday())).all()
            # Récupère toutes les réservations correspondant à la date donnée
            query_reservations = session.query(Reservations_Client_Resource.heure).where(Reservations_Client_Resource.resource == ressource_label).where(Reservations_Client_Resource.date_reservation == jour_date).all()
            # Ressort une liste de temps
            query_reservations_time = [time[0] for time in query_reservations]
            query_result = jsonable_encoder(query)
            # query_reservations_result = jsonable_encoder(query_reservations)
            print(f"Réservations: {query_reservations_time}")
            print(query_result)

            total_sec_calc = lambda hour,minute,second: (hour*3600 + minute*60 + second)

            
            final_schedule = []
            # Créer une liste d'horaires sous format `HEURE:MINUTE:SECONDE`
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
                new_schedule_no_reserved_schedules = []
                for schedule in new_schedule:
                    if(datetime.datetime.strptime(schedule,"%H:%M:%S").time() not in query_reservations_time):
                        new_schedule_no_reserved_schedules.append(schedule)
                final_schedule += new_schedule_no_reserved_schedules


            return JSONResponse(content={"horaire_heures":final_schedule,"horaire":query_result},status_code=status.HTTP_200_OK)



@app.get("/get-ressources")
async def get_ressources():
    with Session.begin() as session:
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