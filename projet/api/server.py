import datetime
import time
from typing import Any, List
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException, status
from fastapi.concurrency import asynccontextmanager
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import asyncio
import httpx
import os

import numpy as np
from google_cal import add_event_reservation, gen_share_link_google_cal, create_ical_event


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
    list_options:list[int]

class Temp_Reservation_API(BaseModel):
    ressource:str
    heure: datetime.time
    date_reserv: datetime.date

origins = [
    "http://0.0.0.0",
    "http://0.0.0.0:5500",
    "http://localhost:5500",
    "http://localhost",
    "*",
]


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



from sqlalchemy import Column, ForeignKey, Row, Time, Tuple, create_engine, TIMESTAMP, func, null, tuple_
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
    reservation = Column(Integer(),ForeignKey('reservation.id'),  nullable=False)
    resource = Column(VARCHAR(),ForeignKey('ressource.label'),primary_key=True,nullable=False)
    date_reservation = Column(Date(),primary_key=True,nullable=False)
    heure = Column(Time(),primary_key=True,nullable=False)

class Temp_Reservation(Base):
    __tablename__ = 'temp_reservation'
    label_ressource = Column(VARCHAR(),ForeignKey('ressource.label'),primary_key=True, nullable=False)
    heure = Column(Time(),primary_key=True, nullable=False)
    date_reserv = Column(Date(),primary_key=True, nullable=False)
    timestamp_reserv = Column(TIMESTAMP(), nullable=False)

class Options_Resource(Base):
    __tablename__ = 'options_resource'
    label_resource = Column(VARCHAR(),ForeignKey('ressource.label'),nullable=False,primary_key=True)
    label_option = Column(VARCHAR(),nullable=False, primary_key=True)
    description = Column(Text(),nullable=True)

class Options_Resource_Choix(Base):
    __tablename__ = 'options_resource_choix'
    id = Column(Integer(),primary_key=True,autoincrement="auto")
    label_option = Column(VARCHAR(),ForeignKey('ressource.label'), nullable=False)
    choix = Column(VARCHAR(), nullable=False)

class Reservations_Client_Choix(Base):
    __tablename__ = 'reservations_client_choix'
    id = Column(Integer(),primary_key=True,autoincrement="auto")
    reservation = Column(Integer(),ForeignKey('reservation.id'),nullable=False)
    resource = Column(VARCHAR(),ForeignKey('ressource.label'),nullable=False)
    id_choix_ressource = Column(Integer(),ForeignKey('options_resource_choix.id'),nullable=False)
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

time_for_deletion = datetime.timedelta(minutes=1,seconds=15)
interval_exec_remove = 10
"""
Requête à la bdd permettant de supprimer les pré-réservations plus vieilles que le temps spécifié
"""
async def delete_reservation_query():   
    with Session.begin() as session:
        query = session.query(Temp_Reservation).where(Temp_Reservation.timestamp_reserv < ( datetime.datetime.now(ZoneInfo('Europe/Paris')) - time_for_deletion)).delete()
    return query

"""
Fonction exécutant la suppression de pré-réservations chaque fois que le temps défini s'est écoulé
"""
async def remove_old_reservations(interval: int):
    while True:
        print(f"Removed old temp. reservations at {datetime.datetime.now(ZoneInfo('Europe/Paris'))}")
        await delete_reservation_query()
        await asyncio.sleep(interval)


"""
Fonction faisant usage du lifespan de l'app pour démarrer une tache de suppression continuelle des pré-réservations jusqu'à l'arrêt du serveur
"""
@asynccontextmanager
async def start_remove_reserv_task(app:FastAPI):
    print("Starting execution of removal of temp reservations")
    task = asyncio.create_task(remove_old_reservations(interval_exec_remove))
    yield
    print("Stopping execution of removal of temp reservations")
    task.cancel()



app = FastAPI(lifespan=start_remove_reserv_task)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


