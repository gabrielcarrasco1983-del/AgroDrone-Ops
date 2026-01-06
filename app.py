import streamlit as st

# =========================
# IMPORTS DEL CORE
# =========================
from core.calculator import (
    calcular_cobertura,
    calcular_mixers_totales,
    calcular_dosis_productos
)
from core.models import Lote, Producto
from core.exporters import (
    generar_mensaje_whatsapp,
    generar_excel
)
from core.utils.delta_t import calculate_delta_t

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="Drone SprayLogic",
    layout="wide"
)

# =========================
# ESTILOS
# =========================
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.title("Drone SprayLogic")
st.caption("Calculadora de mezclas y dosis para pulverización con drones")

tabs = st.tabs([
    "🧮 Calculadora",
    "🌡️ Delta T",
    "🌦️ Clima",
    "ℹ️ Sobre"
])

# ======================================================
# TAB 1 — CALCULADORA (OPTIMIZADA CAMPO)
# ======================================================
with tabs[0]:

    # ---------- BLOQUE LOTE ----------
    st.subheader("📍 Datos del lote")

    nombre_lote = st.text_input(
        "Nombre del lote",
        value="Lote"
    )

    hectareas = st.number_input(
        "Hectáreas totales",
        min_value=0.0,
        value=10.0,
        step=1.0
    )

    st.divider()

    # ---------- BLOQUE DRON ----------
    st.subheader("🚁 Configuración del dron")

    col1, col2 = st.columns(2)

    with col1:
        tasa = st.number_input(
            "Caudal de aplicación (L/Ha)",
            min_value=0.0,
            value=10.0,
            step=1.0
        )

    with col2:
        mixer_litros = st.number_input(
            "Capacidad del mixer (L)",
            min_value=1,
            value=300,
            step=10
        )

    lote = Lote(
        nombre=nombre_lote,
        hectareas=hectareas,
        tasa_l_ha=tasa,
        mixer_litros=mixer_litros
    )

    st.divider()

    # ---------- BLOQUE PRODUCTOS ----------
    st.subheader("🧪 Productos")

    if "filas" not in st.session_state:
        st.session_state.filas = [{"p": "", "d": 0.0, "u": "L"}]

    for i, fila in enumerate(st.session_state.filas):
        col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
        fila["p"] = col1.text_input(
            f"Producto {i+1}",
            value=fila["p"],
            key=f"p_{i}"
        )
        fila["d"] = col2.number_input(
            "Dosis / Ha",
            min_value=0.0,
            value=fila["d"],
            step=0.1,
            key=f"d_{i}",
            format="%.2f"
        )
        fila["u"] = col3.selectbox(
            "Unidad",
            ["L", "Kg"],
            key=f"u_{i}"
        )

    if st.button("➕ Agregar producto"):
        st.session_state.filas.append({"p": "", "d": 0.0, "u": "L"})
        st.rerun()

    productos = [
        Producto(
            nombre=f["p"] if f["p"] else "Producto",
            dosis=f["d"],
            unidad=f["u"]
        )
        for f in st.session_state.filas
        if f["d"] > 0
    ]

    # ---------- RESULTADOS ----------
    if lote.hectareas > 0 and lote.tasa_l_ha > 0 and productos:

        cobertura = calcular_cobertura(
            lote.mixer_litros,
            lote.tasa_l_ha
        )

        mixers_totales = calcular_mixers_totales(
            lote.hectareas,
            lote.tasa_l_ha,
            lote.mixer_litros
        )

        resultado = calcular_dosis_productos(
            productos=[{
                "nombre": p.nombre,
                "dosis": p.dosis,
                "unidad": p.unidad
            } for p in productos],
            cobertura_ha=cobertura,
            hectareas=lote.hectareas
        )

        st.divider()
        st.subheader("📊 Resultados")

        # Métricas grandes (clave para campo)
        m1, m2 = st.columns(2)
        m1.metric("Hectáreas por mixer", f"{cobertura:.2f} Ha")
        m2.metric("Mixers necesarios", mixers_totales)

        # Mezcla por mixer
        st.subheader("🧪 Mezcla por mixer")
        for p in resultado["por_mixer"]:
            st.write(f"• **{p['producto']}**: {p['cantidad']} {p['unidad']}")

        # Total lote
        st.subheader("📦 Total para el lote")
        for p in resultado["total_lote"]:
            st.write(f"• **{p['producto']}**: {p['cantidad']} {p['unidad']}")

        # Orden de mezcla
        st.subheader("📋 Orden sugerido de mezcla")
        st.markdown(
            """
            1. Agua (50–60%)  
            2. Correctores de pH / dureza  
            3. Polvos mojables (WP, WG)  
            4. Suspensiones concentradas (SC)  
            5. Concentrados emulsionables (EC)  
            6. Soluciones líquidas (SL)  
            7. Coadyuvantes / aceites  
            8. Completar con agua
            """
        )

        # Acciones
        st.divider()

        wa_link = generar_mensaje_whatsapp(
            lote=lote,
            cobertura=cobertura,
            por_mixer=resultado["por_mixer"],
            total_lote=resultado["total_lote"]
        )

        st.markdown(
            f"""
            <a href="{wa_link}" target="_blank">
                <button style="
                    width:100%;
                    background-color:#25D366;
                    color:white;
                    padding:16px;
                    border:none;
                    border-radius:12px;
                    font-size:1rem;
                    font-weight:700;">
                    📲 Enviar receta por WhatsApp
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

        excel_bytes = generar_excel(
            lote.nombre,
            resultado["total_lote"]
        )

        st.download_button(
            "📥 Descargar reporte en Excel",
            excel_bytes,
            file_name=f"Reporte_{lote.nombre}.xlsx"
        )

# ======================================================
# TAB 2 — DELTA T
# ======================================================
with tabs[1]:
    st.subheader("🌡️ Delta T")

    st.write(
        "El Delta T combina temperatura y humedad relativa para estimar "
        "el riesgo de evaporación y deriva durante la aplicación."
    )

    t = st.number_input("Temperatura (°C)", value=25.0)
    h = st.number_input("Humedad relativa (%)", value=60.0)

    dt = calculate_delta_t(t, h)

    st.metric("Delta T", f"{dt} °C")

    if 2 <= dt <= 8:
        st.success("Condiciones óptimas de aplicación")
    elif dt < 2:
        st.warning("Riesgo de deriva")
    else:
        st.error("Alta evaporación")

# ======================================================
# TAB 3 — CLIMA
# ======================================================
with tabs[2]:
    st.markdown(
        '<a href="https://www.windy.com" target="_blank" '
        'style="display:block; background:#0B3D2E; color:white; padding:16px; '
        'text-align:center; border-radius:12px; text-decoration:none;">'
        '🌬️ Ver pronóstico en Windy</a>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<a href="https://www.swpc.noaa.gov/products/planetary-k-index" target="_blank" '
        'style="display:block; background:#003366; color:white; padding:16px; '
        'text-align:center; border-radius:12px; text-decoration:none; margin-top:10px;">'
        '🧭 Ver índice KP (NOAA)</a>',
        unsafe_allow_html=True
    )

# ======================================================
# TAB 4 — SOBRE MI
# ======================================================
with tabs[3]:
    st.write(
        "Herramienta diseñada para asistir al aplicador en el cálculo preciso "
        "de mezclas y dosis para pulverización con drones, priorizando eficiencia, "
        "claridad operativa y toma de decisiones en campo."
    )

    st.divider()

    st.write(
        "**Creado por Gabriel Carrasco**  \n"
        "Proyecto orientado a aplicaciones agrícolas con drones."
    )

    st.write("Contacto: **contacto@dronespraylogic.com**")
