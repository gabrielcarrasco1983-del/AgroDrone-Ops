import streamlit as st
import pandas as pd
import math
import io
import requests 
from datetime import datetime

# --- CONFIGURACIÓN DE CLIMA y APIs ---
LATITUDE = -35.4485
LONGITUDE = -60.8876
OPENWEATHERMAP_API_KEY = "e07ff67318e1b5f6f5bde3dae5b35ec0" 

@st.cache_data(ttl=300)
def get_weather_data(lat, lon):
    if not OPENWEATHERMAP_API_KEY: return None
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=es"
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        temp_c = data['main']['temp'] 
        humidity_pc = data['main']['humidity'] 
        wind_kmh = data['wind']['speed'] * 3.6 
        weather_desc = data['weather'][0]['description'].capitalize()
        cloudiness_pc = data['clouds']['all'] 
        rain_prob = 70 if 'lluvia' in weather_desc.lower() or cloudiness_pc > 80 else (30 if cloudiness_pc > 50 else 0)
        return {
            "T_Actual": f"{temp_c:.1f} °C", "Humedad_Val": humidity_pc, "Humedad_Str": f"{humidity_pc} %",
            "Viento_Val": wind_kmh, "Viento_Str": f"{wind_kmh:.1f} km/h", "Descripcion": weather_desc,
            "Nubosidad_Str": f"{cloudiness_pc} %", "Lluvia_Str": f"{rain_prob} %", "Ciudad": data['name']
        }
    except: return None

# --- VADEMÉCUM DATA (Simplificado para el ejemplo, mantén el tuyo completo) ---
csv_data = """PRINCIPIO_ACTIVO;DOSIS_MARBETE_MIN;DOSIS_MARBETE_MAX;UNIDAD_DOSIS;FAMILIA_QUIMICA;TIPO_PREPARADO;ALERTA_COMPATIBILIDAD;ORDEN_MEZCLA
Glyphosate;0.25;1.5;L/ha;Glicina (EPSPS inhibitor);Herbicida;"Evitar pH alcalino, deriva";Medio
Paraquat (Diquat similar);0.5;2;L/ha;Bipiridilio;Herbicida;"Muy tóxico, restricciones";Temprano
Atrazine;0.5;3;kg/ha;Triazina (photosystem II inhibitor);Herbicida;"Persistente, cuidado en suelos arenosos";Temprano
""" # (AQUÍ DEBES PEGAR TODO EL CSV QUE TENÍAS)

vademecum = {}
productos_disponibles = []
try:
    df = pd.read_csv(io.StringIO(csv_data), sep=";")
    df = df.dropna(subset=['PRINCIPIO_ACTIVO']) 
    vademecum = df.set_index('PRINCIPIO_ACTIVO').T.to_dict('dict')
    productos_disponibles = sorted(list(vademecum.keys()))
except: pass

st.set_page_config(page_title="AgroDrone Ops", page_icon="favicon.png", layout="centered")

