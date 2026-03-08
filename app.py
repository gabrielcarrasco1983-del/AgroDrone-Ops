import streamlit as st
import math

st.set_page_config(page_title="AgroDrone Ops", layout="centered")

st.title("🚁 Planificador Aplicación Drone")

st.markdown("### Datos del lote")

hectareas = st.number_input("Hectáreas", min_value=0.0)
litros_ha = st.number_input("Litros por hectárea", min_value=0.0)
dosis = st.number_input("Dosis producto (cc/ha)", min_value=0.0)
mixer = st.number_input("Capacidad tanque mixer (L)", min_value=0.0)

if st.button("Calcular"):

    agua_total = hectareas * litros_ha
    producto_total_l = (hectareas * dosis) / 1000

    mezclas = agua_total / mixer if mixer > 0 else 0
    tanques = math.ceil(mezclas) if mezclas > 0 else 0

    producto_por_tanque = producto_total_l / mezclas if mezclas > 0 else 0

    st.markdown("---")
    st.markdown("## 📊 Resumen logístico")

    st.write(f"**Total agua:** {agua_total:.2f} L")
    st.write(f"**Producto total:** {producto_total_l:.2f} L")
    st.write(f"**Mezclas de mixer:** {mezclas:.2f}")
    st.write(f"**Tanques necesarios:** {tanques}")

    st.markdown("---")
    st.markdown("## 🧪 Mezcla por tanque")

    st.write(f"Agua por tanque: {mixer} L")
    st.write(f"Producto por tanque: {producto_por_tanque:.2f} L")

st.markdown("---")
st.markdown("## 🌦 Clima y condiciones")

st.markdown("[Windy](https://www.windy.com)")
st.markdown("[Meteoblue](https://www.meteoblue.com)")
st.markdown("[NOAA KP Index](https://www.swpc.noaa.gov/products/planetary-k-index)")
