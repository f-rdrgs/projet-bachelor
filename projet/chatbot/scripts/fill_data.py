import os
import pandas as pd

PATH_DATASET = os.path.join(os.path.dirname(__file__),"../../db/data")
PATH_FILL = os.path.join(os.path.dirname(__file__),"data_filling")
PATH_NLU_DATA = os.path.join(os.path.dirname(__file__),"../data/nlu")
def add_intent(file:str,file_data:str,intent_name:str,file_fill:str,entity_name:str,first_intent:bool):
    f_data = pd.read_csv(os.path.join(PATH_DATASET,file_data))
    f_filling = open(os.path.join(PATH_FILL,file_fill),"r")
    f_intent = open(os.path.join(PATH_NLU_DATA,file),"+a")
    begin_intent = f"version: \"3.1\"\n\nnlu:" if first_intent else ''
    f_intent.write(f"{begin_intent}\n  - intent: {intent_name}\n    examples: |\n")
    filling_lines = f_filling.readlines()
    for data in f_data["label"]:
        data = str(data) 
        temp_fill = [f"      - {fill.strip()}{'' if fill == ' ' else ' ' }[{data if id %2 else data.capitalize()}]({entity_name})\n" for id,fill in enumerate(filling_lines)]
        f_intent.writelines(temp_fill)

    f_filling.close()
    f_intent.close()


if __name__ == "__main__":
    print(PATH_DATASET)
    print(PATH_FILL)
    intent_ress_file = "intents_ressource.yml"
    if os.path.exists(os.path.join(PATH_NLU_DATA,intent_ress_file)):
        os.remove(os.path.join(PATH_NLU_DATA,intent_ress_file))
    add_intent(intent_ress_file,"ressource.csv","ressource_gather","ressource_gather_fill.txt","ressource",True)
    add_intent(intent_ress_file,"ressource.csv","inform_ressource","inform_ressource.txt","ressource",False)
