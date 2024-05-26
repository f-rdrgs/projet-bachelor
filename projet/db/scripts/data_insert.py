import os
import pandas as pd
from __future__ import annotations
from typing import Annotated

import psycopg2
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

def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

'''
tuple d'info sur les fichiers traités
- chemin fichier original
- chemin fichier temporaire
- liste d'en-tête du fichier original
- liste d'en-tête du fichier temporaire
- nom de la table dans la DB
'''
csv_files: Annotated[list[tuple[str,str,list[str],list[str],str]],"Tuple(Filepath originel, Filepath temp, header originel, header temporaire, table DB)"] = []

def process_csv(file:str,table_name:str,*args:str):
    try:
        script_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(script_path,"../data/"+file)
        csv_data = pd.read_csv(filepath)
        og_columns = csv_data.columns.tolist()
        if len(args)>0:
            csv_data = csv_data.drop(columns=[col for col in args])
        temp_name = filepath.removesuffix(".csv")+"_temp.csv"
        csv_data.to_csv(temp_name,index=False)
        csv_files.append(tuple([filepath,temp_name,og_columns,csv_data.columns.tolist(),table_name]))
        print(f"csv files : {csv_files}")
    
    except Exception as e:
        print(f"Error while processing {os.path.basename(file)}: {e}")

def update_sql_script():
    try:
        script_path = os.path.dirname(os.path.realpath(__file__))
        total_string = ""
        for file_data in csv_files:
            columns = file_data[3]
            file = os.path.basename(file_data[1])
            table_name = file_data[4]
            col_string=""
            if len(columns) > 0:
                for col in columns:
                    col_string+=col+","
                col_string = col_string.removesuffix(",")
            total_string+=f"COPY {table_name}({col_string})\nFROM '/data/{file}'\nWITH (FORMAT csv, HEADER);"
    
        # COPY jour_horaire(jour,debut,fin)
        # FROM '/data/horaire.csv'
        # WITH (FORMAT csv, HEADER);
        with open(os.path.join(script_path,"data_insert.sql"),"w") as f:
            f.write(total_string)
    except Exception as e:
        print(f"Error while updating SQL script: {e}")
        


def execute_script():
    with psycopg2.connect(**load_config()) as conn:
        conn.autocommit = True
        cursor = conn.cursor()
        sql = open("data_insert.sql", "r").read()
        cursor.execute(sql)
    while csv_files.__len__() > 0:
        file = csv_files.pop()
        os.remove(file[1])

    

if __name__ == "__main__":
    # https://stackoverflow.com/questions/61428710/insert-data-from-csv-to-postgresql-database-via-python
    # Faire en sorte d'ajouter depuis les csv les liens clés étrangères 
    
    # Commande pour exécuter fichiers sql
    # psql -h 0.0.0.0 -U admin -d chatbot-rasa -p 3401 -a -f db/scripts/data_insert.sql 

    # S'assurer que les en-têtes dans les fichiers CSV sont les mêmes que dans la table et dans le même ordre
    script_path = os.path.dirname(os.path.realpath(__file__))

    process_csv("horaire.csv","jour_horaire","title_ressource")
    process_csv("ressource.csv","ressource")
    update_sql_script()
    execute_script()