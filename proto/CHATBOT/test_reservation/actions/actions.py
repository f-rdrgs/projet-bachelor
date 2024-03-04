# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset, Restarted

class ActionReserveResource(Action):

    def name(self) -> Text:
        return "action_reserve_resource"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        current_time = tracker.get_slot("time")
        print(f"Current Date in reserve date: {current_time}")
        current_resource = next(tracker.get_latest_entity_values("resource"),None)
        print(current_resource)
        if(current_time is None):
            dispatcher.utter_message(text="Et à quelle date ?")

        return []
class ActionReserveDate(Action):
    def name(self) -> Text:
        return "action_reserve_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_time = tracker.get_slot("time")
        resource = tracker.get_slot("resource")
        print(f"Current Date in reserve date: {current_time}")
        if(resource is not None and current_time is not None):
            dispatcher.utter_message(text=f"Souhaitez-vous donc réserver pour le {current_time} un terrain de {resource} ?")

        return []
class ActionGoodbye(Action):
    def name(self) -> Text:
        return "action_goodbye"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Au revoir")
        return [AllSlotsReset(),Restarted()]