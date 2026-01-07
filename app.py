import streamlit as st
from core.models import Lote, Producto
from core.calculator import (
    calcular_cobertura,
    calcular_mixers_totales,
    calcular_dosis_productos
)
from core.exporters import generar_mensaje_whatsapp, generar_excel
from core.utils.delta_t import calculate_delta_t
from core.storage import load_drones, save_drones 

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="Drone SprayLogic",
    layout="wide"
)

# Estilos con manejo de error
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
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
            st.success(f"Dron '{nombre_dron}' activado.")
        else:
            st.error("Nombre requerido.")

    st.divider()
    st.subheader("📍 Datos del Lote")
    nombre_lote = st.text_input("Nombre del lote", value="Lote Principal", key="lote_app")
    hectareas = st.number_input("Hectáreas totales", min_value=0.1, value=10.0, step=1.0)

    # Definimos el objeto lote
    lote = Lote(nombre=nombre_lote, hectareas=hectareas, tasa_l_ha=tasa, mixer_litros=mixer_litros)

    st.divider()
    st.subheader("🧪 Productos")
    for i, fila in enumerate(st.session_state.filas):
        c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
        fila["p"] = c1.text_input(f"Producto {i+1}", fila["p"], key=f"ap_p_{i}")
        fila["d"] = c2.number_input("Dosis / Ha", min_value=0.0, value=float(fila["d"]), step=0.1, key=f"ap_d_{i}")
        fila["u"] = c3.selectbox("Unidad", ["L", "Kg"], key=f"ap_u_{i}")

    if st.button("➕ Agregar Producto"):
        st.session_state.filas.append({"p": "", "d": 0.0, "u": "L"})
        st.rerun()

    prods_val = [{"nombre": f["p"] if f["p"] else "Producto", "dosis": f["d"], "unidad": f["u"]} for f in st.session_state.filas if f["d"] > 0]

    if lote.hectareas > 0 and lote.tasa_l_ha > 0 and prods_val:
        cobertura = calcular_cobertura(lote.mixer_litros, lote.tasa_l_ha)
        mixers_totales = calcular_mixers_totales(lote.hectareas, lote.tasa_l_ha, lote.mixer_litros)
        resultado = calcular_dosis_productos(prods_val, cobertura, lote.hectareas)

        st.divider()
        st.subheader("📊 Resultados")
        m1, m2 = st.columns(2)
        m1.metric("Hectáreas por mixer", f"{cobertura:.2f} Ha")
        m2.metric("Mixers necesarios", mixers_totales)

        # CORRECCIÓN DE LA FUNCIÓN: Quitamos el primer argumento "Aplicación"
        wa_link = generar_mensaje_whatsapp(
            lote=lote, 
            cobertura=cobertura, 
            por_mixer=resultado["por_mixer"], 
            total_lote=resultado["total_lote"]
        )

        st.markdown(f'<a href="{wa_link}" target="_blank"><button style="width:100%;background:#25D366;color:white;padding:16px;border:none;border-radius:12px;font-weight:700;cursor:pointer;">📲 Enviar Receta WhatsApp</button></a>', unsafe_allow_html=True)

# ======================================================
# TAB 1 — FERTILIZACIÓN
# ======================================================
with tabs[1]:
    if not st.session_state.dron_activo:
        st.warning("⚠️ Seleccioná un dron en la pestaña Aplicación.")
    else:
        drones = load_drones()
        conf = drones.get(st.session_state.dron_activo)
        
        st.subheader("🌱 Fertilización")
        st.info(f"Dron: {st.session_state.dron_activo}")
        
        ha_f = st.number_input("Hectáreas (Fert)", min_value=0.1, value=10.0, key="hf")
        lote_f = Lote(nombre="Lote Fertilización", hectareas=ha_f, tasa_l_ha=conf["tasa"], mixer_litros=conf["mixer"])
        
        # Lógica de filas para fertilización...
        # (Aquí puedes repetir la lógica de productos usando st.session_state.filas_fert)

# ======================================================
# TAB 3 — DELTA T (Movido a índice 3)
# ======================================================
with tabs[3]:
    st.subheader("🌡️ Delta T")
    t = st.number_input("Temperatura (°C)", value=25.0, key="dt_t")
    h = st.number_input("Humedad (%)", value=60.0, key="dt_h")
    dt = calculate_delta_t(t, h)
    st.metric("Delta T", f"{dt} °C")

# ... rest of tabs ...
