import streamlit as st
import pandas as pd
import math
import io

# --- 1. PROCESAMIENTO DE DATOS DEL USUARIO (BASE DE DATOS CSV/PUNTO Y COMA) ---

# VADEMÉCUM REVISADO: Se ha reformateado para asegurar que cada campo coincida con el encabezado.
# NOTA: Los campos DOSIS_MARBETE_MIN y MAX han sido rellenados basándose en los datos originales.
csv_data = """
PRINCIPIO_ACTIVO;DOSIS_MARBETE_MIN;DOSIS_MARBETE_MAX;UNIDAD_DOSIS;FAMILIA_QUIMICA;TIPO_PREPARADO;ALERTA_COMPATIBILIDAD;ORDEN_MEZCLA
Glyphosate;0.25;1.5;L/ha;Glicina (EPSPS inhibitor);Herbicida;"Evitar pH alcalino, deriva";Medio
Paraquat (Diquat similar);0.5;2;L/ha;Bipiridilio;Herbicida;"Muy tóxico, restricciones";Temprano
Atrazine;0.5;3;kg/ha;Triazina (photosystem II inhibitor);Herbicida;"Persistente, cuidado en suelos arenosos";Temprano
Simazine;0.5;3;kg/ha;Triazina;Herbicida;Carryover;Temprano
Metolachlor;0.5;2;L/ha;Cloroacetamida;Herbicida;Requiere incorporación al suelo;Medio
S-metolachlor;0.7;1.7;L/ha;Cloroacetamida (isómero);Herbicida;Evitar mezcla con aceites;Medio
Acetochlor;1;2.5;L/ha;Cloroacetamida;Herbicida;Incorporación/actividad en pre-emergencia;Medio
Alachlor;1;3;L/ha;Cloroacetamida;Herbicida;Riesgo de deriva;Medio
Pendimethalin;0.5;2;L/ha;Dinitroanilina;Herbicida;"Fotodegradable, no mezclar con alcalinos";Temprano
Trifluralin;0.5;1.5;L/ha;Dinitroanilina;Herbicida;Incorporación al suelo (PPI);Temprano
Imazethapyr;0.05;0.2;L/ha;Imidazolinona (ALS inhibitor);Herbicida;Persistencia;Medio
Imazamox;0.05;0.1;L/ha;Imidazolinona;Herbicida;Usado en Clearfield;Medio
Metsulfuron-methyl;0.01;0.05;kg/ha;Sulfonilurea;Herbicida;"Residualidad alta, rotación de cultivos";Medio
Chlorsulfuron;0.01;0.03;kg/ha;Sulfonilurea;Herbicida;Muy residual;Medio
Nicosulfuron;0.05;0.1;L/ha;Sulfonilurea;Herbicida;Específico para gramíneas;Medio
Rimsulfuron;0.01;0.04;kg/ha;Sulfonilurea;Herbicida;Residualidad;Medio
Mesotrione;0.1;0.25;L/ha;Tricetona;Herbicida;Blanqueo temporal;Medio
Tembotrione;0.1;0.2;L/ha;Tricetona;Herbicida;Actúa mejor con coadyuvante;Medio
Isoxaflutole;0.1;0.25;L/ha;Isoxazole;Herbicida;Requiere activación por humedad;Temprano
Fluroxypyr;0.2;0.8;L/ha;Ácido piridin carboxílico;Herbicida;Volatilidad;Medio
Picloram;0.1;0.5;L/ha;Ácido piridin carboxílico;Herbicida;Alta residualidad;Medio
Clopyralid;0.1;0.4;L/ha;Ácido piridin carboxílico;Herbicida;Específico para compuestas;Medio
Triclopyr;0.5;1.5;L/ha;Ácido piridin carboxílico;Herbicida;Leñosas;Medio
2,4-D;0.5;1.5;L/ha;Ácido Fenoxiacético;Herbicida;"Deriva, Volatilidad";Medio
Dicamba;0.1;0.5;L/ha;Ácido Benzoico;Herbicida;"Deriva, Volatilidad";Medio
Bromoxynil;0.5;1.5;L/ha;Nitrilo;Herbicida;Contacto;Medio
Ioxynil;0.5;1.5;L/ha;Nitrilo;Herbicida;Contacto;Medio
Saflufenacil;0.05;0.15;kg/ha;Pirimidindiona (PPO inhibitor);Herbicida;Requiere aceite/surfactante;Final
Carfentrazone;0.05;0.1;kg/ha;Triazolinona (PPO inhibitor);Herbicida;Contacto;Final
Sulfentrazone;0.1;0.5;kg/ha;Triazolinona;Herbicida;Residualidad;Temprano
Flumioxazin;0.1;0.5;kg/ha;N-fenilftalimida;Herbicida;Pre-emergencia;Temprano
Flufenacet;0.5;1.5;L/ha;Oxietilcarboxamida;Herbicida;Pre-emergencia;Medio
Diflufenican;0.1;0.3;L/ha;Nicotinanilida;Herbicida;Residualidad;Medio
Linuron;0.5;1.5;kg/ha;Urea (PS II inhibitor);Herbicida;PS II inhibitor;Temprano
MCPA;0.5;1.5;L/ha;Ácido Fenoxiacético;Herbicida;Menor volatilidad que 2,4-D;Medio
Flumetsulam;0.05;0.15;L/ha;Triazolpirimidina (ALS inhibitor);Herbicida;Residualidad;Medio
Bromacil;0.5;1.5;kg/ha;Uracilo (PS II inhibitor);Herbicida;Uso no selectivo/control total;Temprano
Clethodim;0.3;1;L/ha;Ciclohexanodiona (ACCasa inhibitor);Herbicida;Aceite mineral obligatorio;Final
Haloxyfop;0.1;0.3;L/ha;Ariloxifenoxipropionato (ACCasa inhibitor);Herbicida;Selectivo gramíneas;Final
Quizalofop;0.1;0.3;L/ha;Ariloxifenoxipropionato;Herbicida;Selectivo gramíneas;Final
Pinoxaden;0.5;1;L/ha;Fenilpirazolina (ACCasa inhibitor);Herbicida;Específico para cereales;Final
Indaziflam;0.05;0.15;kg/ha;Alquil azolil;Herbicida;Nueva molécula;Temprano
Isoxaben;0.5;1.5;kg/ha;Benzamida;Herbicida;Pre-emergencia;Temprano
Bixlozone;0.5;1.5;L/ha;Isoxazolidinona;Herbicida;Pre-emergencia;Medio
Chlorpyrifos;0.5;1.5;L/ha;Organofosforado (AChE inhibitor);Insecticida;"Alta toxicidad, restricciones";Medio
Malathion;1;2;L/ha;Organofosforado;Insecticida;"Tóxico, cuidado en mezclas";Medio
Diazinon;0.5;1.5;L/ha;Organofosforado;Insecticida;Residuos;Medio
Acephate;0.5;1;kg/ha;Organofosforado;Insecticida;Toxicidad a mamíferos;Medio
Methamidophos;0.5;1;L/ha;Organofosforado;Insecticida;"Muy tóxico, muchos países lo prohíben";Medio
Carbaryl;0.5;1.5;kg/ha;Carbamato (AChE inhibitor);Insecticida;Toxicidad media;Medio
Methomyl;0.2;0.5;L/ha;Carbamato;Insecticida;Tóxico;Medio
Pyrethrins;0.1;0.5;L/ha;Piretroide natural (Na channel modulator);Insecticida;Rápida descomposición;Final
Permethrin;0.1;0.3;L/ha;Piretroide (Na channel modulator);Insecticida;"Tóxico para abejas y peces";Final
Cypermethrin;0.1;0.3;L/ha;Piretroide;Insecticida;Tóxico acuático;Final
Deltamethrin;0.05;0.15;L/ha;Piretroide;Insecticida;Muy tóxico para abejas;Final
Lambda-cyhalothrin;0.05;0.1;L/ha;Piretroide;Insecticida;No aplicar en floración;Final
Bifenthrin;0.1;0.3;L/ha;Piretroide;Insecticida;Persistente en suelos;Final
Abamectin;0.05;0.1;L/ha;Avermectina (Cl channel activator);Acaricida;Riesgo para polinizadores;Medio
Spinosad;0.1;0.3;L/ha;Spinosin (nAChR modulator);Insecticida;Cuidado en polinizadores;Medio
Emamectin benzoate;0.05;0.1;kg/ha;Avermectina;Insecticida;Cuidado en polinizadores;Medio
Chlorantraniliprole;0.05;0.15;L/ha;Diamida (Ryanodine R. modulator);Insecticida;Menor riesgo relativo;Medio
Flubendiamide;0.1;0.3;kg/ha;Diamida;Insecticida;Baja toxicidad mamíferos;Medio
Bacillus thuringiensis;0.5;1.5;kg/ha;Microbiano (Gut disruptor);Insecticida;Eficaz por ingestión;Medio
Azadirachtin;0.5;2;L/ha;Neem oil (various);Insecticida;Restringido en algunos países;Medio
Beauveria bassiana;1;3;L/ha;Hongo;Insecticida;"Biopesticida, cuidar mezcla con insecticidas de contacto";Medio
Metarhizium anisopliae;1;3;L/ha;Hongo;Insecticida;Tóxico para abejas por contacto;Medio
Indoxacarb;0.05;0.15;L/ha;Oxadiazina (Na channel blocker);Insecticida;Eficaz en lepidópteros;Medio
Lufenuron;0.1;0.3;L/ha;Benzoylurea (Chitin synthesis inhibitor);Insecticida;Eficaz ingestión;Medio
Teflubenzuron;0.1;0.3;L/ha;Benzoylurea;Insecticida;Selectivo para Lepidoptera;Medio
Novamuron;0.1;0.3;L/ha;Benzoylurea;Insecticida;Control larval;Medio
Buprofezin;0.5;1.5;L/ha;Tiacina (Chitin synthesis inhibitor);Insecticida;Incompatibilidades cajas;Medio
Spirotetramat;0.1;0.3;L/ha;Tetramic acid (Lipid Biosynthesis Inhibitor);Insecticida;Eficaz en homópteros;Medio
Spiromesifen;0.2;0.5;L/ha;Tetramic acid;Acaricida;Acaricida;Final
Imidacloprid;0.05;0.15;L/ha;Neonicotinoide (nAChR agonist);Insecticida;"No mezclar con alcalinos, amplio espectro";Medio
Thiamethoxam;0.05;0.15;kg/ha;Neonicotinoide;Insecticida;Evitar mezclas con aceites;Medio
Acetamiprid;0.05;0.15;kg/ha;Neonicotinoide;Insecticida;No mezclar con azufre;Medio
Sulfoxaflor;0.05;0.15;L/ha;Sulfoximina (nAChR agonist);Insecticida;Fitotoxicidad en algunas especies;Medio
Pyriproxyfen;0.05;0.15;L/ha;Juvenile Hormone Mimic;Insecticida;Rotar por resistencia;Final
Fenbutatin oxide;0.5;1.5;kg/ha;Organotina;Acaricida;"Oomycete control, resistencia";Medio
Propargite;0.5;1.5;L/ha;Sulfito;Acaricida;Alto riesgo de resistencia;Medio
Cyflumetofen;0.1;0.3;L/ha;Amidoxime;Acaricida;Rotar modos de acción;Final
Captan;0.5;1.5;kg/ha;Ftalimida (multi-site);Fungicida;No mezclar con productos alcalinos;Temprano
Thiram;1;3;kg/ha;Dithiocarbamate;Fungicida;Fitotoxicidad si se sobredosifica;Temprano
Iprodione;0.5;1.5;L/ha;Dicarboximide;Fungicida;Resistencia en algunos patógenos;Medio
Fludioxonil;0.1;0.5;L/ha;Phenylpyrrole;Fungicida;Usado en semillas y postcosecha;Medio
Fenhexamid;0;0;dosis segun etiqueta;Hydroxyanilide;Fungicida;Eficaz en botrytis;Medio
Boscalid;0.2;0.6;L/ha;SDHI (succinate dehydrogenase inhibitors);Fungicida;Rotar para evitar resistencia;Medio
Fluxapyroxad;0;0;dosis segun etiqueta;SDHI;Fungicida;Usado en mezcla con triazoles;Medio
Pyrimethanil;0;0;dosis segun etiqueta;Anilinopyrimidine;Fungicida;Usado en frutas;Medio
Cyprodinil;0;0;dosis segun etiqueta;Anilinopyrimidine;Fungicida;Combinaciones comerciales;Medio
Mandipropamid;0;0;dosis segun etiqueta;Carboxamide (oomycete active);Fungicida;Control de oomicetos;Medio
Zoxamide;0;0;dosis segun etiqueta;Benzamida;Fungicida;Oomycete control;Medio
Fluopicolide;0.1;0.3;L/ha;Benzamida (oomycete active);Fungicida;Común en hortalizas;Medio
Cymoxanil;0.2;0.6;kg/ha;Cianoacetamida oxima;Fungicida;Control curativo;Medio
Propamocarb;1;3;L/ha;Carbamato (oomycete active);Fungicida;Muy selectivo;Medio
Fosetyl-Al;1;3;kg/ha;Fosfonato;Fungicida;Control de Phytophthora;Medio
Mancozeb;1;3;kg/ha;Dithiocarbamate (multi-site);Fungicida;"Contacto, protección foliar";Temprano
Chlorothalonil;1;2.5;L/ha;Cloronitrilo (multi-site);Fungicida;"Amplio espectro, contacto";Temprano
Folpet;1;2.5;kg/ha;Ftalimida (multi-site);Fungicida;Contacto;Temprano
Azoxystrobin;0.1;0.3;L/ha;Estrobilurina (QoI inhibitor);Fungicida;Rotar por resistencia;Medio
Pyraclostrobin;0.1;0.3;L/ha;Estrobilurina;Fungicida;Efecto fisiológico (AgCelence);Medio
Trifloxystrobin;0.05;0.15;L/ha;Estrobilurina;Fungicida;Rotar;Medio
Difenoconazole;0.1;0.3;L/ha;Triazol (DMI inhibitor);Fungicida;Control curativo y preventivo;Medio
Tebuconazole;0.1;0.3;L/ha;Triazol;Fungicida;Amplio uso en cereales;Medio
Cyproconazole;0.05;0.15;L/ha;Triazol;Fungicida;Rotar;Medio
Propiconazole;0.1;0.3;L/ha;Triazol;Fungicida;Común en cereales;Medio
Metconazole;0.05;0.15;L/ha;Triazol;Fungicida;Rotar;Medio
Prochloraz;0.5;1.5;L/ha;Imidazol;Fungicida;Rotar por resistencia;Medio
Fenpropimorph;0.5;1.5;L/ha;Morfolina (SBI);Fungicida;Rotar;Medio
Spinetoram;0.05;0.15;L/ha;Spinosin;Insecticida;Rotar;Medio
Flonicamid;0.05;0.15;kg/ha;Piridinacarboxamida;Insecticida;Tóxico para peces;Medio
Pymetrozine;0.1;0.3;kg/ha;Piridinacarboxamida;Insecticida;Eficaz en pulgones;Medio
Biflubenamide;0.1;0.3;L/ha;Benzamida;Acaricida;Rotar;Final
Diafenthiuron;0.5;1.5;kg/ha;Tiouracil;Acaricida;Requiere alta temperatura;Medio
Spirodiclofen;0.2;0.5;L/ha;Tetramic acid;Acaricida;Rotar;Final
Etoxazole;0.05;0.15;L/ha;Difenil oxazolina;Acaricida;Rotar;Final
"""

