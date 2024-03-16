import csv
from transformers import TapasTokenizer, TapasForQuestionAnswering
import pandas as pd
from datetime import datetime, timedelta
from typing import Any, List
import numpy as np
from datetime import datetime
from icalendar import Calendar, Event

# Code was found on this page https://github.com/christianversloot/machine-learning-articles/blob/main/easy-table-parsing-with-tapas-machine-learning-and-huggingface-transformers.md 

# Define the table
# data = pd.read_csv("./salles.csv").astype(str)

# Define the questions
# queries = ["Nom Terrain Salle tennis disponible mardi 16h ?"]

def load_model_and_tokenizer():
  """
    Load
  """
  # Load pretrained tokenizer: TAPAS finetuned on WikiTable Questions
  tokenizer = TapasTokenizer.from_pretrained("google/tapas-base-finetuned-wtq")

  # Load pretrained model: TAPAS finetuned on WikiTable Questions
  model = TapasForQuestionAnswering.from_pretrained("google/tapas-base-finetuned-wtq")

  # Return tokenizer and model
  return tokenizer, model


def prepare_inputs(data, queries, tokenizer):
  """
    Convert dictionary into data frame and tokenize inputs given queries.
  """
  # Prepare inputs
  inputs = tokenizer(table=data, queries=queries, padding='max_length', return_tensors="pt")
  
  # Return things
  return data, inputs


def generate_predictions(inputs, model, tokenizer):
  """
    Generate predictions for some tokenized input.
  """
  # Generate model results
  outputs = model(**inputs)

  # Convert logit outputs into predictions for table cells and aggregation operators
  predicted_table_cell_coords, predicted_aggregation_operators = tokenizer.convert_logits_to_predictions(
          inputs,
          outputs.logits.detach(),
          outputs.logits_aggregation.detach()
  )
  
  # Return values
  return predicted_table_cell_coords, predicted_aggregation_operators


def postprocess_predictions(predicted_aggregation_operators, predicted_table_cell_coords, table):
  """
    Compute the predicted operation and nicely structure the answers.
  """
  # Process predicted aggregation operators
  aggregation_operators = {0: "NONE", 1: "SUM", 2: "AVERAGE", 3:"COUNT"}
  aggregation_predictions_string = [aggregation_operators[x] for x in predicted_aggregation_operators]

  # Process predicted table cell coordinates
  answers = []
  for coordinates in predicted_table_cell_coords:
    if len(coordinates) == 1:
      # 1 cell
      answers.append(table.iat[coordinates[0]])
    else:
      # > 1 cell
      cell_values = []
      for coordinate in coordinates:
        cell_values.append(table.iat[coordinate])
      answers.append(", ".join(cell_values))
      
  # Return values
  return aggregation_predictions_string, answers


def show_answers(queries, answers, aggregation_predictions_string):
    """
    Visualize the postprocessed answers.
    """
    output = []
    for query, answer, predicted_agg in zip(queries, answers, aggregation_predictions_string):
        print(query)
        print(f"Answer : {answer}")
        if predicted_agg == "NONE":
            print("Predicted answer: " + answer)
            output.append("Predicted answer: " + answer+"\n")
        else:
            print("Predicted answer: " + predicted_agg + " > " + answer)
    return output


def show_answers(queries, answers, aggregation_predictions_string):
    """
    Visualize the postprocessed answers.
    """
    output = []
    output_text = ""
    for query, answer, predicted_agg in zip(queries, answers, aggregation_predictions_string):
        if predicted_agg == "NONE":
            output.append(answer)
            output_text+="Predicted answer: " + answer+"\n"
        else:
            output.append([predicted_agg,answer])
            output_text+="Predicted answer: " + predicted_agg + " > " + answer+"\n"

    return output,output_text


