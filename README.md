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


Información sobre database

La base de datos de BeneAI se ha construido mediante un proceso de curación y estructuración de datos abiertos y catálogos de servicios públicos y privados en Ecuador.

Se llevó a cabo un proceso de Minería de Datos y ETL (Extraer, Transformar y Cargar) para normalizar la información dispersa, enriquecer las coordenadas geográficas mediante geocodificación y estandarizar las especialidades médicas para que fueran procesables por el modelo de IA.

Se adjunta los links de los sitios respectivos:

https://www.saludsa.com/personas/todos-los-planes-medicos

https://www.bmicos.com/ecuador/categoria-producto/bmi-del-ecuador/planes-vida/

https://latinasalud.com.ec/producto-individual-familiar/

https://latinasalud.com.ec/productos-pyme/

https://latinasalud.com.ec/productos-corporativos/

https://www.mediken.com.ec/

https://elyex.com/clinicas-hospitales-y-centros-medicos-en-guayaquil/

https://www.guiamedicos.net/public/especialidades/clinicas/clinica-san-francisco

https://www.edina.com.ec/clinicas-hospitales-y-centros-medicos/hospital-clinica-kennedy/guayaquil/2061/9/238

https://www.doctoranytime.ec/h/hospital-clinica-kennedy-alborada

https://www.paginas-amarillas.com.ec/empresas/hospital-clinica-panamericana-sa-hosclipa/guayaquil-30916568?ad=51064757

https://www.salud.gob.ec/el-hospital-de-especialidades-guayaquil-dr-abel-gilbert-ponton-trabaja-en-el-fortalecimiento-de-la-calidad-de-sus-servicios/

http://www.estadisticas.med.ec/webpages/contactenos.jsp

https://www.salud.gob.ec/ministra-de-salud-visito-instalaciones-del-hospital-leon-becerra-de-guayaquil/

https://www.waze.com/es-419/live-map/directions/hospital-leon-becerra-av.-eloy-alfaro-delgado-2410-guayaquil?to=place.w.183568114.1835746675.291131

https://es.angels-initiative.com/organizations/hospital-de-especialidades-guayaquil-dr-abel-gilbert-ponton

https://www.iess.gob.ec/documents/10162/3321619/PMF+HOSPITAL+TEODORO+MALDONADO+CARBO.pdf

https://ec.linkedin.com/company/hospital-cl%C3%ADnica-san-francisco-de-guayaquil

https://aprofe.org.ec/paginas/ver/16

Asimismo se procesó un archivo csv con información de más de 100 hospitales en la ciudad de Guayaquil, algunos datos pueden estar sujetos a ser solo de prueba, no representan un valor real o significativo en el sistema de salud de la ciudad.


