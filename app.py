import streamlit as st
import math
from urllib.parse import quote
from datetime import datetime
from fpdf import FPDF

st.set_page_config(
    page_title="AgroDrone Mixer",
    page_icon="dronemixer.png",
    layout="wide"
)

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

.stApp { background: #f8faf5 !important; }

.stApp, .stApp p, .stApp span, .stApp div,
.stApp li, .stApp strong, .stApp b {
    color: #1c2b1a !important;
}

.stApp h1, .stApp h2, .stApp h3 {
    color: #1a3d18 !important;
    font-weight: 700 !important;
}

.stApp label,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {
    color: #1c2b1a !important;
    font-weight: 600 !important;
}

input, textarea {
    color: #1c2b1a !important;
    background: #ffffff !important;
}

[data-baseweb="select"] div,
[data-baseweb="select"] span {
    color: #1c2b1a !important;
    background: #ffffff !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    color: #1c2b1a !important;
}

button[data-baseweb="tab"] p,
button[data-baseweb="tab"] span {
    color: #1a3d18 !important;
    font-weight: 600 !important;
}

[data-testid="stCaptionContainer"] p {
    color: #3a4f39 !important;
}

.resumen {
    background: #d6edcc !important;
    padding: 18px;
    border-left: 8px solid #2e7d32;
    border-radius: 8px;
    margin-bottom: 12px;
}
.resumen, .resumen * { color: #0d1f0c !important; }

.total {
    background: #fff3b0 !important;
    padding: 18px;
    border-top: 6px solid #c49a00;
    border-radius: 8px;
    margin-bottom: 12px;
}
.total, .total * { color: #3a2e00 !important; }

.bit-entry {
    background: #eaf4e6 !important;
    padding: 14px 16px;
    border-left: 6px solid #2e7d32;
    border-radius: 8px;
    margin-bottom: 6px;
}
.bit-entry, .bit-entry * { color: #0d1f0c !important; }

.bit-manual {
    background: #e8f0fe !important;
    padding: 14px 16px;
    border-left: 6px solid #3c6bc9;
    border-radius: 8px;
    margin-bottom: 6px;
}
.bit-manual, .bit-manual * { color: #0d1b3e !important; }

.semaforo-apto {
    background: #d6edcc !important;
    border-left: 10px solid #2e7d32;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 12px;
}
.semaforo-apto * { color: #0d1f0c !important; }

.semaforo-precaucion {
    background: #fff3b0 !important;
    border-left: 10px solid #c49a00;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 12px;
}
.semaforo-precaucion * { color: #3a2e00 !important; }

.semaforo-no-apto {
    background: #fde8e8 !important;
    border-left: 10px solid #c62828;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 12px;
}
.semaforo-no-apto * { color: #4a0000 !important; }

.condiciones-fijadas {
    background: #e8f5e9 !important;
    padding: 10px 14px;
    border-radius: 6px;
    border: 1px solid #a5d6a7;
    margin-bottom: 10px;
    font-size: 0.9rem;
}
.condiciones-fijadas * { color: #1b5e20 !important; }

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

.stButton > button {
    background: #2e7d32 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    border: none !important;
    width: 100%;
}
.stButton > button:hover { background: #1b5e20 !important; }

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
# CONSTANTES
# -------------------------------------------------

CULTIVOS = [
    "Soja", "Maíz", "Maíz 2da", "Trigo", "Cebada",
    "Girasol", "Sorgo", "Barbecho", "Pastura", "Otro"
]

SEMILLAS = [
    "Avena", "Rye Grass", "Festuca", "Trébol blanco", "Trébol rojo",
    "Cebada", "Mezcla de pasturas", "Otro"
]

FERTILIZANTES = [
    "Urea", "DAP (Fosfato diamónico)", "Superfosfato simple",
    "Superfosfato triple", "Mezcla", "Otro"
]

ESPECIES_MEZCLA = [
    "Rye Grass", "Festuca", "Trébol blanco", "Trébol rojo",
    "Melilotus", "Cebadilla", "Agropiro", "Pasto ovillo", "Otro"
]

DIRECCIONES_VIENTO = ["N", "NE", "E", "SE", "S", "SO", "O", "NO", "Variable"]

# -------------------------------------------------
# FUNCIONES DE CÁLCULO
# -------------------------------------------------

def calcular_delta_t(temp: float, hum: float) -> float:
    tw = (
        temp * math.atan(0.151977 * (hum + 8.313659) ** 0.5)
        + math.atan(temp + hum)
        - math.atan(hum - 1.676331)
        + 0.00391838 * (hum ** 1.5) * math.atan(0.023101 * hum)
        - 4.686035
    )
    return round(temp - tw, 2)


def evaluar_semaforo(delta_t: float, viento: float) -> dict:
    """
    Devuelve estado, clase CSS, etiqueta y razón del semáforo unificado.
    Criterios:
      - Viento > 25 km/h → NO APTO (deriva severa)
      - Viento > 15 km/h + Delta-T fuera de rango → NO APTO
      - Delta-T < 2 → NO APTO (inversión térmica)
      - Delta-T > 10 → NO APTO (evaporación excesiva)
      - Viento > 15 km/h pero Delta-T OK → PRECAUCIÓN
      - Delta-T 2–4 o 8–10 → PRECAUCIÓN
      - Delta-T 4–8 y viento ≤ 15 → APTO
    """
    razones = []

    if viento > 25:
        razones.append(f"Viento {viento:.0f} km/h: riesgo de deriva severa")
        return {"estado": "NO APTO", "css": "semaforo-no-apto", "icono": "🔴", "razones": razones}

    if delta_t < 2:
        razones.append(f"Delta-T {delta_t} °C: riesgo de inversión térmica")
    if delta_t > 10:
        razones.append(f"Delta-T {delta_t} °C: evaporación excesiva")
    if viento > 15:
        razones.append(f"Viento {viento:.0f} km/h: precaución por deriva")

    if delta_t < 2 or delta_t > 10:
        return {"estado": "NO APTO", "css": "semaforo-no-apto", "icono": "🔴", "razones": razones}

    if viento > 15 or delta_t < 4 or delta_t > 8:
        if not razones:
            if delta_t < 4:
                razones.append(f"Delta-T {delta_t} °C: condición límite baja")
            elif delta_t > 8:
                razones.append(f"Delta-T {delta_t} °C: condición límite alta")
        return {"estado": "PRECAUCIÓN", "css": "semaforo-precaucion", "icono": "⚠️", "razones": razones}

    razones.append("Delta-T y viento dentro del rango óptimo")
    return {"estado": "APTO", "css": "semaforo-apto", "icono": "✅", "razones": razones}


def calcular_mezcla_liquidos(hectareas, volumen_aplicacion, capacidad_mixer, productos):
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


def calcular_solidos(hectareas, dosis_kgha):
    return round(hectareas * dosis_kgha, 2)


import math as _math
def bolsas_necesarias(kg_totales, kg_bolsa):
    return _math.ceil(kg_totales / kg_bolsa)


def condiciones_str(cond: dict) -> str:
    """Devuelve string resumido de condiciones para mostrar en bitácora."""
    if not cond:
        return "Sin condiciones registradas"
    return (
        f"{cond['temp']}°C · {cond['hum']}% HR · "
        f"Delta-T {cond['delta_t']} °C · "
        f"Viento {cond['viento']} km/h {cond['dir_viento']} · "
        f"{cond['icono']} {cond['estado']}"
    )


# -------------------------------------------------
# FUNCIÓN PDF BITÁCORA
# -------------------------------------------------

def _safe(text: str) -> str:
    """Normaliza tildes y elimina todo carácter fuera de latin-1 (emojis incluidos)."""
    repl = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
        "ñ": "n", "Ñ": "N", "ü": "u", "Ü": "U",
        "\u2019": "'", "\u201c": '"', "\u201d": '"',
    }
    for k, v in repl.items():
        text = text.replace(k, v)
    return text.encode("latin-1", errors="ignore").decode("latin-1")


def generar_pdf_bitacora(bitacora: list) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Encabezado
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(26, 61, 24)
    pdf.cell(0, 12, "AGRODRONE MIXER", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(60, 90, 58)
    pdf.cell(0, 8, "Bitacora de Campana", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 120, 100)
    pdf.cell(0, 6, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(6)

    if not bitacora:
        pdf.set_font("Helvetica", "I", 11)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 10, "Sin registros en la bitacora.", ln=True, align="C")
        return bytes(pdf.output())

    for entry in bitacora:
        tipo_label = "Liquidos" if entry.get("tipo") == "Liquidos" else (
            "Solidos" if entry.get("tipo") == "Solidos" else _safe(entry.get("tipo", ""))
        )

        # Cabecera entrada
        pdf.set_fill_color(214, 237, 204)
        pdf.set_text_color(13, 31, 12)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(
            0, 9,
            f"[{tipo_label}]   {entry.get('fecha', '')}   |   Piloto: {_safe(entry.get('piloto', '-'))}",
            ln=True, fill=True
        )

        # Lote / cultivo / ha
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 50, 28)
        pdf.cell(
            0, 7,
            f"Lote: {_safe(entry.get('lote', '-'))}   |   Cultivo: {_safe(entry.get('cultivo', '-'))}   |   {entry.get('ha', 0)} ha",
            ln=True
        )

        # Productos
        for prod in entry.get("productos", []):
            pdf.cell(6)
            pdf.cell(0, 6, f"- {_safe(prod)}", ln=True)

        # Condiciones ambientales
        cond = entry.get("condiciones")
        if cond:
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(26, 61, 24)
            pdf.set_fill_color(232, 245, 233)
            cond_texto = (
                f"Condiciones: {cond['temp']}C  {cond['hum']}% HR  "
                f"Delta-T {cond['delta_t']}C  "
                f"Viento {cond['viento']} km/h {cond['dir_viento']}  "
                f"[ {cond['estado']} ]"
            )
            pdf.cell(0, 7, _safe(cond_texto), ln=True, fill=True)

        # Observaciones
        obs = entry.get("obs", "").strip()
        if obs:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(70, 100, 70)
            pdf.multi_cell(0, 6, f"Obs: {_safe(obs)}")

        pdf.set_text_color(30, 50, 28)
        pdf.ln(4)

    # Totales
    pdf.set_fill_color(255, 243, 176)
    pdf.set_text_color(58, 46, 0)
    pdf.set_font("Helvetica", "B", 10)
    total_ha = sum(e.get("ha", 0) for e in bitacora)
    pdf.cell(
        0, 9,
        f"Total registros: {len(bitacora)}   |   Hectareas totales: {total_ha:.1f} ha",
        ln=True, fill=True
    )

    return bytes(pdf.output())


# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

if "productos" not in st.session_state:
    st.session_state.productos = [{"nombre": "", "dosis": 0.0, "unidad": "L"}]

if "bitacora" not in st.session_state:
    st.session_state.bitacora = []

if "receta_mezcla" not in st.session_state:
    st.session_state.receta_mezcla = [{"especie": "Rye Grass", "kgha": 0.0}]

if "piloto_sesion" not in st.session_state:
    st.session_state.piloto_sesion = ""

# Condiciones ambientales fijadas para la sesión
if "condiciones_sesion" not in st.session_state:
    st.session_state.condiciones_sesion = None

# -------------------------------------------------
# ENCABEZADO CON LOGO
# -------------------------------------------------

col_logo, col_titulo = st.columns([0.10, 0.90])
with col_logo:
    st.image("dronemixer.png", width=90)
with col_titulo:
    st.markdown(
        """
        <div style="padding-top:6px;">
            <h1 style="margin:0; padding:0; color:#1a3d18; font-size:2rem; font-weight:800; line-height:1.1;">
                AGRODRONE MIXER
            </h1>
            <small style="color:#3a4f39; font-size:0.85rem;">
                Calculadora para pilotos de drones agrícolas
            </small>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<hr style='margin:8px 0 16px 0; border-color:#c8e6c9;'>", unsafe_allow_html=True)

# Mostrar condiciones fijadas en el encabezado global si existen
if st.session_state.condiciones_sesion:
    cond = st.session_state.condiciones_sesion
    st.markdown(
        f"""
        <div class="condiciones-fijadas">
        🌡️ <b>Condiciones fijadas:</b>
        {cond['temp']}°C · {cond['hum']}% HR ·
        Delta-T <b>{cond['delta_t']} °C</b> ·
        🌬️ {cond['viento']} km/h {cond['dir_viento']} ·
        {cond['icono']} <b>{cond['estado']}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

tabs = st.tabs([
    "🧪 Líquidos",
    "🌾 Sólidos",
    "🌡️ Delta-T",
    "🌦 Clima",
    "📓 Bitácora",
    "ℹ️ Sobre"
])

# =================================================
# TAB 1 — LÍQUIDOS
# =================================================

with tabs[0]:

    st.subheader("Datos del lote")

    c1, c2 = st.columns(2)
    with c1:
        nombre_lote = st.text_input("Nombre del lote", "Lote sin nombre", key="liq_nombre")
        hectareas = st.number_input("Superficie (ha)", min_value=0.1, value=10.0, step=0.5, key="liq_ha")
    with c2:
        volumen_aplicacion = st.number_input("Volumen aplicación (L/ha)", min_value=1.0, value=10.0, step=0.5)
        capacidad_mixer = st.number_input("Capacidad mixer (L)", min_value=1.0, value=300.0, step=10.0)

    c3, c4, c5 = st.columns(3)
    with c3:
        cultivo = st.selectbox("Cultivo", CULTIVOS, key="liq_cultivo")
        if cultivo == "Otro":
            cultivo = st.text_input("Especificá el cultivo", key="liq_cultivo_otro")
    with c4:
        velocidad = st.number_input("Velocidad (km/h)", min_value=1.0, value=20.0, step=0.5, key="liq_vel")
    with c5:
        altura = st.number_input("Altura de vuelo (m)", min_value=0.5, value=3.0, step=0.5, key="liq_alt")

    st.divider()
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

    if st.button("➕ Agregar producto", key="add_prod"):
        st.session_state.productos.append({"nombre": "", "dosis": 0.0, "unidad": "L"})
        st.rerun()

    st.divider()

    res = calcular_mezcla_liquidos(hectareas, volumen_aplicacion, capacidad_mixer, st.session_state.productos)

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

    wa_mixer = [
        f"- {p['nombre']}: {p['cantidad_mixer']:.2f} {p['unidad']} ({p['dosis']:.2f} {p['unidad']}/ha)"
        for p in res["detalle"]
    ]
    wa_total = [
        f"- {p['nombre']}: {p['total_lote']:.2f} {p['unidad']} ({p['dosis']:.2f} {p['unidad']}/ha)"
        for p in res["detalle"]
    ]

    cond_wa = ""
    if st.session_state.condiciones_sesion:
        c = st.session_state.condiciones_sesion
        cond_wa = (
            f"\n\n--- CONDICIONES AMBIENTALES ---\n"
            f"Temp: {c['temp']}°C | HR: {c['hum']}% | Delta-T: {c['delta_t']} °C\n"
            f"Viento: {c['viento']} km/h {c['dir_viento']} | {c['icono']} {c['estado']}"
        )

    msg_liq = (
        f"*ORDEN APLICACION DRON - LÍQUIDOS*\n"
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
        + cond_wa
    )

    st.markdown(
        f'<a class="btn-wa" href="https://wa.me/?text={quote(msg_liq)}" target="_blank">'
        '📲 Enviar orden por WhatsApp</a>',
        unsafe_allow_html=True
    )

    if st.button("💾 Guardar en bitácora", key="save_liq"):
        st.session_state.bitacora.append({
            "tipo": "Liquidos",
            "fecha": datetime.now().strftime("%d/%m %H:%M"),
            "lote": nombre_lote,
            "cultivo": cultivo,
            "ha": hectareas,
            "piloto": st.session_state.piloto_sesion or "-",
            "productos": [
                f"{p['nombre']} {p['dosis']:.2f} {p['unidad']}/ha"
                for p in res["detalle"]
            ],
            "condiciones": st.session_state.condiciones_sesion,
            "obs": "",
        })
        st.success("✅ Guardado en bitácora")

# =================================================
# TAB 2 — SÓLIDOS
# =================================================

with tabs[1]:

    st.subheader("Datos del lote")

    s1, s2 = st.columns(2)
    with s1:
        sol_nombre = st.text_input("Nombre del lote", "Lote sin nombre", key="sol_nombre")
        sol_ha = st.number_input("Superficie (ha)", min_value=0.1, value=10.0, step=0.5, key="sol_ha")
    with s2:
        sol_cultivo = st.selectbox("Cultivo", CULTIVOS, key="sol_cultivo")
        if sol_cultivo == "Otro":
            sol_cultivo = st.text_input("Especificá el cultivo", key="sol_cultivo_otro")

    s3, s4 = st.columns(2)
    with s3:
        sol_velocidad = st.number_input("Velocidad (km/h)", min_value=1.0, value=20.0, step=0.5, key="sol_vel")
    with s4:
        sol_altura = st.number_input("Altura de vuelo (m)", min_value=0.5, value=3.0, step=0.5, key="sol_alt")

    st.divider()
    st.subheader("Producto")

    tipo_producto = st.radio(
        "Tipo de producto",
        ["Semillas", "Fertilizantes", "Otro"],
        horizontal=True,
        key="sol_tipo"
    )

    es_mezcla = False
    nombre_producto_final = ""
    dosis_total_kgha = 0.0

    if tipo_producto == "Semillas":
        sel_semilla = st.selectbox("Semilla", SEMILLAS, key="sol_semilla")
        if sel_semilla == "Mezcla de pasturas":
            es_mezcla = True
            nombre_producto_final = "Mezcla de pasturas"
        elif sel_semilla == "Otro":
            nombre_producto_final = st.text_input("Especificá la semilla", key="sol_semilla_otro")
        else:
            nombre_producto_final = sel_semilla

    elif tipo_producto == "Fertilizantes":
        sel_ferti = st.selectbox("Fertilizante", FERTILIZANTES, key="sol_ferti")
        if sel_ferti == "Otro":
            nombre_producto_final = st.text_input("Especificá el fertilizante", key="sol_ferti_otro")
        else:
            nombre_producto_final = sel_ferti

    else:
        nombre_producto_final = st.text_input("Nombre del producto", key="sol_otro_nombre")

    receta_lineas = []

    if es_mezcla:
        st.markdown("#### 🌿 Receta de la mezcla")
        st.caption("Ingresá cada especie con su dosis en kg/ha")

        for i, esp in enumerate(st.session_state.receta_mezcla):
            r1, r2, r3 = st.columns([0.50, 0.35, 0.15])
            especie_sel = r1.selectbox(
                f"Especie {i + 1}",
                ESPECIES_MEZCLA,
                index=ESPECIES_MEZCLA.index(esp["especie"]) if esp["especie"] in ESPECIES_MEZCLA else 0,
                key=f"esp_{i}"
            )
            if especie_sel == "Otro":
                especie_sel = r1.text_input("Especificá la especie", key=f"esp_otro_{i}")
            st.session_state.receta_mezcla[i]["especie"] = especie_sel
            st.session_state.receta_mezcla[i]["kgha"] = r2.number_input(
                "kg/ha", value=float(esp["kgha"]), min_value=0.0, step=0.1, key=f"esp_kg_{i}"
            )
            if len(st.session_state.receta_mezcla) > 1:
                if r3.button("🗑️", key=f"del_esp_{i}"):
                    st.session_state.receta_mezcla.pop(i)
                    st.rerun()

        if st.button("➕ Agregar especie", key="add_esp"):
            st.session_state.receta_mezcla.append({"especie": "Rye Grass", "kgha": 0.0})
            st.rerun()

        dosis_total_kgha = sum(
            e["kgha"] for e in st.session_state.receta_mezcla if e["kgha"] > 0
        )
        receta_lineas = [
            f"  - {e['especie']}: {e['kgha']:.2f} kg/ha"
            for e in st.session_state.receta_mezcla if e["kgha"] > 0
        ]
        st.markdown(f"**Dosis total mezcla: {dosis_total_kgha:.2f} kg/ha**")

    else:
        dosis_total_kgha = st.number_input(
            "Dosis (kg/ha)", min_value=0.0, value=0.0, step=0.5, key="sol_dosis"
        )

    st.divider()
    st.subheader("Presentación")

    presentacion = st.radio(
        "¿Cómo viene el producto?",
        ["Granel / Tolva", "Bolsas"],
        horizontal=True,
        key="sol_presentacion"
    )

    kg_bolsa = None
    if presentacion == "Bolsas":
        kg_bolsa = st.number_input(
            "Kilos por bolsa", min_value=0.1, value=25.0, step=0.5, key="sol_kg_bolsa"
        )

    st.divider()

    kg_totales = calcular_solidos(sol_ha, dosis_total_kgha)

    if dosis_total_kgha > 0:
        resumen_html = f"""
        <div class="resumen">
        <b>⚖️ Dosis:</b> {dosis_total_kgha:.2f} kg/ha<br>
        <b>📦 Kilos totales:</b> {kg_totales:.0f} kg
        """
        if presentacion == "Bolsas" and kg_bolsa and kg_bolsa > 0:
            n_bolsas = bolsas_necesarias(kg_totales, kg_bolsa)
            resumen_html += f"<br><b>🗂️ Bolsas necesarias ({kg_bolsa:.0f} kg c/u):</b> {n_bolsas}"
        resumen_html += "</div>"
        st.markdown(resumen_html, unsafe_allow_html=True)

        lineas_wa = ["*ORDEN APLICACION DRON - SÓLIDOS*"]
        lineas_wa.append(f"Lote: {sol_nombre}")
        lineas_wa.append(f"Cultivo: {sol_cultivo}")
        lineas_wa.append(f"Superficie: {sol_ha} ha")
        lineas_wa.append(f"Velocidad: {sol_velocidad} km/h")
        lineas_wa.append(f"Altura: {sol_altura} m")
        lineas_wa.append(f"Producto: {nombre_producto_final}")
        if receta_lineas:
            lineas_wa.extend(receta_lineas)
        lineas_wa.append(f"Dosis total: {dosis_total_kgha:.2f} kg/ha")
        lineas_wa.append(f"Total: {kg_totales:.0f} kg")
        if presentacion == "Bolsas" and kg_bolsa and kg_bolsa > 0:
            n_bolsas = bolsas_necesarias(kg_totales, kg_bolsa)
            lineas_wa.append(f"Presentación: Bolsas {kg_bolsa:.0f} kg")
            lineas_wa.append(f"Bolsas necesarias: {n_bolsas}")
        else:
            lineas_wa.append("Presentación: Granel / Tolva")

        if st.session_state.condiciones_sesion:
            c = st.session_state.condiciones_sesion
            lineas_wa.append(
                f"\n--- CONDICIONES AMBIENTALES ---\n"
                f"Temp: {c['temp']}°C | HR: {c['hum']}% | Delta-T: {c['delta_t']} °C\n"
                f"Viento: {c['viento']} km/h {c['dir_viento']} | {c['icono']} {c['estado']}"
            )

        msg_sol = "\n".join(lineas_wa)

        st.markdown(
            f'<a class="btn-wa" href="https://wa.me/?text={quote(msg_sol)}" target="_blank">'
            '📲 Enviar orden por WhatsApp</a>',
            unsafe_allow_html=True
        )

        if st.button("💾 Guardar en bitácora", key="save_sol"):
            prods_registro = (
                [f"{e['especie']}: {e['kgha']:.2f} kg/ha"
                 for e in st.session_state.receta_mezcla if e["kgha"] > 0]
                if receta_lineas else
                [f"{nombre_producto_final} {dosis_total_kgha:.2f} kg/ha"]
            )
            st.session_state.bitacora.append({
                "tipo": "Solidos",
                "fecha": datetime.now().strftime("%d/%m %H:%M"),
                "lote": sol_nombre,
                "cultivo": sol_cultivo,
                "ha": sol_ha,
                "piloto": st.session_state.piloto_sesion or "-",
                "productos": prods_registro,
                "condiciones": st.session_state.condiciones_sesion,
                "obs": "",
            })
            st.success("✅ Guardado en bitácora")
    else:
        st.info("Ingresá la dosis para ver los resultados.")

# =================================================
# TAB 3 — DELTA-T
# =================================================

with tabs[2]:

    st.subheader("Condiciones ambientales")
    st.caption("Completá los datos y fijá las condiciones para que queden registradas en cada aplicación.")

    d1, d2 = st.columns(2)
    with d1:
        dt_temp  = st.number_input("🌡️ Temperatura (°C)", value=25.0, step=0.5, key="dt_temp")
        dt_hum   = st.number_input("💧 Humedad relativa (%)", value=60.0, step=1.0,
                                    min_value=1.0, max_value=100.0, key="dt_hum")
    with d2:
        dt_viento = st.number_input("🌬️ Velocidad del viento (km/h)", value=10.0,
                                     min_value=0.0, step=0.5, key="dt_viento")
        dt_dir    = st.selectbox("Dirección del viento", DIRECCIONES_VIENTO, key="dt_dir")

    # Cálculo en tiempo real
    dt_valor = calcular_delta_t(dt_temp, dt_hum)
    semaforo = evaluar_semaforo(dt_valor, dt_viento)

    st.divider()

    # Métricas
    m1, m2, m3 = st.columns(3)
    m1.metric("Delta-T", f"{dt_valor} °C", help="Rango óptimo: 2–8 °C")
    m2.metric("Viento", f"{dt_viento:.0f} km/h {dt_dir}")
    m3.metric("Estado", f"{semaforo['icono']} {semaforo['estado']}")

    # Semáforo
    razones_html = "<br>".join(f"• {r}" for r in semaforo["razones"])
    st.markdown(
        f"""
        <div class="{semaforo['css']}">
            <div style="font-size:2.2rem; font-weight:900;">{semaforo['icono']} {semaforo['estado']}</div>
            <div style="margin-top:8px; font-size:0.95rem;">{razones_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Botón fijar
    if st.button("📌 Fijar condiciones de sesión", key="fijar_condiciones"):
        st.session_state.condiciones_sesion = {
            "temp": dt_temp,
            "hum": dt_hum,
            "delta_t": dt_valor,
            "viento": dt_viento,
            "dir_viento": dt_dir,
            "estado": semaforo["estado"],
            "icono": semaforo["icono"],
            "fijado_a": datetime.now().strftime("%d/%m %H:%M"),
        }
        st.success(f"✅ Condiciones fijadas a las {st.session_state.condiciones_sesion['fijado_a']} — se incluirán en cada registro de bitácora")

    if st.session_state.condiciones_sesion:
        c = st.session_state.condiciones_sesion
        st.markdown(
            f"""
            <div class="condiciones-fijadas">
            📌 <b>Fijadas a las {c['fijado_a']}:</b>
            {c['temp']}°C · {c['hum']}% HR · Delta-T {c['delta_t']} °C ·
            🌬️ {c['viento']} km/h {c['dir_viento']} ·
            {c['icono']} <b>{c['estado']}</b>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("🗑️ Limpiar condiciones fijadas", key="limpiar_cond"):
            st.session_state.condiciones_sesion = None
            st.rerun()

    st.divider()
    st.caption("Delta-T = temperatura del aire − temperatura de bulbo húmedo. Rango óptimo: 2–8 °C. Viento óptimo: < 15 km/h.")

# =================================================
# TAB 4 — CLIMA
# =================================================

with tabs[3]:

    st.subheader("Acceso rápido al clima")

    st.markdown('<a class="btn-clima" href="https://www.windy.com" target="_blank">🌬️ Windy</a>', unsafe_allow_html=True)
    st.markdown('<a class="btn-clima" href="https://www.smn.gob.ar" target="_blank">🇦🇷 Servicio Meteorológico Nacional</a>', unsafe_allow_html=True)
    st.markdown('<a class="btn-clima" href="https://www.swpc.noaa.gov/products/planetary-k-index" target="_blank">🛰️ Índice KP NOAA (GPS)</a>', unsafe_allow_html=True)

# =================================================
# TAB 5 — BITÁCORA
# =================================================

with tabs[4]:

    st.subheader("Bitácora de campaña")

    st.session_state.piloto_sesion = st.text_input(
        "👤 Piloto / operador (se aplica a todos los registros de esta sesión)",
        value=st.session_state.piloto_sesion,
        key="piloto_input"
    )

    st.divider()

    with st.expander("✍️ Agregar registro manual", expanded=False):
        m1, m2 = st.columns(2)
        man_lote    = m1.text_input("Lote", key="man_lote")
        man_ha      = m1.number_input("Superficie (ha)", min_value=0.1, value=10.0, step=0.5, key="man_ha")
        man_cultivo = m2.selectbox("Cultivo", CULTIVOS, key="man_cultivo")
        man_tipo    = m2.selectbox("Tipo", ["Liquidos", "Solidos", "Otro"], key="man_tipo")
        man_prod    = st.text_input("Producto(s) y dosis (texto libre)", key="man_prod")
        man_obs     = st.text_area("Observaciones", key="man_obs", height=80)

        if st.button("➕ Agregar a bitácora", key="add_manual"):
            if man_lote.strip():
                st.session_state.bitacora.append({
                    "tipo": man_tipo,
                    "fecha": datetime.now().strftime("%d/%m %H:%M"),
                    "lote": man_lote,
                    "cultivo": man_cultivo,
                    "ha": man_ha,
                    "piloto": st.session_state.piloto_sesion or "-",
                    "productos": [man_prod] if man_prod.strip() else [],
                    "condiciones": st.session_state.condiciones_sesion,
                    "obs": man_obs,
                })
                st.success("✅ Registro agregado")
                st.rerun()
            else:
                st.warning("Ingresá al menos el nombre del lote.")

    st.divider()

    if not st.session_state.bitacora:
        st.info("La bitácora está vacía. Guardá aplicaciones desde Líquidos o Sólidos, o agregá un registro manual.")
    else:
        total_ha_bit = sum(e.get("ha", 0) for e in st.session_state.bitacora)
        st.caption(f"**{len(st.session_state.bitacora)} registros** · **{total_ha_bit:.1f} ha** totales en esta sesión")

        for idx, entry in enumerate(reversed(st.session_state.bitacora)):
            real_idx = len(st.session_state.bitacora) - 1 - idx
            tipo_display = "💧 Líquidos" if entry["tipo"] == "Liquidos" else (
                "🌾 Sólidos" if entry["tipo"] == "Solidos" else entry["tipo"]
            )
            css_class = "bit-manual" if entry["tipo"] == "Otro" else "bit-entry"
            productos_str = " · ".join(entry.get("productos", [])) or "—"

            cond = entry.get("condiciones")
            cond_html = ""
            if cond:
                cond_html = (
                    f"<br><small>🌡️ {cond['temp']}°C · 💧 {cond['hum']}% HR · "
                    f"Delta-T {cond['delta_t']} °C · "
                    f"🌬️ {cond['viento']} km/h {cond['dir_viento']} · "
                    f"{cond['icono']} <b>{cond['estado']}</b></small>"
                )
            else:
                cond_html = "<br><small>⚪ Sin condiciones registradas</small>"

            with st.expander(
                f"{tipo_display}  |  {entry['fecha']}  |  {entry['lote']}  ({entry['ha']} ha)  |  👤 {entry['piloto']}",
                expanded=False
            ):
                st.markdown(
                    f"""
                    <div class="{css_class}">
                    <b>Cultivo:</b> {entry['cultivo']}<br>
                    <b>Productos:</b> {productos_str}
                    {cond_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                nueva_obs = st.text_area(
                    "📝 Observaciones",
                    value=entry.get("obs", ""),
                    key=f"obs_edit_{real_idx}",
                    height=80
                )
                col_save_obs, col_del = st.columns([0.75, 0.25])
                if col_save_obs.button("💾 Guardar obs", key=f"save_obs_{real_idx}"):
                    st.session_state.bitacora[real_idx]["obs"] = nueva_obs
                    st.success("Observación guardada")
                    st.rerun()
                if col_del.button("🗑️ Eliminar entrada", key=f"del_entry_{real_idx}"):
                    st.session_state.bitacora.pop(real_idx)
                    st.rerun()

        st.divider()

        col_pdf, col_clear = st.columns([0.7, 0.3])
        with col_pdf:
            pdf_bytes = generar_pdf_bitacora(st.session_state.bitacora)
            nombre_pdf = f"bitacora_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            st.download_button(
                label="📄 Descargar bitácora en PDF",
                data=pdf_bytes,
                file_name=nombre_pdf,
                mime="application/pdf",
                use_container_width=True
            )
        with col_clear:
            if st.button("🗑️ Limpiar bitácora", use_container_width=True):
                st.session_state.bitacora = []
                st.rerun()

# =================================================
# TAB 6 — SOBRE
# =================================================

with tabs[5]:

    st.subheader("AgroDrone Mixer")

    st.write("""
Aplicación diseñada para pilotos de drones agrícolas.

**Funciones:**
- Calculadora de mezcla para aplicaciones líquidas
- Calculadora de sólidos: semillas y fertilizantes
- Constructor de receta para mezclas de pasturas
- Cálculo de bolsas necesarias por lote
- Envío de orden por WhatsApp con condiciones ambientales
- Delta-T + viento: semáforo unificado de aptitud para aplicar
- Bitácora de campaña con condiciones por registro y exportación PDF
- Acceso rápido a clima y GPS
""")

    st.divider()
    st.caption("Desarrollado por Gabriel Carrasco 🚁")
