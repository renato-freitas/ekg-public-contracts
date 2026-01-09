import os
from crewai import Agent, Task, Crew, LLM, Process
from crewai.tools import tool
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from ontoaligner.encoder import ConceptParentLightweightEncoder 
from ontoaligner.ontology import GenericOntology
from ontoaligner.aligner import SBERTRetrieval
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()
from query import *


kg = Graph().parse("metadata_graph_rag.ttl", format="turtle")
ontology = Graph().parse("vosv.ttl", format="turtle")


#os.environ["GEMINI_API_KEY"] = "AIzaSyCmSA_GD1VoF76eftNQWAJk67CuZkMrSYs"

os.environ["GEMINI_API_KEY"] = "AIzaSyCKVuqzx8O30J6vr0GtCrP8YZvoMwCL8tI"

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # 3. MUDANÇA PRINCIPAL: Nome de um modelo Gemini
    temperature=0.1,
    # Você pode descomentar a linha abaixo se preferir passar a chave explicitamente
     google_api_key="AIzaSyCKVuqzx8O30J6vr0GtCrP8YZvoMwCL8tI"
)
#llm = LLM(model="gemini/gemini-2.0-flash", temperature=0.0)

# serializa para string (formato Turtle)
ttl_string = ontology.serialize(format="turtle")

#@tool
def get_current_svo() -> str:
    """
    Obtain the current Semantic View Ontology (SVO) using a query on metadata graph.

    Not include classes or properties out of tool output
    
    :return: Classes and Properties of Semantic View Ontology
    :rtype: str
    """
    return get_svo()

svo = get_current_svo()

@tool
def regenerate_owl_tool(target_ontology: str) -> str:
    """
    Gera OWL Turtle forçando a redução de URIs para o prefixo 'base:'.
    """
    g = Graph()
    
    # 1. Extração e Limpeza Rigorosa da URI Base
    uri_base = "http://www.arida.ufc.br/ontology#"
    linhas = target_ontology.splitlines()
    for linha in linhas:
        if "OntologyURI:" in linha:
            uri_base = linha.split("OntologyURI:")[1].strip()
            break

    # Garante que a base termine com # ou /
    if not uri_base.endswith(("#", "/")):
        uri_base += "#"

    # 2. Registrar o Namespace
    BASE_NS = Namespace(uri_base)
    g.bind("base", BASE_NS)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)

    def extrair_apenas_nome_final(texto):
        """
        Garante que, se vier uma URI completa, pegamos apenas o que vem 
        depois do último # ou /.
        """
        texto = texto.strip().replace(" ", "_")
        if "#" in texto:
            return texto.split("#")[-1]
        elif "/" in texto and texto.startswith("http"):
            return texto.split("/")[-1]
        return texto

    # 3. Parsing e Adição ao Grafo
    classe_atual_uri = None
    for linha in linhas:
        linha = linha.strip()
        if linha.startswith("Classe:"):
            # Extraímos apenas o nome (ex: 'Contrato') e forçamos no BASE_NS
            nome_limpo = extrair_apenas_nome_final(linha.split("Classe:")[1])
            classe_atual_uri = BASE_NS[nome_limpo]
            g.add((classe_atual_uri, RDF.type, OWL.Class))
            
        elif linha.startswith("-") and classe_atual_uri:
            nome_prop_limpo = extrair_apenas_nome_final(linha.strip("- "))
            prop_uri = BASE_NS[nome_prop_limpo]
            g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            g.add((prop_uri, RDFS.domain, classe_atual_uri))

    # 4. Serialização com checagem de Prefixo
    # O format="turtle" deve agora obrigatoriamente usar base:
    source_onto = g.serialize(format="turtle")
    
    # Debug para você ver no console o que está acontecendo
    print(f"--- DEBUG ---")
    print(f"URI Base usada para bind: {uri_base}")
    print(f"Exemplo de Classe gerada: {classe_atual_uri}")
    
    # Salvamento
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, "source.owl")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(source_onto)
        
    return source_onto


def extract_class_info(ontology) -> Dict[str, str]:
    """Extrai classes com suas propriedades para gerar um texto rico para o encoder"""
    class_info = {}

    for cls in ontology.classes():
        data_props = []
        obj_props = []

        # pega data properties usadas pela classe
        for prop in ontology.data_properties():
            if cls in prop.domain:
                data_props.append(prop.name)

        # pega object properties usadas pela classe
        for prop in ontology.object_properties():
            if cls in prop.domain:
                obj_props.append(prop.name)

        info_text = f"{cls.name}. DataProps: {', '.join(data_props)}. ObjProps: {', '.join(obj_props)}"
        class_info[cls.name] = info_text

    return class_info

