import streamlit as st

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="Drone SprayLogic",
    layout="wide"
)

st.title("🛰️ Drone SprayLogic")
st.caption("Plataforma operativa para aplicaciones, fertilización y siembra con drones")

# =========================
# SESSION STATE INIT
# =========================
if "siembra_especies" not in st.session_state:
    st.session_state.siembra_especies = []

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

# =========================
# TAB SIEMBRA
# =========================
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

    # =========================
    # SIEMBRA SIMPLE
    # =========================
    if tipo_siembra == "Semilla simple":
        especie_simple = st.text_input("Especie")
        dosis_simple = st.number_input(
            "Dosis (kg/ha)",
            min_value=0.0,
            step=0.1
        )

        if superficie > 0 and dosis_simple > 0:
            total_simple = superficie * dosis_simple

            st.markdown("### 📊 Resultado")
            st.write(f"**Total necesario:** {total_simple:.1f} kg")

    # =========================
    # SIEMBRA EN MEZCLA
    # =========================
    else:
        st.markdown("### 🌱 Especies de la mezcla")

        especies_menu = [
            "Avena", "Raigrás anual", "Raigrás perenne", "Cebadilla",
            "Festuca", "Agropiro", "Trébol blanco", "Trébol rojo",
            "Lotus", "Vicia", "Alfalfa", "Centeno", "Triticale",
            "Sorgo forrajero", "Moha", "Otra"
        ]

        with st.form("agregar_especie"):
            col_a, col_b = st.columns([3, 2])

            with col_a:
                especie = st.selectbox("Especie", especies_menu)
                if especie == "Otra":
                    especie = st.text_input("Nombre de la especie")

            with col_b:
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

        # =========================
        # LISTADO EDITABLE
        # =========================
        if st.session_state.siembra_especies:
            st.markdown("### 📋 Mezcla cargada")

            total_kg_ha = 0.0
            total_por_especie = {}

            for i, item in enumerate(st.session_state.siembra_especies):
                col_e1, col_e2, col_e3 = st.columns([4, 2, 1])

                with col_e1:
                    st.write(item["especie"])

                with col_e2:
                    st.write(f'{item["kg_ha"]} kg/ha')

                with col_e3:
                    if st.button("❌", key=f"del_{i}"):
                        st.session_state.siembra_especies.pop(i)
                        st.rerun()


                total_kg_ha += item["kg_ha"]
                total_por_especie[item["especie"]] = item["kg_ha"]

            if superficie > 0:
                st.divider()
                st.markdown("### 📊 Resultados")

                st.write(f"**Total mezcla:** {total_kg_ha:.1f} kg/ha")
                st.write(f"**Total mezcla para el lote:** {total_kg_ha * superficie:.1f} kg")

                st.markdown("**Totales por especie:**")
                for esp, dosis in total_por_especie.items():
                    st.write(
                        f"- {esp}: {dosis * superficie:.1f} kg"
                    )

                # =========================
                # MENSAJE WHATSAPP
                # =========================
                mensaje = f"""🛰️ *Siembra con dron – SprayLogic*

Lote: {lote}
Superficie: {superficie} ha

*Dosis por hectárea*"""
                for esp, dosis in total_por_especie.items():
                    mensaje += f"\n- {esp}: {dosis} kg/ha"

                mensaje += f"""

Total mezcla: {total_kg_ha:.1f} kg/ha

*Totales para el lote*"""
                for esp, dosis in total_por_especie.items():
                    mensaje += f"\n- {esp}: {dosis * superficie:.1f} kg"

                mensaje += f"\n\nTotal mezcla necesaria: {total_kg_ha * superficie:.1f} kg"

                st.text_area("📲 Mensaje para WhatsApp", mensaje, height=260)

# =========================
# TAB DELTA T
# =========================
with tabs[3]:
    st.subheader("🌡️ Delta T")
    st.write(
        "El Delta T es un indicador climático que combina temperatura y humedad relativa. "
        "Permite estimar el riesgo de evaporación durante aplicaciones, ayudando a definir "
        "si el momento es adecuado para pulverizar."
    )

# =========================
# TAB CLIMA
# =========================
with tabs[4]:
    st.subheader("🌦️ Clima")
    st.markdown(
        "[Pronóstico KP – NOAA](https://www.swpc.noaa.gov/products/planetary-k-index)"
    )

# =========================
# TAB SOBRE
# =========================
with tabs[5]:
    st.subheader("ℹ️ Sobre mi")
    st.write(
        "Herramienta diseñada para asistir al aplicador en el cálculo preciso de mezclas y dosis "
        "para pulverización, fertilización y siembra con drones, priorizando eficiencia, "
        "claridad operativa y toma de decisiones en campo."
    )
    st.write("**Creador:** Gabriel Carrasco")

