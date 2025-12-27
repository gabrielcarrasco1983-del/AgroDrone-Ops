import streamlit as st
import pandas as pd
import math
import io
from urllib.parse import quote

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AGRODRONE DOSIS", layout="wide")

# --- CSS ALTO CONTRASTE (PARA SOL DIRECTO) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* Forzar texto negro en etiquetas y entradas */
    label p, .stMarkdown p, .stTextInput label p, .stNumberInput label p, .stSelectbox label p {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }

    /* Tabs / Pestañas */
    .stTabs [data-baseweb="tab"] p {
        color: #000000 !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] { border-bottom-color: #002A20 !important; }

    /* Cajas de resultados */
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
    .link-clima {
        display: block;
        background-color: #002A20;
        color: white !important;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VADEMÉCUM DATA (PARA CONSULTA SOLAMENTE) ---
csv_data = """PRINCIPIO_ACTIVO;DOSIS_MARBETE_MIN;DOSIS_MARBETE_MAX;UNIDAD_DOSIS;ALERTA_COMPATIBILIDAD;ORDEN_MEZCLA
Glyphosate;0.25;1.5;L/ha;Evitar pH alcalino;Medio
2,4-D;0.5;1.5;L/ha;Deriva/Volatilidad;Medio
Atrazine;0.5;3;kg/ha;Persistente;Temprano
Dicamba;0.1;0.5;L/ha;Volatilidad;Medio"""
vademecum_df = pd.read_csv(io.StringIO(csv_data), sep=";")

# --- FUNCIÓN DELTA T ---
def calculate_delta_t(temp, hum):
    tw = temp * math.atan(0.151977 * (hum + 8.313659)**0.5) + \
         math.atan(temp + hum) - math.atan(hum - 1.676331) + \
         0.00391838 * (hum**1.5) * math.atan(0.023101 * hum) - 4.686035
    return round(temp - tw, 2)

st.title("AGRODRONE DOSIS")

tabs = st.tabs(["🧮 Calculadora", "🌡️ Delta T", "🌦️ Clima", "📖 Vademécum", "👥 Sobre Nosotros"])

# --- TAB 1: CALCULADORA (100% MANUAL) ---
with tabs[0]:
    st.subheader("1. Datos del Mixer")
    c1, c2, c3 = st.columns(3)
    with c1:
        has_lote = st.number_input("Hectáreas Lote", value=10.0, step=1.0)
    with c2:
        m_opt = st.selectbox("Mixer (L)", ["100", "200", "300", "500", "Manual"])
        c_mixer = st.number_input("Litros Reales", value=330) if m_opt == "Manual" else int(m_opt)
    with c3:
        tasa = st.number_input("Caudal (L/Ha)", value=10.0, step=1.0)

    st.divider()
    st.subheader("2. Productos (Ingreso Manual)")
    
    if 'filas' not in st.session_state:
        st.session_state.filas = [{"p": "", "d": 0.0, "u": "L"}]

    for i, fila in enumerate(st.session_state.filas):
        col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
        # AQUÍ ESTÁ EL CAMBIO: text_input vacío, no lee del vademecum
        st.session_state.filas[i]["p"] = col1.text_input(f"Producto {i+1}", value=fila["p"], key=f"prod_{i}", placeholder="Escriba el nombre")
        st.session_state.filas[i]["d"] = col2.number_input(f"Dosis/Ha", value=fila["d"], key=f"dose_{i}", format="%.2f")
        st.session_state.filas[i]["u"] = col3.selectbox("Unidad", ["L", "Kg"], key=f"unit_{i}")

    if st.button("➕ Agregar Producto"):
        st.session_state.filas.append({"p": "", "d": 0.0, "u": "L"})
        st.rerun()

    if has_lote > 0 and tasa > 0:
        has_vuelo = c_mixer / tasa
        mixers_totales = (has_lote * tasa) / c_mixer

        st.markdown(f"""
        <div class="resumen-caja">
            <h3>🧪 MEZCLA POR MIXER ({c_mixer}L)</h3>
            <p>📍 Superficie a cubrir: <b>{has_vuelo:.2f} Ha</b></p>
        """, unsafe_allow_html=True)
        
        txt_wa = []
        resumen_final = []
        for f in st.session_state.filas:
            if f["d"] > 0:
                p_nombre = f["p"] if f["p"] != "" else f"Prod. {st.session_state.filas.index(f)+1}"
                # Por Mixer
                cant_m = f["d"] * has_vuelo
                st.write(f"✅ **{p_nombre}:** {cant_m:.3f} {f['u']}")
                txt_wa.append(f"- {p_nombre}: {cant_m:.3f}{f['u']}")
                # Por Lote
                cant_l = f["d"] * has_lote
                resumen_final.append(f"📦 **{p_nombre}:** {cant_l:.2f} {f['u']}")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="total-lote-caja">
            <h4>📊 TOTAL PARA EL LOTE ({has_lote} Ha)</h4>
            <p>Cargas de mixer: <b>{math.ceil(mixers_totales)}</b></p>
        """, unsafe_allow_html=True)
        for r in resumen_final:
            st.write(r)
        st.markdown("</div>", unsafe_allow_html=True)

        msg = f"*ORDEN AGRODRONE DOSIS*\nMixer: {c_mixer}L\nCubre: {has_vuelo:.2f}Ha\n---\n" + "\n".join(txt_wa)
        st.markdown(f'<a href="https://wa.me/?text={quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; padding:15px; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">📲 ENVIAR POR WHATSAPP</button></a>', unsafe_allow_html=True)

# --- TAB 2: DELTA T ---
with tabs[1]:
    st.subheader("Cálculo de Delta T")
    col_t, col_h = st.columns(2)
    t = col_t.number_input("Temp (°C)", value=25.0)
    h = col_h.number_input("Humedad (%)", value=60.0)
    dt = calculate_delta_t(t, h)
    st.metric("Delta T", f"{dt} °C")
    
    

    if 2 <= dt <= 8: st.success("✅ ÓPTIMO")
    elif dt < 2: st.warning("⚠️ DERIVA")
    else: st.error("❌ EVAPORACIÓN")

# --- TAB 3: CLIMA (LINKS EXTERNOS) ---
with tabs[2]:
    st.subheader("Consultas de Clima Crítico")
    st.write("Accede a las herramientas externas recomendadas:")
    
    st.markdown('<a href="https://www.swpc.noaa.gov/products/planetary-k-index" target="_blank" class="link-clima">🛰️ Índice KP (NOAA) - Actividad Geomagnética</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.windy.com" target="_blank" class="link-clima">🌬️ Windy.com - Viento y Radar</a>', unsafe_allow_html=True)
    st.info("El índice KP es vital para la estabilidad del GPS del drone. Valores mayores a 4 pueden causar pérdida de señal.")

# --- TAB 4: VADEMÉCUM (SOLO CONSULTA) ---
with tabs[3]:
    st.subheader("Buscador de Principios Activos")
    b = st.text_input("Buscar en la base...")
    res = vademecum_df[vademecum_df['PRINCIPIO_ACTIVO'].str.contains(b, case=False, na=False)]
    st.dataframe(res, use_container_width=True)

# --- TAB 5: SOBRE NOSOTROS ---
with tabs[4]:
    st.header("AGRODRONE DOSIS")
    st.write("Desarrollado para aplicadores que buscan precisión y seguridad en cada hectárea.")
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
