import streamlit as st

# =========================
# IMPORTS CORE
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
# CONFIG
# =========================
st.set_page_config(
    page_title="Drone SprayLogic",
    layout="wide"
)

# =========================
# HEADER
# =========================
st.title("🚁 Drone SprayLogic")
st.caption("Plataforma inteligente de aplicación, fertilización y siembra con drones")

tabs = st.tabs([
    "🧮 Aplicación",
    "🌱 Siembra",
    "🌡️ Delta T",
    "🌦️ Clima",
    "ℹ️ Sobre mí"
])

# ======================================================
# TAB 1 — APLICACIÓN (PULVERIZACIÓN)
# ======================================================
with tabs[0]:

    st.subheader("📍 Datos del lote")

    nombre_lote = st.text_input("Nombre del lote", value="Lote")
    hectareas = st.number_input("Hectáreas", min_value=0.0, value=10.0, step=1.0)

    st.divider()

    st.subheader("🚁 Configuración del dron")

    col1, col2 = st.columns(2)
    tasa = col1.number_input("Litros por hectárea", min_value=0.0, value=10.0)
    mixer_litros = col2.number_input("Capacidad del mixer (L)", min_value=1, value=300)

    lote = Lote(
        nombre=nombre_lote,
        hectareas=hectareas,
        tasa_l_ha=tasa,
        mixer_litros=mixer_litros
    )

    st.divider()
    st.subheader("🧪 Productos")

    if "productos" not in st.session_state:
        st.session_state.productos = []

    for i, p in enumerate(st.session_state.productos):
        c1, c2, c3, c4 = st.columns([0.4, 0.25, 0.25, 0.1])
        p["nombre"] = c1.text_input("Producto", p["nombre"], key=f"pn_{i}")
        p["dosis"] = c2.number_input("Dosis / Ha", value=p["dosis"], key=f"pd_{i}")
        p["unidad"] = c3.selectbox("Unidad", ["L", "Kg"], index=0 if p["unidad"]=="L" else 1, key=f"pu_{i}")
        if c4.button("❌", key=f"delp_{i}"):
            st.session_state.productos.pop(i)
            st.rerun()

    if st.button("➕ Agregar producto"):
        st.session_state.productos.append({"nombre": "", "dosis": 0.0, "unidad": "L"})
        st.rerun()

    if lote.hectareas > 0 and tasa > 0 and st.session_state.productos:

        cobertura = calcular_cobertura(mixer_litros, tasa)
        mixers = calcular_mixers_totales(lote.hectareas, tasa, mixer_litros)

        resultado = calcular_dosis_productos(
            productos=st.session_state.productos,
            cobertura_ha=cobertura,
            hectareas=lote.hectareas
        )

        st.divider()
        st.subheader("📊 Resultados")

        m1, m2 = st.columns(2)
        m1.metric("Ha por mixer", f"{cobertura:.2f}")
        m2.metric("Mixers totales", mixers)

        st.subheader("🧪 Mezcla por mixer")
        for p in resultado["por_mixer"]:
            st.write(f"• **{p['producto']}**: {p['cantidad']} {p['unidad']}")

        st.subheader("📦 Total para el lote")
        for p in resultado["total_lote"]:
            st.write(f"• **{p['producto']}**: {p['cantidad']} {p['unidad']}")

        st.subheader("📋 Orden de mezcla")
        st.markdown("""
        1. Agua (50–60%)  
        2. Correctores  
        3. WP / WG  
        4. SC  
        5. EC  
        6. SL  
        7. Aceites / coadyuvantes  
        8. Completar agua
        """)

        wa = generar_mensaje_whatsapp(lote, cobertura, resultado["por_mixer"], resultado["total_lote"])
        st.markdown(f"<a href='{wa}' target='_blank'>📲 Enviar por WhatsApp</a>", unsafe_allow_html=True)

# ======================================================
# TAB 2 — SIEMBRA
# ======================================================
with tabs[1]:

    st.subheader("🌱 Siembra con drones")

    tipo = st.radio("Tipo de siembra", ["Semilla simple", "Mezcla de semillas"])

    if "siembra" not in st.session_state:
        st.session_state.siembra = []

    if tipo == "Semilla simple":
        especie = st.text_input("Especie")
        kg_ha = st.number_input("Kg por hectárea", min_value=0.0)

        if hectareas > 0 and kg_ha > 0:
            total = hectareas * kg_ha
            st.success(f"Total necesario: **{total:.1f} kg**")

    else:
        st.subheader("🧬 Mezcla")

        for i, e in enumerate(st.session_state.siembra):
            c1, c2, c3 = st.columns([0.6, 0.3, 0.1])
            e["esp"] = c1.text_input("Especie", e["esp"], key=f"se_{i}")
            e["kg"] = c2.number_input("Kg/Ha", value=e["kg"], key=f"sk_{i}")
            if c3.button("❌", key=f"sdel_{i}"):
                st.session_state.siembra.pop(i)
                st.rerun()

        if st.button("➕ Agregar especie"):
            st.session_state.siembra.append({"esp": "", "kg": 0.0})
            st.rerun()

        if hectareas > 0 and st.session_state.siembra:
            st.divider()
            total_ha = sum(e["kg"] for e in st.session_state.siembra)
            total_lote = total_ha * hectareas

            st.subheader("📊 Resultado")
            for e in st.session_state.siembra:
                st.write(f"• **{e['esp']}**: {e['kg']*hectareas:.1f} kg")

            st.success(f"Total mezcla por ha: **{total_ha:.1f} kg**")
            st.success(f"Total mezcla lote: **{total_lote:.1f} kg**")

# ======================================================
# TAB 3 — DELTA T
# ======================================================
with tabs[2]:
    st.subheader("🌡️ Delta T")
    st.write("Indicador climático clave para deriva y evaporación.")

    t = st.number_input("Temperatura (°C)", value=25.0)
    h = st.number_input("Humedad (%)", value=60.0)

    dt = calculate_delta_t(t, h)
    st.metric("Delta T", dt)

# ======================================================
# TAB 4 — CLIMA
# ======================================================
with tabs[3]:
    st.markdown("[🌬️ Windy](https://www.windy.com)", unsafe_allow_html=True)
    st.markdown("[🧭 Índice KP NOAA](https://www.swpc.noaa.gov/products/planetary-k-index)", unsafe_allow_html=True)

# ======================================================
# TAB 5 — SOBRE MI
# ======================================================
with tabs[4]:
    st.write(
        "Herramienta diseñada para asistir al aplicador en el cálculo preciso "
        "de mezclas, dosis y siembra con drones, priorizando eficiencia y "
        "toma de decisiones en campo."
    )
    st.divider()
    st.write("**Creado por Gabriel Carrasco**")
    st.write("Contacto: contacto@dronespraylogic.com")