# Inicialización por defecto en caso de que no haya datos
vademecum = {}
productos_disponibles = []

try:
    # Leer el DataFrame con el separador punto y coma (;)
    df = pd.read_csv(io.StringIO(csv_data), sep=";")
    # Eliminar filas donde no hay Principio Activo
    df = df.dropna(subset=['PRINCIPIO_ACTIVO']) 
    
    if not df.empty:
        # Convertir a diccionario de diccionarios, usando 'PRINCIPIO_ACTIVO' como clave
        vademecum = df.set_index('PRINCIPIO_ACTIVO').T.to_dict('dict')
        productos_disponibles = sorted(list(vademecum.keys()))
    
except pd.errors.ParserError as e:
    st.error(f"Error en el Vademécum (ParserError): {e}. Asegúrate de que **todos los datos** en la variable 'csv_data' estén separados por punto y coma (`;`).")
    
# --- MOCK DATA PARA PRONÓSTICO (Debe ser reemplazado por una API real) ---
weather_data = {
    "Día": ["Hoy", "Vie", "Sáb", "Dom", "Lun", "Mar", "Mié"],
    "Ícono": ["☀️", "🌤️", "☁️", "🌧️", "☀️", "🌤️", "☁️"],
    "T_Max": [28, 26, 25, 22, 29, 27, 26], # Temperaturas
    "T_Min": [18, 17, 16, 15, 19, 18, 17],
    "Viento_kmh": [15, 25, 10, 30, 12, 18, 14], # Vientos
    "KP": [2, 3, 1, 4, 2, 3, 2], # Índice KP
    "Lluvia_%": [0, 10, 20, 80, 0, 5, 10], # Probabilidad de lluvia
    "Humedad_%": [55, 60, 65, 85, 50, 55, 60], # Humedad Relativa
    "Nubes_%": [10, 30, 70, 90, 15, 40, 60], # Nubosidad
}
df_weather = pd.DataFrame(weather_data)


