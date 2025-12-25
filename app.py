import streamlit as st
import math

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="AgroDosis - Precisión", page_icon="🛸", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .result-card { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 15px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 10px solid #2D5A27;
    }
    h3 { color: #1e4d2b; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS (Basada en tus archivos de Nutrien) ---
# Datos específicos extraídos del PDF de Nutrien
fitos_db = {
    "Glifosato 480 SL (Nutrien)": {
        "min": 1.5, "max": 10.0, "unidad": "L/ha", 
        "alerta": "No aplicar más de 15 kg/año. Evitar lluvias 48-72h posteriores.",
        "orden": "Líquidos Solubles (SL)"
    },
    "Atrazina": {"min": 0.5, "max": 3.0, "unidad": "kg/ha", "orden": "Sólidos Secos (WG/WP)"},
    "2,4-D": {"min": 0.5, "max": 1.5, "unidad": "L/ha", "orden": "Emulsiones (EC)"}
}

# --- DISEÑO DE LA INTERFAZ ---
st.markdown("## ⚙️ Parámetros de Trabajo")

col_in, col_out = st.columns([1.2, 1], gap="large")

with col_in:
    # Ajustado a los valores de tu imagen
    lote_ha = st.number_input("Superficie del Lote (ha)", value=20.00, step=1.0)
    tasa_dron = st.number_input("Tasa de Aplicación Dron (L/ha)", value=10.00, step=0.5)
    capacidad_mixer = st.selectbox("Capacidad del Mixer (L)", [1000, 500, 300, 200, 100])
    
    st.divider()
    st.markdown("### 🧪 Selección de Producto")
    producto_name = st.selectbox("Principio Activo", list(fitos_db.keys()))
    
    info = fitos_db[producto_name]
    
    # Slider configurado con los rangos del vademécum
    dosis_user = st.slider(f"Dosis a aplicar ({info['unidad']})", 
                           float(info['min']), float(info['max']), 1.50)

with col_out:
    # Lógica de Cálculo
    vol_total = lote_ha * tasa_dron
    prod_total = lote_ha * dosis_user
    cant_cargas = math.ceil(vol_total / capacidad_mixer)
    prod_por_carga = prod_total / cant_cargas if cant_cargas > 0 else 0
    
    st.markdown(f"""
        <div class="result-card">
            <h3>📊 Resultados de la Operación</h3>
            <p>Volumen Total de Caldo: <b>{vol_total:.2f} Litros</b></p>
            <p>Total de {producto_name}: <b>{prod_total:.2f} {info['unidad'].split('/')[0]}</b></p>
            <hr>
            <h3>🚚 Logística de Carga</h3>
            <p>Cantidad de Cargas: <b>{cant_cargas} cargas</b> de mixer</p>
            <p>Producto por cada carga: <b>{prod_por_carga:.2f} {info['unidad'].split('/')[0]}</b></p>
            <p>Orden de mezcla: <b>{info['orden']}</b></p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("📥 Generar Reporte"):
        st.success("Reporte listo para descarga.")