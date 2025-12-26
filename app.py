import streamlit as st
import pandas as pd
import math
import requests 
from urllib.parse import quote

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AgroDrone Pro", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS CSS (Fix para móviles y diseño profesional) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* FIX MENÚ TABS MÓVIL */
    .stTabs [data-baseweb="tab"] p {
        color: #002A20 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    .stTabs [aria-selected="true"] { border-bottom-color: #88D600 !important; }
    .stTabs [aria-selected="true"] p { color: #88D600 !important; }

    /* Tarjetas de métricas */
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #88D600;
        margin-bottom: 10px;
    }
    
    .delta-ideal { color: #155724; background-color: #d4edda; padding: 5px; border-radius: 5px; font-weight: bold; }
    .delta-warning { color: #856404; background-color: #fff3cd; padding: 5px; border-radius: 5px; font-weight: bold; }
    .delta-danger { color: #721c24; background-color: #f8d7da; padding: 5px; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES LÓGICAS ---

def calculate_delta_t(temp, humidity):
    """Calcula el Delta T usando la fórmula de Stull para temperatura de bulbo húmedo."""
    tw = temp * math.atan(0.151977 * (humidity + 8.313659)**0.5) + \
         math.atan(temp + humidity) - math.atan(humidity - 1.676331) + \
         0.00391838 * (humidity**1.5) * math.atan(0.023101 * humidity) - 4.686035
    return round(temp - tw, 2)

def get_weather_data(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=es"
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# --- UI PRINCIPAL ---
st.title("🚁 AgroDrone Pro Operations")

tabs = st.tabs(["🧪 Mezclas", "☁️ Clima & Delta T", "📏 Calculadora Área", "⚠️ Compatibilidad"])

# --- TAB 1: MEZCLAS Y WHATSAPP ---
with tabs[0]:
    st.subheader("Configuración de Carga")
    c1, c2 = st.columns(2)
    with c1:
        tanque = st.number_input("Capacidad Tanque (L)", value=30.0)
        vol_ha = st.number_input("Caudal (L/Ha)", value=10.0)
    with c2:
        dosis_prod = st.number_input("Dosis Producto (L/Ha o Kg/Ha)", value=1.5)
        lote_nombre = st.text_input("Nombre del Lote", "Lote Norte")

    if vol_ha > 0:
        has_tanque = tanque / vol_ha
        prod_tanque = has_tanque * dosis_prod
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>Resumen por Tanque:</h4>
            <p>✅ <b>Has por vuelo:</b> {has_tanque:.2f} ha</p>
            <p>✅ <b>Producto a cargar:</b> {prod_tanque:.2f} L (o Kg)</p>
            <p>✅ <b>Agua aproximada:</b> {tanque - prod_tanque:.2f} L</p>
        </div>
        """, unsafe_allow_html=True)

        # Botón Compartir WhatsApp
        msg = f"*REPORTE DE CARGA - {lote_nombre}*\n" \
              f"Tanque: {tanque}L\n" \
              f"Caudal: {vol_ha} L/Ha\n" \
              f"--- CARGAR POR TANQUE ---\n" \
              f"💧 Agua: {tanque - prod_tanque:.2f} L\n" \
              f"🧪 Producto: {prod_tanque:.2f} L/Kg\n" \
              f"📍 Cubre: {has_tanque:.2f} Has"
        
        wa_url = f"https://wa.me/?text={quote(msg)}"
        st.markdown(f'[@ Enviar Instrucciones por WhatsApp]({wa_url})')

    st.markdown("---")
    st.caption("📦 **Orden de Carga (WALES):** 1. Polvos (W) -> 2. Agitación (A) -> 3. Líquidos (L) -> 4. Emulsiones (E) -> 5. Surfactantes (S)")

# --- TAB 2: CLIMA Y DELTA T ---
with tabs[1]:
    st.subheader("Condiciones de Aplicación")
    
    modo_clima = st.radio("Fuente de datos:", ["API Online", "Entrada Manual (Seguro)"], horizontal=True)
    
    temp, hum, wind = 0.0, 0.0, 0.0
    
    if modo_clima == "API Online":
        data = get_weather_data(-35.4485, -60.8876, "e07ff67318e1b5f6f5bde3dae5b35ec0")
        if data:
            temp = data['main']['temp']
            hum = data['main']['humidity']
            wind = data['wind']['speed'] * 3.6
            st.success(f"Datos de {data['name']} obtenidos.")
        else:
            st.error("Error de conexión. Usa el Modo Manual.")
    else:
        c1, c2, c3 = st.columns(3)
        temp = c1.number_input("Temp (°C)", value=25.0)
        hum = c2.number_input("Humedad (%)", value=60.0)
        wind = c3.number_input("Viento (km/h)", value=10.0)

    delta_t = calculate_delta_t(temp, hum)
    
    # Visualización Delta T
    st.metric("Delta T (ΔT)", f"{delta_t} °C")
    
    if 2 <= delta_t <= 8:
        st.markdown('<div class="delta-ideal">✅ ÓPTIMO: Condiciones ideales para pulverizar.</div>', unsafe_allow_html=True)
    elif delta_t < 2:
        st.markdown('<div class="delta-warning">⚠️ RIESGO: Supervivencia de gotas alta, riesgo de deriva por inversión.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="delta-danger">❌ EVITAR: Evaporación muy rápida. Gotas no llegan al objetivo.</div>', unsafe_allow_html=True)

# --- TAB 3: ÁREA RESTANTE ---
with tabs[2]:
    st.subheader("Calculadora de 'Caldo' Restante")
    st.info("¿Te sobró mezcla en el tanque? Mira cuánto más puedes pulverizar.")
    litros_sobra = st.number_input("Litros en el tanque", value=5.0)
    caudal_actual = st.number_input("Caudal configurado (L/Ha)", value=10.0, key="caudal_rest")
    
    if caudal_actual > 0:
        area_posible = litros_sobra / caudal_actual
        st.warning(f"Puedes cubrir **{area_posible * 10000:.0f} m²** ({area_posible:.2f} Has) adicionales.")

# --- TAB 4: COMPATIBILIDAD ---
with tabs[3]:
    st.subheader("Guía de Compatibilidad (Referencia)")
    compat_data = {
        "Mezcla": ["Glifosato + 2,4-D", "Graminicida + Aceite", "Insecticida + Fungicida", "Abono Foliar + Herbicida"],
        "Estado": ["Compatible*", "Obligatorio", "Generalmente OK", "Cuidado (Check pH)"],
        "Nota": ["Puede requerir corrector de agua", "Mejora absorción", "Mezclar bien", "Puede precipitar"]
    }
    st.table(pd.DataFrame(compat_data))
    st.caption("* Siempre realice una 'Prueba de Jarra' antes de llenar el mixer.")

# --- PIE DE PÁGINA ---
st.markdown("---")
st.markdown("Desarrollado por **Gabriel Carrasco** | ☕ [Invítame un café](https://www.buymeacoffee.com/gabrielcarc)")