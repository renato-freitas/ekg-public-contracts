import os
from crewai import LLM 
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llama3_groq = LLM(
   model="groq/llama-3.3-70b-versatile",
   temperature=0,
   api_key=GROQ_API_KEY
)