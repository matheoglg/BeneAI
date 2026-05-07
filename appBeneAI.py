import streamlit as st
import base64
import pandas as pd
import re
import folium

from streamlit_folium import st_folium
from dotenv import load_dotenv
from src.agent import MedAgente

# Cargar la API
load_dotenv()

st.set_page_config(
    page_title="BeneAI - Asistente Médico Inteligente", 
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

local_css("style.css")

st.markdown("""
    <div class="custom-header">
        <div class="logo-text">BeneAI</div>
        <div style="color: white; font-size: 0.9rem; opacity: 0.7;">
            Dashboard 
        </div>
        
    </div>
    <div style="margin-top: 80px;"></div>
""", unsafe_allow_html=True)

if "agente" not in st.session_state:
    st.session_state.agente = MedAgente()

if "messages" not in st.session_state:
    st.session_state.messages = []

col_chat, col_map = st.columns([1, 1.2], gap="large")

with col_chat:
    chat_box = st.container(height=650, border=False)
    
    with chat_box:
        # Bienvenida
        if not st.session_state.messages:
            st.markdown("""
                <div class="chat-bubble ai-bubble">
                    ¡Hola! Soy <b>BeneAI</b>, tu guía inteligente de salud. ¿En qué puedo ayudarte hoy?
                </div>
            """, unsafe_allow_html=True)

        # Variables auxiliares
        if "esperando_respuesta" not in st.session_state:
            st.session_state.esperando_respuesta = False

        @st.cache_data
        def cargar_aseguradoras():
            try:
                return pd.read_csv("data/aseguradoras.csv", sep=";")['nombre'].tolist()
            except Exception:
                return []
                
        lista_aseguradoras = cargar_aseguradoras()

        st.session_state.hospitales_recomendados = []
        for i, message in enumerate(st.session_state.messages):
            role_class = "user-bubble" if message["role"] == "user" else "ai-bubble"
            
            content = message["content"]
            
            pedir_seguro = False
            if "[PEDIR_SEGURO]" in content:
                pedir_seguro = True
                content = content.replace("[PEDIR_SEGURO]", "").strip()

            map_match = re.search(r'\[MAPA:\s*([^\]]+)\]', content)
            if map_match:
                try:
                    ids_str = map_match.group(1)
                    st.session_state.hospitales_recomendados = [int(x.strip()) for x in ids_str.split(',')]
                except Exception:
                    pass
                content = re.sub(r'\[MAPA:[^\]]+\]', '', content).strip()

            # Detectar recomendación
            if "RECOMENDACIÓN" in content.upper() or "ACCION RECOMENDADA" in content.upper():
                 st.markdown(f"""
                    <div class="recommendation-card">
                        <span class="urgency-badge">Acción Recomendada</span>
                        <div style="margin-top:10px;">{content}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble {role_class}">{content}</div>', unsafe_allow_html=True)
                
            if pedir_seguro and i == len(st.session_state.messages) - 1:
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2 = st.columns([3, 1])
                with col1:
                    aseg_elegida = st.selectbox("Selecciona tu aseguradora:", ["No estoy seguro / Ninguna"] + lista_aseguradoras, label_visibility="collapsed")
                with col2:
                    if st.button("Confirmar", use_container_width=True):
                        if aseg_elegida == "No estoy seguro / Ninguna":
                            texto = "No tengo aseguradora o no estoy seguro."
                        else:
                            texto = f"Pertenezco a {aseg_elegida}."
                        st.session_state.messages.append({"role": "user", "content": texto})
                        st.session_state.esperando_respuesta = True
                        st.rerun()

    if st.session_state.esperando_respuesta:
        st.session_state.esperando_respuesta = False
        last_msg = st.session_state.messages[-1]["content"]
        with st.spinner("BeneAI está analizando..."):
            respuesta = st.session_state.agente.obtener_respuesta(last_msg, [])
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        st.rerun()
    elif prompt := st.chat_input("Describe tus síntomas o pregunta por cobertura..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("BeneAI está analizando..."):
            respuesta = st.session_state.agente.obtener_respuesta(prompt, [])
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        
        st.rerun()

with col_map:
    # Cargar datos de hospitales
    @st.cache_data
    def cargar_datos_mapa():
        try:
            df = pd.read_csv("data/hospitales.csv", sep=";")
            df = df.dropna(subset=['lat', 'lng'])
            df['lat'] = df['lat'].apply(lambda x: x/10 if x < -20 else x)
            df['lon'] = df['lng'].apply(lambda x: x/10 if x < -100 else x)
            df = df[['hospital_id', 'Hospital/Clinica', 'direccion', 'lat', 'lon']]
            
            try:
                df_pub = pd.read_csv("data/hospitales_guayaquil_final.csv", sep=";")
                df_pub = df_pub[df_pub['Institucion'].isin(['MSP', 'IESS'])]
                df_pub = df_pub.dropna(subset=['y', 'x']).copy()
                df_pub['lat'] = df_pub['y'].astype(str).str.replace(',', '.').astype(float)
                df_pub['lon'] = df_pub['x'].astype(str).str.replace(',', '.').astype(float)
                df_pub['hospital_id'] = [100 + idx for idx in df_pub.index]
                df_pub['Hospital/Clinica'] = df_pub['Nombre']
                df_pub['direccion'] = df_pub['Direccion']
                df_pub = df_pub[['hospital_id', 'Hospital/Clinica', 'direccion', 'lat', 'lon']]
                
                return pd.concat([df, df_pub], ignore_index=True)
            except Exception:
                return df
                
        except Exception as e:
            st.error(f"Error cargando mapa: {e}")
            return pd.DataFrame()

    df_hospitales = cargar_datos_mapa()
    
    recomendados = st.session_state.get('hospitales_recomendados', [])
    if recomendados and not df_hospitales.empty:
        df_filtrado = df_hospitales[df_hospitales['hospital_id'].isin(recomendados)]
        if not df_filtrado.empty:
            df_hospitales = df_filtrado

    if not df_hospitales.empty:
        center_lat = df_hospitales['lat'].mean()
        center_lon = df_hospitales['lon'].mean()
        zoom = 14 if recomendados else 12
    else:
        center_lat, center_lon = -2.189, -79.889
        zoom = 12
    
    # Crear mapa con Folium (OpenStreetMap) centrado dinámicamente
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom)
    
    # Añadir marcadores de hospitales
    if not df_hospitales.empty:
        for idx, row in df_hospitales.iterrows():
            popup_html = f"<b>{row.get('Hospital/Clinica', 'Hospital')}</b><br>{row.get('direccion', '')}"
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=row.get('Hospital/Clinica', 'Hospital'),
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)

    # Mostrar el mapa en Streamlit
    st_folium(m, height=500, use_container_width=True, returned_objects=[])
