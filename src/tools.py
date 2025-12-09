import csv
import pandas as pd
from crewai.tools import tool

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
	

######################################################
################## INTEGRATION TEAM ##################
######################################################





####################################################
################## FUSION TEAM #####################
####################################################
