import streamlit as st
from core.models import Lote, Producto
from core.calculator import (
    calcular_cobertura,
    calcular_mixers_totales,
    calcular_dosis_productos
)
from core.exporters import generar_mensaje_whatsapp, generar_excel
from core.utils.delta_t import calculate_delta_t
from core.storage import load_drones, save_drones  # Asegúrate de haber creado core/storage.py

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="Drone SprayLogic",
    layout="wide"
)

# Carga de estilos (opcional, con manejo de error)
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# =========================
# SESSION STATE GLOBAL
# =========================
if "dron_activo" not in st.session_state:
    st.session_state.dron_activo = None

if "filas" not in st.session_state:
    st.session_state.filas = [{"p": "", "d": 0.0, "u": "L"}]

if "filas_fert" not in st.session_state:
    st.session_state.filas_fert = [{"p": "", "d": 0.0, "u": "Kg"}]

# =========================
# HEADER Y TABS
# =========================
st.title("🛰️ Drone SprayLogic")
st.caption("Plataforma operativa para aplicaciones, fertilización y siembra con drones")

tabs = st.tabs([
    "🧮 Aplicación", 
    "🌱 Fertilización", 
    "🌾 Siembra", 
    "🌡️ Delta T", 
    "🌦️ Clima", 
    "ℹ️ Sobre"
])

# ======================================================
# TAB 0 — APLICACIÓN
# ======================================================
with tabs[0]:
    drones = load_drones()
    st.subheader("🛰️ Configuración del Equipo")

    col_d1, col_d2 = st.columns([2, 1])
    with col_d1:
        dron_sel = st.selectbox("Seleccionar dron", ["Nuevo dron"] + list(drones.keys()))
    with col_d2:
        nombre_dron = st.text_input("Nombre del dron", value="" if dron_sel == "Nuevo dron" else dron_sel)

    defaults = drones.get(nombre_dron, {"tasa": 10.0, "mixer": 300})

    col1, col2 = st.columns(2)
    with col1:
        tasa = st.number_input("Caudal (L/Ha)", min_value=0.1, value=float(defaults["tasa"]), step=1.0)
    with col2:
        mixer_litros = st.number_input("Capacidad Mixer (L)", min_value=1, value=int(defaults["mixer"]), step=10)

    if st.button("💾 Guardar y Activar Dron"):
        if nombre_dron:
            drones[nombre_dron] = {"tasa": tasa, "mixer": mixer_litros}
            save_drones(drones)
            st.session_state.dron_activo = nombre_dron
            st.success(f"Dron '{nombre_dron}' activado correctamente.")
        else:
            st.error("Asigna un nombre al dron para guardar.")

    st.divider()
    st.subheader("📍 Datos del Lote")
    nombre_lote = st.text_input("Nombre del lote", value="Lote Principal", key="lote_app")
    hectareas = st.number_input("Hectáreas totales", min_value=0.1, value=10.0, step=1.0)

    # CREACIÓN DEL OBJETO LOTE (Evita NameError)
    lote = Lote(nombre=nombre_lote, hectareas=hectareas, tasa_l_ha=tasa, mixer_litros=mixer_litros)

    st.divider()
    st.subheader("🧪 Productos")
    for i, fila in enumerate(st.session_state.filas):
        c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
        fila["p"] = c1.text_input(f"Producto {i+1}", fila["p"], key=f"ap_p_{i}")
        fila["d"] = c2.number_input("Dosis / Ha", min_value=0.0, value=float(fila["d"]), step=0.1, key=f"ap_d_{i}")
        fila["u"] = c3.selectbox("Unidad", ["L", "Kg"], key=f"ap_u_{i}")

    if st.button("➕ Agregar Producto", key="add_ap"):
        st.session_state.filas.append({"p": "", "d": 0.0, "u": "L"})
        st.rerun()

    # Procesamiento de productos con dosis > 0
    productos_validados = [
        {"nombre": f["p"] if f["p"] else f"Producto {idx+1}", "dosis": f["d"], "unidad": f["u"]}
        for idx, f in enumerate(st.session_state.filas) if f["d"] > 0
    ]

    if lote.hectareas > 0 and lote.tasa_l_ha > 0 and productos_validados:
        cobertura = calcular_cobertura(lote.mixer_litros, lote.tasa_l_ha)
        mixers_totales = calcular_mixers_totales(lote.hectareas, lote.tasa_l_ha, lote.mixer_litros)
        resultado = calcular_dosis_productos(productos_validados, cobertura, lote.hectareas)

        st.divider()
        st.subheader("📊 Resultados")
        m1, m2 = st.columns(2)
        m1.metric("Hectáreas por mixer", f"{cobertura:.2f} Ha")
        m2.metric("Mixers necesarios", mixers_totales)

        st.subheader("🧪 Mezcla por mixer")
        for p in resultado["por_mixer"]:
            st.write(f"• **{p['producto']}**: {p['cantidad']} {p['unidad']}")

        wa_link = generar_mensaje_whatsapp("Aplicación", lote, cobertura, resultado["por_mixer"], resultado["total_lote"])
        st.markdown(f'<a href="{wa_link}" target="_blank"><button style="width:100%;background:#25D366;color:white;padding:12px;border:none;border-radius:10px;font-weight:bold;cursor:pointer;">📲 WhatsApp Receta</button></a>', unsafe_allow_html=True)