# --- CONFIGURACIÓN INICIAL DE STREAMLIT ---
st.set_page_config(page_title="AgroDrone Ops", page_icon="🚁", layout="centered")

st.markdown("""
    <style>
    .warning { color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 5px; }
    .success { color: #155724; background-color: #d4edda; padding: 10px; border-radius: 5px; }
    .kp-ok { background-color: #28a745; color: white; padding: 5px; border-radius: 3px; font-weight: bold; }
    .kp-cuidado { background-color: #ffc107; color: black; padding: 5px; border-radius: 3px; font-weight: bold; }
    .kp-peligro { background-color: #dc3545; color: white; padding: 5px; border-radius: 3px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚁 AgroDrone Ops")
st.write("Calculadora de Caldo y Vademécum Fitosanitario")

# Inicializar estado para productos
if 'num_productos' not in st.session_state:
    st.session_state.num_productos = 1

# --- TABS DE NAVEGACIÓN ---
tab1, tab2, tab3, tab4 = st.tabs(["🧮 Calculadora Caldo", "⛽ Grupo Electrógeno", "📖 Vademécum", "☀️ Tiempo de Vuelo"])

# Función para agregar productos (solución al error de recarga)
def add_product():
    """Función que se llama al presionar el botón para agregar producto."""
    if st.session_state.num_productos < 5:
        st.session_state.num_productos += 1

# --- TAB 1: CALCULADORA MIXER ---
with tab1:
    st.header("Armado del Caldo (Mixer)")
    
    col1, col2 = st.columns(2)
    with col1:
        tanque_opcion = st.selectbox("Tamaño del Mixer [Litros]", 
                                     ["100", "200", "300", "500", "Personalizado"])
        if tanque_opcion == "Personalizado":
            capacidad_mixer = st.number_input("Ingresar volumen personalizado (L)", value=330, step=10)
        else:
            capacidad_mixer = int(tanque_opcion)

    with col2:
        tasa_aplicacion = st.number_input("Tasa Dron (Líquido/ha)", value=10.0, step=0.5, format="%.1f")

    st.divider()
    
    # Datos del Lote
    st.subheader("Datos del Lote")
    hectareas_totales = st.number_input("Hectáreas Totales del Lote", value=20.0, step=1.0)
    
    # --- PRODUCTOS DINÁMICOS ---
    st.subheader("Productos a Aplicar (Dosis por Hectárea)")
    productos_seleccionados = []
    
    for i in range(st.session_state.num_productos):
        st.markdown(f"**Producto #{i+1}**")
        cols = st.columns([0.4, 0.3, 0.3])
        
        opciones_productos = ["Otro / Personalizado"] + productos_disponibles
        
        # Selección del producto
        if not productos_disponibles:
             producto_seleccion = cols[0].selectbox("Principio Activo", options=["Otro / Personalizado"], key=f'prod_select_{i}')
        else:
             producto_seleccion = cols[0].selectbox("Principio Activo", options=opciones_productos, key=f'prod_select_{i}')
        
        producto_nombre = producto_seleccion
        
        # Manejo del nombre si es "Otro / Personalizado" o si el vademécum está vacío
        if producto_seleccion == "Otro / Personalizado" or not productos_disponibles: 
            # Si el Vademécum está vacío, forzamos al usuario a ingresar un nombre
            default_value = "" if not productos_disponibles else "" 
            producto_nombre = cols[0].text_input("Escribir nombre:", value=default_value, key=f'prod_input_{i}')
            if not producto_nombre:
                continue 

        unidad = cols[1].selectbox("Unidad Dosis", options=["Litros/ha", "Kg/ha"], key=f'unit_{i}')
        dosis = cols[2].number_input("Dosis", value=0.0, step=0.1, key=f'dose_{i}')
        
        if producto_nombre and dosis > 0:
            productos_seleccionados.append({
                'nombre': producto_nombre,
                'unidad': unidad,
                'dosis_ha': dosis
            })
    
    # --- BOTÓN PARA AGREGAR PRODUCTOS (Con la función corregida) ---
    if st.session_state.num_productos < 5: 
        st.button("➕ Agregar Producto", on_click=add_product) 

            
    # --- CÁLCULOS Y RESULTADOS ---
    volumen_total_caldo = hectareas_totales * tasa_aplicacion
    
    st.markdown("---")
    st.markdown(f"### 📊 Resultados Lote Completo ({hectareas_totales} ha)")
    st.info(f"**Volumen Total de Caldo Necesario:** {volumen_total_caldo:.1f} Litros")
    
    resumen_impresion = f"--- PLANIFICACIÓN DE APLICACIÓN ---\n"
    resumen_impresion += f"Lote: {hectareas_totales} ha\n"
    resumen_impresion += f"Tasa de aplicación: {tasa_aplicacion} L/ha\n"
    resumen_impresion += f"Capacidad del Mixer: {capacidad_mixer} L\n"
    resumen_impresion += f"Volumen Total de Caldo: {volumen_total_caldo:.1f} L\n\n"
    resumen_impresion += "--- INSUMOS TOTALES ---\n"
    
    # 2. Resultados por Producto
    for producto in productos_seleccionados:
        nombre = producto['nombre']
        dosis_ha = producto['dosis_ha']
        unidad = producto['unidad'].split('/')[0] 
        
        producto_total_necesario = hectareas_totales * dosis_ha
        
        st.success(f"**Total de {nombre} a utilizar:** {producto_total_necesario:.2f} {unidad}") 
        resumen_impresion += f"- {nombre}: {producto_total_necesario:.2f} {unidad}\n"
        
        dosis_por_mixer_completo = (capacidad_mixer / tasa_aplicacion) * dosis_ha
        cargas_completas = math.floor(volumen_total_caldo / capacidad_mixer)
        remanente_volumen = volumen_total_caldo % capacidad_mixer

        st.markdown(f"##### Dosis de {nombre} en el Mixer:")
        if cargas_completas > 0:
            st.write(f"- En cada una de las **{cargas_completas}** cargas completas: **{dosis_por_mixer_completo:.2f} {unidad}**")
        
        if remanente_volumen > 0:
            dosis_remanente = (remanente_volumen / tasa_aplicacion) * dosis_ha
            st.write(f"- En la carga final de **{remanente_volumen:.1f} Litros**: **{dosis_remanente:.2f} {unidad}**")
            
    # --- BOTÓN DE IMPRESIÓN ---
    st.markdown("---")
    st.download_button(
        label="🖨️ Imprimir Resumen de Aplicación (TXT)",
        data=resumen_impresion,
        file_name=f'Planificacion_Lote_{hectareas_totales}ha.txt',
        mime='text/plain'
    )

# --- TAB 2: GRUPO ELECTRÓGENO ---
with tab2:
    st.header("⛽ Cálculo de Combustible para Grupo Electrógeno")
    consumo_gen = st.number_input("Consumo Grupo Electrógeno (Litros/ha de aplicación)", value=1.0, step=0.1) 
    total_nafta = hectareas_totales * consumo_gen
    
    st.success(f"**Combustible Necesario:** {total_nafta:.1f} Litros de Nafta/Gasolina para el generador.")
    
    st.markdown("---")
    st.subheader("Orden de Mezcla Sugerido (General)")
    
    st.markdown("""
    El orden de mezcla es crítico para evitar el corte del caldo.
    
    1. **Agua y Corrección (WA/Water Conditioning)**
    2. **Sólidos Secos (WG/SG/WP)**
    3. **Suspensiones Acuosas (SC/CS)**
    4. **Emulsiones (EC/EW/OD)**
    5. **Líquidos Solubles (SL)**
    6. **Coadyuvantes / Surfactantes / Aceites**
    7. **Completar con el resto de agua**
    """)

# --- TAB 3: VADEMECUM ---
with tab3:
    st.header("🔍 Vademécum Fitosanitario")
    
    if vademecum:
        st.info("⚠️ **IMPORTANTE:** El Vademécum se cargó correctamente. Verifica el campo 'Alerta de Compatibilidad' antes de mezclar.")
        opciones_busqueda = [""] + productos_disponibles
        busqueda = st.selectbox("Buscar Principio Activo o Producto", opciones_busqueda)
        
        if busqueda in vademecum:
            data = vademecum[busqueda]
            st.markdown(f"### {busqueda}")
            
            # NOTA: Manejo de dosis que puedan ser 'dosis segun etiqueta' (ej: 0 en min/max)
            dosis_min = data['DOSIS_MARBETE_MIN']
            dosis_max = data['DOSIS_MARBETE_MAX']
            unidad_dosis = data['UNIDAD_DOSIS']
            
            # Formateo condicional de la dosis
            if isinstance(dosis_min, (int, float)) and isinstance(dosis_max, (int, float)) and dosis_min == 0 and dosis_max == 0:
                dosis_str = unidad_dosis # Muestra 'dosis segun etiqueta' si es el caso
            else:
                dosis_str = f"{dosis_min} - {dosis_max} {unidad_dosis}"

            ficha_tecnica = {
                "Dosis Marbete (Mín - Máx)": dosis_str,
                "Familia Química": data['FAMILIA_QUIMICA'],
                "Tipo Preparado": data['TIPO_PREPARADO'],
                "Orden Sugerido": data['ORDEN_MEZCLA'],
                "Alerta de Compatibilidad": data['ALERTA_COMPATIBILIDAD']
            }
            
            df_ficha = pd.DataFrame([ficha_tecnica]).T.rename(columns={0: "Detalle"})
            st.table(df_ficha)
            
            st.markdown(f'<div class="warning">**🚨 Alerta de Mezcla:** {data["ALERTA_COMPATIBILIDAD"]}</div>', unsafe_allow_html=True)
        else:
            st.info("Selecciona un principio activo de la lista para ver su ficha técnica, dosis de marbete y alertas de mezcla.")
    else:
        st.warning("⚠️ **Vademécum no cargado/vacío.**")
        st.markdown("Si la aplicación no arranca o sigue dando errores, el problema está en la **estructura de datos** de la variable `csv_data`.")


# --- TAB 4: TIEMPO DE VUELO ---
with tab4:
    st.header("☀️ Pronóstico de Condiciones para Vuelo")
    st.caption("Los datos mostrados son **simulados (Mock Data)**. Para tener datos en tiempo real se requiere integración con APIs meteorológicas.")
    
    # --- PROMPT VUELO KP ---
    st.markdown("### 🛰️ Índice Geomagnético KP")
    kp_actual = df_weather.iloc[0]['KP']
    if kp_actual <= 3:
        kp_html = f'<div class="kp-ok">Índice KP actual: {kp_actual} (Óptimo para GPS)</div>'
    elif kp_actual <= 5:
        kp_html = f'<div class="kp-cuidado">Índice KP actual: {kp_actual} (Precaución - Puede haber interrupciones leves de GPS)</div>'
    else:
        kp_html = f'<div class="kp-peligro">Índice KP actual: {kp_actual} (PELIGRO - Riesgo de pérdida de GPS. Evitar vuelos)</div>'

    st.markdown(kp_html, unsafe_allow_html=True)
    st.write("El Índice KP mide la actividad geomagnética que afecta la precisión del GPS. Se recomienda volar con KP ≤ 4.")
    
    st.divider()
    
    # --- PRONÓSTICO 7 DÍAS (Barra abajo) ---
    st.markdown("### Pronóstico Extendido (7 días)")
    cols = st.columns(len(df_weather))
    
    for i, row in df_weather.iterrows():
        with cols[i]:
            st.markdown(f"**{row['Día']}**")
            st.markdown(f"## {row['Ícono']}")
            st.markdown(f"**{row['T_Max']}°** / {row['T_Min']}°")
            
            # Icono de viento
            wind_icon = "💨" if row['Viento_kmh'] > 20 else "🌬️"
            st.markdown(f"{wind_icon} {row['Viento_kmh']} km/h")
            
            # Icono de lluvia
            if row['Lluvia_%'] >= 50:
                rain_icon = "☔"
            elif row['Lluvia_%'] > 0:
                rain_icon = "🌦️"
            else:
                rain_icon = "🚫"
            st.markdown(f"{rain_icon} {row['Lluvia_%']}%")
            
            # Colorear según condición de vuelo (ejemplo simple)
            if row['Viento_kmh'] > 25 or row['Lluvia_%'] >= 50:
                 st.error("NO apto")
            elif row['Viento_kmh'] > 15:
                st.warning("Precaución")
            else:
                st.success("Apto")
            
    st.divider()

    # --- DETALLE POR DÍA (usando el día actual para ejemplo) ---
    st.markdown("### 📋 Detalles del Día Actual")
    current_data = df_weather.iloc[0]
    
    dcols = st.columns(4)
    dcols[0].metric("Temperatura Máx", f"{current_data['T_Max']} °C")
    dcols[1].metric("Humedad Relativa", f"{current_data['Humedad_%']} %")
    dcols[2].metric("Viento", f"{current_data['Viento_kmh']} km/h", "Ideal para Vuelo")
    dcols[3].metric("Nubosidad", f"{current_data['Nubes_%']} %")
    
    st.markdown("---")
    st.metric("Probabilidad de Lluvia", f"{current_data['Lluvia_%']} %")