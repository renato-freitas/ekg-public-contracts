from crewai import Crew
from agents import data_schema_agent
from task import extract_csv_schema_task

####################################################
################## PUBLISING TEAM ##################
####################################################
publishing_team = Crew(
	agents=[
      data_schema_agent,
      # agent_ontology_modeler,
      # agent_ontology_aligment
   ],
	tasks=[
      extract_csv_schema_task, 
      # task_dataset_ontology_generation,
      # task_suggest_vocabulary
   ],
	process='sequential'
)



######################################################
################## INTEGRATION TEAM ##################
######################################################





####################################################
################## FUSION TEAM #####################
####################################################
