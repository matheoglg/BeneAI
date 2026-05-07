import streamlit as st
from dotenv import load_dotenv
from src.agent import MedAgente

# Cargar la API
load_dotenv()

st.set_page_config(page_title="Asistente Médico IA", page_icon="🏥")

st.title("🏥 Estimador de Copago y Cobertura")
st.markdown("Consulta tus síntomas y descubre tu cobertura al instante.")

# Inicializar el agente en la sesión para que no se recargue innecesariamente
if "agente" not in st.session_state:
    st.session_state.agente = MedAgente()

# Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar con información útil
with st.sidebar:
    st.header("Red Médica")
    st.info("Consulta los hospitales disponibles y especialidades.")
    for hosp in st.session_state.agente.datos_salud['red_hospitalaria']:
        st.write(f"📍 **{hosp['nombre']}**")
        st.caption(f"Especialidades: {', '.join(hosp['especialidades'])}")

# Mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("Ej: Tengo dolor de espalda y mi plan es Plata"):
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar y mostrar respuesta del agente
    with st.chat_message("assistant"):
        with st.spinner("Consultando red médica..."):
            respuesta = st.session_state.agente.obtener_respuesta(prompt)
            st.markdown(respuesta)
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})