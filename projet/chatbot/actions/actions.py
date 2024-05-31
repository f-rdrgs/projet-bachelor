# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions



# This is a simple example for a custom action which utters "Hello World!"

from enum import Enum
import json
from typing import Any, Text, Dict, List
from urllib import response

from rasa_sdk import Action, Tracker, FormValidationAction, ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import EventType, UserUtteranceReverted, FollowupAction
from rasa_sdk.events import SlotSet, Restarted
import datetime
import requests

class Day_week(Enum):
    lundi = 0
    mardi = 1
    mercredi = 2
    jeudi = 3
    vendredi = 4
    samedi = 5
    dimanche = 6    


@staticmethod
def get_ressource_list()->list[str]:
    res = requests.get("http://api:5500/get-ressources").json()
    # print(res)
    if(len(res)>0):
        return [ressource['label'] for ressource in res]

    return []

@staticmethod
def get_jours_semaine(ressource_label: str)->list:
    # get-jours-semaine/{ressource_label}
    res = requests.get(f"http://api:5500/get-jours-semaine/{ressource_label}").json()
    if(len(res)>0):
        return [ressource for ressource in res]

    return [Day_week.lundi.value,Day_week.mercredi.value,Day_week.jeudi.value,Day_week.vendredi.value]

# res = requests.get(f"http://api:5500/get-horaires/{jour_semaine}/{ressource}").json()
#     print(res)
#     if(len(res)>0):
#         return [horaire for horaire in res["horaire_heures"]]


@staticmethod
def get_heures(jour_semaine:Day_week,ressource:str):
    # Récupérer jour semaine depuis slot date mais assurer au préalable que la date est VALIDE en utilisant duckling pour la récupérer lors de la validation
    res = requests.get(f"http://api:5500/get-horaires/{jour_semaine.name}/{ressource}").json()
    if(len(res)>0):
        return res["horaire_heures"]
    else:
        return []

@staticmethod
def get_dates(ressource:str)->list[datetime.date]:
    curr_date = datetime.datetime.now().date()
    dates_dispo = []
    jours_semaine = get_jours_semaine(ressource)
    for date in range(30):
        if (curr_date + datetime.timedelta(days=date)).weekday() in jours_semaine:
            dates_dispo.append(curr_date + datetime.timedelta(days=date))
    return dates_dispo

@staticmethod
def save_reservation(nom:str,prenom:str,numero_tel:str,date:datetime.date,ressource:str,heure:datetime.time)->tuple[bool,str]:
    try:
        print(nom,prenom,numero_tel,str(date),ressource,str(heure))
        print({
            "nom":nom,
            "prenom":prenom,
            "numero_tel":numero_tel,
            "ressource":ressource,
            "heure":str(heure),
            "date":str(date)
        })
        res = requests.post(f"http://api:5500/add-reservation",json={
            "nom":nom,
            "prenom":prenom,
            "numero_tel":numero_tel,
            "ressource":ressource,
            "heure":str(heure),
            "date":str(date)
        })
    except Exception as e:
        print(e)
        return False,e
    else:
        return res.status_code == 200, ""

class RestartConvo(Action):
    def name(self)-> Text:
        return "restart_convo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message("Pas de soucis")
        return [Restarted(),FollowupAction("utter_que_faire")]

class ActionSaveRessource(Action):
    def name(self) -> Text:
        return "save_ressource"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ressource = tracker.get_slot("ressource")
        date = tracker.get_slot("date")
        heure = tracker.get_slot("heure")
        nom = tracker.get_slot("nom")
        prenom = tracker.get_slot("prenom")   
        num_tel = str(tracker.get_slot("numero_tel")  )
        if ressource is not None and heure is not None and date is not None and prenom is not None and nom is not None and num_tel is not None:
            date_conv = datetime.datetime.fromisoformat(date).date()
            heure_conv = datetime.datetime.fromisoformat(heure).time()
            succes,err = save_reservation(nom,prenom,num_tel,date_conv,ressource,heure_conv)
            if succes:
                dispatcher.utter_message("Réservation enregistrée !")
            else:
                dispatcher.utter_message(f"Une erreur s'est produite lors de l'enregistrement de la réservation: {err}")
        else:
            dispatcher.utter_message(f"Des informations sont manquantes : {ressource} {date} {heure} {nom} {prenom} {num_tel}")

