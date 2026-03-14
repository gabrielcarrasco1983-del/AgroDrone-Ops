import streamlit as st
import math
from urllib.parse import quote
from datetime import datetime

st.set_page_config(page_title="AgroDrone Mixer", layout="wide")

# -------------------------------------------------
# GOOGLE ANALYTICS
# -------------------------------------------------

st.markdown("""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-4607XKJ82V"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-4607XKJ82V');
</script>
""", unsafe_allow_html=True)

# -------------------------------------------------
# ESTILO
# -------------------------------------------------

st.markdown("""
<style>

/* ── BASE: fondo claro y texto oscuro forzado ── */
.stApp {
    background: #f8faf5 !important;
}

.stApp, .stApp p, .stApp span, .stApp div,
.stApp li, .stApp strong, .stApp b {
    color: #1c2b1a !important;
}

/* ── TÍTULOS ── */
.stApp h1, .stApp h2, .stApp h3 {
    color: #1a3d18 !important;
    font-weight: 700 !important;
}

/* ── LABELS DE INPUTS ── */
.stApp label,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {
    color: #1c2b1a !important;
    font-weight: 600 !important;
}

/* ── CAMPOS DE TEXTO Y NÚMERO ── */
input, textarea {
    color: #1c2b1a !important;
    background: #ffffff !important;
}

/* ── SELECTBOX ── */
[data-baseweb="select"] div,
[data-baseweb="select"] span {
    color: #1c2b1a !important;
    background: #ffffff !important;
}

/* ── MÉTRICAS ── */
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    color: #1c2b1a !important;
}

/* ── TABS ── */
button[data-baseweb="tab"] p,
button[data-baseweb="tab"] span {
    color: #1a3d18 !important;
    font-weight: 600 !important;
}

/* ── CAPTION ── */
[data-testid="stCaptionContainer"] p {
    color: #3a4f39 !important;
}

/* ── CAJA RESUMEN (verde claro) ── */
.resumen {
    background: #d6edcc !important;
    padding: 18px;
    border-left: 8px solid #2e7d32;
    border-radius: 8px;
    margin-bottom: 12px;
}

.resumen, .resumen * {
    color: #0d1f0c !important;
}

/* ── CAJA TOTAL (amarillo) ── */
.total {
    background: #fff3b0 !important;
    padding: 18px;
    border-top: 6px solid #c49a00;
    border-radius: 8px;
    margin-bottom: 12px;
}

.total, .total * {
    color: #3a2e00 !important;
}

/* ── CAJA HISTORIAL ── */
.hist {
    background: #e0e0e0 !important;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 8px;
}

.hist, .hist * {
    color: #1c2b1a !important;
}

/* ── CAJA ALERTA ── */
.alerta {
    background: #fff0b3 !important;
    padding: 12px;
    border-left: 6px solid #e6a700;
    border-radius: 6px;
    margin-bottom: 10px;
}

.alerta, .alerta * {
    color: #4d3800 !important;
    font-weight: 600 !important;
}

/* ── BOTONES ── */
.stButton > button {
    background: #2e7d32 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    border: none !important;
    width: 100%;
}

.stButton > button:hover {
    background: #1b5e20 !important;
}

/* ── BOTÓN WHATSAPP ── */
.btn-wa {
    display: block;
    width: 100%;
    background: #1a7a3c !important;
    color: #ffffff !important;
    padding: 14px;
    border-radius: 8px;
    font-weight: 700;
    text-align: center;
    text-decoration: none;
    margin-top: 12px;
    font-size: 1rem;
}

/* ── BOTONES CLIMA ── */
.btn-clima {
    display: block;
    width: 100%;
    background: #1a3d18 !important;
    color: #ffffff !important;
    padding: 14px;
    border-radius: 8px;
    font-weight: 700;
    text-align: center;
    text-decoration: none;
    margin-bottom: 10px;
    font-size: 1rem;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# FUNCIONES
# -------------------------------------------------

def calcular_delta_t(temp: float, hum: float) -> float:
    """Calcula el Delta-T a partir de temperatura y humedad relativa."""
    tw = (
        temp * math.atan(0.151977 * (hum + 8.313659) ** 0.5)
        + math.atan(temp + hum)
        - math.atan(hum - 1.676331)
        + 0.00391838 * (hum ** 1.5) * math.atan(0.023101 * hum)
        - 4.686035
    )
    return round(temp - tw, 2)


def calcular_mezcla(hectareas, volumen_aplicacion, capacidad_mixer, productos):
    """Devuelve dict con todos los resultados de la mezcla."""
    litros_totales = hectareas * volumen_aplicacion
    mixers = litros_totales / capacidad_mixer
    hectareas_por_mixer = capacidad_mixer / volumen_aplicacion

    detalle = []
    total_productos = 0.0

    for p in productos:
        if p["dosis"] > 0 and p["nombre"].strip():
            cantidad_mixer = p["dosis"] * hectareas_por_mixer
            total_lote = p["dosis"] * hectareas
            total_productos += total_lote
            detalle.append({
                "nombre": p["nombre"],
                "unidad": p["unidad"],
                "dosis": p["dosis"],
                "cantidad_mixer": cantidad_mixer,
                "total_lote": total_lote,
            })

    agua_total = max(litros_totales - total_productos, 0.0)

    return {
        "litros_totales": litros_totales,
        "mixers": mixers,
        "hectareas_por_mixer": hectareas_por_mixer,
        "total_productos": total_productos,
        "agua_total": agua_total,
        "detalle": detalle,
    }

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

if "productos" not in st.session_state:
    st.session_state.productos = [{"nombre": "", "dosis": 0.0, "unidad": "L"}]

if "historial" not in st.session_state:
    st.session_state.historial = []

# -------------------------------------------------
# TITULO
# -------------------------------------------------

st.title("🚁 AGRODRONE MIXER")

tabs = st.tabs(["🧪 Calculadora", "🌡️ Delta-T", "🌦 Clima", "📋 Historial", "ℹ️ Sobre"])

# =================================================
# CALCULADORA
# =================================================

with tabs[0]:

    st.subheader("Datos del lote")

    # Fila 1: nombre y superficie
    c1, c2 = st.columns(2)
    with c1:
        nombre_lote = st.text_input("Nombre del lote", "Lote sin nombre")
        hectareas = st.number_input("Superficie (ha)", min_value=0.1, value=10.0, step=0.5)
    with c2:
        volumen_aplicacion = st.number_input("Volumen aplicación (L/ha)", min_value=1.0, value=10.0, step=0.5)
        capacidad_mixer = st.number_input("Capacidad mixer (L)", min_value=1.0, value=300.0, step=10.0)

    # Fila 2: cultivo, velocidad y altura
    c3, c4, c5 = st.columns(3)
    with c3:
        cultivo = st.selectbox("Cultivo", ["Soja", "Maíz", "Trigo", "Girasol", "Sorgo", "Otro"])
    with c4:
        velocidad = st.number_input("Velocidad (km/h)", min_value=1.0, value=20.0, step=0.5)
    with c5:
        altura = st.number_input("Altura de vuelo (m)", min_value=0.5, value=3.0, step=0.5)

    st.divider()

    # -------------------------------------------------
    # PRODUCTOS
    # -------------------------------------------------

    st.subheader("Productos")

    for i, prod in enumerate(st.session_state.productos):

        col1, col2, col3, col4 = st.columns([0.44, 0.22, 0.22, 0.12])

        st.session_state.productos[i]["nombre"] = col1.text_input(
            f"Producto {i + 1}", value=prod["nombre"], key=f"prod_{i}"
        )
        st.session_state.productos[i]["dosis"] = col2.number_input(
            "Dosis/ha", value=float(prod["dosis"]), min_value=0.0, key=f"dosis_{i}"
        )
        st.session_state.productos[i]["unidad"] = col3.selectbox(
            "Unidad", ["L", "Kg"], key=f"unidad_{i}"
        )

        if len(st.session_state.productos) > 1:
            if col4.button("🗑️", key=f"del_{i}"):
                st.session_state.productos.pop(i)
                st.rerun()

    if st.button("➕ Agregar producto"):
        st.session_state.productos.append({"nombre": "", "dosis": 0.0, "unidad": "L"})
        st.rerun()

    st.divider()

    # -------------------------------------------------
    # CALCULOS
    # -------------------------------------------------

    res = calcular_mezcla(hectareas, volumen_aplicacion, capacidad_mixer, st.session_state.productos)

    if res["total_productos"] > res["litros_totales"]:
        st.markdown(
            '<div class="alerta">⚠️ Las dosis ingresadas superan el volumen de aplicación. Revisá los valores.</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div class="resumen">
        <b>📐 Hectáreas por mixer:</b> {res['hectareas_por_mixer']:.2f} ha<br>
        <b>🔁 Mixers necesarios:</b> {res['mixers']:.2f}
        </div>
        """,
        unsafe_allow_html=True
    )

    if res["detalle"]:
        st.subheader("Por mixer")
        for p in res["detalle"]:
            st.write(f"**{p['nombre']}**: {p['cantidad_mixer']:.3f} {p['unidad']}")

    st.markdown(
        f"""
        <div class="total">
        <b>💧 Litros totales aplicación:</b> {res['litros_totales']:.0f} L<br>
        <b>🧴 Producto total:</b> {res['total_productos']:.2f} L/Kg<br>
        <b>🪣 Agua total:</b> {res['agua_total']:.2f} L
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------------------------
    # WHATSAPP
    # -------------------------------------------------

    wa_mixer = [
        f"- {p['nombre']}: {p['cantidad_mixer']:.2f} {p['unidad']} ({p['dosis']:.2f} {p['unidad']}/ha)"
        for p in res["detalle"]
    ]
    wa_total = [
        f"- {p['nombre']}: {p['total_lote']:.2f} {p['unidad']} ({p['dosis']:.2f} {p['unidad']}/ha)"
        for p in res["detalle"]
    ]

    msg = (
        f"*ORDEN APLICACION DRON*\n"
        f"Lote: {nombre_lote}\n"
        f"Cultivo: {cultivo}\n"
        f"Superficie: {hectareas} ha\n"
        f"Volumen: {volumen_aplicacion} L/ha\n"
        f"Velocidad: {velocidad} km/h\n"
        f"Altura: {altura} m\n"
        f"Mixers: {res['mixers']:.2f}\n"
        f"\n--- POR MIXER ---\n"
        + "\n".join(wa_mixer)
        + "\n\n--- TOTAL LOTE ---\n"
        + "\n".join(wa_total)
        + f"\nAgua total: {res['agua_total']:.2f} L"
    )

    st.markdown(
        f'<a class="btn-wa" href="https://wa.me/?text={quote(msg)}" target="_blank">'
        '📲 Enviar orden por WhatsApp</a>',
        unsafe_allow_html=True
    )

    # -------------------------------------------------
    # GUARDAR HISTORIAL
    # -------------------------------------------------

    if st.button("💾 Guardar en historial"):
        registro = {
            "fecha": datetime.now().strftime("%d/%m %H:%M"),
            "lote": nombre_lote,
            "cultivo": cultivo,
            "ha": hectareas,
            "mixers": round(res["mixers"], 2),
            "productos": [
                f"{p['nombre']} {p['dosis']:.2f} {p['unidad']}/ha"
                for p in res["detalle"]
            ],
        }
        st.session_state.historial.append(registro)
        st.success("✅ Guardado en historial")

# =================================================
# DELTA T
# =================================================

with tabs[1]:

    st.subheader("Condiciones ambientales")

    col_t, col_h = st.columns(2)

    temp = col_t.number_input("Temperatura (°C)", value=25.0, step=0.5)
    hum = col_h.number_input("Humedad relativa (%)", value=60.0, step=1.0, min_value=1.0, max_value=100.0)

    dt = calcular_delta_t(temp, hum)

    st.metric("Delta T", f"{dt} °C")

    if 2 <= dt <= 8:
        st.success("✅ Condiciones óptimas para aplicar")
    elif dt < 2:
        st.warning("⚠️ Riesgo de deriva — humedad muy alta")
    else:
        st.error("🔴 Evaporación alta — condiciones no recomendadas")

    st.divider()
    st.caption("Delta-T = diferencia entre temperatura del aire y temperatura de bulbo húmedo. Rango ideal: 2 a 8 °C.")

# =================================================
# CLIMA
# =================================================

with tabs[2]:

    st.subheader("Acceso rápido al clima")

    st.markdown('<a class="btn-clima" href="https://www.windy.com" target="_blank">🌬️ Windy</a>', unsafe_allow_html=True)
    st.markdown('<a class="btn-clima" href="https://www.smn.gob.ar" target="_blank">🇦🇷 Servicio Meteorológico Nacional</a>', unsafe_allow_html=True)
    st.markdown('<a class="btn-clima" href="https://www.swpc.noaa.gov/products/planetary-k-index" target="_blank">🛰️ Índice KP NOAA (GPS)</a>', unsafe_allow_html=True)

# =================================================
# HISTORIAL
# =================================================

with tabs[3]:

    st.subheader("Aplicaciones guardadas")

    if not st.session_state.historial:
        st.info("Todavía no hay aplicaciones guardadas en esta sesión.")
    else:
        if st.button("🗑️ Limpiar historial"):
            st.session_state.historial = []
            st.rerun()

        for reg in reversed(st.session_state.historial):
            productos_str = " | ".join(reg.get("productos", []))
            st.markdown(
                f"""
                <div class="hist">
                📅 {reg['fecha']} &nbsp;|&nbsp;
                🌾 {reg['lote']} ({reg.get('cultivo', '-')}) &nbsp;|&nbsp;
                {reg['ha']} ha &nbsp;|&nbsp;
                {reg['mixers']} mixers<br>
                <small>🧪 {productos_str}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

# =================================================
# SOBRE
# =================================================

with tabs[4]:

    st.subheader("AgroDrone Mixer")

    st.write("""
Aplicación diseñada para pilotos de drones agrícolas.

**Funciones:**
- Cálculo de mezcla por tanque
- Total de agua y producto
- Mixers necesarios (valor decimal)
- Envío de orden por WhatsApp con cultivo, velocidad y altura
- Delta-T para condiciones ambientales
- Historial de aplicaciones por sesión
- Acceso rápido a clima y GPS
""")

    st.divider()
    st.caption("Desarrollado por Gabriel Carrasco 🚁")
