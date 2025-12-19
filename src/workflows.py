from crewai import Crew
from agents import data_schema_agent, ontology_agent, vocabulary_agent
from task import extract_csv_schema_task, dataset_ontology_generation, analyze_ontology_and_suggest_vocab_task

####################################################
################## PUBLISING TEAM ##################
####################################################
publishing_team = Crew(
	agents=[
      # data_schema_agent, # recebe uma descrição do || no retorno do esquema o usuário faça uma validação.
      # Uma conversa
      ontology_agent,      # recebe o esquema extraído
      vocabulary_agent     # recebe a ontologia | interversão humana
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
# Linkset View




####################################################
################## FUSION TEAM #####################
####################################################







####################################################
################# MASHUPS TEAM #####################
####################################################