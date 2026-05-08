BeneAI - Asistente Médico Inteligente (Ecuador)

BeneAI es un asistente conversacional avanzado diseñado para guiar a los usuarios 
en el sistema de salud de Ecuador, específicamente en la ciudad de Guayaquil. Utiliza 
inteligencia de Google (Gemini) para analizar síntomas, 
recomendar especialidades médicas, sugerir centros de salud (públicos y privados) y 
estimar copagos de seguros médicos.


Características Principales

Análisis de Síntomas: Identificación de la especialidad médica adecuada basada en la descripción del usuario.
Recomendación de Centros: Derivación inteligente a hospitales privados (según aseguradora) o centros de la red pública (MSP/IESS).
Cálculo de Copagos: Estimación de costos basada en planes de seguros y tipos de atención.
Mapa Interactivo: Visualización geográfica de centros recomendados con integración a Google Maps para navegación.
Interfaz Fluida: Chat en tiempo real con renderizado inmediato de mensajes.


Estructura del Proyecto

BeneAI/
├── data/               # Archivos CSV con la base de datos (hospitales, planes, etc.)

├── src/

│   └── agent.py        # Lógica del Agente de IA y conexión con Gemini

├── appBeneAI.py        # Interfaz de usuario con Streamlit

├── style.css           # Estilos personalizados para el chat y el mapa

├── requirements.txt    # Dependencias de Python

└── .env                # Variables de entorno (API Key)


Instalación y Configuración

Clone el repositorio: git clone [URL_DEL_REPO]

Instale las dependencias: pip install -r requirements.txt

Configure su API Key de Google Gemini en un archivo .env: GOOGLE_API_KEY=tu_api_key_aqui

Ejecute la aplicación en el terminal: streamlit run appBeneAI.py



