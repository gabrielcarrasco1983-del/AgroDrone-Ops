
import streamlit as st
import math
from urllib.parse import quote

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Drone Mixer", layout="wide")

# -------------------------------------------------
# STYLE (high contrast for field use)
# -------------------------------------------------
st.markdown("""
<style>
.stApp { background-color: #FFFFFF; color:#000000; }
label p, .stNumberInput label p, .stTextInput label p {
    font-weight:800;
    font-size:1.05rem;
}
.resumen {
    background:#f1f3f5;
    padding:18px;
    border-left:8px solid #003b2e;
    border-radius:8px;
}
.total {
    background:#e7f3ff;
    padding:18px;
    border-top:6px solid #0056b3;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# DELTA T FUNCTION
# -------------------------------------------------
def calculate_delta_t(temp, hum):
    tw = temp * math.atan(0.151977 * (hum + 8.313659)**0.5) + \
         math.atan(temp + hum) - math.atan(hum - 1.676331) + \
         0.00391838 * (hum**1.5) * math.atan(0.023101 * hum) - 4.686035
    return round(temp - tw, 2)

# -------------------------------------------------
# TITLE
# -------------------------------------------------
st.title("DRONE MIXER")

tabs = st.tabs(["Calculadora", "Delta‑T", "Clima", "Sobre mí"])

# =================================================
# TAB 1 - CALCULADORA
# =================================================
with tabs[0]:

    st.subheader("Configuración del lote")

    col1, col2, col3 = st.columns(3)

    with col1:
        nombre_lote = st.text_input("Nombre del lote", "Lote sin nombre")
        hectareas = st.number_input("Superficie (ha)", value=10.0)

    with col2:
        volumen_aplicacion = st.number_input("Volumen aplicación (L/ha)", value=10.0)
        capacidad_mixer = st.number_input("Capacidad mixer (L)", value=300)

    with col3:
        tanque_dron = st.number_input("Tanque dron (L)", value=40)
        velocidad = st.number_input("Dato opcional velocidad", value=0.0)

    st.divider()

    st.subheader("Productos")

    if "productos" not in st.session_state:
        st.session_state.productos = [{"nombre":"", "dosis":0.0, "unidad":"L"}]

    for i,prod in enumerate(st.session_state.productos):

        c1,c2,c3 = st.columns([0.5,0.25,0.25])

        st.session_state.productos[i]["nombre"] = c1.text_input(
            f"Producto {i+1}",
            value=prod["nombre"],
            key=f"prod{i}"
        )

        st.session_state.productos[i]["dosis"] = c2.number_input(
            "Dosis/ha",
            value=prod["dosis"],
            key=f"dosis{i}"
        )

        st.session_state.productos[i]["unidad"] = c3.selectbox(
            "Unidad",
            ["L","Kg"],
            key=f"unidad{i}"
        )

    if st.button("Agregar producto"):
        st.session_state.productos.append({"nombre":"","dosis":0.0,"unidad":"L"})
        st.rerun()

    # -------------------------------------------------
    # CALCULOS
    # -------------------------------------------------

    if hectareas > 0 and volumen_aplicacion > 0:

        hectareas_por_mixer = capacidad_mixer / volumen_aplicacion
        mixers_necesarios = math.ceil((hectareas * volumen_aplicacion) / capacidad_mixer)
        vuelos_por_mixer = capacidad_mixer / tanque_dron

        st.markdown(
            f"""
            <div class="resumen">
            <h3>Mezcla por mixer ({capacidad_mixer} L)</h3>
            Cubre: <b>{hectareas_por_mixer:.2f} ha</b><br>
            Vuelos por mixer: <b>{vuelos_por_mixer:.1f}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        wa_mixer = []
        wa_total = []

        for p in st.session_state.productos:

            if p["dosis"] > 0:

                nombre = p["nombre"] if p["nombre"] else "Producto"
                cantidad_mixer = p["dosis"] * hectareas_por_mixer
                total_lote = p["dosis"] * hectareas

                st.write(f"{nombre}: {cantidad_mixer:.3f} {p['unidad']}")

                wa_mixer.append(f"- {nombre}: {cantidad_mixer:.2f} {p['unidad']}")
                wa_total.append(f"- {nombre}: {total_lote:.2f} {p['unidad']}")

        st.markdown(
            f"""
            <div class="total">
            <h3>Total lote</h3>
            Preparaciones mixer: <b>{mixers_necesarios}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        for t in wa_total:
            st.write(t)

        # WHATSAPP MESSAGE
        msg = (
            f"*ORDEN APLICACION DRON*\n"
            f"Lote: {nombre_lote}\n"
            f"Superficie: {hectareas} ha\n"
            f"Mixer: {capacidad_mixer} L\n"
            f"\n--- POR MIXER ---\n"
            + "\n".join(wa_mixer)
            + f"\n\n--- TOTAL LOTE ---\n"
            + "\n".join(wa_total)
        )

        st.markdown(
            f'<a href="https://wa.me/?text={quote(msg)}" target="_blank">'
            '<button style="width:100%;background:#25D366;color:white;padding:14px;border:none;border-radius:8px;font-weight:bold">'
            'Enviar orden por WhatsApp'
            '</button></a>',
            unsafe_allow_html=True
        )

# =================================================
# TAB 2 - DELTA T
# =================================================
with tabs[1]:

    st.subheader("Condiciones ambientales")

    col1,col2 = st.columns(2)

    with col1:
        temp = st.number_input("Temperatura °C", value=25.0)

    with col2:
        hum = st.number_input("Humedad %", value=60.0)

    dt = calculate_delta_t(temp, hum)

    st.metric("Delta‑T", f"{dt} °C")

    if 2 <= dt <= 8:
        st.success("Condiciones óptimas de aplicación")
    elif dt < 2:
        st.warning("Riesgo de deriva por inversión térmica")
    else:
        st.error("Evaporación alta")

# =================================================
# TAB 3 - CLIMA
# =================================================
with tabs[2]:

    st.subheader("Herramientas meteorológicas")

    st.markdown(
        '<a href="https://www.windy.com" target="_blank">'
        '<button style="width:100%;padding:15px">Abrir Windy</button>'
        '</a>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<a href="https://www.smn.gob.ar" target="_blank">'
        '<button style="width:100%;padding:15px">Servicio Meteorológico</button>'
        '</a>',
        unsafe_allow_html=True
    )

# =================================================
# TAB 4 - SOBRE
# =================================================
with tabs[3]:

    st.header("Sobre la aplicación")

    st.write("""
    Herramienta simple para pilotos de drones agrícolas.
    
    Permite calcular rápidamente:
    
    • Mezcla por tanque  
    • Cantidad total de producto  
    • Número de mixers necesarios  
    • Orden de aplicación para compartir por WhatsApp
    
    Diseñada para uso directo en el lote.
    """)

    st.caption("Desarrollado por Gabriel Carrasco")
