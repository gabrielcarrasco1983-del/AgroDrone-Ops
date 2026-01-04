import streamlit as st
import urllib.parse

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config(
    page_title="Drone SprayLogic",
    layout="wide"
)

st.title("🛰️ Drone SprayLogic")
st.caption(
    "Plataforma operativa para aplicación, fertilización y siembra con drones agrícolas"
)

# =====================================================
# SESSION STATE
# =====================================================
if "aplicacion_productos" not in st.session_state:
    st.session_state.aplicacion_productos = []

if "fertilizacion_productos" not in st.session_state:
    st.session_state.fertilizacion_productos = []

if "siembra_especies" not in st.session_state:
    st.session_state.siembra_especies = []

# =====================================================
# TABS
# =====================================================
tabs = st.tabs([
    "🧮 Aplicación",
    "🌱 Fertilización",
    "🌾 Siembra",
    "🌡️ Delta T",
    "🌦️ Clima",
    "ℹ️ Sobre mi"
])

# =====================================================
# TAB APLICACIÓN
# =====================================================
with tabs[0]:
    st.subheader("🧮 Aplicación con drones")

    col1, col2 = st.columns(2)
    with col1:
        lote = st.text_input("Lote", key="lote_app")
    with col2:
        superficie = st.number_input("Superficie (ha)", min_value=0.0, step=0.1, key="sup_app")

    st.divider()
    st.markdown("### 💧 Productos")

    with st.form("add_producto_app"):
        c1, c2 = st.columns([4, 2])
        with c1:
            producto = st.text_input("Producto")
        with c2:
            dosis = st.number_input("Dosis (L o kg/ha)", min_value=0.0, step=0.1)

        if st.form_submit_button("➕ Agregar producto") and producto and dosis > 0:
            st.session_state.aplicacion_productos.append(
                {"producto": producto, "dosis": dosis}
            )

    if st.session_state.aplicacion_productos:
        total_ha = 0
        st.markdown("### 📋 Productos cargados")

        for i, p in enumerate(st.session_state.aplicacion_productos):
            c1, c2, c3 = st.columns([4, 2, 1])
            c1.write(p["producto"])
            c2.write(f'{p["dosis"]} /ha')
            if c3.button("❌", key=f"del_app_{i}"):
                st.session_state.aplicacion_productos.pop(i)
                st.rerun()

        if superficie > 0:
            mensaje = f"""🛰️ *Aplicación con dron – SprayLogic*

Lote: {lote}
Superficie: {superficie} ha

*Dosis por hectárea*"""
            for p in st.session_state.aplicacion_productos:
                mensaje += f"\n- {p['producto']}: {p['dosis']}"

            mensaje += "\n\n*Totales para el lote*"
            for p in st.session_state.aplicacion_productos:
                mensaje += f"\n- {p['producto']}: {p['dosis'] * superficie}"

            st.text_area("📲 Mensaje WhatsApp", mensaje, height=240)
            st.markdown(
                f"[📲 Compartir por WhatsApp](https://wa.me/?text={urllib.parse.quote(mensaje)})",
                unsafe_allow_html=True
            )
        else:
            st.info("👉 Ingresá la superficie para ver totales y compartir")

# =====================================================
# TAB FERTILIZACIÓN
# =====================================================
with tabs[1]:
    st.subheader("🌱 Fertilización con drones")

    col1, col2 = st.columns(2)
    with col1:
        lote = st.text_input("Lote", key="lote_fert")
    with col2:
        superficie = st.number_input("Superficie (ha)", min_value=0.0, step=0.1, key="sup_fert")

    st.divider()
    st.markdown("### 🌱 Fertilizantes")

    with st.form("add_fert"):
        c1, c2 = st.columns([4, 2])
        with c1:
            fertilizante = st.text_input("Fertilizante")
        with c2:
            dosis = st.number_input("Dosis (kg/ha)", min_value=0.0, step=0.1)

        if st.form_submit_button("➕ Agregar fertilizante") and fertilizante and dosis > 0:
            st.session_state.fertilizacion_productos.append(
                {"fertilizante": fertilizante, "dosis": dosis}
            )

    if st.session_state.fertilizacion_productos:
        st.markdown("### 📋 Fertilizantes cargados")

        for i, f in enumerate(st.session_state.fertilizacion_productos):
            c1, c2, c3 = st.columns([4, 2, 1])
            c1.write(f["fertilizante"])
            c2.write(f'{f["dosis"]} kg/ha')
            if c3.button("❌", key=f"del_fert_{i}"):
                st.session_state.fertilizacion_productos.pop(i)
                st.rerun()

        if superficie > 0:
            mensaje = f"""🛰️ *Fertilización con dron – SprayLogic*

Lote: {lote}
Superficie: {superficie} ha

*Dosis por hectárea*"""
            for f in st.session_state.fertilizacion_productos:
                mensaje += f"\n- {f['fertilizante']}: {f['dosis']} kg/ha"

            mensaje += "\n\n*Totales para el lote*"
            for f in st.session_state.fertilizacion_productos:
                mensaje += f"\n- {f['fertilizante']}: {f['dosis'] * superficie} kg"

            st.text_area("📲 Mensaje WhatsApp", mensaje, height=240)
            st.markdown(
                f"[📲 Compartir por WhatsApp](https://wa.me/?text={urllib.parse.quote(mensaje)})",
                unsafe_allow_html=True
            )
        else:
            st.info("👉 Ingresá la superficie para ver totales y compartir")

