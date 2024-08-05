from io import TextIOWrapper
import os
import pandas as pd

PATH_DATASET = os.path.join(os.path.dirname(__file__),"../../db/data")
PATH_FILL = os.path.join(os.path.dirname(__file__),"data_filling")
PATH_NLU_DATA = os.path.join(os.path.dirname(__file__),"../data/nlu")
def add_intent(file:str,file_data:str,intent_name:str,file_fill:str,entity_name:str,first_intent:bool,key_csv_col:str):
    f_data = pd.read_csv(os.path.join(PATH_DATASET,file_data))
    f_filling = open(os.path.join(PATH_FILL,file_fill),"r")
    f_intent = open(os.path.join(PATH_NLU_DATA,file),"+a")
    begin_intent = f"version: \"3.1\"\n\nnlu:" if first_intent else ''
    f_intent.write(f"{begin_intent}\n  - intent: {intent_name}\n    examples: |\n")
    filling_lines = f_filling.readlines()
    for data in f_data[key_csv_col]:
        data = str(data) 
        temp_fill = [f"      - {fill.strip()}{'' if fill == ' ' else ' ' }[{data if id %2 else data.capitalize()}]({entity_name})\n" for id,fill in enumerate(filling_lines)]
        f_intent.writelines(temp_fill)

    f_filling.close()
    f_intent.close()

# files_data: [ [path_file, isCSV, entity name, CSV key] ]
def add_intent_custom(file:str,files_data:list[tuple[str,bool,str,str]],intent_name:str,file_fill:str,first_intent:bool,num_loop_fill:int):
    f_datas = [[pd.read_csv(os.path.join(PATH_DATASET,file_data[0])),file_data[2],file_data[3]] if file_data[1] else [open(os.path.join(PATH_FILL,file_data[0]),"r"),file_data[2]] for file_data in files_data]
    f_filling = open(os.path.join(PATH_FILL,file_fill),"r")
    f_intent = open(os.path.join(PATH_NLU_DATA,file),"+a")
    begin_intent = f"version: \"3.1\"\n\nnlu:" if first_intent else ''
    f_intent.write(f"{begin_intent}\n  - intent: {intent_name}\n    examples: |\n")
    filling_lines = f_filling.readlines()
    temp_fill : list[str]= []
    for i in range(num_loop_fill):
        temp_fill += [f"      - {fill.strip()}{'' if fill == ' ' else ' ' }\n" for fill in filling_lines]
    for i in range(temp_fill.__len__()):
        for index,data in enumerate(f_datas):
            # data = [dataframe, entity, csv key]
            if isinstance(data[0],pd.DataFrame):
                lst_data : pd.DataFrame = data[0]
                key_col = data[2]
                entity = data[1]
                temp_fill[i] = temp_fill[i].replace("["+entity+"]",f"[{lst_data[key_col][i % (lst_data.shape[0])].strip()}]({entity})")
            # data = [open object]
            elif isinstance(data[0],TextIOWrapper):
                lst_data :list[str] = data[0].readlines()
                len_data = lst_data.__len__()
                entity = data[1].strip()
                temp_fill[i] = temp_fill[i].replace("["+entity+"]",f"[{lst_data[i % len_data].strip()}]({entity})")
                data[0].seek(0)
            # data = str(data) 
            # temp_fill = [f"      - {fill.strip()}{'' if fill == ' ' else ' ' }[{data if id %2 else data.capitalize()}]({entity_name})\n" for id,fill in enumerate(filling_lines)]
    f_intent.writelines(temp_fill)
    
    print(list(map(lambda x: x[0].close() if(isinstance(x[0],TextIOWrapper)) else False,f_datas)))
    f_filling.close()
    f_intent.close()


def add_lookup(file:str,file_data:str,lookup_name:str,first_intent:bool,key_csv_col:str):
    f_data = pd.read_csv(os.path.join(PATH_DATASET,file_data))
    f_lookup = open(os.path.join(PATH_NLU_DATA,file),"+a")
    begin_intent = f"version: \"3.1\"\n\nnlu:" if first_intent else ''
    f_lookup.write(f"{begin_intent}\n- lookup: {lookup_name}\n  examples: |\n")
    for data in f_data[key_csv_col]:
        data = str(data) 
        temp_fill = f"    - {data}\n"
        f_lookup.writelines(temp_fill)

    f_lookup.close()

def remove_if_exists(path:str):
    if os.path.exists(path):
        os.remove(path)
     

if __name__ == "__main__":
    print(PATH_DATASET)
    print(PATH_FILL)
    intent_ress_file = "intents_ressource.yml"
    intent_test_file = "intents_ressource_custom.yml"
    lookup_file = "lookup.yml"
    remove_if_exists(os.path.join(PATH_NLU_DATA,intent_ress_file))
    remove_if_exists(os.path.join(PATH_NLU_DATA,lookup_file))
    
    # add_intent(intent_ress_file,"ressource.csv","ressource_gather","ressource_gather_fill.txt","ressource",True,"label")
    add_intent_custom(intent_ress_file,[["random_date.txt",False,"date",""],["random_heure.txt",False,"heure",""],["ressource.csv",True,"ressource","label"]],"ressource_gather","ressource_gather_fill_custom.txt",True,2)
    # add_intent(intent_ress_file,"ressource.csv","inform_ressource","inform_ressource.txt","ressource",False,"label")
    add_intent(intent_ress_file,"ressource.csv","ask_horaire","ask_ressource.txt","ressource",False,"label")
    add_lookup(lookup_file,"ressource.csv","ressource",True,"label")