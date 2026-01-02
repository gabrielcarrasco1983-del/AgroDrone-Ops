import streamlit as st
import pandas as pd
import math
import io
from datetime import datetime
from urllib.parse import quote

# =========================
# IMPORTS DEL CORE
# =========================
from core.calculator import (
    calcular_cobertura,
    calcular_mixers_totales,
    calcular_dosis_productos
)
from core.models import Lote, Producto
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
# TÍTULO
# =========================
st.title("Drone SprayLogic")
st.caption("Plataforma inteligente de pulverización agrícola con drones")

tabs = st.tabs([
    "🧮 Calculadora",
    "🌡️ Delta T",
    "🌦️ Clima",
    "📖 Vademécum",
    "👥 Sobre el Autor"
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
        mixer_opt = st.selectbox("Capacidad Mixer (L)", ["100", "200", "300", "500", "Manual"])
        mixer_litros = (
            st.number_input("Litros Reales", value=330)
            if mixer_opt == "Manual"
            else int(mixer_opt)
        )
    with c3:
        tasa = st.number_input("Caudal Dron (L/Ha)", value=10.0, step=1.0)

    # Objeto Lote
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
            f"Producto {i+1}",
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
    productos = []
    for f in st.session_state.filas:
        if f["d"] > 0:
            productos.append(
                Producto(
                    nombre=f["p"] if f["p"] else "Producto",
                    dosis=f["d"],
                    unidad=f["u"]
                )
            )

    # =========================
    # CÁLCULOS
    # =========================
    if lote.hectareas > 0 and lote.tasa_l_ha > 0:
        cobertura = calcular_cobertura(lote.mixer_litros, lote.tasa_l_ha)
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
            f"<div class='resumen-caja'><h3>🧪 MEZCLA POR MIXER ({lote.mixer_litros} L)</h3>"
            f"<p>Cubre: <b>{cobertura:.2f} Ha</b></p>",
            unsafe_allow_html=True
        )

        wa_mixer = []
        wa_total = []
        excel_data = []

        for p in resultado["por_mixer"]:
            st.write(f"✅ **{p['producto']}:** {p['cantidad']} {p['unidad']}")
            wa_mixer.append(f"- {p['producto']}: {p['cantidad']} {p['unidad']}")

        st.markdown("</div><div class='total-lote-caja'>", unsafe_allow_html=True)
        st.subheader(f"📊 REPORTE TOTAL: {lote.nombre}")
        st.write(f"Preparaciones de Mixer: **{mixers_totales}**")

        for t in resultado["total_lote"]:
            st.write(f"- {t['producto']}: {t['cantidad']} {t['unidad']}")
            wa_total.append(f"- {t['producto']}: {t['cantidad']} {t['unidad']}")
            excel_data.append({
                "Lote": lote.nombre,
                "Producto": t["producto"],
                "Cantidad": t["cantidad"],
                "Unidad": t["unidad"]
            })

        st.markdown("</div>", unsafe_allow_html=True)

        # =========================
        # WHATSAPP
        # =========================
        msg = (
            f"*DRONE SPRAYLOGIC*\n"
            f"*Lote:* {lote.nombre}\n"
            f"Mixer: {lote.mixer_litros}L | Cubre: {cobertura:.2f}Ha\n"
            f"--- POR MIXER ---\n" + "\n".join(wa_mixer) +
            f"\n--- TOTAL LOTE ({lote.hectareas}Ha) ---\n" + "\n".join(wa_total)
        )

        st.markdown(
            f'<a href="https://wa.me/?text={quote(msg)}" target="_blank">'
            f'<button style="width:100%; background-color:#25D366; color:white; '
            f'padding:15px; border:none; border-radius:10px; font-weight:bold;">'
            f'📲 ENVIAR ORDEN COMPLETA</button></a>',
            unsafe_allow_html=True
        )

        # =========================
        # EXCEL
        # =========================
        df_export = pd.DataFrame(excel_data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_export.to_excel(writer, index=False, sheet_name="Reporte")

        st.download_button(
            label="📥 DESCARGAR LOG (EXCEL)",
            data=output.getvalue(),
            file_name=f"Reporte_{lote.nombre}.xlsx",
            mime="application/vnd.ms-excel"
        )

# ======================================================
# TAB 2 — DELTA T
# ======================================================
with tabs[1]:
    st.subheader("Análisis Ambiental")
    t = st.number_input("Temperatura °C", value=25.0)
    h = st.number_input("Humedad %", value=60.0)

    dt = calculate_delta_t(t, h)
    st.metric("Delta T", f"{dt} °C")

    if 2 <= dt <= 8:
        st.success("✅ Condiciones óptimas")
    elif dt < 2:
        st.warning("⚠️ Riesgo de deriva")
    else:
        st.error("❌ Evaporación elevada")

# ======================================================
# TAB 3 — CLIMA
# ======================================================
with tabs[2]:
    st.markdown(
        '<a href="https://www.windy.com" target="_blank" '
        'style="display:block; background:#002A20; color:white; padding:15px; '
        'text-align:center; border-radius:10px; text-decoration:none;">'
        '🌬️ CONSULTAR WINDY</a>',
        unsafe_allow_html=True
    )

# ======================================================
# TAB 4 y 5 — SIN CAMBIOS POR AHORA
# ======================================================
