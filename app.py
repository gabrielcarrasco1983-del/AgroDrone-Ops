import streamlit as st
import urllib.parse

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="Drone SprayLogic",
    layout="wide"
)

st.title("🛰️ Drone SprayLogic")
st.caption(
    "Plataforma operativa para aplicación, fertilización y siembra con drones agrícolas"
)

# =========================
# SESSION STATE
# =========================
if "siembra_especies" not in st.session_state:
    st.session_state.siembra_especies = []

# =========================
# TABS
# =========================
tabs = st.tabs([
    "🧮 Aplicación",
    "🌱 Fertilización",
    "🌾 Siembra",
    "🌡️ Delta T",
    "🌦️ Clima",
    "ℹ️ Sobre mi"
])

# ======================================================
# TAB APLICACIÓN (placeholder funcional)
# ======================================================
with tabs[0]:
    st.subheader("🧮 Aplicación")
    st.info(
        "Módulo de cálculo de dosis para pulverización con drones. "
        "Será ampliado con edición por producto, memoria y exportación."
    )

# ======================================================
# TAB FERTILIZACIÓN (placeholder funcional)
# ======================================================
with tabs[1]:
    st.subheader("🌱 Fertilización")
    st.info(
        "Módulo de fertilización con drones. "
        "Permitirá registrar dosis, mezclas y totales por lote."
    )

# ======================================================
# TAB SIEMBRA (COMPLETO)
# ======================================================
with tabs[2]:
    st.subheader("🌾 Siembra con drones")

    col1, col2 = st.columns(2)

    with col1:
        lote = st.text_input("Lote")
        superficie = st.number_input(
            "Superficie (ha)",
            min_value=0.0,
            step=0.1
        )

    with col2:
        tipo_siembra = st.radio(
            "Tipo de siembra",
            ["Semilla simple", "Mezcla de semillas"]
        )

    st.divider()

    # -------------------------
    # SIEMBRA SIMPLE
    # -------------------------
    if tipo_siembra == "Semilla simple":
        especie = st.text_input("Especie")
        dosis = st.number_input(
            "Dosis (kg/ha)",
            min_value=0.0,
            step=0.1
        )

        if superficie > 0 and dosis > 0:
            total = superficie * dosis

            mensaje = f"""🛰️ *Siembra con dron – SprayLogic*

Lote: {lote}
Superficie: {superficie} ha

Especie: {especie}
Dosis: {dosis} kg/ha

Total necesario: {total:.1f} kg
"""

            st.markdown("### 📊 Resultado")
            st.write(f"**Total necesario:** {total:.1f} kg")

            mensaje_encoded = urllib.parse.quote(mensaje)
            st.markdown(
                f"[📲 Compartir por WhatsApp](https://wa.me/?text={mensaje_encoded})",
                unsafe_allow_html=True
            )

    # -------------------------
    # SIEMBRA EN MEZCLA
    # -------------------------
    else:
        st.markdown("### 🌱 Especies de la mezcla")

        especies_menu = [
            "Avena", "Raigrás anual", "Raigrás perenne", "Cebadilla",
            "Festuca", "Agropiro", "Trébol blanco", "Trébol rojo",
            "Lotus", "Vicia", "Alfalfa", "Centeno", "Triticale",
            "Sorgo forrajero", "Moha", "Otra"
        ]

        with st.form("agregar_especie"):
            c1, c2 = st.columns([3, 2])

            with c1:
                especie = st.selectbox("Especie", especies_menu)
                if especie == "Otra":
                    especie = st.text_input("Nombre de la especie")

            with c2:
                kg_ha = st.number_input(
                    "Kg/ha",
                    min_value=0.0,
                    step=0.1
                )

            agregar = st.form_submit_button("➕ Agregar especie")

            if agregar and especie and kg_ha > 0:
                st.session_state.siembra_especies.append({
                    "especie": especie,
                    "kg_ha": kg_ha
                })

        # -------- listado editable ----------
        if st.session_state.siembra_especies:
            st.markdown("### 📋 Mezcla cargada")

            total_kg_ha = 0.0
            totales = {}

            for i, item in enumerate(st.session_state.siembra_especies):
                c1, c2, c3 = st.columns([4, 2, 1])

                with c1:
                    st.write(item["especie"])
                with c2:
                    st.write(f'{item["kg_ha"]} kg/ha')
                with c3:
                    if st.button("❌", key=f"del_{i}"):
                        st.session_state.siembra_especies.pop(i)
                        st.rerun()

                total_kg_ha += item["kg_ha"]
                totales[item["especie"]] = item["kg_ha"]

            if superficie > 0:
                st.divider()
                st.markdown("### 📊 Resultados")

                st.write(f"**Total mezcla:** {total_kg_ha:.1f} kg/ha")
                st.write(
                    f"**Total mezcla para el lote:** {total_kg_ha * superficie:.1f} kg"
                )

                st.markdown("**Totales por especie:**")
                for esp, dosis in totales.items():
                    st.write(f"- {esp}: {dosis * superficie:.1f} kg")

                mensaje = f"""🛰️ *Siembra con dron – SprayLogic*

Lote: {lote}
Superficie: {superficie} ha

*Dosis por hectárea*"""
                for esp, dosis in totales.items():
                    mensaje += f"\n- {esp}: {dosis} kg/ha"

                mensaje += f"""

Total mezcla: {total_kg_ha:.1f} kg/ha

*Totales para el lote*"""
                for esp, dosis in totales.items():
                    mensaje += f"\n- {esp}: {dosis * superficie:.1f} kg"

                mensaje += f"\n\nTotal mezcla necesaria: {total_kg_ha * superficie:.1f} kg"

                st.text_area("📲 Mensaje para WhatsApp", mensaje, height=260)

                mensaje_encoded = urllib.parse.quote(mensaje)
                st.markdown(
                    f"[📲 Compartir por WhatsApp](https://wa.me/?text={mensaje_encoded})",
                    unsafe_allow_html=True
                )

# ======================================================
# TAB DELTA T
# ======================================================
with tabs[3]:
    st.subheader("🌡️ Delta T")
    st.write(
        "El Delta T combina temperatura y humedad relativa. "
        "Valores altos indican mayor riesgo de evaporación y deriva. "
        "Es una referencia clave para decidir el momento de aplicación."
    )

# ======================================================
# TAB CLIMA
# ======================================================
with tabs[4]:
    st.subheader("🌦️ Clima")
    st.markdown(
        "[🌍 Pronóstico KP – NOAA](https://www.swpc.noaa.gov/products/planetary-k-index)"
    )

# ======================================================
# TAB SOBRE
# ======================================================
with tabs[5]:
    st.subheader("ℹ️ Sobre mi")
    st.write(
        "Herramienta diseñada para asistir al aplicador en el cálculo preciso "
        "de mezclas y dosis para pulverización, fertilización y siembra con drones, "
        "priorizando eficiencia, claridad operativa y toma de decisiones en campo."
    )
    st.write("**Creador:** Gabriel Carrasco")
