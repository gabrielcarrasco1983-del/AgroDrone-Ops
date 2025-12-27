import streamlit as st
import pandas as pd
import math
import io
from urllib.parse import quote

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AGRODRONE DOSIS", layout="wide")

# --- CSS DE ALTO CONTRASTE Y ESTILO ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* Texto negro y negrita para máxima visibilidad al sol */
    label p, .stMarkdown p, .stTextInput label p, .stNumberInput label p, .stSelectbox label p {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }

    /* Estilo de Pestañas */
    .stTabs [data-baseweb="tab"] p {
        color: #000000 !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] { border-bottom-color: #002A20 !important; }

    /* Contenedores de resultados */
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
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VADEMÉCUM DATA (Base de consulta) ---
csv_data = """PRINCIPIO_ACTIVO;DOSIS_MARBETE_MIN;DOSIS_MARBETE_MAX;UNIDAD_DOSIS;FAMILIA_QUIMICA;TIPO_PREPARADO;ALERTA_COMPATIBILIDAD;ORDEN_MEZCLA
Glyphosate;0.25;1.5;L/ha;Glicina;Herbicida;Evitar pH alcalino;Medio
2,4-D;0.5;1.5;L/ha;Fenoxiacético;Herbicida;Deriva/Volatilidad;Medio
Atrazine;0.5;3;kg/ha;Triazina;Herbicida;Persistente;Temprano
Dicamba;0.1;0.5;L/ha;Benzoico;Herbicida;Volatilidad;Medio"""
vademecum_df = pd.read_csv(io.StringIO(csv_data), sep=";")

# --- FUNCIÓN DELTA T ---
def calculate_delta_t(temp, hum):
    tw = temp * math.atan(0.151977 * (hum + 8.313659)**0.5) + \
         math.atan(temp + hum) - math.atan(hum - 1.676331) + \
         0.00391838 * (hum**1.5) * math.atan(0.023101 * hum) - 4.686035
    return round(temp - tw, 2)

st.title("AGRODRONE DOSIS")

tabs = st.tabs(["🧮 Calculadora de Dosis", "🌡️ Delta T", "📖 Vademécum", "👥 Sobre Nosotros"])

# --- TAB 1: CALCULADORA (PRODUCTO LIBRE Y TOTALES) ---
with tabs[0]:
    st.subheader("Configuración del Lote y Mixer")
    c1, c2, c3 = st.columns(3)
    with c1:
        hectareas_lote = st.number_input("Hectáreas del Lote", value=10.0, step=1.0)
    with c2:
        mixer_opt = st.selectbox("Capacidad Mixer (L)", ["100", "200", "300", "500", "Personalizado"])
        cap_mixer = st.number_input("Litros Reales", value=330) if mixer_opt == "Personalizado" else int(mixer_opt)
    with c3:
        tasa_aplicacion = st.number_input("Caudal Dron (L/Ha)", value=10.0, step=1.0)

    st.divider()
    st.subheader("Productos (Escribe el nombre directamente)")
    
    if 'filas_prod' not in st.session_state:
        st.session_state.filas_prod = [{"nombre": "", "dosis": 0.0, "unidad": "L"}]

    # Renderizar filas de entrada 100% LIBRES
    for i, fila in enumerate(st.session_state.filas_prod):
        col_n, col_d, col_u = st.columns([0.5, 0.25, 0.25])
        st.session_state.filas_prod[i]["nombre"] = col_n.text_input(f"Producto {i+1}", value=fila["nombre"], key=f"n_{i}", placeholder="Ej: Glifosato")
        st.session_state.filas_prod[i]["dosis"] = col_d.number_input(f"Dosis/Ha", value=fila["dosis"], key=f"d_{i}", format="%.2f")
        st.session_state.filas_prod[i]["unidad"] = col_u.selectbox("Unidad", ["L", "Kg"], key=f"u_{i}")

    if st.button("➕ Añadir otro producto"):
        st.session_state.filas_prod.append({"nombre": "", "dosis": 0.0, "unidad": "L"})
        st.rerun()

    if hectareas_lote > 0 and tasa_aplicacion > 0:
        has_por_mixer = cap_mixer / tasa_aplicacion
        total_preparaciones = (hectareas_lote * tasa_aplicacion) / cap_mixer

        st.markdown(f"""
        <div class="resumen-caja">
            <h3>🧪 CARGA POR MIXER ({cap_mixer}L)</h3>
            <p>📍 Cubre: <b>{has_por_mixer:.2f} Hectáreas</b></p>
        """, unsafe_allow_html=True)
        
        items_wa = []
        totales_lote = []

        for f in st.session_state.filas_prod:
            if f["dosis"] > 0:
                p_nombre = f["nombre"] if f["nombre"] != "" else f"Producto {st.session_state.filas_prod.index(f)+1}"
                # Cálculo por carga de Mixer
                calc_mixer = f["dosis"] * has_por_mixer
                st.write(f"✅ **{p_nombre}:** {calc_mixer:.3f} {f['unidad']}")
                items_wa.append(f"- {p_nombre}: {calc_mixer:.3f} {f['unidad']}")
                
                # Cálculo Total del Lote
                calc_total = f["dosis"] * hectareas_lote
                totales_lote.append(f"📦 **{p_nombre}:** {calc_total:.2f} {f['unidad']}")

        st.markdown("</div>", unsafe_allow_html=True)

        # SECCIÓN DE TOTALES REQUERIDOS
        st.markdown(f"""
        <div class="total-lote-caja">
            <h4>📊 TOTAL PRODUCTO PARA EL LOTE ({hectareas_lote} Ha)</h4>
            <p>Cant. de Mixers: <b>{math.ceil(total_preparaciones)}</b></p>
        """, unsafe_allow_html=True)
        for t in totales_lote:
            st.write(t)
        st.markdown("</div>", unsafe_allow_html=True)

        # Botón WhatsApp
        msg = f"*AGRODRONE DOSIS*\nMixer: {cap_mixer}L\nCubre: {has_por_mixer:.2f}Ha\n---\n" + "\n".join(items_wa)
        st.markdown(f'<a href="https://wa.me/?text={quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; padding:15px; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">📲 ENVIAR ORDEN POR WHATSAPP</button></a>', unsafe_allow_html=True)

# --- TAB 2: DELTA T ---
with tabs[1]:
    st.subheader("Condiciones Ambientales")
    ct, ch = st.columns(2)
    temp_in = ct.number_input("Temperatura (°C)", value=25.0)
    hum_in = ch.number_input("Humedad (%)", value=60.0)
    dt_res = calculate_delta_t(temp_in, hum_in)
    st.metric("Delta T", f"{dt_res} °C")
    
    
    if 2 <= dt_res <= 8: st.success("✅ CONDICIÓN ÓPTIMA")
    elif dt_res < 2: st.warning("⚠️ RIESGO DE DERIVA")
    else: st.error("❌ EVAPORACIÓN ALTA")

# --- TAB 3: VADEMÉCUM ---
with tabs[2]:
    st.subheader("Consulta Técnica")
    search = st.text_input("Buscar principio activo...")
    res = vademecum_df[vademecum_df['PRINCIPIO_ACTIVO'].str.contains(search, case=False, na=False)]
    for _, item in res.iterrows():
        st.markdown(f"""
        <div style="border:2px solid #002A20; margin-bottom:10px; padding:10px;">
            <b style="color:#002A20; font-size:1.2rem;">{item['PRINCIPIO_ACTIVO']}</b><br>
            Dosis: {item['DOSIS_MARBETE_MIN']}-{item['DOSIS_MARBETE_MAX']} {item['UNIDAD_DOSIS']}<br>
            Alerta: {item['ALERTA_COMPATIBILIDAD']} | Orden: {item['ORDEN_MEZCLA']}
        </div>
        """, unsafe_allow_html=True)

# --- TAB 4: SOBRE NOSOTROS ---
with tabs[3]:
    st.header("Sobre AGRODRONE DOSIS")
    st.write("Herramienta diseñada para simplificar el cálculo de mezclas en campo y asegurar la eficacia de la aplicación.")
    
    st.subheader("☕ Apoya el Desarrollo")
    st.info("Si esta aplicación te es útil, puedes apoyar su mantenimiento.")

    st.markdown("""
        <a href="https://www.buymeacoffee.com/gabrielcarc" target="_blank">
            <button style="background-color: #FF813F; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">
                ☕ Invítame un café
            </button>
        </a>
    """, unsafe_allow_html=True)
    st.divider()
    st.caption("Desarrollado por Gabriel Carrasco - AgroDrone Solutions")
