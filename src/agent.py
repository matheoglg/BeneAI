import json
import pandas as pd
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

class MedAgente:
    def __init__(self):
        # Carga de datos
        # Carga de datos
        try:
            self.df_hospitales = pd.read_csv("data/hospitales.csv", sep=";")
            self.df_aseguradoras = pd.read_csv("data/aseguradoras.csv", sep=";")
            self.df_planes = pd.read_csv("data/planes.csv", sep=";")
            self.df_diccionario = pd.read_csv("data/diccionario.csv", sep=";", header=None, names=['especialidad', 'k'])
            self.df_especialidades = pd.read_csv("data/especialidades.csv", sep=";")
            self.df_publicos = pd.read_csv("data/hospitales_guayaquil_final.csv", sep=";")
        except Exception as e:
            print(f"Error cargando CSVs: {e}")
            self.df_hospitales = pd.DataFrame()
            self.df_aseguradoras = pd.DataFrame()
            self.df_planes = pd.DataFrame()
            self.df_diccionario = pd.DataFrame()
            self.df_especialidades = pd.DataFrame()
            self.df_publicos = pd.DataFrame()
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite"
        )

        # Para memoria
        self.historial = []

    def _preparar_contexto(self, aseguradoras):
        contexto_aseg = ""
        if aseguradoras:
            contexto_aseg = "Aseguradoras del usuario:\n"
            for aseg in aseguradoras:
                try:
                    aseg_id = self.df_aseguradoras[self.df_aseguradoras['nombre'] == aseg]['aseguradora_id'].values[0]
                    planes_aseg = self.df_planes[self.df_planes['aseguradora_id'] == aseg_id]
                    planes_str = ", ".join(planes_aseg['nombre_plan'].tolist())
                    contexto_aseg += f"- {aseg}: Planes disponibles -> {planes_str}\n"
                except Exception:
                    pass
        else:
            contexto_aseg = "El usuario no ha seleccionado ninguna aseguradora aún. Muestra las disponibles y pídele que seleccione en el menú lateral."

        hosp_dict = []
        if not self.df_hospitales.empty:
            hosp_dict = self.df_hospitales[['hospital_id', 'Hospital/Clinica', 'ciudad']].to_dict('records')
        
        dic_esp = {}
        if not self.df_diccionario.empty:
            dic_esp = dict(zip(self.df_diccionario['k'], self.df_diccionario['especialidad']))
        
        hosp_especialidades = {}
        if not self.df_especialidades.empty:
            for _, row in self.df_especialidades.iterrows():
                h_id = row['hospital_id']
                esp_list = []
                for k_val, nombre_esp in dic_esp.items():
                    if pd.notna(row.get(k_val)) and str(row.get(k_val)).strip() == '1*':
                        esp_list.append(nombre_esp)
                hosp_especialidades[h_id] = esp_list

        hosp_info = []
        for h in hosp_dict:
            esp = hosp_especialidades.get(h['hospital_id'], [])
            hosp_info.append({
                "ID": h['hospital_id'],
                "Nombre": h['Hospital/Clinica'],
                "Especialidades": esp
            })
            
        lista_aseg = []
        if not self.df_aseguradoras.empty:
            lista_aseg = self.df_aseguradoras['nombre'].tolist()

        hosp_publicos_info = []
        if getattr(self, 'df_publicos', None) is not None and not self.df_publicos.empty:
            df_pub = self.df_publicos[self.df_publicos['Institucion'].isin(['MSP', 'IESS'])].copy()
            for idx, row in df_pub.iterrows():
                hosp_publicos_info.append({
                    "ID": 100 + idx,
                    "Nombre": row.get('Nombre', ''),
                    "Nivel": row.get('Nivel', ''),
                    "Institucion": row.get('Institucion', ''),
                    "Servicios": str(row.get('servicios', '')),
                })

        return f"""
        {contexto_aseg}
        
        RED PRIVADA/ESPECIALIZADA (Para seguros privados o cirugías mayores):
        {json.dumps(hosp_info, indent=2)}
        
        RED PÚBLICA / CENTROS DE SALUD (Si no tiene seguro, si es MSP/IESS, o requiere servicios generales. Es Gratuito):
        {json.dumps(hosp_publicos_info, indent=2)}
        
        LISTA DE ASEGURADORAS DISPONIBLES:
        {json.dumps(lista_aseg)}
        """


    def obtener_respuesta(self, consulta_usuario, aseguradoras=[]):
            datos_contexto = self._preparar_contexto(aseguradoras)
            
            contexto = f"""
            Eres un 'Asistente de Seguros Médicos' experto de Ecuador, empático y respondes con calidez y preocupación genuina.
            Tu misión es ayudar al usuario a encontrar la especialidad médica, el hospital y calcular su copago.
            
            DATOS DISPONIBLES:
            {datos_contexto}

            REGLAS ESTRICTAS:
            1. EMPATÍA: Si el usuario indica un dolor o malestar, tu primera respuesta DEBE mostrar preocupación ("Entiendo cómo te sientes...", "Lamento mucho que tengas ese dolor...").
            2. DIAGNÓSTICO: Analiza el síntoma y sugiere la especialidad médica adecuada.
            3. HOSPITALES Y DERIVACIÓN: 
               - Si el usuario NO tiene seguro, no tiene dinero, o menciona MSP/IESS, recomiéndale EXCLUSIVAMENTE opciones de la RED PÚBLICA e indícale que el costo es de $0 (Gratuito).
               - Si el usuario tiene un seguro privado (SaludSA, etc.), recomiéndale opciones de la RED PRIVADA/ESPECIALIZADA.
            4. ASEGURADORA Y PLANES: 
               - Si el usuario NO menciona su aseguradora y necesitas saberla para calcular el copago, pregúntale amablemente a cuál pertenece y DEBES añadir exactamente la etiqueta [PEDIR_SEGURO] al final de tu respuesta. Esto activará un botón en la interfaz.
               - Si el usuario YA mencionó su aseguradora (máximo 1), usa esa información para buscar el plan y darle el estimado del copago.
            5. COSTOS Y COPAGOS:
               - Costos Base (si no los conoces, usa estos por defecto): Medicina General: $40, Especialidad: $80, Emergencia: $100.
               - Si el plan se menciona o ya se sabe, calcula un descuento figurativo (ej. 80% cobertura) o usa la info real si aplica. Detalla el costo de la consulta menos el descuento = Copago a pagar.
            6. FORMATO DE TARJETA: Cuando des una recomendación médica o sugieras un hospital, inicia esa línea o párrafo exactamente con la palabra "RECOMENDACIÓN:" en mayúsculas para que el sistema lo resalte.
            7. MAPA DINÁMICO: Si en tu respuesta estás recomendando u ofreciendo opciones de hospitales específicos, DEBES incluir al final de todo tu mensaje la etiqueta [MAPA: id1, id2, ...] usando los IDs de esos hospitales (ej. [MAPA: 1, 3]). Si no recomiendas hospitales, no incluyas la etiqueta.
            8. Sé directo, claro y no agobies con demasiada información.
            """

            mensajes = [("system", contexto)]
            
            for msg in self.historial[-4:]:
                if isinstance(msg, HumanMessage):
                    mensajes.append(("human", msg.content))
                elif isinstance(msg, AIMessage):
                    mensajes.append(("ai", msg.content))

            mensajes.append(("human", consulta_usuario))

            try:
                respuesta = self.llm.invoke(mensajes)
                
                contenido = ""
                if isinstance(respuesta.content, list):
                    for item in respuesta.content:
                        if isinstance(item, dict) and 'text' in item:
                            contenido = item['text']
                            break
                else:
                    contenido = respuesta.content

                # Guardar en el historial interno la conversación limpia (sin el tag para el próximo prompt)
                contenido_limpio = contenido.replace("[PEDIR_SEGURO]", "").strip()
                contenido_limpio = re.sub(r'\[MAPA:[^\]]+\]', '', contenido_limpio).strip()
                self.historial.append(HumanMessage(content=consulta_usuario))
                self.historial.append(AIMessage(content=contenido_limpio))
                
                return contenido
                            
            except Exception as e:
                return f"Error en el motor de IA: {str(e)}"