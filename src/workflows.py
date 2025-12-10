from crewai import Crew
from agents import data_schema_agent, ontology_agent, vocabulary_agent
from task import extract_csv_schema_task, dataset_ontology_generation, analyze_ontology_and_suggest_vocab_task

####################################################
################## PUBLISING TEAM ##################
####################################################
publishing_team = Crew(
	agents=[
      # data_schema_agent,
      ontology_agent,
      vocabulary_agent
   ],
	tasks=[
      # extract_csv_schema_task, 
      dataset_ontology_generation,
      analyze_ontology_and_suggest_vocab_task
   ],
	process='sequential'
)



######################################################
################## INTEGRATION TEAM ##################
######################################################





####################################################
################## FUSION TEAM #####################
####################################################
