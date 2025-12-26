import streamlit as st
import pandas as pd
import math
import io
import requests 
from datetime import datetime
from urllib.parse import quote

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AgroDrone Ops", layout="wide")

# --- ESTILOS CSS (Fix para visibilidad en móviles y diseño limpio) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* FIX MENÚ TABS MÓVIL: Forzar texto oscuro en las pestañas */
    .stTabs [data-baseweb="tab"] p {
        color: #002A20 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    .stTabs [aria-selected="true"] { border-bottom-color: #88D600 !important; }
    .stTabs [aria-selected="true"] p { color: #88D600 !important; }

    /* Estilos para etiquetas y métricas */
    .stWidget label p { color: #000000 !important; font-weight: bold; }
    .resumen-total { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 10px solid #002A20; margin-bottom: 20px; }
    .resumen-mixer { background-color: #f1f8e9; padding: 15px; border-radius: 10px; border-left: 10px solid #88D600; }
    
    /* Vademécum Estilo Ficha */
    .ficha-box { border: 1px solid #002A20; margin-bottom: 20px; background-color: #ffffff; }
    .ficha-titulo { background-color: #002A20; color: #ffffff !important; padding: 10px; font-weight: 700; text-align: center; }
    .seccion-gris { background-color: #F2F2F2; padding: 5px 15px; font-weight: 700; color: #002A20; border-top: 1px solid #002A20; font-size: 0.8rem; }
    .contenido-ficha { padding: 10px 15px; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# --- DATOS DEL VADEMÉCUM (RESTORED) ---
csv_data = """PRINCIPIO_ACTIVO;DOSIS_MARBETE_MIN;DOSIS_MARBETE_MAX;UNIDAD_DOSIS;FAMILIA_QUIMICA;TIPO_PREPARADO;ALERTA_COMPATIBILIDAD;ORDEN_MEZCLA
Glyphosate;0.25;1.5;L/ha;Glicina;Herbicida;"Evitar pH alcalino";Medio
Paraquat;0.5;2;L/ha;Bipiridilio;Herbicida;"Muy tóxico";Temprano
Atrazine;0.5;3;kg/ha;Triazina;Herbicida;"Persistente";Temprano
2,4-D;0.5;1.5;L/ha;Fenoxiacético;Herbicida;"Deriva/Volatilidad";Medio
Dicamba;0.1;0.5;L/ha;Benzoico;Herbicida;"Alta volatilidad";Medio
Metsulfuron-methyl;0.01;0.05;kg/ha;Sulfonilurea;Herbicida;"Residualidad";Medio
Chlorpyrifos;0.5;1.5;L/ha;Organofosforado;Insecticida;"Alta toxicidad";Medio
Cypermethrin;0.1;0.3;L/ha;Piretroide;Insecticida;"Tóxico peces";Final
Abamectin;0.05;0.1;L/ha;Avermectina;Acaricida;"Tóxico abejas";Medio
Mancozeb;1;3;kg/ha;Ditiocarbamato;Fungicida;"Contacto";Temprano
Azoxystrobin;0.1;0.3;L/ha;Estrobilurina;Fungicida;"Resistencia";Medio
Tebuconazole;0.1;0.3;L/ha;Triazol;Fungicida;"Curativo";Medio""" 
# ... (Aquí irían los 100+ productos del CSV que tienes en tu archivo original)

vademecum_df = pd.read_csv(io.StringIO(csv_data), sep=";")
productos_disponibles = sorted(vademecum_df['PRINCIPIO_ACTIVO'].unique().tolist())

# --- FUNCIONES ---
def calculate_delta_t(temp, humidity):
    tw = temp * math.atan(0.151977 * (humidity + 8.313659)**0.5) + \
         math.atan(temp + humidity) - math.atan(humidity - 1.676331) + \
         0.00391838 * (humidity**1.5) * math.atan(0.023101 * humidity) - 4.686035
    return round(temp - tw, 2)

# --- UI PRINCIPAL ---
st.title("🚁 AgroDrone Ops")

tabs = st.tabs(["🧮 Mezcla y Lote", "🌡️ Delta T", "📖 Vademécum", "⛽ Generador"])

# --- TAB 1: MEZCLA Y LOTE (ENFOQUE EN MIXER) ---
with tabs[0]:
    st.subheader("Configuración del Trabajo")
    c1, c2 = st.columns(2)
    with c1:
        hectareas_totales = st.number_input("Hectáreas del Lote", value=20.0, step=1.0)
        tasa_aplicacion = st.number_input("Tasa Aplicación (L/Ha)", value=10.0, step=1.0)
    with c2:
        mixer_opcion = st.selectbox("Capacidad del Mixer (L)", ["100", "200", "300", "500", "Personalizado"])
        if mixer_opcion == "Personalizado":
            capacidad_mixer = st.number_input("Litros Mixer", value=330)
        else:
            capacidad_mixer = int(mixer_opcion)

    st.divider()
    st.subheader("Productos a Aplicar")
    
    # Manejo de múltiples productos
    if 'items' not in st.session_state:
        st.session_state.items = [{"prod": productos_disponibles[0], "dosis": 0.0}]

    def add_row(): st.session_state.items.append({"prod": productos_disponibles[0], "dosis": 0.0})

    for i, item in enumerate(st.session_state.items):
        cols = st.columns([0.6, 0.4])
        st.session_state.items[i]["prod"] = cols[0].selectbox(f"Producto {i+1}", productos_disponibles, key=f"p_{i}")
        st.session_state.items[i]["dosis"] = cols[1].number_input(f"Dosis/Ha", value=0.0, key=f"d_{i}")

    st.button("➕ Agregar otro producto", on_click=add_row)

    if hectareas_totales > 0 and tasa_aplicacion > 0:
        vol_total_caldo = hectareas_totales * tasa_aplicacion
        has_por_mixer = capacidad_mixer / tasa_aplicacion
        cant_mixers = vol_total_caldo / capacidad_mixer

        st.markdown(f"""
        <div class="resumen-total">
            <h4>📊 RESUMEN TOTAL DEL LOTE</h4>
            <p>💧 <b>Caldo Total:</b> {vol_total_caldo:.1f} Litros</p>
            <p>🔄 <b>Cargas de Mixer:</b> {math.ceil(cant_mixers)} (de {capacidad_mixer}L cada una)</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="resumen-mixer">
            <h4>🧪 CARGA POR MIXER ({capacidad_mixer}L)</h4>
            <p>📍 Cubre: <b>{has_por_mixer:.2f} Ha</b> por carga</p>
        """, unsafe_allow_html=True)
        
        lista_wa = []
        for item in st.session_state.items:
            if item["dosis"] > 0:
                prod_mixer = item["dosis"] * has_por_mixer
                st.write(f"✅ **{item['prod']}:** {prod_mixer:.3f} L/Kg")
                lista_wa.append(f"- {item['prod']}: {prod_mixer:.3f}")
        
        st.markdown("</div>", unsafe_allow_html=True)

        msg = f"*ORDEN DE MIXER*\nMixer: {capacidad_mixer}L\nCubre: {has_por_mixer:.2f}Ha\n---\n" + "\n".join(lista_wa)
        st.markdown(f'[@ Enviar Receta WhatsApp](https://wa.me/?text={quote(msg)})')

# --- TAB 2: DELTA T ---
with tabs[1]:
    st.subheader("Monitoreo Delta T")
    c1, c2 = st.columns(2)
    temp = c1.number_input("Temperatura (°C)", value=25.0)
    hum = c2.number_input("Humedad (%)", value=60.0)
    
    dt = calculate_delta_t(temp, hum)
    st.metric("Delta T Actual", f"{dt} °C")

    # 
    if 2 <= dt <= 8:
        st.success("✅ ÓPTIMO")
    elif dt < 2:
        st.warning("⚠️ PRECAUCIÓN: DERIVA")
    else:
        st.error("❌ CRÍTICO: EVAPORACIÓN")

# --- TAB 3: VADEMÉCUM ---
with tabs[2]:
    st.subheader("Buscador de Productos")
    busc = st.text_input("Buscar principio activo...")
    
    for _, r in vademecum_df.iterrows():
        if busc.lower() in r['PRINCIPIO_ACTIVO'].lower():
            st.markdown(f"""
            <div class="ficha-box">
                <div class="ficha-titulo">{r['PRINCIPIO_ACTIVO']}</div>
                <div class="seccion-gris">FAMILIA / TIPO</div>
                <div class="contenido-ficha">{r['FAMILIA_QUIMICA']} | {r['TIPO_PREPARADO']}</div>
                <div class="seccion-gris">DOSIS MARBETE</div>
                <div class="contenido-ficha">{r['DOSIS_MARBETE_MIN']} - {r['DOSIS_MARBETE_MAX']} {r['UNIDAD_DOSIS']}</div>
                <div class="seccion-gris">ALERTA</div>
                <div class="contenido-ficha" style="color:red;"><b>{r['ALERTA_COMPATIBILIDAD']}</b></div>
            </div>
            """, unsafe_allow_html=True)

# --- TAB 4: GENERADOR ---
with tabs[3]:
    st.subheader("Combustible para Generador")
    cons = st.number_input("Consumo (L/Ha)", value=1.0)
    st.info(f"Para {hectareas_totales} Has necesitas: **{hectareas_totales * cons:.1f} Litros**")

st.markdown("---")
st.caption("Gabriel Carrasco - AgroDrone Pro")
