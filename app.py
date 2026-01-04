import streamlit as st
import os
import urllib.parse

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
# HEADER CON ICONO SEGURO
# =========================
col_i1, col_i2 = st.columns([1, 6])

with col_i1:
    icon_path = "zumbido.png"
    if os.path.exists(icon_path):
        st.image(icon_path, width=80)
    else:
        st.write("🛰️")

with col_i2:
    st.title("Drone SprayLogic")
    st.caption(
        "Plataforma operativa para aplicación, fertilización y siembra con drones"
    )

# =========================
# TABS PRINCIPALES
# =========================
tabs = st.tabs([
    "🧮 Aplicación",
    "🌱 Fertilización",
    "🌾 Siembra",
    "🌡️ Delta T",
    "🌦️ Clima",
    "ℹ️ Sobre"
])

# ======================================================
# TAB 0 — APLICACIÓN (CORE)
# ======================================================
with tabs[0]:

    st.subheader("📍 Datos del lote")

    nombre_lote = st.text_input("Nombre del lote", value="Lote")

    hectareas = st.number_input(
        "Hectáreas totales",
        min_value=0.0,
        value=10.0,
        step=1.0
    )

    st.divider()

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
        mixer_litros = st.selectbox(
            "Capacidad del mixer (L)",
            options=[100, 200, 300, 500],
            index=2
        )

    lote = Lote(
        nombre=nombre_lote,
        hectareas=hectareas,
        tasa_l_ha=tasa,
        mixer_litros=mixer_litros
    )

    st.divider()
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

        m1, m2 = st.columns(2)
        m1.metric("Hectáreas por mixer", f"{cobertura:.2f} Ha")
        m2.metric("Mixers necesarios", mixers_totales)

        st.subheader("🧪 Mezcla por mixer")
        for p in resultado["por_mixer"]:
            st.write(f"• **{p['producto']}**: {p['cantidad']} {p['unidad']}")

        st.subheader("📦 Total para el lote")
        for p in resultado["total_lote"]:
            st.write(f"• **{p['producto']}**: {p['cantidad']} {p['unidad']}")

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
# TAB 1 — FERTILIZACIÓN (AGREGADO BOTÓN WHATSAPP)
# ======================================================
with tabs[1]:
    st.subheader("🌱 Fertilización con drones")

    col1, col2 = st.columns(2)

    with col1:
        lote_f = st.text_input("Lote", key="fert_lote")
        superficie_f = st.number_input(
            "Superficie (ha)",
            min_value=0.0,
            step=0.1,
            key="fert_sup"
        )

    with col2:
        fertilizante = st.text_input("Fertilizante", key="fert_prod")
        dosis_f = st.number_input(
            "Dosis (kg/ha)",
            min_value=0.0,
            step=0.1,
            key="fert_dosis"
        )

    if superficie_f > 0 and dosis_f > 0:
        total_f = superficie_f * dosis_f

        st.divider()
        st.subheader("📊 Resultados")
        st.write(f"**Total necesario:** {total_f:.1f} kg")

        mensaje = f"""🛰️ Fertilización con dron – SprayLogic

Lote: {lote_f}
Superficie: {superficie_f} ha

Fertilizante: {fertilizante}
Dosis: {dosis_f} kg/ha

Total necesario: {total_f:.1f} kg
"""
        st.text_area("📲 Mensaje para WhatsApp", mensaje, height=220)

        wa_fert = "https://wa.me/?text=" + urllib.parse.quote(mensaje)

        st.markdown(
            f"""
            <a href="{wa_fert}" target="_blank">
                <button style="
                    width:100%;
                    background-color:#25D366;
                    color:white;
                    padding:14px;
                    border:none;
                    border-radius:12px;
                    font-weight:700;">
                    📲 Enviar por WhatsApp
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

# ======================================================
# TAB 2 — SIEMBRA (AGREGADO BOTÓN WHATSAPP)
# ======================================================
with tabs[2]:
    st.subheader("🌾 Siembra con drones")

    if "siembra_especies" not in st.session_state:
        st.session_state.siembra_especies = []

    col1, col2 = st.columns(2)

    with col1:
        lote_s = st.text_input("Lote", key="siem_lote")
        superficie_s = st.number_input(
            "Superficie (ha)",
            min_value=0.0,
            step=0.1,
            key="siem_sup"
        )

    with col2:
        tipo_siembra = st.radio(
            "Tipo de siembra",
            ["Semilla simple", "Mezcla de semillas"],
            key="siem_tipo"
        )

    st.divider()

    mensaje_siembra = ""

    if tipo_siembra == "Semilla simple":
        especie = st.text_input("Especie", key="siem_esp_simple")
        dosis = st.number_input(
            "Dosis (kg/ha)",
            min_value=0.0,
            step=0.1,
            key="siem_dosis_simple"
        )

        if superficie_s > 0 and dosis > 0:
            total = superficie_s * dosis

            st.subheader("📊 Resultado")
            st.write(f"**Total necesario:** {total:.1f} kg")

            mensaje_siembra = f"""🛰️ Siembra con dron – SprayLogic

Lote: {lote_s}
Superficie: {superficie_s} ha

Especie: {especie}
Dosis: {dosis} kg/ha

Total necesario: {total:.1f} kg
"""

    else:
        especies_menu = [
            "Avena", "Raigrás anual", "Raigrás perenne", "Cebadilla",
            "Festuca", "Agropiro", "Trébol blanco", "Trébol rojo",
            "Lotus", "Vicia", "Alfalfa", "Centeno", "Triticale",
            "Sorgo forrajero", "Moha", "Otra"
        ]

        with st.form("add_especie"):
            col_a, col_b = st.columns([3, 2])

            with col_a:
                esp = st.selectbox("Especie", especies_menu, key="siem_mix_esp")
                if esp == "Otra":
                    esp = st.text_input("Nombre de la especie", key="siem_mix_otra")

            with col_b:
                kg_ha = st.number_input(
                    "Kg/ha",
                    min_value=0.0,
                    step=0.1,
                    key="siem_mix_kg"
                )

            if st.form_submit_button("➕ Agregar"):
                if esp and kg_ha > 0:
                    st.session_state.siembra_especies.append(
                        {"especie": esp, "kg_ha": kg_ha}
                    )

        if st.session_state.siembra_especies and superficie_s > 0:
            total_kg_ha = sum(e["kg_ha"] for e in st.session_state.siembra_especies)

            st.divider()
            st.subheader("📊 Resultados")

            mensaje_siembra = f"""🛰️ Siembra con dron – SprayLogic

Lote: {lote_s}
Superficie: {superficie_s} ha
"""

            for e in st.session_state.siembra_especies:
                st.write(f"- {e['especie']}: {e['kg_ha'] * superficie_s:.1f} kg")
                mensaje_siembra += f"\n- {e['especie']}: {e['kg_ha']} kg/ha"

            mensaje_siembra += f"\n\nTotal mezcla necesaria: {total_kg_ha * superficie_s:.1f} kg"

            st.write(f"**Total mezcla:** {total_kg_ha * superficie_s:.1f} kg")

    if mensaje_siembra:
        st.text_area("📲 Mensaje para WhatsApp", mensaje_siembra, height=260)

        wa_siembra = "https://wa.me/?text=" + urllib.parse.quote(mensaje_siembra)

        st.markdown(
            f"""
            <a href="{wa_siembra}" target="_blank">
                <button style="
                    width:100%;
                    background-color:#25D366;
                    color:white;
                    padding:14px;
                    border:none;
                    border-radius:12px;
                    font-weight:700;">
                    📲 Enviar por WhatsApp
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

# ======================================================
# TAB 3 — DELTA T
# ======================================================
with tabs[3]:
    st.subheader("🌡️ Delta T")

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
# TAB 4 — CLIMA (AGREGADO NOAA KP)
# ======================================================
with tabs[4]:
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
        '🧭 Ver índice KP – NOAA</a>',
        unsafe_allow_html=True
    )

# ======================================================
# TAB 5 — SOBRE
# ======================================================
with tabs[5]:
    st.write(
        "Herramienta diseñada para asistir al aplicador en el cálculo preciso "
        "de dosis y mezclas para aplicación, fertilización y siembra con drones."
    )
    st.divider()
    st.write("**Creado por Gabriel Carrasco**")
