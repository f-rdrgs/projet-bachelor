# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions



# This is a simple example for a custom action which utters "Hello World!"

from enum import Enum
import enum
import json
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction, ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import EventType, FollowupAction
from rasa_sdk.events import SlotSet, Restarted
import datetime
import requests
from dataclasses import dataclass

@dataclass
class Reservation_save_API():
    nom:str
    prenom:str
    numero_tel:str
    date:datetime.date
    ressource:str
    heure:datetime.time
    list_choix:list[int]

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
def add_temp_reservation(ressource:str, date_reserv:datetime.date,heure_reserv:datetime.time):
    try:
        data = {
            "ressource":ressource,
            "heure":heure_reserv,
            "date_reserv":date_reserv
        }
        res = requests.post("http://api:5500/add-temp-reservation/",data=data)
        return (res.status_code == 200)
    except Exception as e:
        print(e)
        return False


@staticmethod
def get_jours_disponibles(ressource_label: str,nombre_jours:int,heure_prechoisie:datetime.time|None)->list[datetime.date]:
    # get-jours-semaine/{ressource_label}
        res = []
        if heure_prechoisie is not None:
            res = requests.get(f"http://api:5500/get-jours-semaine/{ressource_label}/{nombre_jours}/{heure_prechoisie}").json() 
        else:
            res = requests.get(f"http://api:5500/get-jours-semaine/{ressource_label}/{nombre_jours}").json()
        
        print(f"result res :{res}")
        if(len(res["dates"])>0):
            return [datetime.date.fromisoformat(date) for date in res["dates"]]
        else:
            print("No dates found")
            return []
@staticmethod
def get_heures(jour:datetime.date,ressource:str):
    # Récupérer jour semaine depuis slot date mais assurer au préalable que la date est VALIDE en utilisant duckling pour la récupérer lors de la validation
    res = requests.get(f"http://api:5500/get-horaires/{str(jour)}/{ressource}").json()
    if(len(res)>0):
        return res
    else:
        return []

@staticmethod
def get_heures_semaine(ressource:str):
    res = requests.get(f"http://api:5500/get-horaires/{ressource}").json()
    if(len(res)>0):
        return res
    else:
        return []

@staticmethod
def get_reserved_ressources_since_date(date:datetime.date,ressource:str):
    res = requests.get(f"http://api:5500/get-reservations-ressources-from-date/{ressource}/{str(date)}").json()
    if(len(res)>0):
        return res
    else:
        return []

@staticmethod
def save_reservation(data: Reservation_save_API)->tuple[bool,str,requests.Response]:
    try:
        nom = str(data.nom)
        prenom = str(data.prenom)
        numero_tel = str(data.numero_tel)
        date = str(data.date)
        ressource = str(data.ressource)
        heure = str(data.heure)
        list_choix = data.list_choix
        print({
            "nom":nom,
            "prenom":prenom,
            "numero_tel":numero_tel,
            "ressource":ressource,
            "heure":str(heure),
            "date":str(date),
            "list_options":list_choix
        })
        res = requests.post(f"http://api:5500/add-reservation",json={
            "nom":nom,
            "prenom":prenom,
            "numero_tel":numero_tel,
            "ressource":ressource,
            "heure":str(heure),
            "date":str(date),
            "list_options":list_choix
        })
    except Exception as e:
        print(e)
        return False,e
    else:
        return res.status_code == 200, "",res.json()