@tool
def match_ontologies_tool(src_ontology: str, target_ontology: str):
    """Gera o match entre classes considerando propriedades de cada classe"""

    # ---------- 1) Carrega ontologias ----------
    onto_src = get_ontology(src_ontology).load()
    onto_tgt = get_ontology(target_ontology).load()

    # ---------- 2) Extrai propriedades e cria textos ricos ----------
    src_text = extract_class_info(onto_src)
    tgt_text = extract_class_info(onto_tgt)

    # ---------- 3) Monta entrada do SBERT ----------
    encoder_input = [{"source": s, "target": t}
                     for s in src_text.keys() for t in tgt_text.keys()]

    # Ajustando o encoder para trabalhar com nosso texto enriquecido
    encoder = ConceptParentLightweightEncoder()
    enriched_data = []
    for pair in encoder_input:
        enriched_data.append({
            "source": src_text[pair["source"]],
            "target": tgt_text[pair["target"]]
        })

    # ---------- 4) Matching com SBERT ----------
    sbert = SBERTRetrieval(device="cpu", top_k=3)
    sbert.load(path="all-MiniLM-L6-v2")
    matches = sbert.generate(input_data=enriched_data)

    results = []
    for entry in matches:
        best_idx = entry["score-cands"].index(max(entry["score-cands"]))
        results.append({
            "source": entry["source"],
            "target_best": entry["target-cands"][best_idx],
            "score": entry["score-cands"][best_idx]
        })

    return results



# --- 3. AGENTE AJUSTADO ---
align_agent = Agent(
    role="Executor de Ferramentas e Alinhamento",
    goal="Executar a conversão SVO para OWL e, em seguida, usar a ferramenta de matching entre as ontologias Source e Target.",
    backstory="Você é um especialista em processamento de ontologias. Sua função principal é invocar ferramentas, garantindo que a saída de uma sirva como entrada para a próxima.",

    verbose=True,
    llm=llm
)


# --- 4. TAREFAS AJUSTADAS PARA O FLUXO SEQUENCIAL ---
# Fluxo: SVO (input inicial) -> OWL -> Match

# Etapa 1: Conversão SVO -> OWL
regenerating_owl_task = Task(
    description=f"""
        **CONVERSÃO (SVO para OWL):**
        Utilize a ferramenta `regenerate_owl_tool` para converter a ontologia fornecida como entrada (`{{svo_atual}}`)
        em um formato OWL Turtle (.ttl) válido. 
        O Agente DEVE apenas retornar a saída da ferramenta.
    """,
    agent=align_agent,
    tools=[regenerate_owl_tool], # As tools DEVEM ser passadas para o Agent
    expected_output="A representação completa e validada da ontologia em formato OWL Turtle (.ttl).",
    context=None # Não precisa de context, usa o input inicial
)

# Etapa 2: Matching de Ontologias
match_ontologies_task = Task(
    description="""
        **MATCHING (OWL Source vs. OWL Target):**
        Utilize a ferramenta `match_ontologies_tool`. A entrada para esta ferramenta 
        DEVE ser a **saída (o OWL Turtle) da tarefa anterior**.
        Seu objetivo é gerar uma lista JSON dos alinhamentos entre as classes e propriedades.
    """,
    agent=align_agent,
    tools=[match_ontologies_tool],
    expected_output="Uma lista concisa e estruturada em formato JSON dos alinhamentos encontrados, detalhando a entidade source, a entidade target e o score de confiança para cada match.",
    context=[regenerating_owl_task] # Define que esta tarefa depende da anterior
)


# --- 5. CREW E EXECUÇÃO ---

rag_unit = Crew(
    agents=[align_agent],
    # Ordem das tarefas: 1. Conversão (OWL) -> 2. Matching
    tasks=[regenerating_owl_task, match_ontologies_task], 
    process=Process.sequential,
    manager=llm,
    verbose=True,
    output_log_file="logs.txt",
)

if __name__ == "__main__":
    # Obtém o SVO inicial (simulando a sua função 'get_current_svo')
    svo_input = get_svo() 

    print("--- INICIANDO RAG UNIT ---")
    
    # O 'svo_atual' é o input da PRIMEIRA tarefa
    result = rag_unit.kickoff(inputs={"svo_atual": svo_input})

    print("\n--- PROCESSO FINALIZADO ---")
    print(result)

