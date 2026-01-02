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
from utils.delta_t import calculate_delta_t

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
# TEXTOS BASE (API / PRODUCTO)
# =========================
PRODUCT_NAME = "Drone SprayLogic"
PRODUCT_TAGLINE = "Plataforma inteligente de pulverización agrícola con drones"
PRODUCT_DESCRIPTION = (
    "Herramienta diseñada para asistir al aplicador en el cálculo preciso "
    "de mezclas y dosis para pulverización con drones, priorizando eficiencia, "
    "claridad operativa y toma de decisiones en campo."
)

# =========================
# HEADER
# =========================
st.title(PRODUCT_NAME)
st.caption(PRODUCT_TAGLINE)

tabs = st.tabs([
    "🧮 Calculadora",
    "🌡️ Delta T",
    "🌦️ Clima",
    "ℹ️ Sobre"
])

# ======================================================
# TAB 1 — CALCULADORA
# ======================================================
with tabs[0]:
    st.subheader("Configuración del Lote")

    nombre_lote = st.text_input("Nombre del Lote", value="Lote Sin Nombre")

    c1, c2, c3 = st.columns(3)
    with c1:
        hectareas = st.number_input("Hectáreas Totales", value=10.0, step=1.0)
    with c2:
        mixer_opt = st.selectbox(
            "Capacidad Mixer (L)",
            ["100", "200", "300", "500", "Manual"]
        )
        mixer_litros = (
            st.number_input("Litros Reales", value=330)
            if mixer_opt == "Manual"
            else int(mixer_opt)
        )
    with c3:
        tasa = st.number_input("Caudal del Dron (L/Ha)", value=10.0, step=1.0)

    # Objeto de dominio
    lote = Lote(
        nombre=nombre_lote,
        hectareas=hectareas,
        tasa_l_ha=tasa,
        mixer_litros=mixer_litros
    )

    st.divider()
    st.subheader("Productos")

    if "filas" not in st.session_state:
        st.session_state.filas = [{"p": "", "d": 0.0, "u": "L"}]

    for i, fila in enumerate(st.session_state.filas):
        col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
        fila["p"] = col1.text_input(
            f"Producto {i + 1}",
            value=fila["p"],
            key=f"p_{i}"
        )
        fila["d"] = col2.number_input(
            "Dosis/Ha",
            value=fila["d"],
            key=f"d_{i}",
            format="%.3f"
        )
        fila["u"] = col3.selectbox(
            "Unidad",
            ["L", "Kg"],
            key=f"u_{i}"
        )

    if st.button("➕ Añadir Producto"):
        st.session_state.filas.append({"p": "", "d": 0.0, "u": "L"})
        st.rerun()

    # =========================
    # ARMADO DE PRODUCTOS
    # =========================
    productos = [
        Producto(
            nombre=f["p"] if f["p"] else "Producto",
            dosis=f["d"],
            unidad=f["u"]
        )
        for f in st.session_state.filas
        if f["d"] > 0
    ]

    # =========================
    # CÁLCULOS
    # =========================
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

        st.markdown(
            f"<div class='resumen-caja'>"
            f"<h3>🧪 Mezcla por mixer ({lote.mixer_litros} L)</h3>"
            f"<p>Cobertura: <b>{cobertura:.2f} Ha</b></p>",
            unsafe_allow_html=True
        )

        for p in resultado["por_mixer"]:
            st.write(f"• **{p['producto']}**: {p['cantidad']} {p['unidad']}")

        st.markdown("</div>", unsafe_allow_html=True)

        st.subheader(f"📊 Total para el lote: {lote.nombre}")
        st.write(f"Preparaciones necesarias: **{mixers_totales} mixers**")

        for p in resultado["total_lote"]:
            st.write(f"• {p['producto']}: {p['cantidad']} {p['unidad']}")

        # =========================
        # EXPORTACIONES
        # =========================
        wa_link = generar_mensaje_whatsapp(
            lote=lote,
            cobertura=cobertura,
            por_mixer=resultado["por_mixer"],
            total_lote=resultado["total_lote"]
        )

        st.markdown(
            f'<a href="{wa_link}" target="_blank">'
            f'<button style="width:100%; background-color:#25D366; color:white; '
            f'padding:15px; border:none; border-radius:10px; font-weight:bold;">'
            f'📲 Enviar orden por WhatsApp</button></a>',
            unsafe_allow_html=True
        )

        excel_bytes = generar_excel(
            nombre_lote=lote.nombre,
            total_lote=resultado["total_lote"]
        )

        st.download_button(
            label="📥 Descargar reporte (Excel)",
            data=excel_bytes,
            file_name=f"Reporte_{lote.nombre}.xlsx",
            mime="application/vnd.ms-excel"
        )

# ======================================================
# TAB 2 — DELTA T
# ======================================================
with tabs[1]:
    st.subheader("Análisis Ambiental")

    t = st.number_input("Temperatura (°C)", value=25.0)
    h = st.number_input("Humedad Relativa (%)", value=60.0)

    dt = calculate_delta_t(t, h)

    st.metric("Delta T", f"{dt} °C")

    if 2 <= dt <= 8:
        st.success("Condiciones óptimas para aplicación")
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
        'style="display:block; background:#002A20; color:white; padding:15px; '
        'text-align:center; border-radius:10px; text-decoration:none;">'
        '🌬️ Consultar Windy</a>',
        unsafe_allow_html=True
    )

# ======================================================
# TAB 4 — SOBRE
# ======================================================
with tabs[3]:
    st.write(PRODUCT_DESCRIPTION)
