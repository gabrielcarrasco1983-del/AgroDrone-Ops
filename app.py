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
    
    .resumen-carga {
        background-color: #f1f3f5;
        padding: 20px;
        border-radius: 10px;
        border-left: 10px solid #88D600;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES AUXILIARES ---
def calculate_delta_t(temp, humidity):
    tw = temp * math.atan(0.151977 * (humidity + 8.313659)**0.5) + \
         math.atan(temp + humidity) - math.atan(humidity - 1.676331) + \
         0.00391838 * (humidity**1.5) * math.atan(0.023101 * humidity) - 4.686035
    return round(temp - tw, 2)

# --- UI PRINCIPAL ---
st.title("🚁 Sistema de Carga AgroDrone")

tabs = st.tabs(["🧪 Mezcla de Químicos", "☁️ Clima & Delta T", "📏 Área Restante"])

with tabs[0]:
    st.subheader("Configuración del Tanque")
    c1, c2, c3 = st.columns(3)
    with c1:
        tanque_cap = st.number_input("Capacidad Tanque (L)", value=30.0, step=1.0)
    with c2:
        vol_ha = st.number_input("Caudal de Aplicación (L/Ha)", value=10.0, step=1.0)
    with c3:
        nombre_lote = st.text_input("Lote / Trabajo", "Lote 1")

    has_por_tanque = tanque_cap / vol_ha if vol_ha > 0 else 0
    st.info(f"💡 Con un tanque lleno cubrirás: **{has_por_tanque:.2f} Hectáreas**")

    st.markdown("---")
    st.subheader("Lista de Productos (Químicos)")
    
    # Tabla interactiva para agregar productos
    df_init = pd.DataFrame([
        {"Producto": "Glifosato", "Dosis/Ha": 2.0, "Unidad": "L"},
        {"Producto": "Coadyuvante", "Dosis/Ha": 0.2, "Unidad": "L"}
    ])
    
    # Usamos data_editor para que el usuario agregue filas fácilmente
    edited_df = st.data_editor(
        df_init, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Unidad": st.column_config.SelectboxColumn(options=["L", "cc", "Kg", "gr"])
        }
    )

    if has_por_tanque > 0:
        st.markdown('<div class="resumen-carga">', unsafe_allow_html=True)
        st.markdown("### 📋 RECETA POR TANQUE")
        
        lista_whatsapp = []
        for index, row in edited_df.iterrows():
            total_prod = row["Dosis/Ha"] * has_por_tanque
            st.write(f"🔹 **{row['Producto']}:** {total_prod:.3f} {row['Unidad']}")
            lista_whatsapp.append(f"- {row['Producto']}: {total_prod:.3f} {row['Unidad']}")
        
        # Cálculo de agua
        total_quimicos_l = 0 # Simplificado para el ejemplo
        st.write(f"💧 **Agua:** Completar hasta los {tanque_cap} L")
        st.markdown('</div>', unsafe_allow_html=True)

        # Botón WhatsApp mejorado
        msg = f"*ORDEN DE CARGA: {nombre_lote}*\n" \
              f"Tanque: {tanque_cap}L | Caudal: {vol_ha}L/Ha\n" \
              f"Cubre: {has_por_tanque:.2f} Has por vuelo\n" \
              f"--- PRODUCTOS POR TANQUE ---\n" + "\n".join(lista_whatsapp) + \
              f"\n---" \
              f"\n_Generado por AgroDrone Ops_"
        
        wa_url = f"https://wa.me/?text={quote(msg)}"
        st.markdown(f'''
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <div style="background-color:#25D366; color:white; padding:12px; border-radius:8px; text-align:center; font-weight:bold;">
                    📲 Enviar Receta al Ayudante (WhatsApp)
                </div>
            </a>
        ''', unsafe_allow_html=True)

with tabs[1]:
    st.subheader("Monitoreo Delta T")
    c1, c2 = st.columns(2)
    temp = c1.number_input("Temperatura (°C)", value=25.0)
    hum = c2.number_input("Humedad (%)", value=60.0)
    
    dt = calculate_delta_t(temp, hum)
    st.metric("Delta T", f"{dt} °C")
    
    

    if 2 <= dt <= 8:
        st.success("✅ ÓPTIMO: Adelante con la aplicación.")
    elif dt < 2:
        st.warning("⚠️ PRECAUCIÓN: Riesgo de deriva (gotas muy grandes/inversión).")
    else:
        st.error("❌ NO APLICAR: Evaporación excesiva.")

with tabs[2]:
    st.subheader("Cálculo de Área por Remanente")
    litros_quedan = st.number_input("¿Cuántos litros quedan en el drone?", value=0.0)
    if vol_ha > 0:
        area_m2 = (litros_quedan / vol_ha) * 10000
        st.info(f"Con {litros_quedan}L puedes cubrir **{area_m2:.0f} m²** adicionales.")

st.markdown("---")
st.caption("Gabriel Carrasco - AgroDrone Solutions")