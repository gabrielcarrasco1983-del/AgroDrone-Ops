import streamlit as st
import pandas as pd
import math

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO PROFESIONAL ---
st.set_page_config(page_title="AgroDosis - Precisión Aérea", page_icon="🛸", layout="wide")

# CSS para inyectar un diseño de "App Nativa"
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .main-header { color: #1e4d2b; font-size: 2.5rem; font-weight: bold; text-align: center; margin-bottom: 0; }
    .sub-header { color: #666; text-align: center; margin-bottom: 2rem; }
    .result-card { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 8px solid #2D5A27;
    }
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        background-color: #2D5A27;
        color: white;
        font-weight: bold;
        height: 3em;
        border: none;
    }
    .stMetric { background-color: #fff; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BASE DE DATOS ACTUALIZADA (VADEMÉCUM) ---
# He añadido los datos específicos del PDF de Nutrien [cite: 43, 47]
fitos_db = {
    "Glifosato 480 SL (Nutrien)": {
        "min": 1.5, "max": 10.0, "unidad": "L/ha", 
        "alerta": "No aplicar más de 15 kg/año. Evitar lluvias 48-72h posteriores.",
        "orden": "Líquidos Solubles (SL)"
    },
    "Atrazina": {"min": 0.5, "max": 3.0, "unidad": "kg/ha", "alerta": "Persistente en suelos.", "orden": "Sólidos Secos"},
    "2,4-D": {"min": 0.5, "max": 1.5, "unidad": "L/ha", "alerta": "Alta volatilidad. Cuidado con deriva.", "orden": "Emulsiones (EC)"}
}

# --- 3. ENCABEZADO ---
st.markdown('<p class="main-header">🛸 AgroDosis</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Cálculo de Pulverización y Consultoría Técnica</p>', unsafe_allow_html=True)

# --- 4. SISTEMA DE PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["💧 Calculadora de Caldo", "📖 Vademécum IA", "🛰️ Clima y Vuelo"])

with tab1:
    col_in, col_out = st.columns([1, 1], gap="large")
    
    with col_in:
        st.subheader("⚙️ Parámetros de Trabajo")
        lote_ha = st.number_input("Superficie del Lote (ha)", value=10.0, step=1.0)
        tasa_dron = st.number_input("Tasa de Aplicación Dron (L/ha)", value=10.0, step=0.5)
        capacidad_mixer = st.selectbox("Capacidad del Mixer (L)", [100, 200, 300, 500, 1000])
        
        st.divider()
        st.subheader("🧪 Selección de Producto")
        producto_name = st.selectbox("Principio Activo", list(fitos_db.keys()))
        info = fitos_db[producto_name]
        
        dosis_user = st.slider(f"Dosis a aplicar ({info['unidad']})", 
                               float(info['min']), float(info['max']), float(info['min']))
        
        if dosis_user > 8.0 and "Glifosato" in producto_name:
             st.warning(f"⚠️ {info['alerta']}")

    with col_out:
        st.subheader("📊 Resultados de Aplicación")
        vol_total = lote_ha * tasa_dron
        prod_total = lote_ha * dosis_user
        cant_cargas = math.ceil(vol_total / capacidad_mixer)
        
        # Tarjeta de resultados inspirada en calculado.net
        st.markdown(f"""
            <div class="result-card">
                <h3 style='margin-top:0;'>Total Lote</h3>
                <p>Volumen de Caldo: <b>{vol_total:.1f} Litros</b></p>
                <p>Total {producto_name}: <b>{prod_total:.2f} {info['unidad'].split('/')[0]}</b></p>
                <hr>
                <h3>Logística</h3>
                <p>Cantidad de Cargas: <b>{cant_cargas} cargas</b> de mixer</p>
                <p>Orden de mezcla: <b>{info['orden']}</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        if st.button("📥 Generar Reporte de Aplicación"):
            st.success("Reporte generado con éxito (Simulado)")

with tab2:
    st.subheader("🤖 Consultor Agronómico IA")
    pregunta = st.text_input("Pregunta sobre mezclas, boquillas o condiciones...")
    if pregunta:
        st.info(f"Análisis para: '{pregunta}'... (Aquí conectaremos tu API Key de OpenAI/Gemini)")

with tab3:
    st.subheader("🛰️ Telemetría y Seguridad de Vuelo")
    c1, c2, c3 = st.columns(3)
    c1.metric("Viento", "12 km/h", "Ideal")
    c2.metric("Índice KP", "2", "Óptimo")
    c3.metric("Delta T", "4.2", "Seguro")