class ActionCheckRessource(Action):

    def name(self) -> Text:
        return "validate_existance_ressource"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        ressource = next(tracker.get_latest_entity_values("ressource"),None).lower()
        if ressource not in get_ressource_list():
            dispatcher.utter_message(text=f"{ressource.capitalize()} n'existe pas. Veuillez réessayer avec une ressource valide.")
            SlotSet("ressource",None)
            return []
        
        SlotSet("ressource",ressource)
        dispatcher.utter_message(tracker.get_slot("ressource"))
        return []

class ActionSalutation(Action):

    def name(self) -> Text:
        return "action_salutation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        response_mess = "Les ressources possible à réserver sont :"
        for ress in get_ressource_list():
            response_mess += f"\n\t- {ress}"
        dispatcher.utter_message(text="Bonjour!")
        dispatcher.utter_message(text=response_mess)
        dispatcher.utter_message(text="Que souhaitez-vous réserver ?")
       
        return []


class ActionConfirmSwitchRessource(Action):

    def name(self) -> Text:
        return "action_ask_switch_ressource"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text=f"Voulez-vous vraiment réserver {next(tracker.get_latest_entity_values('ressource'),None).lower()} à la place ?")

        return []
    
class ActionSwitchRessource(Action):

    def name(self) -> Text:
        return "action_switch_ressource"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        SlotSet("ressource",next(tracker.get_latest_entity_values("ressource"),None).lower())

        return []
    