# CARGAR CSS EXTERNO
try:
    with open("style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except: pass

# --- CSS INTERNO PARA FORMATO PDF NUTRIEN ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    
    /* Clases para simular el PDF de Glifosato */
    .ficha-box { border: 1px solid #002A20; margin-top: 10px; }
    .ficha-titulo { background-color: #002A20; color: white; padding: 10px; font-weight: bold; text-align: center; }
    .seccion-gris { background-color: #F2F2F2; padding: 5px 10px; font-weight: bold; color: #002A20; border-top: 1px solid #002A20; }
    .contenido-blanco { padding: 10px; background-color: white; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚁 AgroDrone Ops")
st.write("Calculadora de Caldo y Vademécum Fitosanitario")

if 'num_productos' not in st.session_state: st.session_state.num_productos = 1
def add_product(): 
    if st.session_state.num_productos < 5: st.session_state.num_productos += 1

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧮 Calculadora Caldo", "⛽ Grupo Electrógeno", "📖 Vademécum", "☀️ Tiempo de Vuelo", "👤 Sobre la App"])

with tab1:
    st.header("Armado del Caldo (Mixer)")
    c1, c2 = st.columns(2)
    with c1: t_op = st.selectbox("Mixer [L]", ["100", "200", "300", "500", "Personalizado"])
    cap_mixer = int(t_op) if t_op != "Personalizado" else st.number_input("L", value=330)
    with c2: tasa_ap = st.number_input("Tasa Dron (L/ha)", value=10.0)
    
    ha_totales = st.number_input("Hectáreas Totales", value=20.0)
    st.subheader("Productos")
    prods_sel = []
    for i in range(st.session_state.num_productos):
        cols = st.columns([0.4, 0.3, 0.3])
        p_sel = cols[0].selectbox("Producto", ["Otro"] + productos_disponibles, key=f'p{i}')
        p_nom = p_sel if p_sel != "Otro" else cols[0].text_input("Nombre", key=f'pi{i}')
        uni = cols[1].selectbox("Unidad", ["L/ha", "kg/ha"], key=f'u{i}')
        ds = cols[2].number_input("Dosis", value=0.0, key=f'd{i}')
        if p_nom and ds > 0: prods_sel.append({'n': p_nom, 'u': uni, 'd': ds})
    
    if st.session_state.num_productos < 5: st.button("➕ Agregar", on_click=add_product)

    if prods_sel:
        st.markdown('<div class="ficha-box"><div class="ficha-titulo">RESULTADOS DE OPERACIÓN</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="seccion-gris">RESUMEN DEL LOTE: {ha_totales} HA</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="contenido-blanco"><b>Volumen Total:</b> {ha_totales*tasa_ap:.1f} L</div>', unsafe_allow_html=True)
        
        for p in prods_sel:
            total_p = ha_totales * p['d']
            st.markdown(f'<div class="seccion-gris">INSUMO: {p["n"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="contenido-blanco">Total Lote: {total_p:.2f} {p["u"]}<br>Dosis Mixer: {(cap_mixer/tasa_ap)*p["d"]:.2f} {p["u"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.header("📖 Vademécum Nutrien Style")
    busqueda = st.selectbox("Seleccione un Producto", [""] + productos_disponibles)
    if busqueda:
        d = vademecum[busqueda]
        # RECREACIÓN DEL FORMATO PDF DE NUTRIEN
        st.markdown(f"""
        <div class="ficha-box">
            <div class="ficha-titulo">FICHA TÉCNICA: {busqueda.upper()}</div>
            <div class="seccion-gris">PRINCIPALES CARACTERÍSTICAS</div>
            <div class="contenido-blanco">
                <b>Tipo:</b> {d['TIPO_PREPARADO']}<br>
                <b>Grupo Químico:</b> {d['FAMILIA_QUIMICA']}
            </div>
            <div class="seccion-gris">INSTRUCCIONES DE USO</div>
            <div class="contenido-blanco">
                <b>Dosis de Marbete:</b> {d['DOSIS_MARBETE_MIN']} - {d['DOSIS_MARBETE_MAX']} {d['UNIDAD_DOSIS']}<br>
                <b>Orden de Mezcla Sugerido:</b> {d['ORDEN_MEZCLA']}
            </div>
            <div class="seccion-gris">PRECAUCIONES Y COMPATIBILIDAD</div>
            <div class="contenido-blanco" style="color: #D32F2F;">
                <b>ALERTA:</b> {d['ALERTA_COMPATIBILIDAD']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# (EL RESTO DE TABS SE MANTIENEN IGUAL QUE EN TU CÓDIGO ORIGINAL)
with tab4:
    st.header("☀️ Tiempo de Vuelo")
    weather = get_weather_data(LATITUDE, LONGITUDE)
    if weather:
        st.metric("Viento", weather['Viento_Str'])
        st.metric("Humedad", weather['Humedad_Str'])