@staticmethod
def get_options(ressource:str)->dict[str,list]:
    res = requests.get(f"http://api:5500/get-options-choix/{ressource}").json()
    if(len(res)>0):
        if len(res["options"]) > 0:
            return res["options"]
        
    return []

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
        list_choix = tracker.get_slot("options_ressource")
        nom_prenom = str(tracker.get_slot("nom_prenom"))
        nom_prenom_list = nom_prenom.split(' ')
        nom = ""
        prenom = ""
        for mot in nom_prenom_list[:len(nom_prenom_list)-1]:
            nom+= mot.capitalize()+" "
        nom = nom.rstrip()
        prenom = nom_prenom_list[-1].capitalize()

        num_tel = tracker.get_slot("numero_tel")
        # S'assure que toute les informations sont fournies avant de procéder à la sauvegarde
        if ressource is not None and heure is not None and date is not None and nom_prenom is not None and nom_prenom_list.__len__()>1 and num_tel is not None:
            ressource = str(ressource)
            date_conv = datetime.datetime.fromisoformat(str(date)).date()
            heure_conv = datetime.datetime.fromisoformat(str(heure)).time()
            num_tel = str(num_tel)
            save_reserv_data = Reservation_save_API(nom=str(nom),prenom=str(prenom),numero_tel=str(num_tel),date=str(date_conv),heure=str(heure_conv),ressource=ressource,list_choix=list_choix)
            succes,err,res = save_reservation(save_reserv_data)
            if succes:
                dispatcher.utter_message("Réservation enregistrée !")
                dispatcher.utter_message(f"Événement google: {res['data']['lien_reservation_google']}")
            else:
                dispatcher.utter_message(f"Une erreur s'est produite lors de l'enregistrement de la réservation: {err}")
        else:
            dispatcher.utter_message(f"Des informations sont manquantes : {ressource} {date} {heure} {nom} {prenom} {num_tel}")


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

class UtterListOptions(Action):
    def name(self) -> Text:
        return "list_list_options"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        list_options = tracker.get_slot("options_ressource")
        if list_options is not None or str(list_options) != "None":
            dispatcher.utter_message(str(list_options))
        return []

