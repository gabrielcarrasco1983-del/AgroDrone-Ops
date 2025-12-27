import streamlit as st
import pandas as pd
import math
import io
from urllib.parse import quote

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AGRODRONE DOSIS", layout="wide")

# --- CSS DE ALTO CONTRASTE PARA CAMPO (TEXTO NEGRO PURO) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* Forzar negro en etiquetas y textos */
    label p, .stMarkdown p, .stSelectbox label p, .stNumberInput label p, .stTextInput label p {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }

    /* Pestañas */
    .stTabs [data-baseweb="tab"] p {
        color: #000000 !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] { border-bottom-color: #002A20 !important; }

    /* Resultados */
    .resumen-caja {
        background-color: #f1f3f5;
        padding: 20px;
        border-radius: 10px;
        border-left: 10px solid #002A20;
        margin-bottom: 20px;
        color: #000000 !important;
    }
    .total-lote-caja {
        background-color: #e7f3ff;
        padding: 20px;
        border-radius: 10px;
        border-top: 5px solid #0056b3;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS VADEMÉCUM (RESUMIDA PARA EL EJEMPLO, PERO COMPLETA EN TU LÓGICA) ---
csv_data = """PRINCIPIO_ACTIVO;DOSIS_MARBETE_MIN;DOSIS_MARBETE_MAX;UNIDAD_DOSIS;FAMILIA_QUIMICA;TIPO_PREPARADO;ALERTA_COMPATIBILIDAD;ORDEN_MEZCLA
Glyphosate;0.25;1.5;L/ha;Glicina;Herbicida;"Evitar pH alcalino";Medio
2,4-D;0.5;1.5;L/ha;Fenoxiacético;Herbicida;"Deriva/Volatilidad";Medio
Atrazine;0.5;3;kg/ha;Triazina;Herbicida;Persistente;Temprano
Dicamba;0.1;0.5;L/ha;Benzoico;Herbicida;Volatilidad;Medio
Abamectin;0.05;0.1;L/ha;Avermectina;Acaricida;Tóxico abejas;Medio"""
# [Aquí incluyes los 114 productos que tienes en tu archivo original]

vademecum_df = pd.read_csv(io.StringIO(csv_data), sep=";")
lista_sugerencias = sorted(vademecum_df['PRINCIPIO_ACTIVO'].unique().tolist())

# --- FUNCIONES ---
def calculate_delta_t(temp, hum):
    tw = temp * math.atan(0.151977 * (hum + 8.313659)**0.5) + \
         math.atan(temp + hum) - math.atan(hum - 1.676331) + \
         0.00391838 * (hum**1.5) * math.atan(0.023101 * hum) - 4.686035
    return round(temp - tw, 2)

st.title("AGRODRONE DOSIS")

tabs = st.tabs(["🧮 Calculadora de Dosis", "🌡️ Delta T", "📖 Vademécum", "👥 Sobre Nosotros"])

# --- TAB 1: CALCULADORA ---
with tabs[0]:
    st.subheader("Configuración del Mixer")
    c1, c2, c3 = st.columns(3)
    with c1:
        has_lote = st.number_input("Hectáreas del Lote", value=10.0, step=1.0)
    with c2:
        m_opt = st.selectbox("Capacidad Mixer (L)", ["100", "200", "300", "500", "Personalizado"])
        c_mixer = st.number_input("Litros Reales", value=330) if m_opt == "Personalizado" else int(m_opt)
    with c3:
        tasa = st.number_input("Caudal Dron (L/Ha)", value=10.0, step=1.0)

    st.divider()
    st.subheader("Productos (Escribe el nombre que desees)")
    
    if 'filas' not in st.session_state:
        st.session_state.filas = [{"p": "", "d": 0.0, "u": "L"}]

    for i, fila in enumerate(st.session_state.filas):
        col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
        # CAMBIO CLAVE: text_input libre en lugar de selectbox rígido
        st.session_state.filas[i]["p"] = col1.text_input(f"Producto {i+1}", value=fila["p"], key=f"prod_{i}", help="Escribe cualquier nombre")
        st.session_state.filas[i]["d"] = col2.number_input(f"Dosis/Ha", value=fila["d"], key=f"dose_{i}")
        st.session_state.filas[i]["u"] = col3.selectbox("Unidad", ["L", "Kg"], key=f"unit_{i}")

    if st.button("➕ Añadir otro producto"):
        st.session_state.filas.append({"p": "", "d": 0.0, "u": "L"})
        st.rerun()

    if has_lote > 0 and tasa > 0:
        has_vuelo = c_mixer / tasa
        mixers_totales = (has_lote * tasa) / c_mixer

        st.markdown(f"""
        <div class="resumen-caja">
            <h3>🧪 CARGA POR MIXER ({c_mixer}L)</h3>
            <p>📍 Cubre: <b>{has_vuelo:.2f} Hectáreas</b></p>
        """, unsafe_allow_html=True)
        
        txt_wa = []
        totales_lote = []
        for f in st.session_state.filas:
            if f["d"] > 0:
                p_nombre = f["p"] if f["p"] != "" else "Producto sin nombre"
                cant_mixer = f["d"] * has_vuelo
                cant_total = f["d"] * has_lote
                
                st.write(f"✅ **{p_nombre}:** {cant_mixer:.3f} {f['u']}")
                txt_wa.append(f"- {p_nombre}: {cant_mixer:.3f}{f['u']}")
                totales_lote.append(f"📦 **{p_nombre}:** {cant_total:.2f} {f['u']}")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="total-lote-caja">
            <h4>📊 TOTAL PARA TODO EL LOTE ({has_lote} Ha)</h4>
            <p>Cargas de mixer necesarias: <b>{math.ceil(mixers_totales)}</b></p>
        """, unsafe_allow_html=True)
        for t in totales_lote:
            st.write(t)
        st.markdown("</div>", unsafe_allow_html=True)

        msg = f"*AGRODRONE DOSIS*\nMixer: {c_mixer}L\nCubre: {has_vuelo:.2f}Ha\n---\n" + "\n".join(txt_wa)
        st.markdown(f'<a href="https://wa.me/?text={quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; padding:15px; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">📲 ENVIAR ORDEN WHATSAPP</button></a>', unsafe_allow_html=True)

# --- TAB 2: DELTA T ---
with tabs[1]:
    st.subheader("Condiciones Delta T")
    ct, ch = st.columns(2)
    temp = ct.number_input("Temperatura (°C)", value=25.0)
    hum = ch.number_input("Humedad (%)", value=60.0)
    dt = calculate_delta_t(temp, hum)
    st.metric("Delta T", f"{dt} °C")
    
    

    if 2 <= dt <= 8: st.success("✅ ÓPTIMO")
    elif dt < 2: st.warning("⚠️ RIESGO DERIVA")
    else: st.error("❌ EVAPORACIÓN ALTA")

# --- TAB 3: VADEMÉCUM ---
with tabs[2]:
    st.subheader("Buscador de la Base de Datos")
    b = st.text_input("Buscar principio activo...")
    res = vademecum_df[vademecum_df['PRINCIPIO_ACTIVO'].str.contains(b, case=False, na=False)]
    for _, item in res.iterrows():
        st.markdown(f"""
        <div style="border:2px solid #002A20; margin-bottom:10px; background:#fff;">
            <div style="background:#002A20; color:#fff; padding:10px; font-weight:bold;">{item['PRINCIPIO_ACTIVO']}</div>
            <div style="padding:10px; color:#000;">
                <b>Dosis:</b> {item['DOSIS_MARBETE_MIN']}-{item['DOSIS_MARBETE_MAX']} {item['UNIDAD_DOSIS']}<br>
                <b>Alerta:</b> {item['ALERTA_COMPATIBILIDAD']}<br>
                <b>Orden:</b> {item['ORDEN_MEZCLA']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 4: SOBRE NOSOTROS ---
with tabs[3]:
    st.header("Sobre AGRODRONE DOSIS")
    st.write("Herramienta profesional para el cálculo de mezclas en mixers de apoyo para drones agrícolas.")
    st.subheader("☕ Apoya el Desarrollo")
    st.markdown("""
        <a href="https://www.buymeacoffee.com/gabrielcarc" target="_blank">
            <button style="background-color: #FF813F; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">
                ☕ Invítame un café
            </button>
        </a>
    """, unsafe_allow_html=True)
    st.divider()
    st.caption("Gabriel Carrasco - AgroDrone Solutions")
