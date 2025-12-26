import streamlit as st
import pandas as pd
import math
import io
import requests 
from datetime import datetime
from urllib.parse import quote

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AgroDrone Ops", layout="wide")

# --- SOLUCIÓN DE VISIBILIDAD MÓVIL (CSS ALTO CONTRASTE) ---
st.markdown("""
    <style>
    /* Forzar fondo blanco y texto negro en toda la app */
    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Forzar color negro en etiquetas de inputs (Hectáreas, Mixer, etc.) */
    label p {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }

    /* Estilo para las pestañas (Tabs) visibles en móvil */
    .stTabs [data-baseweb="tab"] p {
        color: #000000 !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] {
        border-bottom-color: #002A20 !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #002A20 !important;
    }

    /* Estilo de los resultados */
    .resumen-caja {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 8px solid #002A20;
        margin-bottom: 20px;
        color: #000000 !important;
    }
    
    .ficha-box {
        border: 2px solid #002A20;
        margin-bottom: 20px;
        background-color: #ffffff;
    }
    .ficha-titulo {
        background-color: #002A20;
        color: #ffffff !important;
        padding: 10px;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VADEMÉCUM DATA (BASE DE DATOS COMPLETA REINTEGRADA) ---
csv_data = """PRINCIPIO_ACTIVO;DOSIS_MARBETE_MIN;DOSIS_MARBETE_MAX;UNIDAD_DOSIS;FAMILIA_QUIMICA;TIPO_PREPARADO;ALERTA_COMPATIBILIDAD;ORDEN_MEZCLA
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
Etoxazole;0.05;0.15;L/ha;Difenil oxazolina;Acaricida;Rotar;Final"""

vademecum_df = pd.read_csv(io.StringIO(csv_data), sep=";")
vademecum_df = vademecum_df.dropna(subset=['PRINCIPIO_ACTIVO'])
productos_lista = sorted(vademecum_df['PRINCIPIO_ACTIVO'].unique().tolist())

# --- FUNCIONES ---
def calculate_delta_t(temp, hum):
    tw = temp * math.atan(0.151977 * (hum + 8.313659)**0.5) + \
         math.atan(temp + hum) - math.atan(hum - 1.676331) + \
         0.00391838 * (hum**1.5) * math.atan(0.023101 * hum) - 4.686035
    return round(temp - tw, 2)

# --- UI PRINCIPAL ---
st.title("🚁 AgroDrone Ops")

tabs = st.tabs(["🧮 Caldo (Mixer)", "🌡️ Delta T", "📖 Vademécum", "⛽ Generador"])

# --- TAB 1: MEZCLA ENFOQUE MIXER ---
with tabs[0]:
    st.subheader("1. Configuración del Trabajo")
    c1, c2 = st.columns(2)
    with c1:
        hectareas_lote = st.number_input("Hectáreas Totales del Lote", value=20.0, step=1.0)
        tasa_aplicacion = st.number_input("Volumen de Aplicación (L/Ha)", value=10.0, step=1.0)
    with c2:
        mixer_size_opt = st.selectbox("Capacidad del Mixer (L)", ["100", "200", "300", "500", "Personalizado"])
        if mixer_size_opt == "Personalizado":
            cap_mixer = st.number_input("Litros Mixer", value=330)
        else:
            cap_mixer = int(mixer_size_opt)

    st.divider()
    st.subheader("2. Productos a Aplicar")
    
    if 'rows' not in st.session_state:
        st.session_state.rows = [{"p": productos_lista[0], "d": 0.0}]

    def add_product_row(): st.session_state.rows.append({"p": productos_lista[0], "d": 0.0})

    for i, row_data in enumerate(st.session_state.rows):
        cols = st.columns([0.6, 0.4])
        st.session_state.rows[i]["p"] = cols[0].selectbox(f"Producto {i+1}", productos_lista, key=f"sel_{i}")
        st.session_state.rows[i]["d"] = cols[1].number_input(f"Dosis/Ha", value=0.0, key=f"num_{i}")

    st.button("➕ Agregar Producto", on_click=add_product_row)

    if hectareas_lote > 0 and tasa_aplicacion > 0:
        vol_total_caldo = hectareas_lote * tasa_aplicacion
        has_por_mixer = cap_mixer / tasa_aplicacion
        total_mixers = vol_total_caldo / cap_mixer

        st.markdown(f"""
        <div class="resumen-caja">
            <h3>📊 Resumen Lote Completo</h3>
            <p>💧 <b>Volumen Total Caldo:</b> {vol_total_caldo:.1f} Litros</p>
            <p>🔄 <b>Cantidad de Mixers:</b> {math.ceil(total_mixers)} cargas</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="resumen-caja" style="border-left-color: #88D600;">
            <h3>🧪 RECETA POR MIXER ({cap_mixer}L)</h3>
            <p>📍 Cada carga cubre: <b>{has_por_mixer:.2f} Hectáreas</b></p>
        """, unsafe_allow_html=True)
        
        lista_whatsapp = []
        for r in st.session_state.rows:
            if r["d"] > 0:
                calc_mixer = r["d"] * has_por_mixer
                st.write(f"✅ **{r['p']}:** {calc_mixer:.3f} L o Kg")
                lista_whatsapp.append(f"- {r['p']}: {calc_mixer:.3f}")
        
        st.markdown("</div>", unsafe_allow_html=True)

        # WhatsApp Share
        msg = f"*ORDEN DE CARGA MIXER*\nLote: {hectareas_lote}Ha\nMixer: {cap_mixer}L\nCubre: {has_por_mixer:.2f}Ha\n---\n" + "\n".join(lista_whatsapp)
        wa_link = f"https://wa.me/?text={quote(msg)}"
        st.markdown(f'<a href="{wa_link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; padding:10px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📲 Compartir Receta por WhatsApp</button></a>', unsafe_allow_html=True)

# --- TAB 2: DELTA T ---
with tabs[1]:
    st.subheader("Condiciones de Vuelo (Delta T)")
    col_t, col_h = st.columns(2)
    t_v = col_t.number_input("Temperatura (°C)", value=25.0)
    h_v = col_h.number_input("Humedad (%)", value=60.0)
    
    dt_v = calculate_delta_t(t_v, h_v)
    st.metric("Delta T", f"{dt_v} °C")

    if 2 <= dt_v <= 8:
        st.success("✅ ÓPTIMO: Adelante con la aplicación.")
    elif dt_v < 2:
        st.warning("⚠️ PRECAUCIÓN: Riesgo de deriva.")
    else:
        st.error("❌ CRÍTICO: Evaporación excesiva.")

# --- TAB 3: VADEMÉCUM COMPLETO ---
with tabs[2]:
    st.subheader("Consulta Técnica de Productos")
    busqueda = st.text_input("Buscar por nombre del producto...")
    
    resultados = vademecum_df[vademecum_df['PRINCIPIO_ACTIVO'].str.contains(busqueda, case=False, na=False)]
    
    for _, item in resultados.iterrows():
        st.markdown(f"""
        <div class="ficha-box">
            <div class="ficha-titulo">{item['PRINCIPIO_ACTIVO']}</div>
            <div class="seccion-gris">FAMILIA Y TIPO</div>
            <div class="contenido-ficha">{item['FAMILIA_QUIMICA']} | {item['TIPO_PREPARADO']}</div>
            <div class="seccion-gris">DOSIS MARBETE</div>
            <div class="contenido-ficha">{item['DOSIS_MARBETE_MIN']} - {item['DOSIS_MARBETE_MAX']} {item['UNIDAD_DOSIS']}</div>
            <div class="seccion-gris">COMPATIBILIDAD Y ORDEN</div>
            <div class="contenido-ficha">⚠️ {item['ALERTA_COMPATIBILIDAD']}<br>📦 Orden: {item['ORDEN_MEZCLA']}</div>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 4: GENERADOR ---
with tabs[3]:
    st.subheader("Combustible para Generador")
    consumo_gen = st.number_input("Consumo Estimado (L/Ha)", value=1.0)
    st.info(f"Para trabajar las {hectareas_lote} Has, necesitas aproximadamente: **{hectareas_lote * consumo_gen:.1f} Litros** de combustible.")

st.markdown("---")
st.caption("Desarrollado por Gabriel Carrasco - AgroDrone Pro")