# https://learning.rasa.com/rasa-forms-3/validation/
class ValidateRessourceForm(FormValidationAction):
    def name(self)->Text:
        return "validate_get_ressource_form"
    def validate_ressource(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        # print(f"SLOT VALUE{slot_value}")
        if slot_value is not None:
            ressource = str(slot_value).lower()
            # print(f"RESSOURCE : {ressource}")
            if ressource in get_ressource_list():
                return {"ressource":ressource,"accept_deny":None}
            dispatcher.utter_message(text=f"{ressource} n'existe pas. Veuillez réserver une ressource qui existe")
            # print("LEAVING FORM")
            return {"ressource":None}
        else:
            dispatcher.utter_message("Veuillez spécifier une ressource")
            return {"ressource":None}
    def validate_accept_deny(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value is not None:
            yes_no = bool(slot_value)
            dispatcher.utter_message(f"{yes_no}")
            if yes_no:
                return {"accept_deny":True}
            else:
                SlotSet("ressource", None)
                return {"accept_deny":None,"ressource": None}
        else:
            dispatcher.utter_message("Veuillez répondre oui ou non")
            return {"accept_deny":None}
        

class ValidateInfoReserv(FormValidationAction):
    def name(self)->Text:
        return "validate_get_info_reserv_form"
    
    def validate_prenom( self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"prenom":slot_value,"accept_deny":None}

    def validate_numero_tel(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        numero = str(slot_value)
        data = {
            "locale":"fr_FR",
            "text":numero
        }
        if  slot_value is not None:
            res = requests.post("http://duckling:8000/parse",data=data)
            if res.status_code == 200:
                res_json = res.json()
                dispatcher.utter_message(f"Duckling: {res_json}")
                dim_time_index = -1
                for index in range(len(res_json)):
                    if res_json[index]["dim"] == "phone-number" and dim_time_index == -1:
                        dim_time_index = index
                if dim_time_index >= 0:
                        numero_duckling = res_json[index]["value"]["value"]
                        ressource = tracker.get_slot("ressource")
                        date = tracker.get_slot("date")
                        heure = tracker.get_slot("heure")
                        nom = tracker.get_slot("nom")
                        prenom = tracker.get_slot("prenom")   
                        num_tel = tracker.get_slot("numero_tel")  
                        date_conv = datetime.datetime.fromisoformat(date).date()
                        heure_conv = datetime.datetime.fromisoformat(heure).time()
                        dispatcher.utter_message(f"{ressource} {str(heure_conv)} {str(date_conv)} {nom} {prenom} {num_tel}")
                        return {"numero_tel": str(numero_duckling)}
                else:
                    dispatcher.utter_message(text=f"Pouvez-vous répéter votre numéro de téléphone d'une autre manière ?")
                
            

        
            return {"date":None}
        else:
            dispatcher.utter_message("Veuillez spécifier une date")
            return {"date":tracker.get_slot("date")}


    def validate_accept_deny(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value is not None:
            yes_no = bool(slot_value)
            dispatcher.utter_message(f"{yes_no}")
            if yes_no:
                return {"accept_deny":True}
            else:
                SlotSet("nom", None)
                SlotSet("prenom", None)
                return {"accept_deny":None,"nom": None,"prenom":None,"numero_tel":None}
        else:
            dispatcher.utter_message("Veuillez répondre oui ou non")
            return {"accept_deny":None}


class ActionResetValidation(Action):
    def name(self)->Text:
        return "reset_validation"
    

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("accept_deny",None)]

class ValidateHeuresForm(FormValidationAction):
    def name(self)->Text:
        return "validate_get_date_heure_form"
    # Duckling ne gère pas les dates sous forme de 15.05 ! ! !
    def validate_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        date = str(slot_value)
        ressource = str(tracker.get_slot("ressource"))
        data = {
            "locale":"fr_FR",
            "text":date
        }
        if  slot_value is not None:
            dispatcher.utter_message(text=f"Date : {date}")
            res = requests.post("http://duckling:8000/parse",data=data)
            if res.status_code == 200:
                res_json = res.json()
                dim_time_index = -1
                grain = "day"
                dispatcher.utter_message(f"Duckling: {res_json}")
                for index in range(len(res_json)):
                    if res_json[index]["dim"] == "time" and dim_time_index == -1:
                        dim_time_index = index
                        grain = res_json[index]["value"]["grain"]
                if dim_time_index >= 0:
                    if grain == "day":
                        dates_dispo = get_dates(ressource)
                        date_duckling = res_json[index]["value"]["value"]
                        date_datetime = datetime.datetime.fromisoformat(date_duckling).date()
                        if(date_datetime in dates_dispo):
                            return {"date": date_duckling}
                        else:
                            dispatcher.utter_message(f"La date du {date_datetime.day}/{date_datetime.month}/{date_datetime.year} n'est pas disponible. Veuillez choisir une autre date")
                    else:
                        dispatcher.utter_message(text=f"2. Pouvez-vous répéter la date d'une autre manière ?")
                else:
                    dispatcher.utter_message(text=f"Pouvez-vous répéter la date d'une autre manière ?")
                
            

        
            return {"date":None}
        else:
            dispatcher.utter_message("Veuillez spécifier une date")
            return {"date":tracker.get_slot("date")}

    def validate_heure(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        heure = str(slot_value)
        ressource = str(tracker.get_slot("ressource"))
        date = str(tracker.get_slot("date"))
        

        data = {
            "locale":"fr_FR",
            "text":heure
        }
        if slot_value is not None:
            res = requests.post("http://duckling:8000/parse",data=data)
            if res.status_code == 200:
                res_json = res.json()
                dim_time_index = -1
                grain= "minute"
                dispatcher.utter_message(f"Duckling: {res_json}")
                for index in range(len(res_json)):
                    if res_json[index]["dim"] == "time" and dim_time_index == -1:
                        dim_time_index = index
                        grain = res_json[index]["value"]["grain"]
                if dim_time_index >= 0:
                    dispatcher.utter_message(f"Grain {grain}")
                    if grain == "minute" or grain == "hour":
                        heures_horaire_ressource = get_heures(Day_week(datetime.datetime.fromisoformat(date).weekday()),ressource)
                        heures_dispo = [datetime.datetime.strptime(heure_disp,"%H:%M:%S").time() 
                        for heure_disp in heures_horaire_ressource]
                        heure_duckling = res_json[dim_time_index]["value"]["value"]
                        heure_datetime = datetime.datetime.fromisoformat(heure_duckling)

                        if heure_datetime.time() in heures_dispo:
                            return {"heure": heure_duckling,"accept_deny":None}
                        else:
                            dispatcher.utter_message(f"{heure_datetime.strftime('%Hh%M')} n'est pas une heure valide. Veuillez en choisir une autre")
                    else:
                        dispatcher.utter_message(text=f"2. Pouvez-vous répéter l'heure d'une autre manière ?")
                else:
                    dispatcher.utter_message(text=f"Pouvez-vous répéter l'heure d'une autre manière ?")
        
            return {"heure":None}
        else:
            dispatcher.utter_message("Veuillez spécifier une heure")
            return {"heure":tracker.get_slot("heure")}
    
    def validate_accept_deny(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value is not None:
            yes_no = bool(slot_value)
            dispatcher.utter_message(f"{yes_no}")
            if yes_no:
                return {"accept_deny":True}
            else:
                SlotSet("heure", None)
                SlotSet("date", None)
                return {"accept_deny":None,"heure": None,"date":None}
        else:
            dispatcher.utter_message("Veuillez répondre oui ou non")
            return {"accept_deny":None}
    # async def extract_date(self,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: DomainDict,
    # ) -> Dict[Text, Any]:
    #     last_intent = tracker.latest_message.get("intent")["name"]
    #     dispatcher.utter_message(tracker.latest_message)
    #     dispatcher.utter_message(f"INTENT :{last_intent}")
    #     if last_intent == "inform_date":
    #         date_value = next(tracker.get_latest_entity_values("date"),None)
    #         dispatcher.utter_message(f"VALUE DATE: {date_value}")
    #         # SlotSet("date",date_value)
    #         return {"date":date_value}

    #     return []
    
    # async def extract_heure(self,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: DomainDict,
    # ) -> Dict[Text, Any]:
    #     last_intent = tracker.latest_message.get("intent")["name"]
    #     dispatcher.utter_message(tracker.latest_message)
    #     dispatcher.utter_message(f"INTENT :{last_intent}")
    #     if last_intent == "inform_heure":
    #         heure_value = next(tracker.get_latest_entity_values("heure"),None)
    #         dispatcher.utter_message(f"VALUE heure: {heure_value}")
    #         # SlotSet("heure",heure_value)
    #         return {"heure":heure_value}

    #     return []




# https://rasa.com/docs/rasa/action-server/validation-action/
# class ValidateRessourceSlot(ValidationAction):
#     def validate_ressource(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         """Validate location value."""
#         if isinstance(slot_value, str):
#             ressource :str = str(slot_value).lower()
#             dispatcher.utter_message(f"Ressource: {ressource}")

#             if ressource in get_ressource_list():
#                 return {"ressource": ressource.capitalize()}
#             else:
#                 dispatcher.utter_message(f"{ressource.capitalize()} n'existe pas. Veuillez suggérer une ressource valide.")
#                 return {"ressource": None}
#         else:
#             # validation failed, set this slot to None
#             return {"ressource": None}
        
# https://rasa.com/docs/rasa/forms/#using-a-custom-action-to-ask-for-the-next-slot
class AskForRessourceAction(Action):
    def name(self) -> Text:
        return "action_ask_ressource"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        response_mess = "Les ressources possible à réserver sont :"
        liste_ressources = get_ressource_list()
        for ress in liste_ressources:
            response_mess += f"\n\t- {ress}"
        dispatcher.utter_message(text=response_mess)
        dispatcher.utter_message(text="Que souhaitez-vous réserver ?")
        return []
    
class AskForHeureAction(Action):
    def name(self) -> Text:
        return "action_ask_heure"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        ressource = tracker.get_slot("ressource")
        date = tracker.get_slot("date")
        weekday_date = Day_week(datetime.datetime.fromisoformat(date).weekday())
        response_mess = "Les heures disponibles à la réservation sont :"
        heures_horaires = get_heures(weekday_date,ressource)
        for ress in [datetime.datetime.strptime(horaire,'%H:%M:%S').strftime('%Hh%M') for horaire in heures_horaires]:
            response_mess += f"\n\t- {ress}"
        dispatcher.utter_message(text=response_mess)
        dispatcher.utter_message(text="Pour quelle heure souhaitez-vous réserver ?")
        return []
    
class AskForDateAction(Action):
    def name(self) -> Text:
        return "action_ask_date"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        response_mess = "Les dates disponibles à la réservation sont :"
        ressource = tracker.get_slot("ressource")
        dates_for_ressource = get_dates(ressource)
        for date in dates_for_ressource:
            response_mess += f"\n\t- {date.day}/{date.month}/{date.year}"
        dispatcher.utter_message(text=response_mess)
        dispatcher.utter_message(text="Quand souhaitez-vous réserver ?")
        return []
    

