import json
from langchain_google_genai import ChatGoogleGenerativeAI

class MedAgente:
    def __init__(self):
        # Carga de datos
        with open('hospitales.json', 'r' , encoding="utf-8") as f:
            self.datos_salud = json.load(f)
        
        self.llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")
