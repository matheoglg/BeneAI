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
    st.title("📊 Red de Guayaquil")
    st.write(f"Total centros: {len(st.session_state.agente.df)}")
    
    # Buscador rápido
    zona = st.selectbox("Explorar por Parroquia:", ["Seleccionar..."] + list(st.session_state.agente.df['Parroquia'].unique()))
    if zona != "Seleccionar...":
        resumen = st.session_state.agente.df[st.session_state.agente.df['Parroquia'] == zona]
        st.dataframe(resumen[['Nombre', 'Institucion', 'costo_consulta']], hide_index=True)

    if st.button("Reiniciar Chat"):
        st.session_state.messages = []
        st.session_state.agente.historial = []
        st.rerun()

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

# --- MAPA DE COBERTURA ---
st.divider()
st.subheader("📍 Mapa de Establecimientos en Guayaquil")
# Preparamos las coordenadas para st.map (Streamlit necesita columnas lat y lon)
map_df = st.session_state.agente.df[['y', 'x']].copy().dropna()
map_df.columns = ['lat', 'lon']
st.map(map_df)

# Limpia la memoria del agente
with st.sidebar:
    if st.button("Reiniciar Conversación"):
        st.session_state.messages = []
        st.session_state.agente.historial = []  
        st.rerun()