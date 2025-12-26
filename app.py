import streamlit as st
import pandas as pd
import math
import requests 
from urllib.parse import quote

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AgroDrone Pro", layout="wide")

# --- ESTILOS CSS (Móvil y Legibilidad) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    .stTabs [data-baseweb="tab"] p { color: #002A20 !important; font-weight: 600; font-size: 0.9rem; }
    .stTabs [aria-selected="true"] { border-bottom-color: #88D600 !important; }
    .stTabs [aria-selected="true"] p { color: #88D600 !important; }
    .stWidget label p { color: #000000 !important; font-weight: bold; }
    
    /* Diseño de Fichas (Vademécum) */
    .ficha-box { border: 1px solid #002A20; margin-bottom: 20px; background-color: #ffffff; }
    .ficha-titulo { background-color: #002A20; color: #ffffff !important; padding: 10px; font-weight: 700; text-align: center; }
    .seccion-gris { background-color: #F2F2F2; padding: 5px 15px; font-weight: 700; color: #002A20; border-top: 1px solid #002A20; font-size: 0.8rem; }
    .contenido-ficha { padding: 10px 15px; font-size: 0.9rem; }
    
    .resumen-total { background-color: #e9ecef; padding: 15px; border-radius: 10px; border-left: 10px solid #002A20; margin-bottom: 20px; }
    .resumen-tanque { background-color: #f1f8e9; padding: 15px; border-radius: 10px; border-left: 10px solid #88D600; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES ---
def calculate_delta_t(temp, humidity):
    tw = temp * math.atan(0.151977 * (humidity + 8.313659)**0.5) + \
         math.atan(temp + humidity) - math.atan(humidity - 1.676331) + \
         0.00391838 * (humidity**1.5) * math.atan(0.023101 * humidity) - 4.686035
    return round(temp - tw, 2)

# --- UI PRINCIPAL ---
st.title("🚁 AgroDrone Ops Pro")

tabs = st.tabs(["🧪 Mezcla y Lote", "🌡️ Delta T", "📚 Vademécum"])

with tabs[0]:
    st.subheader("1. Configuración del Trabajo")
    c1, c2, c3 = st.columns(3)
    with c1:
        hectareas_totales = st.number_input("Hectáreas Totales del Lote", value=10.0, step=1.0)
    with c2:
        vol_ha = st.number_input("Caudal (L/Ha)", value=10.0, step=1.0)
    with c3:
        tanque_cap = st.number_input("Capacidad Tanque Drone (L)", value=30.0, step=1.0)

    st.markdown("---")
    st.subheader("2. Productos y Dosis")
    
    df_init = pd.DataFrame([
        {"Producto": "Herbicida X", "Dosis/Ha": 2.0, "Unidad": "L"},
        {"Producto": "Coadyuvante", "Dosis/Ha": 0.2, "Unidad": "L"}
    ])
    
    edited_df = st.data_editor(df_init, num_rows="dynamic", use_container_width=True)

    if hectareas_totales > 0 and vol_ha > 0:
        total_caldo_lote = hectareas_totales * vol_ha
        vuelos_necesarios = total_caldo_lote / tanque_cap
        has_por_vuelo = tanque_cap / vol_ha

        # --- RESUMEN TOTAL ---
        st.markdown(f"""
        <div class="resumen-total">
            <h4>📊 TOTAL PARA EL LOTE ({hectareas_totales} Ha)</h4>
            <p>💧 <b>Agua Total:</b> {total_caldo_lote:.1f} L</p>
            <p>🚁 <b>Vuelos estimados:</b> {math.ceil(vuelos_necesarios)} vuelos</p>
        """, unsafe_allow_html=True)
        
        lista_wa = []
        for _, row in edited_df.iterrows():
            total_lote = row["Dosis/Ha"] * hectareas_totales
            st.write(f"📦 **{row['Producto']}:** {total_lote:.2f} {row['Unidad']} (Total Lote)")
            
        st.markdown("</div>", unsafe_allow_html=True)

        # --- RESUMEN POR TANQUE ---
        st.markdown(f"""
        <div class="resumen-tanque">
            <h4>🧪 CARGA POR TANQUE ({tanque_cap}L)</h4>
            <p>📍 Cubre: <b>{has_por_vuelo:.2f} Ha</b> por vuelo</p>
        """, unsafe_allow_html=True)
        
        for _, row in edited_df.iterrows():
            prod_tanque = row["Dosis/Ha"] * has_por_vuelo
            st.write(f"✅ **{row['Producto']}:** {prod_tanque:.3f} {row['Unidad']}")
            lista_wa.append(f"- {row['Producto']}: {prod_tanque:.3f}{row['Unidad']}")
        
        st.markdown("</div>", unsafe_allow_html=True)

        # WhatsApp
        msg = f"*ORDEN DE CARGA*\nLote: {hectareas_totales}Ha\nTanque: {tanque_cap}L\nCaudal: {vol_ha}L/Ha\n--- POR TANQUE ---\n" + "\n".join(lista_wa)
        st.markdown(f'[@ Enviar Receta WhatsApp](https://wa.me/?text={quote(msg)})')

with tabs[1]:
    st.subheader("Condiciones Ambientales (Delta T)")
    
    # Opción manual por seguridad
    c1, c2 = st.columns(2)
    temp = c1.number_input("Temperatura (°C)", value=25.0)
    hum = c2.number_input("Humedad (%)", value=60.0)
    
    dt = calculate_delta_t(temp, hum)
    st.metric("Delta T", f"{dt} °C")

    

    if 2 <= dt <= 8:
        st.success("✅ ÓPTIMO")
    elif dt < 2:
        st.warning("⚠️ RIESGO DE DERIVA")
    else:
        st.error("❌ EVAPORACIÓN ALTA")

with tabs[2]:
    st.subheader("📚 Vademécum de Productos")
    
    busqueda = st.text_input("Buscar producto (ej. Glifosato)...").lower()
    
    # Datos del Vademécum
    productos = [
        {"nombre": "GLIFOSATO 66.2%", "tipo": "Herbicida", "dosis": "2-4 L/Ha", "obs": "No aplicar con vientos mayores a 10km/h."},
        {"nombre": "2,4-D ENLIST", "tipo": "Herbicida", "dosis": "1-1.5 L/Ha", "obs": "Uso exclusivo en soja/maíz Enlist."},
        {"nombre": "ACEITE METILADO", "tipo": "Coadyuvante", "dosis": "0.5 L/Ha", "obs": "Mejora penetración en cutículas difíciles."}
    ]

    for p in productos:
        if busqueda in p["nombre"].lower() or busqueda in p["tipo"].lower():
            st.markdown(f"""
            <div class="ficha-box">
                <div class="ficha-titulo">{p['nombre']}</div>
                <div class="seccion-gris">TIPO DE PRODUCTO</div>
                <div class="contenido-ficha">{p['tipo']}</div>
                <div class="seccion-gris">DOSIS RECOMENDADA</div>
                <div class="contenido-ficha">{p['dosis']}</div>
                <div class="seccion-gris">OBSERVACIONES TÉCNICAS</div>
                <div class="contenido-ficha">{p['obs']}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Gabriel Carrasco - AgroDrone Pro v2.0")