class ValidateGetOptionsReservForm(FormValidationAction):
    def name(self)->Text:
        return "validate_get_options_reserv_form"
    
    def validate_choix_option(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        ressource = tracker.get_slot("ressource")
        option_count = tracker.get_slot("option_count")
        choix_option = tracker.get_slot("choix_option")
        options_list = tracker.get_slot("options_ressource")
        options = get_options(ressource)
        print(f"List choix: {str(options_list)}")
        if tracker.latest_message.get("intent")["name"] == "stop":
            return {}
        if option_count is None:
            return {"choix_option":None}
        option_count = int(option_count)
        
        if options.keys().__len__()>0 and option_count >=0 and option_count < options.keys().__len__() and choix_option is not None:
            # print(f"{int(choix_option)} in {range(0,options.keys().__len__())} {int(choix_option) in range(0,options.keys().__len__()+1)}")
            if int(choix_option) in range(0,list(options.items())[option_count][1][1].keys().__len__()+1):
                # list(list(dico.items())[option_count][1][1].items())[2-1][0]
                options_list.append(int(list(list(options.items())[option_count][1][1].items())[int(choix_option)-1][0]))
                if option_count+1 < options.keys().__len__():
                    print(f"LIST : {options_list}")
                    return {"choix_option":None,"option_count":float(option_count+1),"options_ressource":options_list}
                else:
                    print(f"LIST : {options_list}")
                    return {"choix_option":1.0,"option_count":0.0,"options_ressource":options_list}
            else:
                dispatcher.utter_message("Choix invalide")
                return {"choix_option":None}
        else:
            dispatcher.utter_message("Erreur lors de la sélection de choix")
            return {"choix_option":None}
    

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
        if slot_value is not None:
            ressource = str(slot_value).lower()
            if ressource in get_ressource_list():
                return {"ressource":ressource,"accept_deny":None}
            dispatcher.utter_message(text=f"{ressource} n'existe pas. Veuillez réserver une ressource qui existe")
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
    
    def validate_nom_prenom( self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        nom_prenom_list = str(slot_value).split(' ')
        if nom_prenom_list.__len__() >1:
            return {"nom_prenom":slot_value,"accept_deny":None}
        else:
            dispatcher.utter_message("Veuillez entrer un nom et prénom")
            return {"nom_prenom":None,"accept_deny":None}

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
            # Récupération de la requête duckling pour vérifier le numéro de téléphone
            if res.status_code == 200:
                res_json = res.json()
                # dispatcher.utter_message(f"Duckling: {res_json}")
                dim_time_index = -1
                # Récupère l'index de la valeur comportant un numéro de téléphone
                for index in range(len(res_json)):
                    if res_json[index]["dim"] == "phone-number" and dim_time_index == -1:
                        dim_time_index = index
                # Si un numéro est bien trouvé
                if dim_time_index >= 0:
                        numero_duckling = str(res_json[dim_time_index]["value"]["value"])
                        ressource = tracker.get_slot("ressource")
                        date = tracker.get_slot("date")
                        heure = tracker.get_slot("heure")
                        nom = tracker.get_slot("nom")
                        prenom = tracker.get_slot("prenom")
                        date_conv = datetime.datetime.fromisoformat(date).date()
                        heure_conv = datetime.datetime.fromisoformat(heure).time()
                        # dispatcher.utter_message(f"{ressource} {str(heure_conv)} {str(date_conv)} {nom} {prenom} {numero_duckling}")
                        # Sauvegarde le numéro venant de duckling dans le slot
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
            # dispatcher.utter_message(f"{yes_no}")
            if yes_no:
                return {"accept_deny":True}
            else:
                return {"accept_deny":None,"nom_prenom": None,"numero_tel":None}
        else:
            dispatcher.utter_message("Veuillez répondre oui ou non")
            return {"accept_deny":None}


class ActionPreDefineRessourceSlot(Action):
    def name(self)->Text:
        return "predefine_ressource"
    
    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        pre_ressource = tracker.get_slot("ressource_prereserv")
        if pre_ressource is not None:
            pre_ressource_processed = str(pre_ressource).lower()
            if pre_ressource_processed not in get_ressource_list():
                dispatcher.utter_message(f"La ressource {pre_ressource_processed} n'est pas disponible")
                return [SlotSet("ressource_prereserv",None)]
            else:
                dispatcher.utter_message(f"Préselection de {pre_ressource_processed}")
                return [SlotSet("ressource",pre_ressource_processed)]
        return []

class ActionResetValidation(Action):
    def name(self)->Text:
        return "reset_validation"
    

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("accept_deny",None)]


class AnnulerDateHeureReset(Action):
    def name(self)->Text:
        return "annuler_date_heure"
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message("Retour au choix des dates ou heures")
        return [SlotSet("heure",None),SlotSet("date",None), FollowupAction("action_ask_date"),FollowupAction("get_date_heure_form")]
    
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
        date = slot_value
        heure = tracker.get_slot("heure")
        ressource = str(tracker.get_slot("ressource"))
        data = {
            "locale":"fr_FR",
            "text":date
        }

        if  slot_value is not None:
            date = str(date)
            # Récupère date parsé par Duckling
            res = requests.post("http://duckling:8000/parse",data=data)
            if res.status_code == 200:
                res_json = res.json()
                dim_time_index = -1
                grain = "day"
                # S'assure de trouver une valeur de type temps dans la réponse
                for index in range(len(res_json)):
                    if res_json[index]["dim"] == "time" and dim_time_index == -1:
                        dim_time_index = index
                        grain = res_json[index]["value"]["grain"]
                if dim_time_index >= 0:
                    if grain == "day":
                        dates_dispo = []
                        if heure is None:
                            # Si la date donnée est trouvable dans les dates disponibles et non réservées, sauvegarde dans le slot
                            dates_dispo = get_jours_disponibles(ressource,30,None)
                        else:
                            dates_dispo = get_jours_disponibles(ressource,30,datetime.datetime.fromisoformat(str(heure)).time())
                        date_duckling = res_json[index]["value"]["value"]
                        date_datetime = datetime.datetime.fromisoformat(date_duckling).date()
                        if(date_datetime in dates_dispo):
                            dispatcher.utter_message(f"Sélection de la date du {date_datetime.day}/{date_datetime.month}/{date_datetime.year}.")
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
        heure = slot_value
        ressource = str(tracker.get_slot("ressource"))
        date = tracker.get_slot("date")
        
        data = {
            "locale":"fr_FR",
            "text":heure
        }
        
        if slot_value is not None:
            heure = str(heure)
            # Récupération de l'heure parsée par duckling
            res = requests.post("http://duckling:8000/parse",data=data)
            if res.status_code == 200:
                res_json = res.json()
                dim_time_index = -1
                grain= "minute"
                # dispatcher.utter_message(f"Duckling: {res_json}")
                for index in range(len(res_json)):
                    if res_json[index]["dim"] == "time" and dim_time_index == -1:
                        dim_time_index = index
                        grain = res_json[index]["value"]["grain"]
                if dim_time_index >= 0:
                    # dispatcher.utter_message(f"Grain {grain}")
                    if grain == "minute" or grain == "hour":
                        if date is not None:
                            date = str(date)
                            heures_horaire_ressource = get_heures(datetime.datetime.fromisoformat(date),ressource)
                            heures_dispo = [datetime.datetime.strptime(heure_disp,"%H:%M:%S").time() for heure_disp in heures_horaire_ressource["horaire_heures"]]
                            heure_duckling = res_json[dim_time_index]["value"]["value"]
                            heure_datetime = datetime.datetime.fromisoformat(heure_duckling)
                            # S'assure que l'heure choisie est disponible à la réservation
                            if heure_datetime.time() in heures_dispo :
                                dispatcher.utter_message(f"Sélection de l'heure pour {heure_datetime.strftime('%Hh%M')}")
                                return {"heure": heure_duckling,"accept_deny":None}
                            else:
                                dispatcher.utter_message(f"{heure_datetime.strftime('%Hh%M')} n'est pas une heure valide. Veuillez en choisir une autre")
                        else:
                            heure_duckling = res_json[dim_time_index]["value"]["value"]
                            heure_datetime = datetime.datetime.fromisoformat(heure_duckling)
                            result_query_heures = get_heures_semaine(ressource)
                            list_heures_dispo : dict[int,dict[str,list[datetime.time]]] = result_query_heures["heures_dispo"]
                            dict_horaires_jour : dict[str,dict] = result_query_heures["horaires"]

                            found_heure_in_horaire = False
                            for day in list_heures_dispo.keys():
                                if str(heure_datetime.time()) in list_heures_dispo[day] and not found_heure_in_horaire:
                                    found_heure_in_horaire = True
                            if found_heure_in_horaire:
                                dispatcher.utter_message(f"Sélection de l'heure pour {heure_datetime.strftime('%Hh%M')}")
                                return {"heure": heure_duckling,"accept_deny":None}
                            else:
                                dispatcher.utter_message(f"{heure_datetime.strftime('%Hh%M')} n'est pas une heure valide. Veuillez en choisir une autre")
                                for day in dict_horaires_jour.keys():
                                    for horaire in result_query_heures["horaires"][day]["horaires"]:
                                        dispatcher.utter_message(f"Le {Day_week(int(day)).name.capitalize()} de {horaire[0]} à {horaire[1]} par intervalles de {result_query_heures['horaires'][day]['decoupage']}")

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
            # dispatcher.utter_message(f"{yes_no}")
            if yes_no:
                ressource = str(tracker.get_slot("ressource"))
                heure = str(tracker.get_slot("heure"))
                date = str(tracker.get_slot("date"))
                add_temp_reservation(ressource,heure,date)
                return {"accept_deny":True}
            else:
                SlotSet("heure", None)
                SlotSet("date", None)
                return {"accept_deny":None,"heure": None,"date":None}
        else:
            dispatcher.utter_message("Veuillez répondre oui ou non")
            return {"accept_deny":None}
 
class AskForChoixOptionAction(Action):
    def name(self)->Text:
        return "action_ask_choix_option"
    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        ressource = tracker.get_slot("ressource")
        option_count = tracker.get_slot("option_count")
        options_list = tracker.get_slot("options_ressource")
        dispatcher.utter_message(str(options_list))
        if ressource is not None and option_count is not None:
            ressource = str(ressource)
            options = get_options(ressource)
            option_count = int(option_count)
            if option_count < options.keys().__len__():
                message_sent = ""
                for i,option in enumerate(options.keys()):
                    if i == option_count:
                        message_sent =f"Les options disponible pour {option} sont: \n"
                        for j,value in enumerate(options[option][1].items()):
                            message_sent+=f"{j}: {value[1]}\n"
                        message_sent+="Veuillez entrer le nombre correspondant"
                dispatcher.utter_message(message_sent)
            else:
                dispatcher.utter_message("Aucune option n'est disponible")
                return [SlotSet("option_count",-1),SlotSet("choix_option",-1),SlotSet("options_ressource",[])]
        else:
            dispatcher.utter_message("Aucune ressource trouvée pour récupérer ses options")
        return []
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
        # Ajouter test pour affichage variable pour récupérer date ou heure en premier
        ressource = tracker.get_slot("ressource")
        date = tracker.get_slot("date")
        date_datetime = datetime.datetime.fromisoformat(date)
        response_mess = "Les heures disponibles à la réservation sont :"
        heures_horaires = get_heures(date_datetime,ressource)
        print(heures_horaires)
        for ress in [datetime.datetime.strptime(horaire,'%H:%M:%S').strftime('%Hh%M') for horaire in heures_horaires["horaire_heures"]]:
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
        heure = tracker.get_slot("heure")
        date = tracker.get_slot("date")
        dispatcher.utter_message(f"Heure {heure} date {date}")
        if heure is not None:
            response_mess = f"Les dates disponibles à la réservation pour {str(heure)} sont :"
            ressource = tracker.get_slot("ressource")
            dates_for_ressource = get_jours_disponibles(ressource,30,datetime.datetime.fromisoformat(str(heure)).time())
            # dispatcher.utter_message(dates_for_ressource)
            for date in dates_for_ressource:
                response_mess += f"\n\t- {str(date.day)}/{str(date.month)}/{str(date.year)}"
            dispatcher.utter_message(text=response_mess)
            dispatcher.utter_message(text="Quand souhaitez-vous réserver ?")
            return []     
        elif heure is None and date is None:
            ressource = str(tracker.get_slot("ressource"))
            result_query_heures = get_heures_semaine(ressource)
            dict_horaires_jour : dict[str,dict] = result_query_heures["horaires"]
            dispatcher.utter_message("Les horaires de réservation sont les suivants: ")
            for day in dict_horaires_jour.keys():
                for horaire in result_query_heures["horaires"][day]["horaires"]:
                    dispatcher.utter_message(f"Le {Day_week(int(day)).name.capitalize()} de {horaire[0]} à {horaire[1]} par intervalles de {result_query_heures['horaires'][day]['decoupage']}")
            response_mess = "Les dates disponibles à la réservation pour le prochain mois sont :"
            ressource = tracker.get_slot("ressource")
            dates_for_ressource = get_jours_disponibles(ressource,30,None)
            # dispatcher.utter_message(dates_for_ressource)
            for date in dates_for_ressource:
                response_mess += f"\n\t- {str(date.day)}/{str(date.month)}/{str(date.year)}"
            dispatcher.utter_message(text=response_mess)
            dispatcher.utter_message(text="Quand souhaitez-vous réserver ?")

        else:
            response_mess = "Les dates disponibles à la réservation sont :"
            ressource = tracker.get_slot("ressource")
            dates_for_ressource = get_jours_disponibles(ressource,30,None)
            # dispatcher.utter_message(dates_for_ressource)
            for date in dates_for_ressource:
                response_mess += f"\n\t- {str(date.day)}/{str(date.month)}/{str(date.year)}"
            dispatcher.utter_message(text=response_mess)
            dispatcher.utter_message(text="Quand souhaitez-vous réserver ?")
            
            return []