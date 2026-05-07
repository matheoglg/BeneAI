import pandas as pd
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

class MedAgente:
    def __init__(self):
        # Carga de datos
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ruta_csv = os.path.join(base_path, "data", "hospitales_guayaquil_final.csv")
        
        self.df = pd.read_csv(ruta_csv, sep=';', encoding='utf-8', decimal=',')
        
        self.llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")

        # Para memoria
        self.historial = []

    def obtener_respuesta(self, consulta_usuario):
            #Filtrado    
            consulta_lower = consulta_usuario.lower()
            parroquias_en_db = self.df['Parroquia'].unique()

            #Hablo de una parroquia antes?
            parroquia_detectada = None
            for p in parroquias_en_db:
                if str(p).lower() in consulta_lower:
                    parroquia_detectada = p
                    break
            
            if parroquia_detectada:
                contexto_df = self.df[self.df['Parroquia'] == parroquia_detectada]
                # También añadimos los 5 más baratos de toda la ciudad como opción de ahorro
                ahorro_df = self.df.nsmallest(5, 'costo_consulta')
                df_final = pd.concat([contexto_df, ahorro_df]).drop_duplicates()
            else:
                df_final = self.df.sample(15) # Muestra aleatoria si no hay zona definida

            contexto_datos = df_final.to_string(index=False)
            
            # Construcción del prompt con el contexto
            contexto = f"""
            Eres 'BeneAI', un asistente experto en salud para Guayaquil y la provincia del Guayas.
            Tu objetivo es recomendar la mejor opción de salud usando estos datos reales:
            {contexto_datos}

            REGLAS DE DECISIÓN CRÍTICAS:
            1. ¿EMERGENCIA?: Si el usuario tiene síntomas graves (de vida o muerte), recomienda el hospital MÁS CERCANO (misma Parroquia) sin importar el costo.
            2. COSTO VS DISTANCIA: Si no es emergencia, ofrece el más cercano PERO menciona si hay uno mucho más barato en otra parroquia (ahorro),
            menciona de ser posible otras opciones dentro de la misma parroquia priorizando el copago.
            3. AFILIACIÓN (MSP/IESS/ISSFA): Pregunta siempre "¿Eres afiliado o ciudadano ecuatoriano?". 
            - Si SÍ: En hospitales públicos (Institucion = MSP, IESS, FUERZAS ARMADAS, SNAI, POLICIA NACIONAL), el costo es $0 (Gratis por ley).
            - Si NO: Se aplica el 'costo_consulta' del tarifario.
            4. SEGUROS PRIVADOS (Oro, Plata, Bronce): 
            - Solo aplican en Instituciones PRIVADAS o Junta de Beneficencia.
            - Coberturas: Oro (90%), Plata (70%), Bronce (50%).
            - Cálculo: Pago = costo_consulta * (1 - Cobertura).
            5. ESTILO: Sé empático, usa términos de Guayaquil si es natural y ve directo al punto.
            6. MEMORIA: Recuerda los datos que te digan, a no ser que el usuario decida cambiarlos,
            si es afiliado al IESS y te pregunta por un hospital afiliado al SNAI, recuérdale que
            tendrá que pagar el valor completo en lugar de cero.
            """

            # Historial para evitar repeticiones
            mensajes = [
                ("system", contexto),
            ]
            
            for msg in self.historial[-4:]:
                if isinstance(msg, HumanMessage):
                    mensajes.append(("human", msg.content))
                elif isinstance(msg, AIMessage):
                    mensajes.append(("ai", msg.content))

            mensajes.append(("human", consulta_usuario))

            try:
                respuesta = self.llm.invoke(mensajes)
                
                # Si la respuesta es una lista
                contenido = ""
                if isinstance(respuesta.content, list):
                    for item in respuesta.content:
                        if isinstance(item, dict) and 'text' in item:
                            contenido = item['text']
                            break;
                
                else:
                    contenido = respuesta.content

                # Guardar historial de la conversación
                self.historial.append(HumanMessage(content=consulta_usuario))
                self.historial.append(AIMessage(content=contenido))
                
                # Si ya es texto plano
                return contenido
                            
            except Exception as e:
                return f"Error en el motor de IA: {str(e)}"