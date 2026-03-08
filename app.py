import streamlit as st
import math
from urllib.parse import quote

# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------

st.set_page_config(
    page_title="AgroDrone Mixer",
    layout="wide"
)

# -------------------------------------------------
# ESTILO VISUAL (AGRO)
# -------------------------------------------------

st.markdown("""
<style>

.stApp {
background-color:#f9faf6;
}

h1, h2, h3 {
color:#2e5d2c;
}

.resumen{
background:#eef6ea;
padding:18px;
border-left:8px solid #4CAF50;
border-radius:8px;
}

.total{
background:#fff8d6;
padding:18px;
border-top:6px solid #d4b106;
border-radius:8px;
}

button{
border-radius:8px !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# FUNCIÓN DELTA T
# -------------------------------------------------

def calculate_delta_t(temp, hum):

    tw = temp * math.atan(0.151977 * (hum + 8.313659)**0.5) + \
         math.atan(temp + hum) - math.atan(hum - 1.676331) + \
         0.00391838 * (hum**1.5) * math.atan(0.023101 * hum) - 4.686035

    return round(temp - tw,2)

# -------------------------------------------------
# TITULO
# -------------------------------------------------

st.title("AGRODRONE MIXER")

tabs = st.tabs([
"Calculadora",
"Delta-T",
"Clima",
"Sobre la app"
])

# =================================================
# CALCULADORA
# =================================================

with tabs[0]:

    st.subheader("Datos del lote")

    c1,c2,c3 = st.columns(3)

    with c1:
        nombre_lote = st.text_input("Nombre del lote","Lote sin nombre")
        hectareas = st.number_input("Superficie (ha)", value=10.0)

    with c2:
        volumen_aplicacion = st.number_input("Volumen aplicación (L/ha)", value=10.0)
        capacidad_mixer = st.number_input("Capacidad tanque mixer (L)", value=300)

    with c3:
        st.write("")
        st.write("")
        st.info("Cálculo optimizado para aplicaciones con drone")

    st.divider()

    st.subheader("Productos")

    if "productos" not in st.session_state:
        st.session_state.productos = [{"nombre":"", "dosis":0.0, "unidad":"L"}]

    for i,prod in enumerate(st.session_state.productos):

        col1,col2,col3 = st.columns([0.5,0.25,0.25])

        st.session_state.productos[i]["nombre"] = col1.text_input(
            f"Producto {i+1}",
            value=prod["nombre"],
            key=f"prod{i}"
        )

        st.session_state.productos[i]["dosis"] = col2.number_input(
            "Dosis/ha",
            value=prod["dosis"],
            key=f"dosis{i}"
        )

        st.session_state.productos[i]["unidad"] = col3.selectbox(
            "Unidad",
            ["L","Kg"],
            key=f"unidad{i}"
        )

    if st.button("Agregar producto"):
        st.session_state.productos.append({"nombre":"","dosis":0.0,"unidad":"L"})
        st.rerun()

# -------------------------------------------------
# CÁLCULOS
# -------------------------------------------------

    if hectareas > 0 and volumen_aplicacion > 0:

        litros_totales = hectareas * volumen_aplicacion

        mixers_necesarios = math.ceil(litros_totales / capacidad_mixer)

        hectareas_por_mixer = capacidad_mixer / volumen_aplicacion

        st.markdown(
        f"""
        <div class="resumen">
        <h3>Mezcla por tanque mixer</h3>
        Cubre: <b>{hectareas_por_mixer:.2f} ha</b>
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

                st.write(f"**{nombre}**: {cantidad_mixer:.3f} {p['unidad']} por mixer")

                wa_mixer.append(f"- {nombre}: {cantidad_mixer:.2f} {p['unidad']}")
                wa_total.append(f"- {nombre}: {total_lote:.2f} {p['unidad']}")

        st.markdown(
        f"""
        <div class="total">
        <h3>Total del lote</h3>
        Litros totales: <b>{litros_totales:.0f} L</b><br>
        Tanques mixer necesarios: <b>{mixers_necesarios}</b>
        </div>
        """,
        unsafe_allow_html=True
        )

        for t in wa_total:
            st.write(t)

# -------------------------------------------------
# MENSAJE WHATSAPP
# -------------------------------------------------

        msg = (
        f"*ORDEN APLICACION DRON*\n"
        f"Lote: {nombre_lote}\n"
        f"Superficie: {hectareas} ha\n"
        f"Volumen: {volumen_aplicacion} L/ha\n"
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
# DELTA T
# =================================================

with tabs[1]:

    st.subheader("Condiciones ambientales")

    col1,col2 = st.columns(2)

    with col1:
        temp = st.number_input("Temperatura °C", value=25.0)

    with col2:
        hum = st.number_input("Humedad %", value=60.0)

    dt = calculate_delta_t(temp, hum)

    st.metric("Delta-T", f"{dt} °C")

    if 2 <= dt <= 8:
        st.success("Condiciones óptimas para pulverización")

    elif dt < 2:
        st.warning("Riesgo de deriva")

    else:
        st.error("Evaporación alta")

# =================================================
# CLIMA
# =================================================

with tabs[2]:

    st.subheader("Herramientas meteorológicas")

    st.markdown(
    '<a href="https://www.windy.com" target="_blank"><button style="width:100%;padding:15px">Windy</button></a>',
    unsafe_allow_html=True
    )

    st.markdown(
    '<a href="https://www.smn.gob.ar" target="_blank"><button style="width:100%;padding:15px">Servicio Meteorológico Nacional</button></a>',
    unsafe_allow_html=True
    )

    st.markdown(
    '<a href="https://www.swpc.noaa.gov/products/planetary-k-index" target="_blank"><button style="width:100%;padding:15px">Índice KP NOAA (GPS)</button></a>',
    unsafe_allow_html=True
    )

# =================================================
# SOBRE
# =================================================

with tabs[3]:

    st.header("Sobre la aplicación")

    st.write("""
Aplicación simple para pilotos de drones agrícolas.

Permite calcular rápidamente:

• mezcla por tanque mixer  
• cantidad total de producto  
• tanques necesarios por lote  
• generación de orden de aplicación por WhatsApp  

Diseñada para uso directo en el campo.
""")

    st.caption("Desarrollado por Gabriel Carrasco")
