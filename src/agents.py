from crewai import Agent
from tools import get_data_schema_from_csv
from llms import llama3_groq


####################################################
################## PUBLISING TEAM ##################
####################################################

# 1
data_schema_agent = Agent(
   role="Schema Extraction Specialist",
   goal="Extract and document schemas from different data sources (SQL, NoSQL, APIs, CSV, JSON).",
   backstory=(
      "This agent was trained to automatically identify the structure "
      "of data sources, including tables, columns, data types, and relationships. "
      "It generates clear and organized documentation to support data engineers and analysts."
   ),
   tools=[get_data_schema_from_csv],  
   verbose=True,
   llm=llama3_groq
)

# 2
ontology_agent = Agent(
   role="Ontology Specialist",
   goal="Generate formal ontologies (OWL/RDF) directly from data source schemas.",
   backstory=(
      "This agent was designed to support data engineers and scientists "
      "in transforming data schemas into semantic ontologies (RDF/OWL). "
      "It identifies tables, columns, and relationships and converts them into classes, "
      "properties, and axioms, enabling semantic interoperability."
   ),
   verbose=True,
   llm=llama3_groq
)

# 3
vocabulary_agent = Agent(
   role="Ontology and Semantic Vocabulary Specialist",
   goal=(
      "Analyze existing ontologies and suggest widely used vocabularies "
      "from the Semantic Web community, such as FOAF, Schema.org, Dublin Core, RDF(S), and OWL."
   ),
   backstory=(
      "This agent was designed to support data engineers and scientists "
      "in aligning their ontologies with recognized semantic standards. "
      "It identifies classes and properties in an ontology and recommends "
      "external vocabularies that promote interoperability and reuse."
   ),
   verbose=True,
   llm=llama3_groq
)








####################################################
################# INTEGRATION TEAM #################
####################################################





####################################################
################## FUSION TEAM #####################
####################################################








####################################################
################# MASHUPS TEAM #####################
####################################################