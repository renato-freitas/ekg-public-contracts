from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef, Literal

kg = Graph().parse("metadata_graph_rag.ttl", format="turtle")
ontology = Graph().parse("vosv.ttl", format="turtle")

ttl_string = ontology.serialize(format="turtle")

llm = LLM(model="gemini/gemini-2.5-flash")

#@tool
def get_vosv(view_type:str):
    """
    Query VOSV vocabulary and return all triples (?subject ?predicate ?object).

    Returns:
        list of dict: List of triples in format {"subject":..., "predicate":..., "object":...}
        or a string indcating that nothing is returned.
    """
    query_vosv = """
    SELECT ?subject ?predicate ?object
    WHERE {
      ?subject a ?type;
        ?predicate ?object .
    }
    """

    results = ontology.query(query_vosv)

    triplas = []
    for row in results:
        triplas.append({
            "subject": str(row.subject),
            "predicate": str(row.predicate),
            "object": str(row.object)
        })

    if triplas:
        return triplas
    else:
        return "Nada foi retornado"
    
@tool
def generate_sparql_query(source_name: str) -> str:
    """
    Uses LLM to generate a SPARQL query for retrieving source schema and ontology info.
    """
    # Obtemos o esquema VOSV
    result = ttl_string  

    prompt = f"""
Given the source name "{source_name}", write a SPARQL query to retrieve: metadata from data source and ontology (vosv:SemanticViewOntology)
- Assume the query is formulated only follows VoSV vocabulary: {result}
- Follow the types defined accordly VoSV;
- Get SemanticView Ontology metadata, all, including vosv:hasClass and vosv:hasProperty:
- Consider the rdfs:domain to related Classes and Properties
- Their types and labels (if available)

Not suggests classes or properties that is not present in VoSV vocabulary
    """

    # Chama o modelo LLM
    return llm.call(prompt)


@tool
def get_metadata_sparql_query(
    query_type: str = "",
    extra_instructions: str = ""
) -> str:
    """
    Uses LLM to generate a SPARQL query for retrieving info restricted to the VoSV vocabulary.
    """
    vocab_context = ttl_string  # já serializado

    prompt = f"""
You are an expert in SPARQL query generation. 
Generate a SPARQL query to retrieve **{query_type}**.

⚠️ VERY IMPORTANT:
- Use ONLY the following vocabulary/ontology (VoSV): {vocab_context}
- Do NOT use other namespaces such as drm:, dcterms:, schema:, etc.
- Only return SPARQL code, no explanations.
- Consider vosv:LinksetView as the class representing linkset views.
- Also include related properties (vosv:hasClass, vosv:hasProperty, rdfs:domain, rdfs:range, rdfs:label).

Extra instructions:
{extra_instructions}
    """

    return llm.call(prompt)




@tool
def query_metadata_graph(sparql_query: str) -> str:
    """
    Function for querying a Metadata Graph following a sparql query

    Args:
        sparql_query: Query to be executed in metadata graph

    Returns:
        dict | str: A query result from metadata graph
    """
    results = kg.query(sparql_query)

    triplas = []
    for row in results:
        triplas.append({
            "subject": str(row.subject),
            "predicate": str(row.predicate),
            "object": str(row.object)
        })

    if triplas:
        return triplas
    else:
        return "Nada foi retornado"
    

query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?x ?y ?z
    WHERE {
        ?x rdfs:subClassOf ?z .
        ?y rdfs:subClassOf ?z .
        ?z rdf:type <http://www.arida.ufc.br/vosv#GeneralizationClass>.
        FILTER(?x != ?y)

    }
"""

query2 = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT ?x 
    WHERE {
        ?x rdfs:subClassOf ?z .
        ?z rdf:type <http://www.arida.ufc.br/vosv#GeneralizationClass>.

    }
"""


query_exported_views = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX vosv: <http://www.arida.ufc.br/vosv#>
    SELECT ?x ?y ?z
    WHERE {
        ?x a vosv:ExportedView .
        ?y ?z.

    }
"""

query_linkset_views = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX vosv: <http://www.arida.ufc.br/vosv#>
    SELECT ?x ?y ?z
    WHERE {
        ?x a vosv:LinksetView .
        ?y ?z.

    }
"""

query_unification_views = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX vosv: <http://www.arida.ufc.br/vosv#>
    SELECT ?x ?y ?z
    WHERE {
        ?x a vosv:UnificationView .
        ?y ?z.

    }
"""

query_fusion_views = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX vosv: <http://www.arida.ufc.br/vosv#>
    SELECT ?x ?y ?z
    WHERE {
        ?x a vosv:FusionView .
        ?y ?z.

    }
"""

intro_query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?x ?p. 
    WHERE {
        ?x a ?z ;
            ?p ?o.
        ?z a owl:Class.
    }
"""

query_mappings = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX vosv: <http://www.arida.ufc.br/vosv#>

SELECT ?mapping ?property ?object
WHERE {
    ?mapping rdf:type vosv:Mappings ;
         ?property ?object .
}

"""

query_svo = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX vosv: <http://www.arida.ufc.br/vosv#>

SELECT ?class ?property
WHERE {
  {
    ?svo rdf:type vosv:SemanticViewOntology ;
         vosv:hasClass ?class ;
         vosv:hasProperty ?property .
  }
  UNION
  {
    ?class rdf:type owl:Class .
    ?class ?property ?object .
  }
}

