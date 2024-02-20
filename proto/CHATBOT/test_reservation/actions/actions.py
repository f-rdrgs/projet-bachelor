# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionReserveResource(Action):

    def name(self) -> Text:
        return "action_reserve_resource"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        current_resource = next(tracker.get_latest_entity_values("resource"),None)
        print(current_resource)
        dispatcher.utter_message(text="Hello World!")

        return []