# ======================================================
# TAB 1 — FERTILIZACIÓN
# ======================================================
with tabs[1]:
    st.subheader("🌱 Fertilización Sólida")
    if not st.session_state.dron_activo:
        st.warning("⚠️ Debes activar un dron en la pestaña **Aplicación**.")
    else:
        conf = load_drones().get(st.session_state.dron_activo)
        st.success(f"Dron: **{st.session_state.dron_activo}** ({conf['tasa']} L/ha)")

        nombre_lote_f = st.text_input("Lote de Fertilización", value="Lote Fert", key="lote_f")
        ha_f = st.number_input("Hectáreas", min_value=0.1, value=10.0, key="ha_f")

        lote_f = Lote(nombre_lote_f, ha_f, conf["tasa"], conf["mixer"])

        for i, fila in enumerate(st.session_state.filas_fert):
            c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
            fila["p"] = c1.text_input(f"Fertilizante {i+1}", fila["p"], key=f"f_p_{i}")
            fila["d"] = c2.number_input("Dosis / Ha", min_value=0.0, value=float(fila["d"]), key=f"f_d_{i}")
            fila["u"] = c3.selectbox("Unidad", ["Kg", "L"], key=f"f_u_{i}")

        if st.button("➕ Agregar Fertilizante", key="add_f"):
            st.session_state.filas_fert.append({"p": "", "d": 0.0, "u": "Kg"})
            st.rerun()

        prods_f = [{"nombre": f["p"], "dosis": f["d"], "unidad": f["u"]} for f in st.session_state.filas_fert if f["d"] > 0]
        
        if ha_f > 0 and prods_f:
            cob_f = calcular_cobertura(lote_f.mixer_litros, lote_f.tasa_l_ha)
            res_f = calcular_dosis_productos(prods_f, cob_f, ha_f)
            
            st.divider()
            st.subheader("📋 Plan de Carga")
            for p in res_f["por_mixer"]:
                st.write(f"• **{p['producto']}**: {p['cantidad']} {p['unidad']}")

# ======================================================
# TABS RESTANTES
# ======================================================
with tabs[2]:
    st.subheader("🌾 Siembra")
    st.info("Módulo en desarrollo.")

with tabs[3]:
    st.subheader("🌡️ Delta T")
    t_dt = st.number_input("Temperatura (°C)", value=25.0, key="dt_t")
    h_dt = st.number_input("Humedad (%)", value=60.0, key="dt_h")
    dt_val = calculate_delta_t(t_dt, h_dt)
    st.metric("Delta T", f"{dt_val} °C")

with tabs[4]:
    st.subheader("🌦️ Clima")
    st.markdown("[Pronóstico Windy](https://www.windy.com)")
    st.markdown("[Índice KP NOAA](https://www.swpc.noaa.gov/products/planetary-k-index)")

with tabs[5]:
    st.write("Drone SprayLogic v0.7.2 - Gabriel Carrasco")
