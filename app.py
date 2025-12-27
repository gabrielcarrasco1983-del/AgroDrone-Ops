import streamlit as st
import pandas as pd
import math
import io
from urllib.parse import quote

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AGRODRONE DOSIS", layout="wide")

# --- CSS DE ALTO CONTRASTE PARA CAMPO ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* Texto negro puro para etiquetas */
    label p, .stMarkdown p, .stSelectbox label p, .stNumberInput label p {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }

    /* Pestañas con visibilidad mejorada */
    .stTabs [data-baseweb="tab"] p {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 1rem !important;
    }
    .stTabs [aria-selected="true"] { border-bottom-color: #002A20 !important; }

    /* Cuadros de resultados */
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
        margin-top: 10px;
        color: #000000 !important;
    }
    
    /* Vademécum */
    .ficha-box { border: 2px solid #002A20; margin-bottom: 20px; background-color: #ffffff; }
    .ficha-titulo { background-color: #002A20; color: #ffffff !important; padding: 10px; font-weight: bold; text-align: center; }
    .seccion-gris { background-color: #F2F2F2; padding: 5px 15px; font-weight: bold; color: #002A20; border-top: 1px solid #002A20; font-size: 0.85rem; }
    .contenido-ficha { padding: 10px 15px; color: #000000; font-size: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- DATOS VADEMÉCUM ---
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
Tebuconazole;0.1;0.3;L/ha;Triazol;Fungicida;"Curativo";Medio
Clethodim;0.3;1;L/ha;Ciclohexanodiona;Herbicida;Aceite mineral obligatorio;Final
Haloxyfop;0.1;0.3;L/ha;Ariloxifenoxipropionato;Herbicida;Selectivo;Final
Chlorantraniliprole;0.05;0.15;L/ha;Diamida;Insecticida;Seguro;Medio"""
# Se asume que aquí están los 100+ productos que mencionaste

vademecum_df = pd.read_csv(io.StringIO(csv_data), sep=";")
productos_lista = sorted(vademecum_df['PRINCIPIO_ACTIVO'].unique().tolist())
productos_lista.append("Otro / Personalizado")

# --- FUNCIONES ---
def calculate_delta_t(temp, hum):
    tw = temp * math.atan(0.151977 * (hum + 8.313659)**0.5) + \
         math.atan(temp + hum) - math.atan(hum - 1.676331) + \
         0.00391838 * (hum**1.5) * math.atan(0.023101 * hum) - 4.686035
    return round(temp - tw, 2)

st.title("AGRODRONE DOSIS")

tabs = st.tabs(["🧮 Calculadora de Dosis", "🌡️ Delta T", "📖 Vademécum", "👥 Sobre Nosotros"])

# --- TAB 1: CALCULADORA (ENFOQUE MIXER) ---
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
    st.subheader("Productos")
    
    if 'rows' not in st.session_state:
        st.session_state.rows = [{"p": productos_lista[0], "d": 0.0, "u": "L", "custom": ""}]

    for i, row in enumerate(st.session_state.rows):
        col_p, col_custom, col_d, col_u = st.columns([0.4, 0.3, 0.15, 0.15])
        
        st.session_state.rows[i]["p"] = col_p.selectbox(f"Producto {i+1}", productos_lista, key=f"p_{i}")
        
        # Si elige "Otro", habilitar texto
        if st.session_state.rows[i]["p"] == "Otro / Personalizado":
            st.session_state.rows[i]["custom"] = col_custom.text_input("Nombre del producto", key=f"c_{i}")
        else:
            col_custom.write("") # Espacio vacío

        st.session_state.rows[i]["d"] = col_d.number_input(f"Dosis/Ha", value=0.0, key=f"d_{i}")
        st.session_state.rows[i]["u"] = col_u.selectbox("Unidad", ["L", "Kg"], key=f"u_{i}")

    if st.button("➕ Añadir otro producto"):
        st.session_state.rows.append({"p": productos_lista[0], "d": 0.0, "u": "L", "custom": ""})
        st.rerun()

    if hectareas_lote > 0 and tasa_aplicacion > 0:
        has_por_mixer = cap_mixer / tasa_aplicacion
        total_mixers = (hectareas_lote * tasa_aplicacion) / cap_mixer

        st.markdown(f"""
        <div class="resumen-caja">
            <h3>🧪 CARGA POR MIXER ({cap_mixer}L)</h3>
            <p>📍 Cubre: <b>{has_por_mixer:.2f} Hectáreas</b> por carga</p>
        """, unsafe_allow_html=True)
        
        lista_wa = []
        totales_lote = []

        for r in st.session_state.rows:
            if r["d"] > 0:
                nombre = r["custom"] if r["p"] == "Otro / Personalizado" else r["p"]
                # Cálculo por Mixer
                calc_mixer = r["d"] * has_por_mixer
                st.write(f"✅ **{nombre}:** {calc_mixer:.3f} {r['u']}")
                lista_wa.append(f"- {nombre}: {calc_mixer:.3f}{r['u']}")
                
                # Cálculo Total Lote
                calc_total = r["d"] * hectareas_lote
                totales_lote.append(f"📦 **{nombre}:** {calc_total:.2f} {r['u']}")
        
        st.markdown("</div>", unsafe_allow_html=True)

        # SECCIÓN NUEVA: TOTAL PARA EL LOTE
        st.markdown(f"""
        <div class="total-lote-caja">
            <h4>📊 NECESIDAD TOTAL PARA EL LOTE ({hectareas_lote} Ha)</h4>
            <p>Cargas de mixer estimadas: <b>{math.ceil(total_mixers)}</b></p>
        """, unsafe_allow_html=True)
        for t in totales_lote:
            st.write(t)
        st.markdown("</div>", unsafe_allow_html=True)

        # WhatsApp
        msg = f"*AGRODRONE DOSIS*\nMixer: {cap_mixer}L\nCubre: {has_por_mixer:.2f}Ha\n---\n" + "\n".join(lista_wa)
        st.markdown(f'<a href="https://wa.me/?text={quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; padding:15px; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">📲 ENVIAR ORDEN AL AYUDANTE</button></a>', unsafe_allow_html=True)

# --- TAB 2: DELTA T ---
with tabs[1]:
    st.subheader("Condiciones Ambientales (Delta T)")
    c_t, c_h = st.columns(2)
    temp = c_t.number_input("Temperatura (°C)", value=25.0)
    hum = c_h.number_input("Humedad (%)", value=60.0)
    
    dt = calculate_delta_t(temp, hum)
    st.metric("Delta T", f"{dt} °C")

    # Referencia visual (Placeholder para la imagen del gráfico)
    

    if 2 <= dt <= 8:
        st.success("✅ ÓPTIMO")
    elif dt < 2:
        st.warning("⚠️ DERIVA ALTA")
    else:
        st.error("❌ EVAPORACIÓN ALTA")

# --- TAB 3: VADEMÉCUM ---
with tabs[2]:
    st.subheader("Buscador Técnico")
    busc = st.text_input("Escribe el principio activo...")
    
    res = vademecum_df[vademecum_df['PRINCIPIO_ACTIVO'].str.contains(busc, case=False, na=False)]
    
    for _, item in res.iterrows():
        st.markdown(f"""
        <div class="ficha-box">
            <div class="ficha-titulo">{item['PRINCIPIO_ACTIVO']}</div>
            <div class="seccion-gris">FAMILIA / TIPO</div>
            <div class="contenido-ficha">{item['FAMILIA_QUIMICA']} | {item['TIPO_PREPARADO']}</div>
            <div class="seccion-gris">DOSIS MARBETE</div>
            <div class="contenido-ficha">{item['DOSIS_MARBETE_MIN']} - {item['DOSIS_MARBETE_MAX']} {item['UNIDAD_DOSIS']}</div>
            <div class="seccion-gris">OBSERVACIONES</div>
            <div class="contenido-ficha">⚠️ {item['ALERTA_COMPATIBILIDAD']}<br>📦 Orden: {item['ORDEN_MEZCLA']}</div>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 4: SOBRE NOSOTROS ---
with tabs[3]:
    st.header("Sobre AGRODRONE DOSIS")
    st.write("""
    Esta herramienta fue diseñada para simplificar el trabajo del aplicador de drones agrícolas. 
    Nuestro enfoque es la precisión en la carga del mixer y la seguridad en la aplicación basándonos en condiciones climáticas reales.
    """)
    
    st.subheader("☕ Apoya el Desarrollo")
    st.info("Si esta app te ahorró tiempo y errores en el campo, considera apoyar el mantenimiento del proyecto.")

    BUY_ME_A_COFFEE_URL = "https://www.buymeacoffee.com/gabrielcarc"  

    st.markdown(
        f"""
        <a href="{BUY_ME_A_COFFEE_URL}" target="_blank">
            <button style="background-color: #FF813F; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 18px; font-weight: bold;">
                ☕ Invítame un café
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.caption("Desarrollado por Gabriel Carrasco | AgroDrone Solutions")
