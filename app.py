import streamlit as st
import pandas as pd
import math
import io
import requests 
from datetime import datetime

# --- CONFIGURACIÓN DE CLIMA y APIs ---
LATITUDE = -35.4485
LONGITUDE = -60.8876
OPENWEATHERMAP_API_KEY = "e07ff67318e1b5f6f5bde3dae5b35ec0" 

@st.cache_data(ttl=300)
def get_weather_data(lat, lon):
    if not OPENWEATHERMAP_API_KEY:
        return None
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=es"
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        temp_c = data['main']['temp'] 
        humidity_pc = data['main']['humidity'] 
        wind_kmh = data['wind']['speed'] * 3.6 
        weather_desc = data['weather'][0]['description'].capitalize()
        cloudiness_pc = data['clouds']['all'] 
        rain_prob = 70 if 'lluvia' in weather_desc.lower() or cloudiness_pc > 80 else (30 if cloudiness_pc > 50 else 0)
        return {
            "T_Actual": f"{temp_c:.1f} °C", "Humedad_Val": humidity_pc, "Humedad_Str": f"{humidity_pc} %",
            "Viento_Val": wind_kmh, "Viento_Str": f"{wind_kmh:.1f} km/h", "Descripcion": weather_desc,
            "Nubosidad_Str": f"{cloudiness_pc} %", "Lluvia_Str": f"{rain_prob} %", "Ciudad": data['name']
        }
    except: return None

# --- VADEMÉCUM DATA (TU BLOQUE ORIGINAL COMPLETO) ---
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

vademecum = {}
productos_disponibles = []
try:
    df = pd.read_csv(io.StringIO(csv_data), sep=";")
    df = df.dropna(subset=['PRINCIPIO_ACTIVO']) 
    vademecum = df.set_index('PRINCIPIO_ACTIVO').T.to_dict('dict')
    productos_disponibles = sorted(list(vademecum.keys()))
except: pass

st.set_page_config(page_title="AgroDrone Ops", page_icon="favicon.png", layout="centered")

# CARGAR CSS EXTERNO
try:
    with open("style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except: pass

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚁 AgroDrone Ops")
st.write("Calculadora de Caldo y Vademécum Fitosanitario")

if 'num_productos' not in st.session_state: st.session_state.num_productos = 1
def add_product(): 
    if st.session_state.num_productos < 5: st.session_state.num_productos += 1

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧮 Calculadora Caldo", "⛽ Grupo Electrógeno", "📖 Vademécum", "☀️ Tiempo de Vuelo", "👤 Sobre la App"])

with tab1:
    st.header("Armado del Caldo (Mixer)")
    c1, c2 = st.columns(2)
    with c1: t_op = st.selectbox("Mixer [L]", ["100", "200", "300", "500", "Personalizado"])
    cap_mixer = int(t_op) if t_op != "Personalizado" else st.number_input("L", value=330)
    with c2: tasa_ap = st.number_input("Tasa Dron (L/ha)", value=10.0)
    
    ha_totales = st.number_input("Hectáreas Totales", value=20.0)
    st.subheader("Productos")
    prods_sel = []
    for i in range(st.session_state.num_productos):
        cols = st.columns([0.4, 0.3, 0.3])
        p_sel = cols[0].selectbox("Producto", ["Otro / Personalizado"] + productos_disponibles, key=f'p{i}')
        p_nom = p_sel if p_sel != "Otro / Personalizado" else cols[0].text_input("Nombre", key=f'pi{i}')
        uni = cols[1].selectbox("Unidad", ["L/ha", "kg/ha"], key=f'u{i}')
        ds = cols[2].number_input("Dosis", value=0.0, key=f'd{i}')
        if p_nom and ds > 0: prods_sel.append({'n': p_nom, 'u': uni, 'd': ds})
    
    if st.session_state.num_productos < 5: st.button("➕ Agregar Producto", on_click=add_product)

    if prods_sel:
        st.markdown('<div class="ficha-box"><div class="ficha-titulo">REPORTE DE OPERACIÓN</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="seccion-gris">LOTE: {ha_totales} HA | VOLUMEN TOTAL: {ha_totales*tasa_ap:.1f} L</div>', unsafe_allow_html=True)
        
        for p in prods_sel:
            total_p = ha_totales * p['d']
            unidad_limpia = p['u'].split('/')[0]
            st.markdown(f"""
            <div class="contenido-blanco">
                <b>INSUMO: {p['n'].upper()}</b><br>
                Total para el Lote: {total_p:.2f} {unidad_limpia}<br>
                Dosis por Carga Mixer ({cap_mixer}L): {(cap_mixer/tasa_ap)*p['d']:.2f} {unidad_limpia}
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.header("⛽ Combustible")
    cons = st.number_input("Consumo Gen (L/ha)", value=1.0)
    st.success(f"Combustible Total: {ha_totales*cons:.1f} L")

with tab3:
    st.header("🔍 Consulta Vademécum")
    busqueda = st.selectbox("Seleccionar Principio Activo", [""] + productos_disponibles)
    if busqueda:
        d = vademecum[busqueda]
        st.markdown(f"""
        <div class="ficha-box">
            <div class="ficha-titulo">FICHA TÉCNICA: {busqueda.upper()}</div>
            <div class="seccion-gris">CARACTERÍSTICAS GENERALES</div>
            <div class="contenido-blanco">
                <b>Tipo de Producto:</b> {d['TIPO_PREPARADO']}<br>
                <b>Familia Química:</b> {d['FAMILIA_QUIMICA']}
            </div>
            <div class="seccion-gris">DOSIFICACIÓN Y MEZCLA</div>
            <div class="contenido-blanco">
                <b>Dosis de Marbete:</b> {d['DOSIS_MARBETE_MIN']} - {d['DOSIS_MARBETE_MAX']} {d['UNIDAD_DOSIS']}<br>
                <b>Orden Sugerido en Mezcla:</b> {d['ORDEN_MEZCLA']}
            </div>
            <div class="seccion-gris" style="background-color: #fce8e8; color: #b71c1c;">ALERTAS Y COMPATIBILIDAD</div>
            <div class="contenido-blanco" style="color: #b71c1c; font-weight: bold;">
                {d['ALERTA_COMPATIBILIDAD']}
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.header("☀️ Condiciones de Vuelo")
    weather = get_weather_data(LATITUDE, LONGITUDE)
    if weather:
        st.metric("Viento", weather['Viento_Str'])
        st.metric("Humedad", weather['Humedad_Str'])
        if weather['Viento_Val'] > 20: st.error("¡ALERTA! Viento excesivo.")
        else: st.success("Condiciones aptas para volar.")

with tab5:
    st.header("👤 Sobre la App")
    st.write("Desarrollado por Gabriel Carrasco.")
    st.markdown(f'<a href="https://www.buymeacoffee.com/gabrielcarc" target="_blank"><button style="background-color: #FF813F; color: white; width: 100%; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">Apoyar con un Café</button></a>', unsafe_allow_html=True)