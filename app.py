import streamlit as st

# =========================
# IMPORTS DEL CORE
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
from core.storage import load_drones, save_drones  # Importamos la nueva lógica

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
# HEADER Y TABS (Actualizado)
# =========================
st.title("Drone SprayLogic")
st.caption("Calculadora de mezclas y dosis para pulverización con drones")

tabs = st.tabs([
    "🧮 Aplicación",    # tabs[0]
    "🌱 Fertilización", # tabs[1] (Nueva)
    "🌾 Siembra",       # tabs[2] (Nueva)
    "🌡️ Delta T",       # tabs[3] (Antes era tabs[1])
    "🌦️ Clima",         # tabs[4]
    "ℹ️ Sobre"          # tabs[5]
])

# ======================================================
# TAB 1 — CALCULADORA (OPTIMIZADA CAMPO)
# ======================================================
with tabs[0]:

    # ---------- BLOQUE LOTE ----------
    st.subheader("📍 Datos del lote")

    nombre_lote = st.text_input(
        "Nombre del lote",
        value="Lote"
    )

    hectareas = st.number_input(
        "Hectáreas totales",
        min_value=0.0,
        value=10.0,
        step=1.0
    )

    st.divider()

    # ---------- BLOQUE DRON ----------
with tabs[0]:
    drones = load_drones()
    
    st.subheader("🛰️ Selección de Equipo")
    col_d1, col_d2 = st.columns([2, 1])
    
    with col_d1:
        dron_sel = st.selectbox(
            "Seleccionar dron guardado", 
            ["Nuevo dron"] + list(drones.keys())
        )
    with col_d2:
        nombre_dron = st.text_input(
            "Nombre del dron", 
            value="" if dron_sel == "Nuevo dron" else dron_sel
        )

    # Valores por defecto basados en la memoria
    defaults = drones.get(nombre_dron, {"tasa": 10.0, "mixer": 300})
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        tasa = st.number_input("Caudal (L/Ha)", min_value=0.1, value=float(defaults["tasa"]))
    with col_c2:
        mixer_litros = st.number_input("Capacidad Mixer (L)", min_value=1, value=int(defaults["mixer"]))

    if st.button("💾 Guardar y Activar Dron"):
        if nombre_dron:
            drones[nombre_dron] = {"tasa": tasa, "mixer": mixer_litros}
            save_drones(drones)
            st.session_state.dron_activo = nombre_dron
            st.success(f"Configuración de '{nombre_dron}' guardada.")
        else:
            st.error("Por favor, asigna un nombre al dron.")

    # ---------- BLOQUE PRODUCTOS ----------
    st.subheader("🧪 Productos")

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
            "Dosis / Ha",
            min_value=0.0,
            value=fila["d"],
            step=0.1,
            key=f"d_{i}",
            format="%.2f"
        )
        fila["u"] = col3.selectbox(
            "Unidad",
            ["L", "Kg"],
            key=f"u_{i}"
        )

    if st.button("➕ Agregar producto"):
        st.session_state.filas.append({"p": "", "d": 0.0, "u": "L"})
        st.rerun()

    productos = [
        Producto(
            nombre=f["p"] if f["p"] else "Producto",
            dosis=f["d"],
            unidad=f["u"]
        )
        for f in st.session_state.filas
        if f["d"] > 0
    ]

    # ---------- RESULTADOS ----------
    if lote.hectareas > 0 and lote.tasa_l_ha > 0 and productos:

        cobertura = calcular_cobertura(
            lote.mixer_litros,
            lote.tasa_l_ha
        )

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

        st.divider()
        st.subheader("📊 Resultados")

        # Métricas grandes (clave para campo)
        m1, m2 = st.columns(2)
        m1.metric("Hectáreas por mixer", f"{cobertura:.2f} Ha")
        m2.metric("Mixers necesarios", mixers_totales)

        # Mezcla por mixer
        st.subheader("🧪 Mezcla por mixer")
        for p in resultado["por_mixer"]:
            st.write(f"• **{p['producto']}**: {p['cantidad']} {p['unidad']}")

        # Total lote
        st.subheader("📦 Total para el lote")
        for p in resultado["total_lote"]:
            st.write(f"• **{p['producto']}**: {p['cantidad']} {p['unidad']}")

        # Orden de mezcla
        st.subheader("📋 Orden sugerido de mezcla")
        st.markdown(
            """
            1. Agua (50–60%)  
            2. Correctores de pH / dureza  
            3. Polvos mojables (WP, WG)  
            4. Suspensiones concentradas (SC)  
            5. Concentrados emulsionables (EC)  
            6. Soluciones líquidas (SL)  
            7. Coadyuvantes / aceites  
            8. Completar con agua
            """
        )

        # Acciones
        st.divider()

        wa_link = generar_mensaje_whatsapp(
            lote=lote,
            cobertura=cobertura,
            por_mixer=resultado["por_mixer"],
            total_lote=resultado["total_lote"]
        )

        st.markdown(
            f"""
            <a href="{wa_link}" target="_blank">
                <button style="
                    width:100%;
                    background-color:#25D366;
                    color:white;
                    padding:16px;
                    border:none;
                    border-radius:12px;
                    font-size:1rem;
                    font-weight:700;">
                    📲 Enviar receta por WhatsApp
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

        excel_bytes = generar_excel(
            lote.nombre,
            resultado["total_lote"]
        )

        st.download_button(
            "📥 Descargar reporte en Excel",
            excel_bytes,
            file_name=f"Reporte_{lote.nombre}.xlsx"
        )

# ======================================================
# TAB 1 — FERTILIZACIÓN (Lógica integrada)
# ======================================================
with tabs[1]:
    st.subheader("🌱 Gestión de Fertilización")

    # Verificación de Seguridad: Requiere un dron configurado en Tab 0
    if not st.session_state.dron_activo:
        st.warning("⚠️ Primero seleccioná y guardá un dron en la pestaña **Aplicación**.")
        st.info("Esto es necesario para conocer el caudal (L/Ha) y la capacidad del equipo.")
    else:
        # Recuperamos la configuración del dron activo
        drones = load_drones()
        conf = drones.get(st.session_state.dron_activo)
        
        tasa_dron = conf["tasa"]
        mixer_cap = conf["mixer"]

        # Banner informativo del equipo actual
        st.success(f"✅ Equipo: **{st.session_state.dron_activo}** | {tasa_dron} L/Ha | Mixer: {mixer_cap} L")

        # --- Datos del Lote ---
        col_l1, col_l2 = st.columns([2, 1])
        with col_l1:
            nombre_lote_fert = st.text_input("Nombre del lote (Fert)", value="Lote Fert", key="n_l_f")
        with col_l2:
            ha_fert = st.number_input("Hectáreas", min_value=0.1, value=10.0, step=1.0, key="h_f")

        st.divider()

        # --- Selección de Fertilizantes ---
        st.subheader("🧪 Fertilizantes / Productos Sólidos")
        
        for i, fila in enumerate(st.session_state.filas_fert):
            c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
            fila["p"] = c1.text_input(f"Producto {i+1}", fila["p"], key=f"f_p_{i}")
            fila["d"] = c2.number_input("Dosis / Ha", min_value=0.0, value=float(fila["d"]), key=f"f_d_{i}")
            fila["u"] = c3.selectbox("Unidad", ["Kg", "L"], index=0, key=f"f_u_{i}")

        if st.button("➕ Agregar otro fertilizante"):
            st.session_state.filas_fert.append({"p": "", "d": 0.0, "u": "Kg"})
            st.rerun()

        # --- Cálculos y Resultados ---
        lote_obj = Lote(nombre_lote_fert, ha_fert, tasa_dron, mixer_cap)
        prods_filtrados = [p for p in st.session_state.filas_fert if p["d"] > 0]

        if ha_fert > 0 and prods_filtrados:
            from core.calculator import calcular_cobertura, calcular_dosis_productos
            
            cobertura = calcular_cobertura(mixer_cap, tasa_dron)
            res = calcular_dosis_productos(
                [{"nombre": p["p"], "dosis": p["d"], "unidad": p["u"]} for p in prods_filtrados],
                cobertura,
                ha_fert
            )

            st.divider()
            st.subheader("📊 Plan de Carga (Por Mixer)")
            for p in res["por_mixer"]:
                st.write(f"• **{p['producto']}**: {p['cantidad']} {p['unidad']}")

            # Botón de WhatsApp específico para Fertilización
            from core.exporters import generar_mensaje_whatsapp
            wa_link = generar_mensaje_whatsapp(
                lote=lote_obj,
                cobertura=cobertura,
                por_mixer=res["por_mixer"],
                total_lote=res["total_lote"]
            )
            
            st.markdown(
                f'<a href="{wa_link}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:12px; border-radius:10px; cursor:pointer; font-weight:bold;">📲 Enviar Receta de Fertilización</button></a>',
                unsafe_allow_html=True
            )

# ======================================================
# TAB 3 — DELTA T (Movido del índice 1 al 3)
# ======================================================
with tabs[3]:
    st.subheader("🌡️ Delta T")
    # Mantén tu lógica original aquí:
    t = st.number_input("Temperatura (°C)", value=25.0, key="dt_t")
    h = st.number_input("Humedad relativa (%)", value=60.0, key="dt_h")
    
    from core.utils.delta_t import calculate_delta_t
    dt = calculate_delta_t(t, h)
    st.metric("Delta T", f"{dt} °C")

    if 2 <= dt <= 8:
        st.success("Condiciones óptimas de aplicación")
    elif dt < 2:
        st.warning("Riesgo de deriva")
    else:
        st.error("Alta evaporación")

# ======================================================
# TAB 4 — CLIMA
# ======================================================
with tabs[4]:
    st.markdown(
        '<a href="https://www.windy.com" target="_blank" '
        'style="display:block; background:#0B3D2E; color:white; padding:16px; '
        'text-align:center; border-radius:12px; text-decoration:none;">'
        '🌬️ Ver pronóstico en Windy</a>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<a href="https://www.swpc.noaa.gov/products/planetary-k-index" target="_blank" '
        'style="display:block; background:#003366; color:white; padding:16px; '
        'text-align:center; border-radius:12px; text-decoration:none; margin-top:10px;">'
        '🧭 Ver índice KP (NOAA)</a>',
        unsafe_allow_html=True
    )

# ======================================================
# TAB 5 — SOBRE MI
# ======================================================
with tabs[5]:
    st.write(
        "Herramienta diseñada para asistir al aplicador en el cálculo preciso "
        "de mezclas y dosis para pulverización con drones, priorizando eficiencia, "
        "claridad operativa y toma de decisiones en campo."
    )

    st.divider()

    st.write(
        "**Creado por Gabriel Carrasco**  \n"
        "Proyecto orientado a aplicaciones agrícolas con drones."
    )

    st.write("Contacto: **gabriel.carrasco1983@gmail.com**")