"""
Ressort les horaires de la semaine pour une ressource sous ce format :

{
Jour de la semaine (lundi = 0, mardi = 1, ...)
 "0": [ [ Array d'heures de début[début1, début2], Array d'heures de fin[fin1,fin2], découpage horaire], [ Array d'heures de début[début1, début2], Array d'heures de fin[fin1,fin2], découpage horaire]],
 ...
 Un jour peut posséder de multiples horaires différents avec des découpages différents, d'où la présence d'un array de tuples ici
}
"""
def get_all_horaires_semaine_for_ressource(ressource:str,jours_semaine:list[Jours_Semaine])-> tuple[dict[int,tuple[list[datetime.time],list[datetime.time],datetime.time]],Any]:
    try:
        with Session.begin() as session:
            query = session.query(Jour_Horaire.jour,Jour_Horaire.temps_reservation,func.array_agg(Jour_Horaire.debut).label("heures_debut"),func.array_agg(Jour_Horaire.fin).label("heures_fin")).where(Jour_Horaire.label == ressource).filter(Jour_Horaire.jour.in_(jours_semaine)).group_by(Jour_Horaire.jour,Jour_Horaire.temps_reservation).distinct().all()
            output : dict[int,tuple[list[datetime.time],list[datetime.time]]] = {}
            output_query = {}
            for day in query:
                if Jours_Semaine(day[0]).value not in output.keys():
                    output[Jours_Semaine(day[0]).value] = []
                output[Jours_Semaine(day[0]).value].append(tuple([day[2],day[3],day[1]]))
            for day in query:
                if Jours_Semaine(day[0]).value not in output_query.keys():
                    output_query[Jours_Semaine(day[0]).value] = []
                output_query[Jours_Semaine(day[0]).value].append({"horaires":[[debut,fin]for debut,fin in zip(day[2],day[3])],"decoupage":day[1]})
            return jsonable_encoder(output), jsonable_encoder(output_query)
    except Exception as e:
        print(f"An error has occured while getting horaires: {e}")
        return {},[]
    

"""
Permet de récupérer l'ensemble des heures pour chaque jour de la semaine pour une ressource

{
"0"(0 Correspond à lundi):[
    "14:30:00", "15:00:00", ...
]
}
"""
def get_heures_semaine_for_ressource(ressource:str,jours_semaine:list[Jours_Semaine] = [Jours_Semaine.lundi,Jours_Semaine.mardi,Jours_Semaine.mercredi,Jours_Semaine.jeudi,Jours_Semaine.vendredi,Jours_Semaine.samedi,Jours_Semaine.dimanche]):
    try:
        horaires,query_horaire = get_all_horaires_semaine_for_ressource(ressource,jours_semaine)
        print(f"horaires: {horaires}\n\n\nhoraire_query: {query_horaire}")
        heures_semaine = {}
        for jour in horaires.keys():
            for sub_horaire in horaires[jour]:

                decoupage = datetime.time.fromisoformat(sub_horaire[2])
                horaires_debut_fin = [(datetime.datetime.strptime(debut,"%H:%M:%S").time(),datetime.datetime.strptime(fin,"%H:%M:%S").time(),decoupage) for debut,fin in zip(sub_horaire[0],sub_horaire[1])]

                total_sec_calc = lambda hour,minute,second: (hour*3600 + minute*60 + second)
                final_schedule = []
                for heures_tuple in horaires_debut_fin:
                    debut, fin, decoupage = heures_tuple

                    debut_delta = datetime.timedelta(seconds=total_sec_calc(debut.hour,debut.minute,debut.second))
                    fin_delta = datetime.timedelta(seconds=total_sec_calc(fin.hour,fin.minute,fin.second))


                    decoupage_delta = datetime.timedelta(seconds=total_sec_calc(decoupage.hour,decoupage.minute,decoupage.second))

                    slot_count = (fin_delta.total_seconds()-debut_delta.total_seconds()) / decoupage_delta.total_seconds()



                    # print(f"Number of slots : {slot_count}")
                    new_schedule = [str((datetime.datetime.combine(datetime.date.today(), debut)+(decoupage_delta*offset)).time()) for offset in range(int(slot_count))]
                    final_schedule += new_schedule
                    if jour not in heures_semaine.keys():
                        heures_semaine[jour] = []
                    heures_semaine[jour] += (final_schedule)
            
        
        return heures_semaine,query_horaire

    except Exception as e:
        print(f"Error on horaire semaine: {e}")
        return {},{}

# Récupérer les réservations pour une date et ressource donnée
def get_reservations_for_dates_for_ressource(ressource:str,dates:list[datetime.date])->dict[datetime.date,list[datetime.time]]:
    try:
        with Session.begin() as session:
            query = session.query(Reservations_Client_Resource.date_reservation,func.array_agg(Reservations_Client_Resource.heure).label("heures")).filter(Reservations_Client_Resource.date_reservation.in_(dates)).where(Reservations_Client_Resource.resource == ressource).group_by(Reservations_Client_Resource.date_reservation)
            print(query)
            return jsonable_encoder(query)
    except Exception as e:
        return []

