# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction, ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import EventType
from rasa_sdk.events import SlotSet
@staticmethod
def get_ressource_list()->list[str]:
    return ["tennis","badminton","ping-pong","pétanque","handball","basket"]

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

class ActionEnumerateRessource(Action):

    def name(self) -> Text:
        return "action_enumerate_ressource"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Les ressources à disposition sont : \n\t- Tennis\n\t- Pétanque\n\t- Handball\n\t- basket\n\t- ping-pong")

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

# https://rasa.com/docs/rasa/action-server/validation-action/
class ValidateRessourceSlot(ValidationAction):
    def validate_ressource(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate location value."""
        if isinstance(slot_value, str):
            ressource :str = str(slot_value).lower()
            dispatcher.utter_message(f"Ressource: {ressource}")

            if ressource in get_ressource_list():
                return {"ressource": ressource.capitalize()}
            else:
                dispatcher.utter_message(f"{ressource.capitalize()} n'existe pas. Veuillez suggérer une ressource valide.")
                return {"ressource": None}
        else:
            # validation failed, set this slot to None
            return {"ressource": None}
        
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