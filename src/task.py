from crewai import Task
from pydantic import BaseModel
from agents import data_schema_agent, ontology_agent, vocabulary_agent, ontology_alignment_agent

OUTPUTS_FOLDER = "src/outputs"

####################################################
################## PUBLISING TEAM ##################
####################################################
extract_csv_schema_task = Task(
   description="Extrair o esquema de um CSV e gerar um JSON.",
   expected_output="Um documento JSON com {'name', 'dtype','isActive': true}.",
   output_file=OUTPUTS_FOLDER + "/extracted_schema_from_csv.json",
   agent=data_schema_agent
)

extract_sql_schema_task = Task(
   description="Extrair o esquema de uma base de dados relacional e gerar um JSON.",
   expected_output="Um documento JSON com {'name', 'dtype','isActive': true}.",
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

file_1 = get_ontology_file("outputs/ontologization_ceis.json")
file_2 = get_ontology_file("outputs/ontologization_cgu.json")

alignment_task = Task(
    description=f"""
    Analyze the two JSON files below to find the best class matches:

    ONTOLOGY A:
    {file_1}

    ONTOLOGY B:
    {file_2}

    Your mission:
    1. Identify class pairs with the highest match score (Based on names, comments, and property types).
    2. For each match found, present:
       - URI_Class_A and URI_Class_B.
       - Confidence Score (0.0 to 1.0).
       - Evidence (Shared properties).
       - Semantic Justification.
    3. **Integrated Class Suggestion**: Propose an 'IntegratedClass' (Fusion). 
       NAMING RULES: 
       - Do not use generic terms like 'Party', 'Entity', or 'Object'.
       - The name must be a compound noun reflecting the nature of both datasets.
       - If Class A deals with punishment and Class B deals with supply, the name should be something like 'PunishedSupplier' or 'SanctionedContractor'.
    4. **Specialized Classes Suggestion**: Also suggest the name of each class with a suffix_ according to the data source,
    following the URI pattern (e.g., **URI_Class_A**: `http://example.com/sanctions#SanctioningAuthority`, the suggested specialized class should be SanctioningAuthority_SANCTIONS).
    """,
    expected_output="""A detailed alignment report. 
    For each pair, include a section 'Suggestion for GeneralizationClass with value: [Specific Compound Name]' and 'Suggestion for Specialized Class' and wait for human feedback.""",
    agent=ontology_alignment_agent,
    human_input=True 
)

rdf_generation_task = Task(
    description="""
    Based on the approved matches, generate an alignment ontology in RDF Turtle format.
    Use the 'align:' prefix for mapping relationships.
    Include the new integrated classes (GeneralizationClass) as :GeneralizationClass and owl:Class.
    Include the new Specialized classes as owl:Class and use rdfs:subClassOf to connect these classes with their respective integrated classes.
    """,
    expected_output="Full file content in RDF Turtle format.",
    agent=ontology_alignment_agent,
    context=[alignment_task], 
    output_file="outputs/alignment.ttl" 
)

mapping_generator_task = Task(
    description="""
        Generate a COMPLETE and VALID RML mapping (Turtle syntax) using the context :

        - Source Schema 
        - Domain Ontology 
        - Schema Metadata Matching (RDF/Trig) 

        ---


        ### OBJECTIVE:
        Produce a fully compliant RML mapping where each source attribute is explicitly mapped 
        to an ontology property based strictly on the provided alignment metadata.

        ---

        ### INPUT INTERPRETATION:

        1. SOURCE SCHEMA:
        - Extract all attributes and datatypes
        - Ignore attributes where isActive = false

        2. ONTOLOGY:
        - Use ONLY classes and properties defined in the ontology
        - Preserve exact IRIs and prefixes

        3. ALIGNMENT (CRITICAL):
        - Extract mappings of the form:
            source_element → target_property
        - DO NOT infer mappings
        - DO NOT create new ontology terms
         Read the metadata alignment and interpret mappings:
         source_element → target_element ,mapping_type (equivalence, broader, narrower) ,  confidence_score,  semantic_justification
        ---

        ### RML GENERATION:

         Generate RML mapping: Define Logical Source ; Create Triples Maps ; Use rr:subjectMap and rr:predicateObjectMap ; Use ontology terms as predicates ;Assign correct datatypes (xsd:string, xsd:date, etc.)

        4. CREATE ONE TriplesMap:

        - Use:
            rml:logicalSource [
                a rml:LogicalSource ;
                rml:source "<source_file>" ;
                rml:referenceFormulation ql:CSV
            ]

        ---

        5. SUBJECT MAP:

        - Use rr:subjectMap
        - Generate unique URIs using rr:template
        - Use a meaningful identifier from source (e.g., numeroContrato)

        Example:
        rr:template "http://agentic-ai/resource/contrato/{numeroContrato}"

        - Assign correct class from ontology (e.g., cgu:Contract)

        ---

        6. PREDICATE-OBJECT MAPS (STRICT):

        For EACH mapping in the alignment:

        - Generate EXACTLY ONE rr:predicateObjectMap

        MANDATORY STRUCTURE:

        # source_attribute → ontology_property
        rr:predicateObjectMap [
        rr:predicate <ONTOLOGY_PROPERTY> ;
        rr:objectMap [
            rml:reference "<SOURCE_ATTRIBUTE>" ;
            rr:datatype <XSD_TYPE>
        ]
        ] ;

        ---

        ### DATATYPE RULES:

        Map schema types to XSD:

        - int64 → xsd:integer
        - float64 → xsd:decimal
        - object → xsd:string
        - datetime64 → xsd:dateTime

        ---

        ### STRICT CONSTRAINTS:

        - Use ONLY:
            ✔ rml:reference (NEVER rr:column)
            ✔ rml:logicalSource

        - NEVER use:
            ✘ rr:column
            ✘ rr:LogicalSource
            ✘ rr:source

        - Do NOT group attributes
        - Do NOT omit mappings
        - Do NOT create mappings outside alignment
        - Do NOT hallucinate ontology terms

        ---

        ### OUTPUT REQUIREMENTS:

        - Output a COMPLETE TriplesMap
        - One predicateObjectMap per attribute
        - Fully expanded syntax (no shorthand)
        - Valid Turtle syntax
        - Use correct prefixes (rr, rml, ql, xsd, ontology prefix)

        ---

        ### STYLE REQUIREMENT:

        - Include comments for each mapping:

        Example:
        # nomeOrgao → cgu:organizationName

        ---

        ### FINAL OUTPUT:

        Return ONLY the RML mapping.
        Do NOT include explanations.
        """,

            expected_output="""
        A valid RML mapping in Turtle syntax with:
        - One TriplesMap
        - One subjectMap using rr:template
        - One predicateObjectMap per aligned attribute
        - Correct ontology predicates from alignment
        - Correct XSD datatypes
        And mappings Metadatas
        """,

    human_input=True,
    output_file= OUTPUTS_FOLDER + "/mappings.ttl",
    context=[data_schema_agent,ontology_agent,vocabulary_agent,metadata_agent],
    agent=mapping_agent
)

triplification_task = Task(
    description=(
        "Execute a ferramenta morph_kgc_tool usando EXATAMENTE estes caminhos:\n"
        "- mapping_path: '({mapping_generator_task.output})\n"
        "- data_path: '/ekg-public-contracts-main/sources/contratos_153045.csv'\n"
        "- output_path: 'Triplas.nt'\n"
        "Não tente buscar informações de outras tarefas. Use apenas estes valores."
    ),
    expected_output=" Arquivo de triplas.nt gerado com sucesso.",
    agent=triplification_agent,
    output_file= OUTPUTS_FOLDER + "/Triples.nt",
    context=[mapping_generator_task], # Puxa o resultado da task anterior

)

######################################################
################## INTEGRATION TEAM ##################
######################################################





####################################################
################## FUSION TEAM #####################
####################################################
