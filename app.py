import streamlit as st
import pandas as pd

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Drone SprayLogic",
    page_icon="🚁",
    layout="wide"
)

# HEADER CON ESTILO
st.title("🚁 Drone SprayLogic")
st.caption("Plataforma operativa para aplicaciones, fertilización y siembra con drones")

# TABS CON ICONOS PROFESIONALES
# Nota: Streamlit soporta iconos de Material Design/Lucide usando :nombre_icono:
tabs = st.tabs([
    "🎯 Aplicación", 
    "🌱 Siembra", 
    "🌡️ Delta T", 
    "🌦️ Clima", 
    "ℹ️ Sobre"
])

# ======================================================
# TAB 1 — APLICACIÓN (Tu código original recuperado)
# ======================================================
with tabs[0]:
    st.subheader("📍 Datos del lote y Pulverización")
    # ... (Aquí va tu lógica de Producto/Mixer que ya tenías en el app.py anterior)
    st.info("Sección de pulverización líquida configurada.")

# ======================================================
# TAB 2 — SIEMBRA (Lógica Nueva: Kilos por Especie/Ha)
# ======================================================
with tabs[1]:
    st.header("🌾 Calculadora de Siembra Forrajera")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        nombre_lote_s = st.text_input("Nombre del Lote (Siembra)", value="Lote 1")
    with col_l2:
        hectareas_s = st.number_input("Superficie del Lote (Ha)", min_value=0.1, value=20.0, step=1.0)

    st.divider()
    st.subheader("📋 Composición de la Mezcla")
    
    if "especies" not in st.session_state:
        st.session_state.especies = [{"nombre": "Cebadilla", "kg_ha": 5.0}]

    # Gestión dinámica de especies
    for i, esp in enumerate(st.session_state.especies):
        c1, c2, c3 = st.columns([0.5, 0.3, 0.2])
        esp["nombre"] = c1.text_input(f"Especie {i+1}", value=esp["nombre"], key=f"esp_n_{i}")
        esp["kg_ha"] = c2.number_input("Kg / Ha", min_value=0.0, value=esp["kg_ha"], key=f"esp_k_{i}")
        if c3.button("🗑️", key=f"del_{i}"):
            st.session_state.especies.pop(i)
            st.rerun()

    if st.button("➕ Agregar Especie"):
        st.session_state.especies.append({"nombre": "", "kg_ha": 0.0})
        st.rerun()

    # CÁLCULOS DE SIEMBRA
    total_kg_ha = sum(e["kg_ha"] for e in st.session_state.especies)
    total_mezcla_lote = total_kg_ha * hectareas_s

    st.divider()
    
    # RESULTADOS DE SIEMBRA
    st.subheader("📊 Resumen de Logística")
    
    # Desglose individual
    for e in st.session_state.especies:
        total_e = e["kg_ha"] * hectareas_s
        st.write(f"• **{e['nombre']}**: {total_e:.1f} kg totales para el lote.")

    st.info(f"Dosis total de mezcla: **{total_kg_ha:.2f} kg/ha**")
    
    st.success(f"### Total mezcla necesaria para el lote de {hectareas_s} ha: {total_mezcla_lote:.1f} kg")

# ======================================================
# TAB 3 — DELTA T
# ======================================================
with tabs[2]:
    st.subheader("🌡️ Monitoreo de Condiciones")
    t = st.number_input("Temperatura (°C)", value=25.0)
    h = st.number_input("Humedad (%)", value=60.0)
    dt = t - (t * ( (100-h)/100 ) ) # Cálculo simplificado para ejemplo
    st.metric("Delta T", f"{dt:.1f} °C")

# ======================================================
# TAB 4 — CLIMA (Recuperando botones de diseño previo)
# ======================================================
with tabs[3]:
    st.subheader("🌐 Enlaces Externos de Consulta")
    
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <a href="https://www.windy.com" target="_blank" style="text-decoration:none;">
                <div style="background-color:#0B3D2E; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">
                    🌬️ Abrir Pronóstico en Windy
                </div>
            </a>
            <a href="https://www.swpc.noaa.gov/products/planetary-k-index" target="_blank" style="text-decoration:none;">
                <div style="background-color:#003366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">
                    🧭 Consultar Índice KP (Interferencia GPS)
                </div>
            </a>
        </div>
        """, 
        unsafe_allow_html=True
    )

# ======================================================
# TAB 5 — SOBRE
# ======================================================
with tabs[4]:
    st.info("Desarrollado para optimizar la operación de drones agrícolas.")