def run_tapas(data : pd.DataFrame, queries : np.ndarray[str]):
    """
        Invoke the TAPAS model.
    """
    tokenizer, model = load_model_and_tokenizer()
    # data = pd.read_csv("./data.csv").astype(str)
    # data1 = pd.read_csv("./Sports.csv").astype(str)
    # data2 = pd.read_csv("./Terrains.csv").astype(str)
    # data3 = pd.read_csv("./Lieux.csv").astype(str)
    # data4 = pd.read_csv("./Horaires.csv").astype(str)
    # data5 = pd.read_csv("./Tarifs.csv").astype(str)

    # data =  pd.concat([data1,data2,data3,data4,data5],axis=0,join='outer')
    # data = data.replace("nan", '', regex=True)
    # # print(data)
    # data = data.astype(str)
    # data.to_csv('data.csv', index=False)
    # print(data)
    # print(data)
    # print(data)
    table, inputs = prepare_inputs(data, queries, tokenizer)
    predicted_table_cell_coords, predicted_aggregation_operators = generate_predictions(inputs, model, tokenizer)
    aggregation_predictions_string, answers = postprocess_predictions(predicted_aggregation_operators, predicted_table_cell_coords, table)
    output,output_text = show_answers(queries, answers, aggregation_predictions_string)
    with open("output.txt", 'w') as file:
        file.write(output_text)
        file.close()
    return output

def convert_csv_to_ics(csv_file, ics_file):
    # Open the CSV file for reading
    with open(csv_file, 'r') as csv_file:
        
        reader = csv.reader(csv_file)
        data = pd.read_csv("./test.csv")
        print(data)

        # Create a new iCalendar object
        cal = Calendar()

        # Skip the header if your CSV file has one
        next(reader, None)

        # Iterate through the CSV rows
        for row in reader:
            # Extract relevant data from the CSV row (modify as needed)
            event_summary = row[0]
            event_description = row[1]
            event_date_str = row[2]

            # Convert the date string to a datetime object (modify format as needed)
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d')

            # Create a new event
            event = Event()
            event.add('summary', event_summary)
            event.add('description', event_description)
            event.add('dtstart', event_date)

            # Add the event to the calendar
            cal.add_component(event)

    # Write the iCalendar data to a file
    with open(ics_file, 'wb') as ics_file:
        ics_file.write(cal.to_ical())

def parse_response(arr_response:np.ndarray):
	parsed_response = []
	for response in arr_response:
		print(f"Response : {response}")
		if isinstance(response,list):
			parsed_enums = [element.strip() for element in response[1].split(",")]
			parsed_response.append([response[0],parsed_enums])
		else:
			parsed_response.append([element.strip() for element in response.split(",")])

	return parsed_response

if __name__ == '__main__':
	queries = ["What are all the available tennis courts by name column ?"]
	data =  pd.read_csv("./Terrains.csv").astype(str)
	print(data[data.apply(lambda row: any("Tennis 1" in value for value in row.values), axis=1)])
	res = run_tapas(data,queries)
	res = parse_response(res)
	print(res)


	newDf = pd.DataFrame()
	for element in res:
		if len(element) == 2:
			if element[0] == "COUNT":
				for info in element[1]:
					newDf = pd.concat([newDf,data[data.apply(lambda row: any(info in value for value in row.values), axis=1)]])
	else:
		print(f"Elem : {element}")
		for info in element:
			newDf = pd.concat([newDf,data[data.apply(lambda row: any(info in value for value in row.values), axis=1)]])
		newDf = newDf.drop_duplicates()
          
	print("Output") 
	print(newDf)
				
	queries = ["Which horaire by id allows for a reservation on tuesday at 18h30 ?"]
	data =  pd.read_csv("./Horaires.csv").astype(str)
	print(data[data.apply(lambda row: any("Tennis 1" in value for value in row.values), axis=1)])
	res = run_tapas(data,queries)
	res = parse_response(res)
	print(res)



  # res = parse_response(res)
  # print(f"Res : {res[0][1]}")
  # rows = [data.filter(like=item,axis=1) for item in res[0][1]]
  # print(rows)
  # data1 = pd.read_csv("./Sports.csv").astype(str)
  # data2 = pd.read_csv("./Terrains.csv").astype(str)
  # data3 = pd.read_csv("./Lieux.csv").astype(str)
  # data4 = pd.read_csv("./Horaires.csv").astype(str)
  # data5 = pd.read_csv("./Tarifs.csv").astype(str)

  # data = pd.concat([data1,data2,data3,data4,data5],axis=0,join='outer').astype(str)
  # data = data.replace("nan", '', regex=True)
  # print(data)
  # data.to_csv('data.csv', index=False)
  # convert_csv_to_ics('your_input.csv', 'output.ics')

