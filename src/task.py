from crewai import Task
from pydantic import BaseModel
from agents import data_schema_agent, ontology_agent, vocabulary_agent

OUTPUTS_FOLDER = "src/outputs"

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


class OntologizationResult(BaseModel):
   explanation: str
   ontology: str

dataset_ontology_generation = Task(
   description=(
      "Extract an ontology from <dataset_schema>.\n"
		"Generate an ontology, in Turtle serialization, to represent the <dataset_schema>{dataset_schema}</dataset_schema>.\n"
      "Get as context the dataset name and the dataset description <dataset_description>{dataset_description}</dataset_description> to generate an ontology.\n"
      "Define classes from the dataset name.\n"
      "When a field/column looks like as an entity or concept, represent it as an owl:Class.\n"
      "When a field/column is a relationship, represent as owl:ObjectProperty.\n"
      "When a field/column is a data type, represent it as an owl:DatatypeProperty.\n"
      "For each property, define its owl:domain and owl:range.\n"
      "Infere hierarchical relationships.\n"
      "Make relationships between classes.\n"
      "Do not include any individual as an example.\n"
      "Use the prefix ':' for generated terms.\n"
      "Separe the terms usin comment blocks like: ### Object Properties.\n"
      "Translate all classes and properties to english."
	),
   expected_output=(
      "A json document with the following keys:"
		"'explanation'"
      "'ontology'"
	),
   output_json=OntologizationResult,
   output_file=OUTPUTS_FOLDER + "/ontologization.json",
   agent=ontology_agent
)



analyze_ontology_and_suggest_vocab_task = Task(
   description=(
      "Analyze a given ontology and suggest widely used vocabularies "
      "from the Semantic Web community that can be reused or aligned "
      "with the concepts of the ontology."
   ),
   agent=vocabulary_agent,
   expected_output=(
      "A structured JSON with vocabulary recommendations."
      "For each term in the provided ontology, recommend 2 existing vocabularies,"
      "following form:"
      "{ "
      "  ontology term: ["
      "     {vocabulary1, namespace (vocabulary URL), term, preferred prefix, isActive = false},"
      "     {vocabulary2, namespace (vocabulary URL), term, preferred prefix, isActive = false}"
      "  ]"
      "}"
   ),
   context=[dataset_ontology_generation],
   output_file=OUTPUTS_FOLDER + "/vocabulary.json",
)

######################################################
################## INTEGRATION TEAM ##################
######################################################





####################################################
################## FUSION TEAM #####################
####################################################
