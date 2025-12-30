import streamlit as st
import pandas as pd
import math
import io
from urllib.parse import quote

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AGRODRONE DOSIS", layout="wide")

# --- CSS DE ALTO CONTRASTE ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    label p, .stMarkdown p, .stTextInput label p, .stNumberInput label p, .stSelectbox label p {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }
    .stTabs [data-baseweb="tab"] p { color: #000000 !important; font-weight: bold !important; }
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
    /* Estilo Ficha Alltec */
    .alltec-ficha { border: 1px solid #002A20; margin-bottom: 20px; }
    .alltec-header { background-color: #002A20; color: white !important; padding: 10px; font-weight: bold; text-align: center; }
    .alltec-body { padding: 15px; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS AMPLIADA (Incluye Alltec) ---
vademecum_data = [
    {"PRODUCTO": "A35T GOLD", "TIPO": "Coadyuvante", "DOSIS": "50-100 cc/ha", "INFO": "Antievaporante, humectante y tensioactivo de alta performance."},
    {"PRODUCTO": "ALL-OK", "TIPO": "Corrector/Secuestrante", "DOSIS": "25-75 cc/100L", "INFO": "Corrector de pH y secuestrante de cationes (Calcio/Magnesio)."},
    {"PRODUCTO": "GLIFOSATO 54%", "TIPO": "Herbicida", "DOSIS": "2-4 L/ha", "INFO": "Control sistémico de malezas. Orden: Medio."},
    {"PRODUCTO": "2,4-D", "TIPO": "Herbicida", "DOSIS": "0.5-1.5 L/ha", "INFO": "Hormonal. Cuidado con la volatilidad y deriva."},
    # Aquí puedes seguir pegando el resto de tu lista original...
]
df_vademecum = pd.DataFrame(vademecum_data)

def calculate_delta_t(temp, hum):
    tw = temp * math.atan(0.151977 * (hum + 8.313659)**0.5) + \
         math.atan(temp + hum) - math.atan(hum - 1.676331) + \
         0.00391838 * (hum**1.5) * math.atan(0.023101 * hum) - 4.686035
    return round(temp - tw, 2)

st.title("AGRODRONE DOSIS")

tabs = st.tabs(["🧮 Calculadora", "🌡️ Delta T", "🌦️ Clima", "📖 Vademécum", "👥 Sobre el Autor"])

# --- TAB 1: CALCULADORA ---
with tabs[0]:
    st.subheader("Datos del Mixer")
    nombre_lote = st.text_input("Nombre del Lote", placeholder="Ej: La Posta - Cuadro 4")
    c1, c2, c3 = st.columns(3)
    with c1:
        has_lote = st.number_input("Hectáreas Lote", value=10.0, step=1.0)
    with c2:
        m_opt = st.selectbox("Mixer (L)", ["100", "200", "300", "500", "Manual"])
        c_mixer = st.number_input("Litros Reales", value=330) if m_opt == "Manual" else int(m_opt)
    with c3:
        tasa = st.number_input("Caudal (L/Ha)", value=10.0, step=1.0)

    st.divider()
    st.subheader("Productos (Carga Manual)")
    
    if 'filas' not in st.session_state:
        st.session_state.filas = [{"p": "", "d": 0.0, "u": "L"}]

    for i, fila in enumerate(st.session_state.filas):
        col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
        st.session_state.filas[i]["p"] = col1.text_input(f"Producto {i+1}", value=fila["p"], key=f"p_{i}")
        st.session_state.filas[i]["d"] = col2.number_input(f"Dosis/Ha", value=fila["d"], key=f"d_{i}", format="%.3f")
        st.session_state.filas[i]["u"] = col3.selectbox("Unidad", ["L", "Kg"], key=f"u_{i}")

    if st.button("➕ Agregar Producto"):
        st.session_state.filas.append({"p": "", "d": 0.0, "u": "L"})
        st.rerun()

    if has_lote > 0 and tasa > 0:
        has_vuelo = c_mixer / tasa
        mixers_totales = math.ceil((has_lote * tasa) / c_mixer)

        st.markdown(f"""
        <div class="resumen-caja">
            <h3>🧪 CARGA POR MIXER ({c_mixer}L)</h3>
            <p>📍 Cubre: <b>{has_vuelo:.2f} Ha</b></p>
        """, unsafe_allow_html=True)
        
        wa_mixer = []
        wa_total = []
        for f in st.session_state.filas:
            if f["d"] > 0:
                p_n = f["p"] if f["p"] else f"P{st.session_state.filas.index(f)+1}"
                cant_m = f["d"] * has_vuelo
                cant_t = f["d"] * has_lote
                st.write(f"✅ **{p_n}:** {cant_m:.3f} {f['u']}")
                wa_mixer.append(f"- {p_n}: {cant_m:.3f} {f['u']}")
                wa_total.append(f"- {p_n}: {cant_t:.2f} {f['u']}")

        st.markdown("</div><div class="total-lote-caja">", unsafe_allow_html=True)
        st.subheader(f"📊 TOTAL PARA EL LOTE: {nombre_lote}")
        st.write(f"Preparaciones de Mixer: **{mixers_totales}**")
        for t in wa_total:
            st.write(t)
        st.markdown("</div>", unsafe_allow_html=True)

        # WHATSAPP INTEGRADO
        msg = (f"*ORDEN AGRODRONE DOSIS*\n"
               f"*Lote:* {nombre_lote}\n"
               f"Mixer: {c_mixer}L | Cubre: {has_vuelo:.2f}Ha\n"
               f"--- POR MIXER ---\n" + "\n".join(wa_mixer) + 
               f"\n--- TOTAL LOTE ({has_lote}Ha) ---\n" + "\n".join(wa_total))
        
        st.markdown(f'<a href="https://wa.me/?text={quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; padding:15px; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">📲 ENVIAR ORDEN COMPLETA</button></a>', unsafe_allow_html=True)

# --- TAB 2: DELTA T ---
with tabs[1]:
    st.subheader("Condiciones de Aplicación")
    ct, ch = st.columns(2)
    t, h = ct.number_input("Temp °C", 25.0), ch.number_input("Hum %", 60.0)
    dt = calculate_delta_t(t, h)
    st.metric("Delta T", f"{dt} °C")
    

# --- TAB 3: CLIMA ---
with tabs[2]:
    st.subheader("Pronósticos Críticos")
    st.markdown('<a href="https://www.swpc.noaa.gov/products/planetary-k-index" target="_blank" style="display:block; background:#002A20; color:white; padding:15px; text-align:center; border-radius:10px; margin-bottom:10px; text-decoration:none;">🛰️ VER ÍNDICE KP (NOAA)</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.windy.com" target="_blank" style="display:block; background:#002A20; color:white; padding:15px; text-align:center; border-radius:10px; text-decoration:none;">🌬️ VER CLIMA EN WINDY</a>', unsafe_allow_html=True)

# --- TAB 4: VADEMÉCUM ---
with tabs[3]:
    st.subheader("Buscador Técnico (Incluye Alltec)")
    busc = st.text_input("🔍 Buscar producto o principio activo...")
    res = df_vademecum[df_vademecum['PRODUCTO'].str.contains(busc, case=False)]
    for _, r in res.iterrows():
        st.markdown(f"""
        <div class="alltec-ficha">
            <div class="alltec-header">{r['PRODUCTO']}</div>
            <div class="alltec-body">
                <b>Tipo:</b> {r['TIPO']}<br>
                <b>Dosis Sugerida:</b> {r['DOSIS']}<br>
                <b>Info:</b> {r['INFO']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 5: SOBRE NOSOTROS ---
with tabs[4]:
    st.header("Sobre el Autor")
    st.write("""
    Esta herramienta fue creada para simplificar el armado del **Caldo (Mixer)**, asegurando que las dosis 
    lleguen con precisión al objetivo. 
    
    El objetivo no es reemplazar la experiencia del aplicador, sino complementarla con cálculos rápidos en el lote.
    
    **Si esta aplicación te ha sido de utilidad y te ayudó a ahorrar tiempo y errores, considera apoyarme invitándome un café.**
    """)
    st.markdown('<a href="https://www.buymeacoffee.com/gabrielcarc" target="_blank"><button style="background-color: #FF813F; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">☕ Invítame un café</button></a>', unsafe_allow_html=True)
    st.divider()
    st.caption("Gabriel Carrasco - AgroDrone Solutions")
