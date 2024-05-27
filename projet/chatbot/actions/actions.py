# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from enum import Enum
from typing import Any, Text, Dict, List
from urllib import response

from rasa_sdk import Action, Tracker, FormValidationAction, ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import EventType, UserUtteranceReverted, FollowupAction
from rasa_sdk.events import SlotSet
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
    print(res)
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
def get_heures():
    # Récupérer jour semaine depuis slot date mais assurer au préalable que la date est VALIDE en utilisant duckling pour la récupérer lors de la validation
    return ["11h00","11h30","12h00","13h00","13h30","14h00"]

@staticmethod
def get_dates(ressource:str)->list[datetime.date]:
    curr_date = datetime.datetime.now().date()
    dates_dispo = []
    for date in range(30):
        if (curr_date + datetime.timedelta(days=date)).weekday() in get_jours_semaine(ressource):
            dates_dispo.append(curr_date + datetime.timedelta(days=date))
    return dates_dispo
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
        ressource = str(slot_value).lower()
        print(f"RESSOURCE : {ressource}")
        if ressource in get_ressource_list():
            return {"ressource":ressource}
        dispatcher.utter_message(text=f"{ressource} n'existe pas. Veuillez réserver une ressource qui existe")
        print("LEAVING FORM")
        return {"ressource":None}

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
        jours_dispo = get_jours_semaine(ressource)
        data = {
            "locale":"fr_FR",
            "text":date
        }
        res = requests.post("http://duckling:8000/parse",data=data)
        if res.status_code == 200:
            dispatcher.utter_message(text=f"{res.json()}")
        
        dispatcher.utter_message(text=f"Date : {date}")

      
        return {"date":date}

    def validate_heure(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        heure = str(slot_value)
        ressource = str(tracker.get_slot("ressource"))
        jours_dispo = get_jours_semaine(ressource)
        data = {
            "locale":"fr_FR",
            "text":heure
        }
        res = requests.post("http://duckling:8000/parse",data=data)
        if res.status_code == 200:
            dispatcher.utter_message(text=f"{res.json()}")

        dispatcher.utter_message(text=f"Heure : {heure}")

      
        return {"heure":heure}
    
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
        for ress in get_ressource_list():
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
        response_mess = "Les heures disponibles à la réservation sont :"
        for ress in get_heures():
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
        for date  in get_dates(ressource):
            response_mess += f"\n\t- {date.day}/{date.month}/{date.year}"
        dispatcher.utter_message(text=response_mess)
        dispatcher.utter_message(text="Quand souhaitez-vous réserver ?")
        return []