# =====================================================
# TAB SIEMBRA (CORREGIDO Y FINAL)
# =====================================================
with tabs[2]:
    st.subheader("🌾 Siembra con drones")

    col1, col2 = st.columns(2)
    lote = col1.text_input("Lote", key="lote_siembra")
    superficie = col2.number_input("Superficie (ha)", min_value=0.0, step=0.1, key="sup_siembra")

    st.divider()
    st.markdown("### 🌱 Especies")

    especies_menu = [
        "Avena", "Raigrás anual", "Raigrás perenne", "Cebadilla", "Festuca",
        "Agropiro", "Trébol blanco", "Trébol rojo", "Lotus", "Vicia",
        "Alfalfa", "Centeno", "Triticale", "Moha", "Otra"
    ]

    with st.form("add_especie"):
        c1, c2 = st.columns([4, 2])
        especie = c1.selectbox("Especie", especies_menu)
        if especie == "Otra":
            especie = c1.text_input("Nombre de la especie")
        dosis = c2.number_input("Kg/ha", min_value=0.0, step=0.1)

        if st.form_submit_button("➕ Agregar especie") and especie and dosis > 0:
            st.session_state.siembra_especies.append(
                {"especie": especie, "dosis": dosis}
            )

    if st.session_state.siembra_especies:
        total_kg_ha = 0
        st.markdown("### 📋 Mezcla")

        for i, e in enumerate(st.session_state.siembra_especies):
            c1, c2, c3 = st.columns([4, 2, 1])
            c1.write(e["especie"])
            c2.write(f'{e["dosis"]} kg/ha')
            if c3.button("❌", key=f"del_siembra_{i}"):
                st.session_state.siembra_especies.pop(i)
                st.rerun()
            total_kg_ha += e["dosis"]

        mensaje = f"""🛰️ *Siembra con dron – SprayLogic*

Lote: {lote}
Superficie: {superficie} ha

*Dosis por hectárea*"""
        for e in st.session_state.siembra_especies:
            mensaje += f"\n- {e['especie']}: {e['dosis']} kg/ha"

        mensaje += f"\n\nTotal mezcla: {total_kg_ha} kg/ha"

        if superficie > 0:
            mensaje += "\n\n*Totales para el lote*"
            for e in st.session_state.siembra_especies:
                mensaje += f"\n- {e['especie']}: {e['dosis'] * superficie} kg"
            mensaje += f"\n\nTotal mezcla necesaria: {total_kg_ha * superficie} kg"

            st.text_area("📲 Mensaje WhatsApp", mensaje, height=260)
            st.markdown(
                f"[📲 Compartir por WhatsApp](https://wa.me/?text={urllib.parse.quote(mensaje)})",
                unsafe_allow_html=True
            )
        else:
            st.info("👉 Ingresá la superficie para calcular totales y compartir")

# =====================================================
# TAB DELTA T
# =====================================================
with tabs[3]:
    st.subheader("🌡️ Delta T")
    st.write(
        "Indicador que combina temperatura y humedad relativa. "
        "Valores altos implican mayor riesgo de evaporación y deriva."
    )

# =====================================================
# TAB CLIMA
# =====================================================
with tabs[4]:
    st.subheader("🌦️ Clima")
    st.markdown(
        "[🌍 Pronóstico KP – NOAA](https://www.swpc.noaa.gov/products/planetary-k-index)"
    )

# =====================================================
# TAB SOBRE
# =====================================================
with tabs[5]:
    st.subheader("ℹ️ Sobre mi")
    st.write(
        "Herramienta diseñada para asistir al aplicador y al asesor técnico "
        "en el cálculo y registro de dosis, mezclas y siembras con drones."
    )
    st.write("**Creador:** Gabriel Carrasco")
