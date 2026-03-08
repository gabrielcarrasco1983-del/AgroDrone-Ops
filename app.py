import streamlit as st
import math
from urllib.parse import quote
from datetime import datetime

st.set_page_config(page_title="AgroDrone Mixer", layout="wide")

# -------------------------------------------------
# ESTILO AGRO (MEJOR CONTRASTE PARA CELULAR)
# -------------------------------------------------

st.markdown("""
<style>

.stApp{
background:#f8faf5;
color:#1c2b1a;
}

/* TITULOS */

h1,h2,h3{
color:#2e5d2c;
font-weight:700;
}

/* TEXTO GENERAL */

p, span, label, div{
color:#1c2b1a !important;
}

/* INPUTS */

input{
color:#1c2b1a !important;
background:#ffffff !important;
}

/* SELECT */

select{
color:#1c2b1a !important;
background:#ffffff !important;
}

/* NUMBERS */

[data-baseweb="input"]{
color:#1c2b1a !important;
}

/* RESUMEN */

.resumen{
background:#eef6ea;
padding:18px;
border-left:8px solid #4CAF50;
border-radius:8px;
color:#1c2b1a;
font-weight:500;
}

/* TOTAL */

.total{
background:#fff8d6;
padding:18px;
border-top:6px solid #d4b106;
border-radius:8px;
color:#1c2b1a;
font-weight:600;
}

/* HISTORIAL */

.hist{
background:#f3f3f3;
padding:10px;
border-radius:6px;
margin-bottom:5px;
color:#1c2b1a;
}

/* BOTONES STREAMLIT */

.stButton>button{
background:#4CAF50;
color:white;
font-weight:600;
border-radius:6px;
}

/* TABS */

button[data-baseweb="tab"]{
font-weight:600;
color:#2e5d2c;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# FUNCION DELTA T
# -------------------------------------------------

def calculate_delta_t(temp, hum):

    tw = temp * math.atan(0.151977 * (hum + 8.313659)**0.5) + \
         math.atan(temp + hum) - math.atan(hum - 1.676331) + \
         0.00391838 * (hum**1.5) * math.atan(0.023101 * hum) - 4.686035

    return round(temp - tw,2)

# -------------------------------------------------
# VARIABLES SESSION
# -------------------------------------------------

if "productos" not in st.session_state:
    st.session_state.productos = [{"nombre":"", "dosis":0.0, "unidad":"L"}]

if "historial" not in st.session_state:
    st.session_state.historial = []

# -------------------------------------------------
# TITULO
# -------------------------------------------------

st.title("AGRODRONE MIXER")

tabs = st.tabs([
"Calculadora",
"Delta-T",
"Clima",
"Historial",
"Sobre"
])

# =================================================
# CALCULADORA
# =================================================

with tabs[0]:

    st.subheader("Datos del lote")

    c1,c2,c3 = st.columns(3)

    with c1:
        nombre_lote = st.text_input("Nombre del lote","Lote sin nombre")
        hectareas = st.number_input("Superficie (ha)",10.0)

    with c2:
        volumen_aplicacion = st.number_input(
    "Volumen aplicación (L/ha)",
    min_value=1.0,
    value=10.0,
    step=0.5
)

    with c3:
        modo_campo = st.checkbox("Modo pantalla campo")

    if modo_campo:
        st.markdown("<style>body{zoom:120%;}</style>", unsafe_allow_html=True)

    st.divider()

# -------------------------------------------------
# PRODUCTOS
# -------------------------------------------------

    st.subheader("Productos")

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
# CALCULOS
# -------------------------------------------------

    if hectareas > 0 and volumen_aplicacion > 0:

        litros_totales = hectareas * volumen_aplicacion
        mixers = litros_totales / capacidad_mixer
        hectareas_por_mixer = capacidad_mixer / volumen_aplicacion

        total_productos = 0
        wa_mixer=[]
        wa_total=[]

        st.markdown(
        f"""
        <div class="resumen">
        <b>Hectáreas por mixer:</b> {hectareas_por_mixer:.2f} ha
        </div>
        """,
        unsafe_allow_html=True)

        for p in st.session_state.productos:

            if p["dosis"]>0:

                nombre=p["nombre"] if p["nombre"] else "Producto"

                cantidad_mixer=p["dosis"]*hectareas_por_mixer
                total_lote=p["dosis"]*hectareas

                total_productos+=total_lote

                st.write(f"**{nombre}**: {cantidad_mixer:.3f} {p['unidad']} por mixer")

                wa_mixer.append(f"- {nombre}: {cantidad_mixer:.2f} {p['unidad']}")
                wa_total.append(f"- {nombre}: {total_lote:.2f} {p['unidad']}")

        agua_total = litros_totales - total_productos

        st.markdown(
        f"""
        <div class="total">

        <b>Litros totales aplicación:</b> {litros_totales:.0f} L  
        <b>Producto total:</b> {total_productos:.2f} L/Kg  
        <b>Agua total:</b> {agua_total:.2f} L  

        <br>

        <b>Mixers necesarios:</b> {mixers:.2f}

        </div>
        """,
        unsafe_allow_html=True)

        for t in wa_total:
            st.write(t)

# -------------------------------------------------
# WHATSAPP
# -------------------------------------------------

        msg=(
        f"*ORDEN APLICACION DRON*\n"
        f"Lote: {nombre_lote}\n"
        f"Superficie: {hectareas} ha\n"
        f"Volumen: {volumen_aplicacion} L/ha\n"
        f"Mixers: {mixers:.2f}\n"
        f"\n--- POR MIXER ---\n"
        +"\n".join(wa_mixer)+
        "\n\n--- TOTAL LOTE ---\n"+
        "\n".join(wa_total)+
        f"\nAgua total: {agua_total:.2f} L"
        )

        st.markdown(
        f'<a href="https://wa.me/?text={quote(msg)}" target="_blank">'
        '<button style="width:100%;background:#25D366;color:white;padding:14px;border:none;border-radius:8px;font-weight:bold">'
        'Enviar orden por WhatsApp'
        '</button></a>',
        unsafe_allow_html=True
        )

# -------------------------------------------------
# GUARDAR HISTORIAL
# -------------------------------------------------

        if st.button("Guardar en historial"):

            registro={
            "fecha":datetime.now().strftime("%d/%m %H:%M"),
            "lote":nombre_lote,
            "ha":hectareas,
            "mixers":round(mixers,2)
            }

            st.session_state.historial.append(registro)

# =================================================
# DELTA T
# =================================================

with tabs[1]:

    st.subheader("Condiciones ambientales")

    t,h=st.columns(2)

    temp=t.number_input("Temperatura",25.0)
    hum=h.number_input("Humedad",60.0)

    dt=calculate_delta_t(temp,hum)

    st.metric("Delta T",f"{dt} °C")

    if 2<=dt<=8:
        st.success("Condiciones óptimas")

    elif dt<2:
        st.warning("Riesgo deriva")

    else:
        st.error("Evaporación alta")

# =================================================
# CLIMA
# =================================================

with tabs[2]:

    st.markdown(
    '<a href="https://www.windy.com" target="_blank"><button style="width:100%;padding:15px">Windy</button></a>',
    unsafe_allow_html=True)

    st.markdown(
    '<a href="https://www.smn.gob.ar" target="_blank"><button style="width:100%;padding:15px">Servicio Meteorológico</button></a>',
    unsafe_allow_html=True)

    st.markdown(
    '<a href="https://www.swpc.noaa.gov/products/planetary-k-index" target="_blank"><button style="width:100%;padding:15px">Índice KP NOAA</button></a>',
    unsafe_allow_html=True)

# =================================================
# HISTORIAL
# =================================================

with tabs[3]:

    st.subheader("Aplicaciones guardadas")

    for h in reversed(st.session_state.historial):

        st.markdown(
        f"""
        <div class="hist">
        {h['fecha']} | {h['lote']} | {h['ha']} ha | {h['mixers']} mixers
        </div>
        """,
        unsafe_allow_html=True)

# =================================================
# SOBRE
# =================================================

with tabs[4]:

    st.write("""
Aplicación diseñada para pilotos de drones agrícolas.

Funciones:

• cálculo de mezcla por tanque  
• total de agua y producto  
• mixers necesarios (decimal)  
• envío de orden por WhatsApp  
• Delta-T  
• historial de aplicaciones
""")

    st.caption("Gabriel Carrasco")

