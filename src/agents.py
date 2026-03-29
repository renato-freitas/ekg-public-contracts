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


#4
ontology_alignment_agent = Agent(
    role="Ontology Engineer with Integration Focus",
    goal="Align ontology classes and propose generalized classes for data fusion",
    backstory="""You are an expert in data architecture and Semantic Web. 
    Your role is to identify matches between different schemas and suggest how this 
    data could be unified into a new class hierarchy (Generalization).""",
    #llm=gemini_llm,
    verbose=True
)


# 5
mapping_agent = Agent(
   role="Semantic Mapping Expert",
   goal=(
      "Design and validate formal mappings between structured data sources "
      "(such as relational databases, CSV files, and JSON schemas) and target ontologies. "
      "The agent generates mapping rules using standards like R2RML, RML, and CSVW, "
      "ensuring semantic consistency between source attributes and ontology classes and properties."
   ),
   backstory=(
      "This agent was created to bridge the gap between raw structured data and semantic models. "
      "It understands both data schemas and ontological structures, allowing it to define precise "
      "correspondences between fields, keys, and relationships. "
      "The agent supports OBDA pipelines and ensures that mappings are explainable, reusable, "
      "and aligned with semantic web best practices."
   ),
   verbose=True,
   llm=llama3_groq
)

# 6
triplification_agent = Agent(
    role='Especialista em Materialização RDF',
    goal='Executar o motor Morph-KGC para gerar arquivos de triplas válidos',
    backstory='Você é um executor técnico que transforma mapeamentos RML em grafos de conhecimento reais.',
    tools=[morph_kgc_tool],
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
