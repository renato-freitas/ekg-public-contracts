from crewai import Task
from agents import data_schema_agent


####################################################
################## PUBLISING TEAM ##################
####################################################
extract_csv_schema_task = Task(
   description="Extrair o esquema de um CSV e gerar um JSON.",
   expected_output="Um documento JSON com {'name', 'dtype','isActive': True}.",
   agent=data_schema_agent
)

extract_sql_schema_task = Task(
   description="Extrair o esquema de uma base de dados relacional e gerar um JSON.",
   expected_output="Um documento JSON com {'name', 'dtype','isActive': True}.",
   agent=data_schema_agent
)



######################################################
################## INTEGRATION TEAM ##################
######################################################





####################################################
################## FUSION TEAM #####################
####################################################
