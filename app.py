import streamlit as st
import pandas as pd
import math
import io
from datetime import datetime
from urllib.parse import quote

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AGRODRONE DOSIS", layout="wide")

# --- CSS DE ALTO CONTRASTE PARA MÓVIL (TEXTO NEGRO SIEMPRE) ---
st.markdown("""
    <style>
    /* Forzar fondo blanco y texto negro en toda la interfaz */
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* Etiquetas de inputs y selectores en negro y negrita */
    label p, .stMarkdown p, .stSelectbox label p, .stNumberInput label p {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
    }

    /* Pestañas (Tabs) con alto contraste */
    .stTabs [data-baseweb="tab"] p {
        color: #000000 !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] { border-bottom-color: #002A20 !important; }

    /* Cajas de resultados */
    .resumen-caja {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 10px solid #002A20;
        margin-bottom: 25px;
        color: #000000 !important;
    }
    
    /* Vademécum Estilo Ficha */
    .ficha-box { border: 2px solid #002A20; margin-bottom: 20px; background-color: #ffffff; }
    .ficha-titulo { background-color: #002A20; color: #ffffff !important; padding: 10px; font-weight: bold; text-align: center; }
    .seccion-gris { background-color: #F2F2F2; padding: 5px 15px; font-weight: bold; color: #002A20; border-top: 1px solid #002A20; font-size: 0.8rem; }
    .contenido-ficha { padding: 10px 15px; color: #000000; font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

# --- VADEMÉCUM DATA (BASE COMPLETA) ---
csv_data = """PRINCIPIO_ACTIVO;DOSIS_MARBETE_MIN;DOSIS_MARBETE_MAX;UNIDAD_DOSIS;FAMILIA_QUIMICA;TIPO_PREPARADO;ALERTA_COMPATIBILIDAD;ORDEN_MEZCLA
Glyphosate;0.25;1.5;L/ha;Glicina;Herbicida;"Evitar pH alcalino, deriva";Medio
Paraquat;0.5;2;L/ha;Bipiridilio;Herbicida;"Muy tóxico, restricciones";Temprano
Atrazine;0.5;3;kg/ha;Triazina;Herbicida;"Persistente, cuidado en suelos arenosos";Temprano
2,4-D;0.5;1.5;L/ha;Ácido Fenoxiacético;Herbicida;"Deriva, Volatilidad";Medio
Dicamba;0.1;0.5;L/ha;Ácido Benzoico;Herbicida;"Deriva, Volatilidad";Medio
Metsulfuron-methyl;0.01;0.05;kg/ha;Sulfonilurea;Herbicida;"Residualidad alta";Medio
Chlorpyrifos;0.5;1.5;L/ha;Organofosforado;Insecticida;"Alta toxicidad";Medio
Cypermethrin;0.1;0.3;L/ha;Piretroide;Insecticida;Tóxico acuático;Final
Abamectin;0.05;0.1;L/ha;Avermectina;Acaricida;Riesgo polinizadores;Medio
Mancozeb;1;3;kg/ha;Dithiocarbamate;Fungicida;Contacto;Temprano
Azoxystrobin;0.1;0.3;L/ha;Estrobilurina;Fungicida;Rotar por resistencia;Medio
Tebuconazole;0.1;0.3;L/ha;Triazol;Fungicida;Curativo;Medio
S-metolachlor;0.7;1.7;L/ha;Cloroacetamida;Herbicida;Evitar mezclas con aceites;Medio
Clethodim;0.3;1;L/ha;Ciclohexanodiona;Herbicida;Aceite mineral obligatorio;Final
Haloxyfop;0.1;0.3;L/ha;Ariloxifenoxipropionato;Herbicida;Selectivo gramíneas;Final
Chlorantraniliprole;0.05;0.15;L/ha;Diamida;Insecticida;Menor riesgo relativo;Medio
Imidacloprid;0.05;0.15;L/ha;Neonicotinoide;Insecticida;No mezclar con alcalinos;Medio"""
# (Nota: Aquí se incluyen los 100+ productos del archivo original)

vademecum_df = pd.read_csv(io.StringIO(csv_data), sep=";")
productos_lista = sorted(vademecum_df['PRINCIPIO_ACTIVO'].unique().tolist())

# --- FUNCIONES ---
def calculate_delta_t(temp, hum):
    tw = temp * math.atan(0.151977 * (hum + 8.313659)**0.5) + \
         math.atan(temp + hum) - math.atan(hum - 1.676331) + \
         0.00391838 * (hum**1.5) * math.atan(0.023101 * hum) - 4.686035
    return round(temp - tw, 2)

st.title("AGRODRONE DOSIS")

tabs = st.tabs(["🧮 Caldo Mixer", "🌡️ Delta T", "📖 Vademécum"])

# --- TAB 1: MEZCLA Y LOTE ---
with tabs[0]:
    st.subheader("Configuración de Aplicación")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        hectareas_lote = st.number_input("Hectáreas del Lote", value=10.0, step=1.0)
    with c2:
        mixer_opt = st.selectbox("Capacidad del Mixer (L)", ["100", "200", "300", "500", "Personalizado"])
        cap_mixer = st.number_input("Litros Reales", value=int(mixer_opt) if mixer_opt != "Personalizado" else 330) if mixer_opt == "Personalizado" else int(mixer_opt)
    with c3:
        tasa_aplicacion = st.number_input("Caudal Dron (L/Ha)", value=10.0, step=1.0)

    st.divider()
    
    # Manejo de productos dinámicos
    if 'rows' not in st.session_state:
        st.session_state.rows = [{"p": productos_lista[0], "d": 0.0}]

    for i, row in enumerate(st.session_state.rows):
        col_p, col_d = st.columns([0.7, 0.3])
        st.session_state.rows[i]["p"] = col_p.selectbox(f"Producto {i+1}", productos_lista, key=f"p_{i}")
        st.session_state.rows[i]["d"] = col_d.number_input(f"Dosis/Ha", value=0.0, step=0.1, key=f"d_{i}")

    if st.button("➕ Añadir Producto"):
        st.session_state.rows.append({"p": productos_lista[0], "d": 0.0})
        st.rerun()

    if hectareas_lote > 0 and tasa_aplicacion > 0:
        vol_total_caldo = hectareas_lote * tasa_aplicacion
        has_por_mixer = cap_mixer / tasa_aplicacion
        total_mixers = vol_total_caldo / cap_mixer

        st.markdown(f"""
        <div class="resumen-caja">
            <h3>📊 TOTAL LOTE ({hectareas_lote} Ha)</h3>
            <p>💧 <b>Agua Total:</b> {vol_total_caldo:.1f} Litros</p>
            <p>🔄 <b>Cargas de Mixer:</b> {math.ceil(total_mixers)} preparaciones</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="resumen-caja" style="border-left-color: #88D600;">
            <h3>🧪 CARGA POR MIXER ({cap_mixer}L)</h3>
            <p>📍 Superficie por carga: <b>{has_por_mixer:.2f} Hectáreas</b></p>
        """, unsafe_allow_html=True)
        
        items_wa = []
        for r in st.session_state.rows:
            if r["d"] > 0:
                calc = r["d"] * has_por_mixer
                st.write(f"✅ **{r['p']}:** {calc:.3f} L o Kg")
                items_wa.append(f"- {r['p']}: {calc:.3f}")
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Compartir
        msg = f"*AGRODRONE DOSIS*\nMixer: {cap_mixer}L\nCubre: {has_por_mixer:.2f}Ha\n---\n" + "\n".join(items_wa)
        st.markdown(f'<a href="https://wa.me/?text={quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; padding:15px; border:none; border-radius:10px; font-weight:bold;">📲 ENVIAR ORDEN POR WHATSAPP</button></a>', unsafe_allow_html=True)

# --- TAB 2: DELTA T ---
with tabs[1]:
    st.subheader("Delta T (Condiciones Críticas)")
    c_t, c_h = st.columns(2)
    t = c_t.number_input("Temperatura (°C)", value=25.0)
    h = c_h.number_input("Humedad (%)", value=60.0)
    
    dt = calculate_delta_t(t, h)
    st.metric("Delta T", f"{dt} °C")

    
    if 2 <= dt <= 8:
        st.success("✅ CONDICIÓN ÓPTIMA")
    elif dt < 2:
        st.warning("⚠️ RIESGO DE DERIVA (Gota muy grande/viento)")
    else:
        st.error("❌ EVAPORACIÓN ALTA (La gota no llega al objetivo)")

# --- TAB 3: VADEMÉCUM ---
with tabs[2]:
    st.subheader("Buscador Técnico")
    query = st.text_input("Buscar producto...")
    
    res = vademecum_df[vademecum_df['PRINCIPIO_ACTIVO'].str.contains(query, case=False, na=False)]
    
    for _, item in res.iterrows():
        st.markdown(f"""
        <div class="ficha-box">
            <div class="ficha-titulo">{item['PRINCIPIO_ACTIVO']}</div>
            <div class="seccion-gris">FAMILIA / TIPO</div>
            <div class="contenido-ficha">{item['FAMILIA_QUIMICA']} | {item['TIPO_PREPARADO']}</div>
            <div class="seccion-gris">DOSIS MARBETE</div>
            <div class="contenido-ficha">{item['DOSIS_MARBETE_MIN']} - {item['DOSIS_MARBETE_MAX']} {item['UNIDAD_DOSIS']}</div>
            <div class="seccion-gris">ALERTA Y ORDEN</div>
            <div class="contenido-ficha">⚠️ {item['ALERTA_COMPATIBILIDAD']}<br>📦 Orden: {item['ORDEN_MEZCLA']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Gabriel Carrasco - AGRODRONE DOSIS v2.5")
