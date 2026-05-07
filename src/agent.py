import json
from langchain_google_genai import ChatGoogleGenerativeAI

class MedAgente:
    def __init__(self):
        # Carga de datos
        with open('hospitales.json', 'r' , encoding="utf-8") as f:
            self.datos_salud = json.load(f)
        
        self.llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")

    def obtener_respuesta(self, consulta_usuario):
            # Construcción del prompt con el contexto
            contexto = f"""
            Eres un 'Asistente de Seguros Médicos' experto y empático. 
            Tu misión es ayudar al usuario a encontrar la especialidad, el hospital y calcular su copago.

            DATOS DE LA ASEGURADORA:
            {json.dumps(self.datos_salud, indent=2)}

            REGLAS:
            1. Analiza el síntoma y sugiere la especialidad médica adecuada.
            2. Indica en qué hospital de la red puede atenderse.
            3. Si el usuario menciona su plan (Oro, Plata o Bronce), calcula el copago: 
            Costo Final = Costo Base del Hospital * (1 - Cobertura del Plan).
            4. Si no menciona el plan, pregúntale cuál tiene para darle el costo exacto.
            5. Sé breve, profesional y directo.
            """

            mensajes = [
                ("system", contexto),
                ("human", consulta_usuario)
            ]

            try:
                respuesta = self.llm.invoke(mensajes)
                
                # Si la respuesta es una lista 
                if isinstance(respuesta.content, list):
                    for item in respuesta.content:
                        if isinstance(item, dict) and 'text' in item:
                            return item['text']
                
                # Si ya es texto plano
                return respuesta.content
                
            except Exception as e:
                return f"Error en el motor de IA: {str(e)}"