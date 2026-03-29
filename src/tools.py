import os
import csv, json
import pandas as pd
from crewai.tools import tool
import morph_kgc

####################################################
################## PUBLISING TEAM ##################
####################################################

def _get_col_dtype(col:pd.Series):
	"""
	Infer datatype of a pandas column, process only if the column dtype is object. 
	input:   col: a pandas Series representing a df column. 
	"""
	if col.dtype == "object":
		try:
			col_new = pd.to_datetime(col.dropna().unique())
			return col_new.dtype
		except:
			try:
				col_new = pd.to_numeric(col.dropna().unique())
				return col_new.dtype
			except:
				try:
					col_new = pd.to_timedelta(col.dropna().unique())
					return col_new.dtype
				except:
					return "object"
	else:
		return col.dtype
	

def detect_csv_separetor(csv_file_path):
	count = 0
	lines = ""
	with open(csv_file_path, "r") as csv_file:
		for row in csv_file:
			lines += str(row)
			count += 1
			if count == 1:
				break
	sniffer = csv.Sniffer()
	return sniffer.sniff(lines, delimiters=[",", ";", "\t", "|"]).delimiter

@tool
def get_data_schema_from_csv(csv_path:str):
	"""Usefull for extract the schema of CSV file"""
	try:
		csv_path = "D:\Doutorado\datasets\contratos\csv_contratos_cgu\contratos_160051.csv"
		csv_separetor = detect_csv_separetor(csv_path)

		df = pd.read_csv(csv_path, sep=csv_separetor)
		df = df.head(5)
		return [{
			"name": f"{col}", 
			"dtype": f"{_get_col_dtype(df[col])}",
			"isActive": False
		} for col in df.dtypes.index]
		
	except Exception as e:
		print('+ error:', e)
		raise Exception(f"Error reading CSV: {e}")
	

def load_json_data(filename:str):
	"""Retrieve schema whose fields are active

	Paremeters
	---
	filename
		name of file with path

	Returns
	---
	filtered_data
		schema with active fields
	"""
	module_dir = os.path.dirname(__file__)
	filepath = os.path.join(module_dir, filename)
	
	try:
		with open(filepath, 'r') as f:
			data = json.load(f)
			filtered_data = [item for item in data if item.get("isActive") == True]
		return str(filtered_data)
	except FileNotFoundError:
		print(f"Error: JSON file '{filename}' not found at '{filepath}'")
		return None
	except json.JSONDecodeError:
		print(f"Error: Invalid JSON format in '{filename}'")
		return None
	
def get_ontology_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # We pass the raw JSON so the LLM has full access to metadata
        return json.dumps(data, indent=2, ensure_ascii=False)

@tool("morph_kgc_tool")
def morph_kgc_tool(mapping_path: str, data_path: str, output_path: str):
    """
    Executa o Morph-KGC para triplificação. 
    mapping_path: Caminho para o arquivo .ttl gerado pelo MapGen.
    data_path: Caminho para o arquivo de dados (ex: .csv).
    output_path: Caminho onde o arquivo .nt será salvo.
    """
    config_setup = f"""
    [CONFIGURATION]
    output_format: N-TRIPLES
    [DataSource1]
    mappings: {mapping_path}
    file_path: {data_path}
    """
    resultado = morph_kgc.materialize(config_setup)
    try:
        #resultado = morph_kgc.materialize(config_setup)
        #resultado.serialize(destination="resultado_final1.nt", format="nt")
        # Lógica de salvamento que você validou
        if hasattr(resultado, 'serialize'):
            resultado.serialize(destination=output_path, format="nt")
        else:
            with open(output_path, "w", encoding="utf-8") as f:
                for content in resultado.values():
                    f.write(content)
        
        return f"Sucesso! O arquivo RDF foi criado fisicamente em: {os.path.abspath(output_path)}"
    except Exception as e:
        return f"Erro durante a execução do Morph-KGC: {str(e)}"	
######################################################
################## INTEGRATION TEAM ##################
######################################################





####################################################
################## FUSION TEAM #####################
####################################################