"""
Récupère les titres associés à une liste d'ids de choix
"""
def get_choix_titres_from_ids(list_choix:list[int])->list[str]:
    try:
        with Session.begin() as session:
            query = session.query(Options_Resource_Choix.choix).where(Options_Resource_Choix.id.in_(list_choix)).all()
            return jsonable_encoder([opt[0] for opt in query])
    except Exception as e:
        print(e)
        return [] 

"""
Récupère une liste des pré réservations pour une liste de dates et une ressource donnée

[
[date, [heure1, heure2, heure3]]
]
"""
def get_reservations_temporaire_for_dates_for_ressource(ressource:str,dates:list[datetime.date])->dict[datetime.date,list[datetime.time]]:
    try:
        with Session.begin() as session:
            query = session.query(Temp_Reservation.date_reserv, func.array_agg(Temp_Reservation.heure).label("heures")).filter(Temp_Reservation.date_reserv.in_(dates)).where(Temp_Reservation.label_ressource.like(ressource)).group_by(Temp_Reservation.date_reserv)
            print(f"Temp Res: {query}")
            return jsonable_encoder(query)
    except Exception as e:
        return []

# Temps stocké en UTC (2h en moins qu'en Suisse)

"""
Route d'ajout de pré-réservation à la base de données
"""
@app.post("/add-temp-reservation/")
async def add_temp_reserv(data:Temp_Reservation_API):
    new_temp_res = Temp_Reservation(label_ressource = data.ressource, heure = data.heure, date_reserv = data.date_reserv, timestamp_reserv = datetime.datetime.now(ZoneInfo('Europe/Paris')))

    try:
        output_pre_res = {}
        with Session.begin() as session:
            session.add(new_temp_res)
            session.flush()
            session.refresh(new_temp_res)
            output_pre_res = Temp_Reservation(label_ressource = new_temp_res.label_ressource, heure = new_temp_res.heure, date_reserv = new_temp_res.date_reserv, timestamp_reserv = new_temp_res.timestamp_reserv)
        return JSONResponse(content={
                    "message":"Pré-Réservation ajoutée",
                    "data":{"reservation":jsonable_encoder(output_pre_res)}
                },status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

@app.post("/add-reservation/")
async def add_reservation(data:Reservation_API):
    
        new_reservation = Reservation(nom=data.nom,prenom=data.prenom,numero_tel=data.numero_tel,date_reservation=datetime.datetime.now(ZoneInfo('Europe/Paris')))
        print(datetime.datetime.now())
        output_reserv = Reservation()
        output_reserv_ressource = Reservations_Client_Resource()
        output_choix_res = {}
        try:
        # Ajout de la nouvelle réservation (infos client)
            with Session.begin() as session:
                session.add(new_reservation)
                session.flush()
                session.refresh(new_reservation)
                output_reserv = {"id": new_reservation.id,"nom": new_reservation.nom,"prenom": new_reservation.prenom,"numero_tel": new_reservation.numero_tel,"date_reservation": new_reservation.date_reservation}
            # Ajout de la réservation coté ressources
            with Session.begin() as session:
                reservation_ressource = Reservations_Client_Resource(reservation=output_reserv["id"],resource=data.ressource,date_reservation=data.date,heure=data.heure)
                session.add(reservation_ressource)
                session.flush()
                session.refresh(reservation_ressource)
                output_reserv_ressource = {"heure": reservation_ressource.heure,"date_reservation": reservation_ressource.date_reservation,"ressource": reservation_ressource.resource,"date_reservation": reservation_ressource.date_reservation}
            choix_text = ""
            choix_list = []
            if data.list_options.__len__()> 0:
                with Session.begin() as session:
                    for id in data.list_options:
                        reserv_choix = Reservations_Client_Choix(reservation=output_reserv["id"],resource=data.ressource,id_choix_ressource=id)
                        choix_list.append(id)
                        session.add(reserv_choix)
                        session.flush()
                        session.refresh(reserv_choix)
                        output_choix_res[str(id)] = {"id":reserv_choix.id,"ressource":reserv_choix.resource,"res_id":reserv_choix.reservation,"id_choix":reserv_choix.id_choix_ressource}
            if choix_list.__len__()>0:
                choix_titres = get_choix_titres_from_ids(choix_list)
                for choix in choix_titres:
                    choix_text+= f", {choix}"
            date_reserv = output_reserv_ressource["date_reservation"]
            heure_reserv = output_reserv_ressource["heure"]
            # datetime_start = datetime.datetime()
            result_fin_heure = await get_fin_heure(output_reserv_ressource['ressource'],date_reserv,heure_reserv)
            heure_fin_reserv = datetime.datetime.strptime(result_fin_heure["heure_fin"],"%H:%M:%S").time()
            heure_start_print = datetime.datetime.combine(date_reserv,heure_reserv,tzinfo=ZoneInfo('Europe/Paris'))
            heure_fin_print = datetime.datetime.combine(date_reserv,heure_fin_reserv,tzinfo=ZoneInfo('Europe/Paris'))
            # Ajout de la réservation au calendrier google associé et retourne un lien pour ajouter l'event à son propre calendrier

            lien_google_cal = add_event_reservation(f"Réservation de {output_reserv_ressource['ressource']}",output_reserv['numero_tel'],output_reserv['prenom'],output_reserv['nom'],f"Une réservation de {output_reserv_ressource['ressource']}{choix_text}",heure_start_print,heure_fin_print)
            uuid_file = create_ical_event(f"Réservation de {output_reserv_ressource['ressource']}",output_reserv['numero_tel'],output_reserv['prenom'],output_reserv['nom'],f"Une réservation de {output_reserv_ressource['ressource']}{choix_text}",heure_start_print,heure_fin_print)
            return JSONResponse(content={
                    "message":"Réservation ajoutée",
                    "data":{"lien_reservation_google":lien_google_cal,"reservation":jsonable_encoder(output_reserv),"reservation_ressource":jsonable_encoder(output_reserv_ressource),"reservation_choix":jsonable_encoder(output_choix_res),"uuid_ical":uuid_file}
                },status_code=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Une erreur s'est produite à l'ajout d'une réservation: {str(e)}")
        
"""
Route pour récupérer les choix et options associés à une ressource

{
   "options": {
    "nom option 1": {
        "description option 1", {id 1 : "choix 1", id 2: "choix 2", ...}
    }
   } 
}
"""
@app.get("/get-options-choix/{ressource}")
async def get_options_choix(ressource:str):
    with Session.begin() as session:
        query = session.query(Options_Resource.label_option,Options_Resource.description,func.array_agg(Options_Resource_Choix.choix).label("choix"),func.array_agg(Options_Resource_Choix.id).label("id")).join(Options_Resource_Choix,Options_Resource.label_option == Options_Resource_Choix.label_option).where(Options_Resource.label_resource.like(ressource)).group_by(Options_Resource.label_option).group_by(Options_Resource.description).all()
        query = {elem[0]: [elem[1],{id: choix for id, choix in zip(elem[3],elem[2])}]for elem in query}
        test = [1,3]
        # print(list(jsonable_encoder(query).items()))
        for i,item in enumerate(list(jsonable_encoder(query).items())):
            print(list(item[1][1].items())[test[i]-1])
        print(query.keys().__len__())
        return JSONResponse(content={"options":jsonable_encoder(query)},status_code=status.HTTP_200_OK)

"""
Route permettant de récupérer toutes les réservations

[
[id reservation ,ressource ,date_reservation, heure], ...
]
"""
@app.get("/get-reservations-ressources/")    
async def get_reservations_ressources():
    with Session.begin() as session:
        query = session.query(Reservations_Client_Resource).distinct().all()
        
        return JSONResponse(content=jsonable_encoder(query),status_code=status.HTTP_200_OK)
"""
Route permettant de récupérer toutes les réservations d'une ressource

[
[id reservation ,ressource ,date_reservation, heure], ...
]
"""
@app.get("/get-reservations-ressources/{ressource}")    
async def get_reservations_ressources(ressource:str):
    with Session.begin() as session:
        query = session.query(Reservations_Client_Resource).where(Reservations_Client_Resource.resource == ressource).distinct().all()
        
        return JSONResponse(content=jsonable_encoder(query),status_code=status.HTTP_200_OK)

"""
Route permettant de récupérer toutes les réservations d'une ressource à une date donnée

[
[id reservation ,ressource ,date_reservation, heure], ...
]
"""
@app.get("/get-reservations-ressources-from-date/{ressource}/{date}")
async def get_reservations_ressources_from_date(ressource:str,date:datetime.date):
     with Session.begin() as session:
        query = session.query(Reservations_Client_Resource).where(Reservations_Client_Resource.resource == ressource).where(Reservations_Client_Resource.date_reservation >= date).distinct().all()
        
        return JSONResponse(content=jsonable_encoder(query),status_code=status.HTTP_200_OK)


@app.get("/get-jours-semaine/{ressource_label}/{num_jours}")
async def get_jours_semaine(ressource_label:str,num_jours:int):
    with Session.begin() as session:
        # Récupération des jours de la semaine possédant des horaires
        query = session.query(Jour_Horaire.jour).where(Jour_Horaire.label.like(ressource_label)).distinct().all()
        query_result = []
        dates_dispo :list[datetime.date] = []
        if query.__len__() > 0:
            curr_date = datetime.datetime.now().date()
            # Filtrage en format [0, 1, 2, 3](lundi, mardi, mercredi, ...)
            jours_semaines_values = [Jours_Semaine(jour[0]).value for jour in query]
            # Création array de dates selon les jours disponibles
            for date in range(num_jours):
                if (curr_date + datetime.timedelta(days=date)).weekday() in jours_semaines_values:
                    date_found = curr_date + datetime.timedelta(days=date)
                    dates_dispo.append(date_found)
            curr_reservations = get_reservations_for_dates_for_ressource(ressource_label,dates_dispo)
            pre_reserv = get_reservations_temporaire_for_dates_for_ressource(ressource_label,dates_dispo)
            for date in curr_reservations.keys():
                if date in pre_reserv.keys():
                    curr_reservations[date]+=pre_reserv[date]
            heures_for_semaine, query_horaire = get_heures_semaine_for_ressource(ressource_label)
            # Retire toutes les dates ne possédant aucun horaire de disponible
            for date in curr_reservations.keys():
                diff : list[datetime.date]= np.setdiff1d(heures_for_semaine[datetime.date.fromisoformat(date).weekday()],curr_reservations[date])
                if diff.__len__() == 0:
                    print(f"Removing {date}")
                    dates_dispo.remove(datetime.date.fromisoformat(date))
            
        return JSONResponse(content={"dates":jsonable_encoder([str(date) for date in dates_dispo]),"horaires":query_horaire},status_code=status.HTTP_200_OK)

@app.get("/get-jours-semaine/{ressource_label}/{num_jours}/{heure}")
async def get_jours_semaine(ressource_label:str,num_jours:int,heure:datetime.time):
    with Session.begin() as session:
        # Récupération des jours de la semaine possédant des horaires
        query = session.query(Jour_Horaire.jour).where(Jour_Horaire.label.like(ressource_label)).where(Jour_Horaire.debut <= heure).where(Jour_Horaire.fin>=heure).distinct().all()
        print(query)
        query_result = []
        dates_dispo :list[datetime.date] = []
        query_horaire = []
        if query.__len__() > 0:
            curr_date = datetime.datetime.now().date()
            # Filtrage en format [0, 1, 2, 3](lundi, mardi, mercredi, ...)
            jours_semaines_values = [Jours_Semaine(jour[0]).value for jour in query]
            # Création array de dates selon les jours disponibles
            for date in range(num_jours):
                if (curr_date + datetime.timedelta(days=date)).weekday() in jours_semaines_values:
                    date_found = curr_date + datetime.timedelta(days=date)
                    dates_dispo.append(date_found)
            curr_reservations = get_reservations_for_dates_for_ressource(ressource_label,dates_dispo)
            print(f"CUR RES ! ! ! ! {curr_reservations}")
            temp_res = get_reservations_temporaire_for_dates_for_ressource(ressource_label,dates_dispo)
            heures_for_semaine, query_horaire = get_heures_semaine_for_ressource(ressource_label)
            # print(dates_dispo)
            for date in curr_reservations.keys():
                if date in temp_res.keys():
                    curr_reservations[date].append(temp_res[date])
            # Retire toutes les dates ne possédant aucun horaire de disponible
            for date in curr_reservations.keys():
                diff : list[datetime.date]= np.setdiff1d(heures_for_semaine[datetime.date.fromisoformat(date).weekday()],curr_reservations[date])
                if diff.__len__() == 0:
                    print(f"Removing {date}")
                    dates_dispo.remove(datetime.date.fromisoformat(date))
            
        return JSONResponse(content={"dates":jsonable_encoder([str(date) for date in dates_dispo]),"horaires":query_horaire},status_code=status.HTTP_200_OK)

async def get_fin_heure(ressource_label:str,date:datetime.date,heure:datetime.time):
    query = []
    try:
        with Session.begin() as session:
            query = session.query(Jour_Horaire.temps_reservation).where(Jour_Horaire.label.like(ressource_label)).where(Jour_Horaire.jour == Jours_Semaine(date.weekday())).where(Jour_Horaire.debut <= heure).where(Jour_Horaire.fin>=heure).distinct().all()
            query = [temps[0] for temps in query]
            if query.__len__() >0:
                query = query[0]
            else:
                query = datetime.time(0,30,0)
            sum_time = datetime.timedelta(hours=query.hour,minutes=query.minute,seconds=query.second)
            final_time = (datetime.datetime.combine(datetime.date.today(),heure) + sum_time).time()
        return {"heure_fin":jsonable_encoder(final_time)}
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération du temps de réserv.: {e}")
        temps_reserv = datetime.time(0,30,0)
        sum_time = datetime.timedelta(hours=temps_reserv.hour,minutes=temps_reserv.minute,seconds=temps_reserv.second)
        final_time = (datetime.datetime.combine(datetime.date.today(),heure) + sum_time).time()
        return {"heure_fin":final_time}

@app.get("/get-horaires/{ressource_label}")
async def get_horaires_for_ressource(ressource_label: str):
        heures_for_semaine, query_horaire = get_heures_semaine_for_ressource(ressource_label)
            
        return JSONResponse(content={"heures_dispo":jsonable_encoder(heures_for_semaine),"horaires":query_horaire},status_code=status.HTTP_200_OK)

@app.get("/get-horaires/{jour}/{ressource_label}")
async def get_horaires_for_ressource(jour:str,ressource_label: str):

        with Session.begin() as session:
            # decoupage = datetime.time(minute=30)
            jour_date = datetime.datetime.fromisoformat(jour).date()

            # Récupère toutes les réservations correspondant à la date donnée
            query_reservations = get_reservations_for_dates_for_ressource(ressource_label,[jour_date])
            # Récupère toutes les pré-réservations
            query_pre_reserv = get_reservations_temporaire_for_dates_for_ressource(ressource_label,[jour_date])
            # Ressort une liste de temps
            print(query_reservations)
            query_reservations_time = []
            if str(jour_date) in query_reservations.keys():
                query_reservations_time = [time for time in query_reservations[str(jour_date)]]
            print(f"Query reserv {query_reservations}")
            if str(jour_date) in query_pre_reserv.keys():
                query_reservations_time+=query_pre_reserv[str(jour_date)]
            print(f"Query reserv with pre {query_reservations}")
            # query_result = jsonable_encoder(query)
            # query_reservations_result = jsonable_encoder(query_reservations)
            print(f"Réservations: {query_reservations_time}\n")
            # print(query_result)

            total_sec_calc = lambda hour,minute,second: (hour*3600 + minute*60 + second)
            heures_query, query_horaire = get_heures_semaine_for_ressource(ressource_label,[Jours_Semaine(jour_date.weekday())])
            print(f"Heures query: {heures_query}")
            horaires = []
            if jour_date.weekday() in heures_query.keys():
                horaires = [datetime.datetime.strptime(heure, '%H:%M:%S').time() for heure in heures_query[jour_date.weekday()]]
            
            final_schedule = []

            for heure in horaires:
                print(f"{heure} not in {query_reservations_time}")
                if str(heure) not in query_reservations_time:
                    
                    final_schedule.append(str(heure))

            print("QUERY HORAIRE "+str(query_horaire))
            return JSONResponse(content={"horaire_heures":final_schedule,"horaire":query_horaire},status_code=status.HTTP_200_OK)



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
        return JSONResponse(content=jsonable_encoder(response.json()),status_code=status.HTTP_200_OK)

@app.post("/communicate-rasa")
async def talk_to_rasa(data:Communicate_Rasa):
    headers = {"Content-Type": "application/json"}
    print(data.model_dump_json())
    async with httpx.AsyncClient() as client:
        response = await client.post('http://rasa-core:5005/webhooks/rest/webhook',data=data.model_dump_json(),headers=headers)    
        return JSONResponse(content=response.json(),status_code=status.HTTP_200_OK)




if __name__ == "__main__":
    # asyncio.create_task()
    uvicorn.run("server:app", host="0.0.0.0" , port=5500, log_level="info",reload = True,workers=4,reload_dirs=["/app"],reload_excludes=["/app/.venv"])