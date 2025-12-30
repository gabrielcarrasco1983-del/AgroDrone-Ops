import streamlit as st
import pandas as pd
import math
import io
from datetime import datetime
from urllib.parse import quote

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AGRODRONE DOSIS", layout="wide")

# --- CSS DE ALTO CONTRASTE (OPTIMIZADO PARA CAMPO) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    label p, .stMarkdown p, .stTextInput label p, .stNumberInput label p, .stSelectbox label p {
        color: #000000 !important; font-weight: 800 !important; font-size: 1.1rem !important;
    }
    .resumen-caja {
        background-color: #f1f3f5; padding: 20px; border-radius: 10px;
        border-left: 10px solid #002A20; margin-bottom: 20px; color: #000000 !important;
    }
    .total-lote-caja {
        background-color: #e7f3ff; padding: 20px; border-radius: 10px;
        border-top: 5px solid #0056b3; color: #000000 !important;
    }
    .alltec-ficha { border: 2px solid #002A20; margin-bottom: 15px; border-radius: 5px; overflow: hidden; }
    .alltec-header { background-color: #002A20; color: white !important; padding: 8px; font-weight: bold; text-align: center; }
    .alltec-body { padding: 12px; color: black; font-size: 0.9rem; }
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
Cyflumetofen;0.1;0.3;L/ha;Amidoxime;Acaricida;Rotar por resistencia;Final
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

def calculate_delta_t(temp, hum):
    tw = temp * math.atan(0.151977 * (hum + 8.313659)**0.5) + \
         math.atan(temp + hum) - math.atan(hum - 1.676331) + \
         0.00391838 * (hum**1.5) * math.atan(0.023101 * hum) - 4.686035
    return round(temp - tw, 2)

st.title("AGRODRONE DOSIS")

tabs = st.tabs(["🧮 Calculadora", "🌡️ Delta T", "🌦️ Clima", "📖 Vademécum", "👥 Sobre el Autor"])

# --- TAB 1: CALCULADORA ---
with tabs[0]:
    st.subheader("Configuración del Lote")
    nombre_lote = st.text_input("Nombre del Lote", value="Lote Sin Nombre")
    c1, c2, c3 = st.columns(3)
    with c1:
        has_lote = st.number_input("Hectáreas Totales", value=10.0, step=1.0)
    with c2:
        m_opt = st.selectbox("Capacidad Mixer (L)", ["100", "200", "300", "500", "Manual"])
        c_mixer = st.number_input("Litros Reales", value=330) if m_opt == "Manual" else int(m_opt)
    with c3:
        tasa = st.number_input("Caudal Dron (L/Ha)", value=10.0, step=1.0)

    st.divider()
    st.subheader("Productos (Carga Manual)")
    
    if 'filas' not in st.session_state:
        st.session_state.filas = [{"p": "", "d": 0.0, "u": "L"}]

    for i, fila in enumerate(st.session_state.filas):
        col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
        # Campo de producto LIBRE
        st.session_state.filas[i]["p"] = col1.text_input(f"Producto {i+1}", value=fila["p"], key=f"p_{i}", placeholder="Escriba el producto")
        st.session_state.filas[i]["d"] = col2.number_input(f"Dosis/Ha", value=fila["d"], key=f"d_{i}", format="%.3f")
        st.session_state.filas[i]["u"] = col3.selectbox("Unidad", ["L", "Kg"], key=f"u_{i}")

    if st.button("➕ Añadir Producto"):
        st.session_state.filas.append({"p": "", "d": 0.0, "u": "L"})
        st.rerun()

    if has_lote > 0 and tasa > 0:
        has_vuelo = c_mixer / tasa
        mixers_n = math.ceil((has_lote * tasa) / c_mixer)

        st.markdown(f"<div class='resumen-caja'><h3>🧪 MEZCLA POR MIXER ({c_mixer}L)</h3><p>Cubre: <b>{has_vuelo:.2f} Ha</b></p>", unsafe_allow_html=True)
        
        wa_mixer, wa_total, excel_data = [], [], []
        for f in st.session_state.filas:
            if f["d"] > 0:
                p_n = f["p"] if f["p"] else f"Prod {st.session_state.filas.index(f)+1}"
                c_m = f["d"] * has_vuelo
                c_t = f["d"] * has_lote
                st.write(f"✅ **{p_n}:** {c_m:.3f} {f['u']}")
                wa_mixer.append(f"- {p_n}: {c_m:.3f} {f['u']}")
                wa_total.append(f"- {p_n}: {c_t:.2f} {f['u']}")
                excel_data.append({"Lote": nombre_lote, "Producto": p_n, "Dosis/Ha": f["d"], "Unidad": f["u"], "Total Lote": c_t})

        st.markdown("</div><div class='total-lote-caja'>", unsafe_allow_html=True)
        st.subheader(f"📊 REPORTE TOTAL: {nombre_lote}")
        st.write(f"Preparaciones de Mixer: **{mixers_n}**")
        for t in wa_total: st.write(t)
        st.markdown("</div>", unsafe_allow_html=True)

        # WHATSAPP MEJORADO
        msg = (f"*AGRODRONE DOSIS*\n"
               f"*Lote:* {nombre_lote}\n"
               f"Mixer: {c_mixer}L | Cubre: {has_vuelo:.2f}Ha\n"
               f"--- POR MIXER ---\n" + "\n".join(wa_mixer) + 
               f"\n--- TOTAL LOTE ({has_lote}Ha) ---\n" + "\n".join(wa_total))
        
        st.markdown(f'<a href="https://wa.me/?text={quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; padding:15px; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">📲 ENVIAR ORDEN COMPLETA</button></a>', unsafe_allow_html=True)

        # LOG EXCEL
        df_export = pd.DataFrame(excel_data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Reporte')
        st.download_button(label="📥 DESCARGAR LOG (EXCEL)", data=output.getvalue(), file_name=f"Reporte_{nombre_lote}.xlsx", mime="application/vnd.ms-excel")

# --- TAB 2: DELTA T ---
with tabs[1]:
    st.subheader("Análisis Ambiental")
    t, h = st.number_input("Temp °C", 25.0), st.number_input("Hum %", 60.0)
    dt = calculate_delta_t(t, h)
    st.metric("Delta T", f"{dt} °C")
    
    

    if 2 <= dt <= 8: st.success("✅ **ÓPTIMO:** Condiciones ideales.")
    elif dt < 2: st.warning("⚠️ **DERIVA:** Riesgo de deriva por inversión.")
    else: st.error("❌ **CRÍTICO:** Evaporación alta. Usar antievaporantes.")

# --- TAB 3: CLIMA ---
with tabs[2]:
    st.markdown('<a href="https://www.swpc.noaa.gov/products/planetary-k-index" target="_blank" style="display:block; background:#002A20; color:white; padding:15px; text-align:center; border-radius:10px; margin-bottom:10px; text-decoration:none;">🛰️ CONSULTAR ÍNDICE KP (GPS)</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.windy.com" target="_blank" style="display:block; background:#002A20; color:white; padding:15px; text-align:center; border-radius:10px; text-decoration:none;">🌬️ CONSULTAR WINDY</a>', unsafe_allow_html=True)

# --- TAB 4: VADEMÉCUM ---
with tabs[3]:
    st.subheader("Buscador de la Base de Datos")
    busc = st.text_input("🔍 Buscar principio activo o producto...")
    res = vademecum_df[vademecum_df['PRINCIPIO_ACTIVO'].str.contains(busc, case=False, na=False)]
    for _, r in res.iterrows():
        st.markdown(f"""
        <div class="alltec-ficha">
            <div class="alltec-header">{r['PRINCIPIO_ACTIVO']}</div>
            <div class="alltec-body">
                <b>Tipo:</b> {r['TIPO_PREPARADO']}<br>
                <b>Familia:</b> {r['FAMILIA_QUIMICA']}<br>
                <b>Dosis Sugerida:</b> {r['DOSIS_MARBETE_MIN']} - {r['DOSIS_MARBETE_MAX']} {r['UNIDAD_DOSIS']}<br>
                <b>Alerta:</b> {r['ALERTA_COMPATIBILIDAD']}<br>
                <b>Orden de Mezcla:</b> {r['ORDEN_MEZCLA']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 5: SOBRE NOSOTROS ---
with tabs[4]:
    st.header("Sobre el Autor")
    st.write("""
    Esta herramienta fue creada para simplificar el armado del **Caldo (Mixer)**, asegurando que las dosis 
    lleguen con precisión al objetivo. 
    
    El objetivo no es reemplazar la experiencia del aplicador, sino complementarla con cálculos rápidos en el lote.
    
    **Si esta aplicación te ha sido de utilidad y te ayudó a ahorrar tiempo y errores, considera apoyarme invitándome un café.**
    """)
    st.markdown('<a href="https://www.buymeacoffee.com/gabrielcarc" target="_blank"><button style="background-color: #FF813F; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">☕ Invítame un café</button></a>', unsafe_allow_html=True)
    st.divider()
    st.caption("Gabriel Carrasco - AgroDrone Solutions")
