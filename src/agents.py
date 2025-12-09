from crewai import Agent
from tools import get_data_schema_from_csv
from llms import llama3_groq


####################################################
################## PUBLISING TEAM ##################
####################################################
data_schema_agent = Agent(
   role="Especialista em Extração de Esquemas",
   goal="Extrair e documentar esquemas de diferentes fontes de dados (SQL, NoSQL, APIs, CSV, JSON).",
   backstory=(
      "Este agente foi treinado para identificar automaticamente a estrutura "
      "de fontes de dados, incluindo tabelas, colunas, tipos de dados e relações. "
      "Ele gera documentação clara e organizada para apoiar engenheiros de dados e analistas."
   ),
   tools=[get_data_schema_from_csv],  
   verbose=True,
   llm=llama3_groq
)



######################################################
################## INTEGRATION TEAM ##################
######################################################





####################################################
################## FUSION TEAM #####################
####################################################
