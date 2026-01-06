import streamlit as st
import json
import os
from dataclasses import dataclass

# ======================================================
# Drone SprayLogic — v0.7.2
# Fertilización integrada con dron activo
# ======================================================

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
# MODELOS
# =========================
@dataclass
class Producto:
    nombre: str
    dosis: float
    unidad: str

@dataclass
class Lote:
    nombre: str
    hectareas: float
    tasa_l_ha: float
    mixer_litros: int

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
# MEMORIA DE DRONES
# =========================
DRONES_FILE = "drones.json"

def load_drones():
    if not os.path.exists(DRONES_FILE):
        return {}
    try:
        with open(DRONES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_drones(drones_dict):
    with open(DRONES_FILE, "w") as f:
        json.dump(drones_dict, f, indent=2)

# =========================
# FUNCIONES DE CÁLCULO
# =========================
def calcular_cobertura(mixer_l, tasa):
    return mixer_l / tasa if tasa > 0 else 0

def calcular_mixers_totales(ha, tasa, mixer):
    total_litros = ha * tasa
    return int((total_litros / mixer) + 0.999)

def calcular_dosis_productos(productos, cobertura_ha, hectareas):
    por_mixer = []
    total_lote = []

    for p in productos:
        por_mixer.append({
            "producto": p["nombre"],
            "cantidad": round(p["dosis"] * cobertura_ha, 2),
            "unidad": p["unidad"]
        })
        total_lote.append({
            "producto": p["nombre"],
            "cantidad": round(p["dosis"] * hectareas, 2),
            "unidad": p["unidad"]
        })

    return {"por_mixer": por_mixer, "total_lote": total_lote}

def generar_mensaje_whatsapp(titulo, lote, cobertura, por_mixer, total_lote):
    texto = f"""🛰️ *{titulo} – SprayLogic*

Dron: {st.session_state.dron_activo}
Lote: {lote.nombre}
Superficie: {lote.hectareas} ha
Caudal: {lote.tasa_l_ha} L/ha
Mixer: {lote.mixer_litros} L

Cobertura: {cobertura:.2f} ha/mixer

*Mezcla por mixer*"""
    for p in por_mixer:
        texto += f"\n- {p['producto']}: {p['cantidad']} {p['unidad']}"

    texto += "\n\n*Total para el lote*"
    for p in total_lote:
        texto += f"\n- {p['producto']}: {p['cantidad']} {p['unidad']}"

    return "https://wa.me/?text=" + texto.replace(" ", "%20").replace("\n", "%0A")

# =========================
# TABS
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
    drones = load_drones()

    st.subheader("🛰️ Dron")

    col_d1, col_d2 = st.columns([2, 1])

    with col_d1:
        dron_sel = st.selectbox(
            "Seleccionar dron",
            ["Nuevo dron"] + list(drones.keys())
        )

    with col_d2:
        nombre_dron = st.text_input(
            "Nombre del dron",
            value="" if dron_sel == "Nuevo dron" else dron_sel
        )

    st.subheader("📍 Datos del lote")

    nombre_lote = st.text_input("Nombre del lote", value="Lote")
    hectareas = st.number_input("Hectáreas totales", min_value=0.0, value=10.0, step=1.0)

    st.divider()
    st.subheader("🚁 Configuración del dron")

    defaults = drones.get(nombre_dron, {})
    tasa_default = defaults.get("tasa", 10.0)
    mixer_default = defaults.get("mixer", 300)

    col1, col2 = st.columns(2)

    with col1:
        tasa = st.number_input(
            "Caudal de aplicación (L/Ha)",
            min_value=0.1,
            value=float(tasa_default),
            step=1.0
        )

    with col2:
        mixer_litros = st.selectbox(
            "Capacidad del mixer (L)",
            [100, 200, 300, 500],
            index=[100, 200, 300, 500].index(mixer_default)
            if mixer_default in [100, 200, 300, 500] else 2
        )

    if nombre_dron and st.button("💾 Guardar configuración del dron"):
        drones[nombre_dron] = {"tasa": tasa, "mixer": mixer_litros}
        save_drones(drones)
        st.success("Configuración guardada")

    if nombre_dron:
        st.session_state.dron_activo = nombre_dron

    lote = Lote(nombre_lote, hectareas, tasa, mixer_litros)

    st.divider()
    st.subheader("🧪 Productos")

    for i, fila in enumerate(st.session_state.filas):
        c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
        fila["p"] = c1.text_input(f"Producto {i+1}", fila["p"], key=f"ap_p_{i}")
        fila["d"] = c2.number_input(
            "Dosis / Ha", min_value=0.0, value=float(fila["d"]),
            step=0.1, key=f"ap_d_{i}"
        )
        fila["u"] = c3.selectbox("Unidad", ["L", "Kg"], key=f"ap_u_{i}")

    if st.button("➕ Agregar producto"):
        st.session_state.filas.append({"p": "", "d": 0.0, "u": "L"})
        st.rerun()

    productos = [
        Producto(f["p"], f["d"], f["u"])
        for f in st.session_state.filas if f["d"] > 0
    ]

    if hectareas > 0 and tasa > 0 and productos:
        cobertura = calcular_cobertura(mixer_litros, tasa)
        mixers = calcular_mixers_totales(hectareas, tasa, mixer_litros)

        res = calcular_dosis_productos(
            [{"nombre": p.nombre, "dosis": p.dosis, "unidad": p.unidad} for p in productos],
            cobertura,
            hectareas
        )

        st.divider()
        st.subheader("📊 Resultados")

        st.metric("Hectáreas por mixer", f"{cobertura:.2f}")
        st.metric("Mixers necesarios", mixers)

        wa = generar_mensaje_whatsapp(
            "Aplicación con dron",
            lote, cobertura,
            res["por_mixer"], res["total_lote"]
        )

        st.markdown(
            f"""<a href="{wa}" target="_blank">
            <button style="width:100%;background:#25D366;color:white;
            padding:16px;border:none;border-radius:12px;font-weight:700;">
            📲 Enviar receta por WhatsApp
            </button></a>""",
            unsafe_allow_html=True
        )

# ======================================================
# TAB 1 — FERTILIZACIÓN (v0.7.2)
# ======================================================
with tabs[1]:
    st.subheader("🌱 Fertilización")

    if not st.session_state.dron_activo:
        st.warning("Primero seleccioná y guardá un dron en la pestaña Aplicación.")
    else:
        drones = load_drones()
        conf = drones.get(st.session_state.dron_activo)

        tasa = conf["tasa"]
        mixer_litros = conf["mixer"]

        nombre_lote = st.text_input("Nombre del lote", value="Lote fertilización")
        hectareas = st.number_input("Hectáreas", min_value=0.0, value=10.0, step=1.0)

        lote = Lote(nombre_lote, hectareas, tasa, mixer_litros)

        st.divider()
        st.subheader("🧪 Fertilizantes")

        for i, fila in enumerate(st.session_state.filas_fert):
            c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
            fila["p"] = c1.text_input(f"Fertilizante {i+1}", fila["p"], key=f"f_p_{i}")
            fila["d"] = c2.number_input(
                "Dosis / Ha", min_value=0.0, value=float(fila["d"]),
                step=0.1, key=f"f_d_{i}"
            )
            fila["u"] = c3.selectbox("Unidad", ["Kg", "L"], key=f"f_u_{i}")

        if st.button("➕ Agregar fertilizante"):
            st.session_state.filas_fert.append({"p": "", "d": 0.0, "u": "Kg"})
            st.rerun()

        productos = [
            Producto(f["p"], f["d"], f["u"])
            for f in st.session_state.filas_fert if f["d"] > 0
        ]

        if hectareas > 0 and productos:
            cobertura = calcular_cobertura(mixer_litros, tasa)

            res = calcular_dosis_productos(
                [{"nombre": p.nombre, "dosis": p.dosis, "unidad": p.unidad} for p in productos],
                cobertura,
                hectareas
            )

            wa = generar_mensaje_whatsapp(
                "Fertilización con dron",
                lote, cobertura,
                res["por_mixer"], res["total_lote"]
            )

            st.markdown(
                f"""<a href="{wa}" target="_blank">
                <button style="width:100%;background:#25D366;color:white;
                padding:16px;border:none;border-radius:12px;font-weight:700;">
                📲 Enviar fertilización por WhatsApp
                </button></a>""",
                unsafe_allow_html=True
            )

# ======================================================
# TAB 2 — SIEMBRA (placeholder)
# ======================================================
with tabs[2]:
    st.subheader("🌾 Siembra")
    st.info("Módulo en construcción. Próximo paso.")

# ======================================================
# TAB 3–5
# ======================================================
with tabs[3]:
    st.subheader("🌡️ Delta T")

with tabs[4]:
    st.subheader("🌦️ Clima")
    st.markdown("[Pronóstico KP – NOAA](https://www.swpc.noaa.gov/products/planetary-k-index)")

with tabs[5]:
    st.subheader("ℹ️ Sobre")
    st.write("Drone SprayLogic — Plataforma profesional para drones agrícolas.")