"""

"""HITL"""


def get_classes_properties_svo():
    """
    Consulta um grafo para identificar as classes e propriedades da SVO.

    Args:
        kg: Grafo RDF
        query, Consulta a ser realizada no kg

    Returns:
        string: Classes and properties from SVO    
    """
    #result = kg.query(intro_query)
    classes = {}
    #kg.setReturnFormat("JSON")

    # 3. Executando e convertendo o resultado
    results = kg.query(intro_query).convert()

    # 4. Transformando a lista de bindings em dicionário
    classes_properties = {
        r["class"]["value"]: r["property"]["value"]
            for r in results["results"]["bindings"]
    }
    
    if classes_properties:
        return classes_properties
    return "Classes and Properties from SVO"


def get_svo():
    """
    Consulta o grafo RDF e retorna uma string formatada
    com as classes e suas propriedades associadas.
    """
    results = kg.query(query_svo)
    classes_properties = defaultdict(list)

    # Agrupa propriedades por classe
    for r in results:
        class_name = str(r["class"])
        property_name = str(r["property"])
        classes_properties[class_name].append(property_name)

    # Caso não haja resultados
    if not classes_properties:
        return "Nenhum resultado encontrado no grafo."

    # Monta a saída final formatada
    output = ["=== Classes e suas Propriedades (SVO) ==="]
    for cls, props in classes_properties.items():
        output.append(f"\nClasse: {cls}")
        output.extend([f"  - {p}" for p in props])

    return "\n".join(output)


def get_exported_views():
    """
    Consulta um grafo para identificar as Exported Views.

    Args:
        kg: Grafo RDF
        query, Consulta a ser realizada no kg

    Returns:
        string: Exported Views    
    """
    #result = kg.query(intro_query)
    classes = {}
    kg.setReturnFormat("JSON")

    # 3. Executando e convertendo o resultado
    results = kg.query(query_exported_views).convert()
    if results:
        return classes
    return "Nenhuma Exported View"

@tool
def get_linkset_views():
    """
    Consulta o grafo para identificar as Linkset Views
    e retorna (?x, ?y, ?z).
    """
    results = ontology.query(query_linkset_views)

    triplas = []
    for row in results:
        x, y, z = row  # cada row é um tuple com (x, y, z)
        triplas.append((str(x), str(y), str(z)))

    if triplas:
        return triplas

    return "Nenhuma Linkset View"




def get_unification_views():
    """
    Consulta um grafo para identificar as Unification Views.

    Args:
        kg: Grafo RDF
        query, Consulta a ser realizada no kg

    Returns:
        string: Linkset Views    
    """
    #result = kg.query(intro_query)
    classes = {}
    kg.setReturnFormat("JSON")

    # 3. Executando e convertendo o resultado
    results = kg.query(intro_query).convert()
    if results:
        return classes
    return "Nenhuma Unification View"

def get_unification_views():
    """
    Consulta um grafo para identificar as Unification Views.

    Args:
        kg: Grafo RDF
        query, Consulta a ser realizada no kg

    Returns:
        string: Fusion Views    
    """
    #result = kg.query(intro_query)
    classes = {}
    kg.setReturnFormat("JSON")

    # 3. Executando e convertendo o resultado
    results = kg.query(intro_query).convert()
    if results:
        return classes
    return "Nenhuma Unification View"


def get_fusion_views():
    """
    Consulta um grafo para identificar as Fusion Views.

    Args:
        kg: Grafo RDF
        query, Consulta a ser realizada no kg

    Returns:
        string: Fusion Views    
    """
    #result = kg.query(intro_query)
    classes = {}
    kg.setReturnFormat("JSON")

    # 3. Executando e convertendo o resultado
    results = kg.query(intro_query).convert()
    if results:
        return classes
    return "Nenhuma Fusion View"

def get_generalization_classes():
    """
    Consulta um grafo para identificar uma generalization class.

    Args:
        kg: Grafo RDF
        query, Consulta a ser realizada no kg

    Returns:
        string: Generalization Class    
    """
    result = kg.query(query)
    for row in result:
        x_val = row.x
        y_val = row.y
        z_val = row.z
    return z_val

def wrapperOntologySVO():
    classes_properties = get_classes_properties_svo()
    g = Graph()
    EX = Namespace("http://example.org/onto#")
    g.bind("ex", EX)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)

    for c, p in classes_properties.items():
        class_uri = URIRef(c)
        prop_uri = URIRef(p)

        # Adicionar a classe
        g.add((class_uri, RDF.type, OWL.Class))

        # Adicionar a propriedade como ObjectProperty genérica
        g.add((prop_uri, RDF.type, OWL.ObjectProperty))
        g.add((prop_uri, RDFS.domain, class_uri))
    
    ontology_graph = ontology_graph.serialize(format="turtle").decode("utf-8")

    return ontology_graph


def get_specialized_classes():
    """
    Query a graph to identify subclasses of a generalization class.

    Args:
    kg: RDF graph
    query, Query to be performed on kg

    Returns:
    string: Subclasses
    """
    result = kg.query(query2)

    classes = []
    for row in result: 
        x_val = row.x
        classes.append(x_val)
    if classes:
        return classes
    return "Nenhuma Classe Especializada"


print(get_vosv("ExportedView"))