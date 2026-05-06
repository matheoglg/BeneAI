import streamlit as st
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# 1. Configuración Inicial
load_dotenv() # Carga tu API KEY desde el archivo .env
st.set_page_config(page_title="Bene AI", page_icon="🏥")

# 2. Carga de Datos (RAG Simple)
with open('hospitales.json', 'r') as f:
    datos_salud = json.load(f)

# 3. Inicializar el Modelo (Gratis con Google API)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

# 4. Interfaz de Usuario con Streamlit
st.title("🏥 Estimador de Copago y Cobertura")
st.markdown("Describe tus síntomas y te ayudaremos a encontrar la mejor opción.")

# Estado de la sesión para el chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("Ej: Me duele mucho el pecho y tengo el plan Oro"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 5. Lógica del Agente
    with st.chat_message("assistant"):
        # Construimos un contexto para la IA con los datos del JSON
        contexto = f"""
        Eres un asistente de seguros. Usa estos datos para responder:
        Planes y Coberturas: {datos_salud['planes']}
        Red Hospitalaria: {datos_salud['red_hospitalaria']}
        
        Instrucciones:
        1. Identifica la especialidad necesaria según el síntoma.
        2. Busca el hospital que tenga esa especialidad.
        3. Si el usuario menciona su plan, calcula el copago: Costo Base * (1 - Cobertura).
        4. Responde de forma amable y profesional.
        """
        
        # Llamada a la IA
        response = llm.invoke([
            ("system", contexto),
            ("human", prompt)
        ])
        
        st.markdown(response.content)
        st.session_state.messages.append({"role": "assistant", "content": response.content})