from typing import Dict, Text, Any, List
 
from langcodes import Language
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.nlu.tokenizers.tokenizer import Token

from spellchecker import SpellChecker
import nltk


def _is_list_tokens(v):
    if isinstance(v, List):
        if len(v) > 0:
            if isinstance(v[0], Token):
                return True
    return False


# https://tatrasdata.medium.com/custom-nlu-component-in-rasa-3-x-484d8b7d2e4f

@DefaultV1Recipe.register(
 [DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER], is_trainable=False
)

class Spellchecking_Comp(GraphComponent):
    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> GraphComponent:
        # TODO: Implement this 
        ...

    def train(self, training_data: TrainingData) -> Resource:
        # TODO: Implement this if your component requires training
        ...
    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        # TODO: Implement this if your component augments the training data with
        #       tokens or message features which are used by other components
        #       during training.
        ...

        return training_data
    
    def process(self, messages: List[Message]) -> List[Message]:
        spell = SpellChecker(language="fr")
        
        # This method is used to modify the user message and remove () if included in the user text.
        data = ["Tennis","Handball","Basketball","Ping-Pong","Pétanque"]
        for message in messages:
            # print(message.data)
            for k, v in message.data.items():
                # print(k, v)
                if _is_list_tokens(v):
                    print(f"{k}: {[t.text for t in v]}")
                else:
                    print(f"{k}: {v.__repr__()}")
            print("\n\n***********************MeSSAges**************************")
            print(message.data)
            print("\n\n\n\n")
        return messages

# Christopher P. Matthews
# christophermatthews1985@gmail.com
# Sacramento, CA, USA
def levenshtein(s, t):
        ''' From Wikipedia article; Iterative with two matrix rows. '''
        if s == t: return 0
        elif len(s) == 0: return len(t)
        elif len(t) == 0: return len(s)
        v0 = [None] * (len(t) + 1)
        v1 = [None] * (len(t) + 1)
        for i in range(len(v0)):
            v0[i] = i
        for i in range(len(s)):
            v1[0] = i + 1
            for j in range(len(t)):
                cost = 0 if s[i] == t[j] else 1
                v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
            for j in range(len(v0)):
                v0[j] = v1[j]
                
        return v1[len(t)]





# if __name__ == "__main__":
#     data = ["Salut","Bonsoir", "Yo","Bonjour"]
#     for sing_d in data:
#         print(levenshtein(sing_d,"Bnsoir"))
