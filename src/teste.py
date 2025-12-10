from pprint import pprint
from workflows import publishing_team
from tools import load_json_data
# from data import extracted_schema




######################################
# Testando a Extração de Ontologia
######################################
# inputs = {
#    'csv_path': "D:\Doutorado\datasets\contratos\csv_contratos_cgu\contratos_160051.csv",
#    'dataset_schema': extracted_schema,
#    'dataset_description': "A dataset of contracts signed between public organizations, the management units of these organizations, and suppliers."
# }




######################################
# Testando a Sugestão de Vocabulário
######################################
# Usage within your module
extracted_schema = load_json_data(filename="outputs/extracted_schema.json")
if extracted_schema:
	# pprint(extracted_schema)
   inputs = {
      'dataset_schema': extracted_schema,
      'dataset_description': "A dataset of contracts signed between public organizations, the management units of these organizations, and suppliers."
   }

   # Execution
   result = publishing_team.kickoff(inputs=inputs)
   print(result)
