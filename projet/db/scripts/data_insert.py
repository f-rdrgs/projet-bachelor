import pandas as pd
if __name__ == "__main__":
    horaire_data = pd.read_csv('../data/horaire.csv')
    # https://stackoverflow.com/questions/61428710/insert-data-from-csv-to-postgresql-database-via-python
    # Faire en sorte d'ajouter depuis les csv les liens clés étrangères 
    
    # Commande pour exécuter fichiers sql
    # psql -h 0.0.0.0 -U admin -d chatbot-rasa -p 3401 -a -f db/scripts/data_insert.sql 