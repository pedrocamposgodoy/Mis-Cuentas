# ================================================================
# SECCIÓN 0 — IMPORTS Y LIBRERÍAS
# No tocar esto salvo que añadas una librería nueva
# ================================================================
import streamlit as st
import pandas as pd
import os
import io
import plotly.graph_objects as go
from datetime import datetime, date

# Importar reportlab con fallback si no está instalado
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Table, TableStyle
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

# ================================================================
# SECCIÓN 1 — CONFIGURACIÓN Y COLORES
# Aquí cambias colores, título, icono de la app
# ================================================================
st.set_page_config(page_title="Nolasco Capital", layout="wide", page_icon="🏛️")

ACCENT     = "#185FA5"
SIDEBAR_BG = "#0F2744"
MAIN_BG    = "#F4F7FB"
CARD_BG    = "#FFFFFF"
BORDER     = "#D0DFF0"
TEXT_PRI   = "#0D1B2A"
TEXT_SEC   = "#5A7A9A"
GREEN      = "#1a7a40"
RED        = "#C0392B"
AMBER      = "#854F0B"
COLOR_TOPS = ["#185FA5","#0F6E56","#378ADD","#639922","#D85A30","#7F77DD"]

# ================================================================
# SECCIÓN 2 — ESTILOS CSS (diseño visual)
# No tocar salvo que quieras cambiar colores o tipografía
# ================================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');
.block-container{{padding-top:1.2rem!important;padding-bottom:0!important;}}
html,body,[class*="css"]{{font-family:'DM Sans',sans-serif;background-color:{MAIN_BG}!important;color:{TEXT_PRI};}}
[data-testid="stSidebar"]{{background:{SIDEBAR_BG}!important;border-right:1px solid #1a3a5c;min-width:260px!important;}}
[data-testid="stSidebar"] .stButton>button{{
    background:transparent!important;border:none!important;color:#A8C4E0!important;
    font-family:'DM Sans',sans-serif!important;font-size:0.88rem!important;font-weight:400!important;
    text-align:left!important;padding:0.65rem 1.4rem!important;border-radius:0 6px 6px 0!important;
    width:100%!important;margin-bottom:1px!important;box-shadow:none!important;
    border-left:3px solid transparent!important;
}}
[data-testid="stSidebar"] .stButton>button:hover{{background:rgba(96,180,255,0.08)!important;color:#fff!important;border-left:3px solid rgba(96,180,255,0.3)!important;}}
.nav-active{{border-left:3px solid #60B4FF;background:rgba(96,180,255,0.12);padding:0.65rem 1.4rem;margin-bottom:1px;border-radius:0 6px 6px 0;font-size:0.88rem;font-weight:600;color:#fff;font-family:'DM Sans',sans-serif;}}
.brand-header{{font-family:'DM Serif Display',serif;font-size:2rem;color:{TEXT_PRI};border-bottom:2px solid {ACCENT};padding-bottom:0.4rem;margin-bottom:0.2rem;}}
.brand-sub{{font-size:0.7rem;letter-spacing:0.18em;text-transform:uppercase;color:{TEXT_SEC};margin-bottom:1.5rem;}}
.section-title{{font-family:'DM Serif Display',serif;font-size:1.35rem;color:{TEXT_PRI};border-left:3px solid {ACCENT};padding-left:0.7rem;margin:1.5rem 0 1rem 0;}}
.kpi-card{{background:{CARD_BG};border:1px solid {BORDER};border-radius:10px;padding:1.2rem 1.3rem;text-align:left;}}
.kpi-card.highlight{{background:{ACCENT};border-color:{ACCENT};}}
.kpi-label{{font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase;color:{TEXT_SEC};margin-bottom:0.4rem;}}
.kpi-card.highlight .kpi-label{{color:#B5D4F4;}}
.kpi-value{{font-family:'DM Serif Display',serif;font-size:2rem;line-height:1;color:{TEXT_PRI};}}
.kpi-card.highlight .kpi-value{{color:#fff;}}
.kpi-sub{{font-size:0.7rem;color:{TEXT_SEC};margin-top:0.3rem;}}
.kpi-card.highlight .kpi-sub{{color:#B5D4F4;}}
.asset-card{{background:{CARD_BG};border:1px solid {BORDER};border-radius:10px 10px 0 0;overflow:hidden;}}
.asset-top{{height:4px;}}
.asset-body{{padding:1rem 1.1rem 0.8rem 1.1rem;}}
.asset-name{{font-size:0.82rem;font-weight:600;color:{TEXT_PRI};margin-bottom:2px;}}
.asset-tenant{{font-size:0.72rem;color:{TEXT_SEC};margin-bottom:0.8rem;}}
.asset-row{{display:flex;justify-content:space-between;margin-bottom:4px;}}
.asset-ml{{font-size:0.65rem;color:{TEXT_SEC};text-transform:uppercase;letter-spacing:0.04em;}}
.asset-mv{{font-size:0.82rem;font-weight:500;}}
.asset-div{{height:0.5px;background:{BORDER};margin:7px 0;}}
.asset-neto{{font-size:1rem;font-weight:600;color:{TEXT_PRI};}}
.pill{{display:inline-block;font-size:0.65rem;padding:2px 7px;border-radius:20px;margin-top:5px;}}
.pill-red{{background:#FCEBEB;color:#A32D2D;}}
.pill-amber{{background:#FAEEDA;color:#854F0B;}}
.pill-green{{background:#EAF3DE;color:#3B6D11;}}
.status-red{{background:#FDECEA;border-left:5px solid {RED};padding:1.2rem;border-radius:6px;}}
.status-yellow{{background:#FFF9E6;border-left:5px solid #F39C12;padding:1.2rem;border-radius:6px;}}
.status-green{{background:#EDF7F1;border-left:5px solid {GREEN};padding:1.2rem;border-radius:6px;}}
div[data-testid="column"] .stButton>button{{
    background:{CARD_BG}!important;border:1px solid {BORDER}!important;
    border-top:none!important;border-radius:0 0 10px 10px!important;
    color:{ACCENT}!important;font-size:0.72rem!important;font-weight:500!important;
    padding:0.4rem 1.1rem!important;width:100%!important;text-align:left!important;
    box-shadow:none!important;margin-top:0!important;
}}
div[data-testid="column"] .stButton>button:hover{{background:#F0F6FF!important;}}
#MainMenu,footer,header{{visibility:hidden;}}
</style>
""", unsafe_allow_html=True)

# ================================================================
# SECCIÓN 3 — ARCHIVOS DE DATOS (CSVs)
# Aquí se definen los nombres de los ficheros de datos
# Si cambias el nombre del CSV, cámbialo también aquí
# ================================================================
DB_INM = "nolasco_inmuebles_v12.csv"
DB_MOV = "nolasco_movimientos_v12.csv"

COLS_INM = [
    "Nombre","Inquilino","Renta","Renta_Mercado","Comunidad","Valor_Construccion",
    "Año_Reforma","Año_Construccion","Mobiliario","Tipo","Ref_Catastral","Titular",
    "M2_Construidos","Habitaciones","CP","Planta","Parking","Estado",
    "Tipo_Arrendamiento","Cochera_Vinculada","Zona_Tensionada",
    "Fecha_Inicio_Contrato","Fecha_Vencimiento_Contrato",
    "NIF_Inquilino","Intereses_Hipoteca","IBI_Anual","Seguro_Anual",
    "Gastos_Juridicos","Retenciones_IRPF","Gastos_Formalizacion",
    "Gastos_Pendientes_Años_Ant","Servicios_Suministros"
]

DEFAULTS_FISCAL = {
    "Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N","Zona_Tensionada":"N",
    "Fecha_Inicio_Contrato":"2022-01-01","Fecha_Vencimiento_Contrato":"2027-01-01",
    "NIF_Inquilino":"","Intereses_Hipoteca":0,"IBI_Anual":0,"Seguro_Anual":0,
    "Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,
    "Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0
}

# ================================================================
# SECCIÓN 4 — INICIALIZACIÓN DE DATOS
# Crea los CSV si no existen con datos de ejemplo
# Para cambiar los inmuebles de ejemplo, edita los "rows" de aquí
# ================================================================
def inicializar_bd():
    if not os.path.exists(DB_INM):
        rows = [
            {"Nombre":"Casa Abarqueros","Inquilino":"Victor Aguiluz","Renta":2200.0,"Renta_Mercado":2600.0,"Comunidad":193.76,"Valor_Construccion":150000.0,"Año_Reforma":2018,"Año_Construccion":1975,"Mobiliario":"S","Tipo":"Casa","Ref_Catastral":"00XX0001","Titular":"Pedro Nolasco","M2_Construidos":180,"Habitaciones":5,"CP":"18001","Planta":0,"Parking":"N","Estado":"Reformado","Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N","Zona_Tensionada":"N","Fecha_Inicio_Contrato":"2022-01-01","Fecha_Vencimiento_Contrato":"2027-01-01","NIF_Inquilino":"12345678A","Intereses_Hipoteca":0,"IBI_Anual":800,"Seguro_Anual":250,"Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0},
            {"Nombre":"Paseo del Salón","Inquilino":"Pool Despachos","Renta":1591.8,"Renta_Mercado":1650.0,"Comunidad":175.18,"Valor_Construccion":120000.0,"Año_Reforma":2020,"Año_Construccion":1990,"Mobiliario":"N","Tipo":"Piso","Ref_Catastral":"00XX0002","Titular":"Pedro Nolasco","M2_Construidos":130,"Habitaciones":4,"CP":"18005","Planta":3,"Parking":"S","Estado":"Bueno","Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"S","Zona_Tensionada":"N","Fecha_Inicio_Contrato":"2021-06-01","Fecha_Vencimiento_Contrato":"2026-06-01","NIF_Inquilino":"B87654321","Intereses_Hipoteca":0,"IBI_Anual":600,"Seguro_Anual":200,"Gastos_Juridicos":0,"Retenciones_IRPF":286.0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0},
            {"Nombre":"Huerto Unidad 1","Inquilino":"Alain","Renta":660.0,"Renta_Mercado":800.0,"Comunidad":74.62,"Valor_Construccion":45000.0,"Año_Reforma":2022,"Año_Construccion":2005,"Mobiliario":"S","Tipo":"Piso","Ref_Catastral":"00XX0003","Titular":"Pedro Nolasco","M2_Construidos":60,"Habitaciones":2,"CP":"18008","Planta":1,"Parking":"N","Estado":"Reformado","Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N","Zona_Tensionada":"S","Fecha_Inicio_Contrato":"2023-03-01","Fecha_Vencimiento_Contrato":"2028-03-01","NIF_Inquilino":"87654321B","Intereses_Hipoteca":0,"IBI_Anual":300,"Seguro_Anual":150,"Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0},
            {"Nombre":"Huerto Unidad 2","Inquilino":"Laura/Alex","Renta":800.0,"Renta_Mercado":800.0,"Comunidad":74.62,"Valor_Construccion":45000.0,"Año_Reforma":2022,"Año_Construccion":2005,"Mobiliario":"S","Tipo":"Piso","Ref_Catastral":"00XX0004","Titular":"Pedro Nolasco","M2_Construidos":65,"Habitaciones":2,"CP":"18008","Planta":2,"Parking":"N","Estado":"Reformado","Tipo_Arrendamiento":"Temporada","Cochera_Vinculada":"N","Zona_Tensionada":"S","Fecha_Inicio_Contrato":"2024-09-01","Fecha_Vencimiento_Contrato":"2025-08-31","NIF_Inquilino":"23456789C","Intereses_Hipoteca":0,"IBI_Anual":300,"Seguro_Anual":150,"Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0},
            {"Nombre":"Huerto Unidad 3","Inquilino":"Jose Manuel","Renta":850.0,"Renta_Mercado":800.0,"Comunidad":74.63,"Valor_Construccion":45000.0,"Año_Reforma":2021,"Año_Construccion":2005,"Mobiliario":"S","Tipo":"Piso","Ref_Catastral":"00XX0005","Titular":"Pedro Nolasco","M2_Construidos":68,"Habitaciones":3,"CP":"18008","Planta":3,"Parking":"N","Estado":"Bueno","Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N","Zona_Tensionada":"N","Fecha_Inicio_Contrato":"2022-11-01","Fecha_Vencimiento_Contrato":"2027-11-01","NIF_Inquilino":"34567890D","Intereses_Hipoteca":0,"IBI_Anual":300,"Seguro_Anual":150,"Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0},
            {"Nombre":"Huerto Unidad 4","Inquilino":"Pendiente","Renta":600.0,"Renta_Mercado":800.0,"Comunidad":74.62,"Valor_Construccion":45000.0,"Año_Reforma":2024,"Año_Construccion":2005,"Mobiliario":"S","Tipo":"Piso","Ref_Catastral":"00XX0006","Titular":"Pedro Nolasco","M2_Construidos":62,"Habitaciones":2,"CP":"18008","Planta":4,"Parking":"N","Estado":"Reformado","Tipo_Arrendamiento":"Vacacional","Cochera_Vinculada":"N","Zona_Tensionada":"N","Fecha_Inicio_Contrato":"2025-01-01","Fecha_Vencimiento_Contrato":"2026-12-31","NIF_Inquilino":"","Intereses_Hipoteca":0,"IBI_Anual":300,"Seguro_Anual":150,"Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0},
        ]
        pd.DataFrame(rows).to_csv(DB_INM, index=False)
    else:
        df = pd.read_csv(DB_INM)
        changed = False
        for c_name in COLS_INM:
            if c_name not in df.columns:
                df[c_name] = DEFAULTS_FISCAL.get(c_name, "")
                changed = True
        if changed:
            df.to_csv(DB_INM, index=False)

    if not os.path.exists(DB_MOV):
        pd.DataFrame([
            {"Fecha":"2026-04-01","Apartamento":"Casa Abarqueros","Concepto":"Renta Mensual","Categoría":"Ingresos","Tipo":"Ingreso","Importe":2200.00,"Deducible":"N"},
            {"Fecha":"2026-04-01","Apartamento":"Casa Abarqueros","Concepto":"Comunidad","Categoría":"Comunidad","Tipo":"Gasto","Importe":193.76,"Deducible":"S"},
        ]).to_csv(DB_MOV, index=False)

inicializar_bd()
df_inm = pd.read_csv(DB_INM)
df_mov = pd.read_csv(DB_MOV)

# ================================================================
# SECCIÓN 5 — DATOS DE HIPOTECAS
# Para añadir/cambiar hipotecas, edita los "rows" de aquí
# Campos: Inmueble, Principal, Tasa_Inicial, Plazo_Años,
#         Fecha_Inicio, Es_Variable, Indice_Variable, Margen, Saldo_Actual
# ================================================================
DB_HIP = "nolasco_hipotecas_v14.csv"
def inicializar_hipotecas():
    if not os.path.exists(DB_HIP):
        rows = [
            {"Inmueble":"Casa Abarqueros","Principal":150000,"Tasa_Inicial":2.5,"Plazo_Años":20,"Fecha_Inicio":"2020-01-15","Es_Variable":"N","Indice_Variable":"","Margen":0,"Saldo_Actual":0},
            {"Inmueble":"Paseo del Salón","Principal":120000,"Tasa_Inicial":2.8,"Plazo_Años":25,"Fecha_Inicio":"2018-06-01","Es_Variable":"S","Indice_Variable":"Euríbor","Margen":0.85,"Saldo_Actual":95000},
            {"Inmueble":"Huerto Unidad 1","Principal":45000,"Tasa_Inicial":3.0,"Plazo_Años":15,"Fecha_Inicio":"2021-03-10","Es_Variable":"N","Indice_Variable":"","Margen":0,"Saldo_Actual":0},
            {"Inmueble":"Huerto Unidad 2","Principal":45000,"Tasa_Inicial":3.0,"Plazo_Años":15,"Fecha_Inicio":"2021-03-10","Es_Variable":"N","Indice_Variable":"","Margen":0,"Saldo_Actual":0},
            {"Inmueble":"Huerto Unidad 3","Principal":45000,"Tasa_Inicial":3.0,"Plazo_Años":15,"Fecha_Inicio":"2021-03-10","Es_Variable":"N","Indice_Variable":"","Margen":0,"Saldo_Actual":0},
            {"Inmueble":"Huerto Unidad 4","Principal":0,"Tasa_Inicial":0,"Plazo_Años":0,"Fecha_Inicio":"2024-01-01","Es_Variable":"N","Indice_Variable":"","Margen":0,"Saldo_Actual":0},
        ]
        pd.DataFrame(rows).to_csv(DB_HIP, index=False)
inicializar_hipotecas()
df_hip = pd.read_csv(DB_HIP)

if "menu" not in st.session_state:      st.session_state.menu = "Torre de Control"
if "ficha_sel" not in st.session_state:  st.session_state.ficha_sel = None

# ================================================================
# SECCIÓN 6 — MENÚ DE NAVEGACIÓN
# Para añadir una pantalla nueva: agrega ("🔑", "Nombre") aquí
# El orden aquí es el orden que aparece en el menú lateral
# ================================================================
PAGES = [
    ("📊","Torre de Control"),
    ("🏠","Fichas (Benchmark)"),
    ("🤖","Auditoría IA"),
    ("📝","Diario Contable"),
    ("⚡","Suministros"),
    ("💰","Fiscalidad"),
    ("💎","Macrofinanzas"),
    ("📂","Datos de la Cartera"),
]

with st.sidebar:
    st.markdown("""
<div style='padding:1.4rem 1.4rem 0.8rem;'>
  <div style='font-family:"DM Serif Display",serif;font-size:1.45rem;color:#60B4FF;line-height:1.2;'>Nolasco Capital</div>
  <div style='font-size:0.62rem;letter-spacing:0.16em;text-transform:uppercase;color:#5a8aaa;margin-top:5px;'>Granada · Gestión Patrimonial</div>
</div>
<hr style='border:0;border-top:1px solid #1a3a5c;margin:0 0 0.4rem 0;'>
""", unsafe_allow_html=True)
    for icon, page in PAGES:
        if st.session_state.menu == page:
            st.markdown(f"<div class='nav-active'>{icon}&nbsp;&nbsp;{page}</div>", unsafe_allow_html=True)
        else:
            if st.button(f"{icon}  {page}", key=f"nav_{page}", use_container_width=True):
                st.session_state.menu = page
                st.rerun()
    st.markdown(f"<div style='padding:1rem 1.4rem;font-size:0.7rem;color:#3a6080;margin-top:0.8rem;'>{len(df_inm)} activos · {datetime.now().strftime('%b %Y')}</div>", unsafe_allow_html=True)

menu = st.session_state.menu

# ================================================================
# SECCIÓN 7 — FUNCIONES AUXILIARES (helpers)
# Funciones pequeñas que usa toda la app
# bench_pill, tasacion, alerta_vencimiento, etc.
# ================================================================
def bench_pill(desv):
    if desv < -15: return "pill-red","🔴"
    if desv < -5:  return "pill-amber","🟡"
    return "pill-green","🟢"

PRECIOS_CP = {"18001":12.5,"18002":11.8,"18003":10.2,"18004":10.8,"18005":11.2,
              "18006":10.0,"18007":9.5,"18008":10.4,"18009":8.2,"18010":9.8,
              "18011":10.1,"18012":9.6,"18013":9.0,"18014":9.3,"18015":8.8}

def tasacion(row):
    p  = PRECIOS_CP.get(str(row.get("CP","18005")),10.0)
    m2 = float(row.get("M2_Construidos",80))
    am = 1.05 if row.get("Mobiliario")=="S" else 1.0
    ap = 1.04 if row.get("Parking")=="S" else 1.0
    ae = {"Reformado":1.08,"Bueno":1.0,"Regular":0.92}.get(row.get("Estado","Bueno"),1.0)
    pl = int(row.get("Planta",1))
    apl= 0.95 if pl==0 else (1.03 if pl>=3 else 1.0)
    h  = int(row.get("Habitaciones",2))
    ah = 1.05 if h>=4 else (0.97 if h==1 else 1.0)
    return round(p*m2*am*ap*ae*apl*ah,2)

def dias_para_vencimiento(fecha_str):
    try:
        return (datetime.strptime(str(fecha_str),"%Y-%m-%d").date() - date.today()).days
    except:
        return None

def alerta_vencimiento(row):
    dias = dias_para_vencimiento(row.get("Fecha_Vencimiento_Contrato",""))
    if dias is None:  return None, None
    if dias < 0:      return "vencido", f"⚠️ Contrato vencido hace {abs(dias)} días"
    if dias < 60:     return "urgente", f"🔴 Vence en {dias} días — actuar ahora"
    if dias < 180:    return "aviso",   f"🟡 Vence en {dias} días ({round(dias/30)} meses)"
    return "ok", f"✅ Vence en {round(dias/30)} meses"

def guardar_movimientos(nuevos):
    df_actual = pd.read_csv(DB_MOV)
    df_nuevos = pd.DataFrame(nuevos)
    df_final  = pd.concat([df_actual, df_nuevos], ignore_index=True)
    df_final.to_csv(DB_MOV, index=False)

def parsear_ingresos(texto, df_inm_local):
    rentas   = dict(zip(df_inm_local["Nombre"], df_inm_local["Renta"]))
    nombres  = df_inm_local["Nombre"].tolist()
    texto_l  = texto.lower()
    registros = []
    hoy = datetime.now().strftime("%Y-%m-%d")
    mes = datetime.now().strftime("%B %Y")
    no_pagaron = [n for n in nombres if any(p in texto_l for p in [n.lower(), n.split()[0].lower(), n.split()[-1].lower()]) and ("menos" in texto_l or "excepto" in texto_l or "no" in texto_l or "pendiente" in texto_l or "falta" in texto_l)]
    if "todos" in texto_l and no_pagaron:
        for n in nombres:
            estado = "Pendiente" if n in no_pagaron else "Cobrado"
            registros.append({"Fecha":hoy,"Apartamento":n,"Concepto":f"Renta {mes}","Categoría":"Ingresos","Tipo":"Ingreso","Importe":rentas.get(n,0),"Deducible":"S","Estado":estado})
    elif "todos" in texto_l:
        for n in nombres:
            registros.append({"Fecha":hoy,"Apartamento":n,"Concepto":f"Renta {mes}","Categoría":"Ingresos","Tipo":"Ingreso","Importe":rentas.get(n,0),"Deducible":"S","Estado":"Cobrado"})
    else:
        mencionados = [n for n in nombres if any(p in texto_l for p in [n.lower(), n.split()[0].lower(), n.split()[-1].lower()])]
        for n in nombres:
            if n in mencionados:
                estado = "Pendiente" if any(p in texto_l for p in ["no","pendiente","falta","sin"]) else "Cobrado"
            else:
                estado = "Cobrado"
            registros.append({"Fecha":hoy,"Apartamento":n,"Concepto":f"Renta {mes}","Categoría":"Ingresos","Tipo":"Ingreso","Importe":rentas.get(n,0),"Deducible":"S","Estado":estado})
    return registros

# ================================================================
# SECCIÓN 8 — FUNCIONES FISCALES (Modelo 100 IRPF)
# calcular_dias_arrendado: días que estuvo alquilado en el año fiscal
# calcular_modelo_100: calcula las 16 casillas del IRPF
# ================================================================
def calcular_dias_arrendado(row, año_fiscal=None):
    try:
        inicio = datetime.strptime(str(row.get("Fecha_Inicio_Contrato","")), "%Y-%m-%d").date()
        fin    = datetime.strptime(str(row.get("Fecha_Vencimiento_Contrato","")), "%Y-%m-%d").date()
        hoy    = date.today()
        # Si no se especifica año fiscal, se usa el año anterior (declaración presentada en el año actual)
        año_actual = año_fiscal if año_fiscal else hoy.year - 1 if hoy.month < 7 else hoy.year
        inicio_año = date(año_actual, 1, 1)
        fin_año    = date(año_actual, 12, 31)
        inicio_efectivo = max(inicio, inicio_año)
        fin_efectivo    = min(fin, fin_año)
        if inicio_efectivo > fin_efectivo:
            return 0
        return (fin_efectivo - inicio_efectivo).days + 1
    except:
        return 365

def calcular_modelo_100(row, df_mov_local, año_fiscal=None):
    dias_arrendado = calcular_dias_arrendado(row, año_fiscal=año_fiscal)
    renta_mensual = float(row.get("Renta", 0))
    ingresos_integros = renta_mensual * 12
    intereses = float(row.get("Intereses_Hipoteca", 0))
    gastos_reparacion = df_mov_local[
        (df_mov_local["Apartamento"] == row["Nombre"]) &
        (df_mov_local["Tipo"] == "Gasto") &
        (df_mov_local["Categoría"].isin(["Mantenimiento", "Reparación"]))
    ]["Importe"].sum()
    ibi_anual = float(row.get("IBI_Anual", 0))
    comunidad_anual = float(row.get("Comunidad", 0)) * 12
    seguro_anual = float(row.get("Seguro_Anual", 0))
    formalizacion = float(row.get("Gastos_Formalizacion", 0))
    casilla_0110 = comunidad_anual + seguro_anual + formalizacion
    servicios = float(row.get("Servicios_Suministros", 0))
    gastos_juridicos = float(row.get("Gastos_Juridicos", 0))
    valor_construccion = float(row.get("Valor_Construccion", 0))
    amortizacion = valor_construccion * 0.03
    gastos_años_ant = float(row.get("Gastos_Pendientes_Años_Ant", 0))
    total_gastos = intereses + gastos_reparacion + ibi_anual + casilla_0110 + servicios + gastos_juridicos + amortizacion + gastos_años_ant
    rendimiento_neto = ingresos_integros - total_gastos
    tipo_arrendamiento = str(row.get("Tipo_Arrendamiento", "Larga Duración"))
    reduccion_pct = 0.60 if tipo_arrendamiento == "Larga Duración" else 0.00
    reduccion_importe = rendimiento_neto * reduccion_pct
    retenciones = float(row.get("Retenciones_IRPF", 0))
    rendimiento_final = rendimiento_neto - reduccion_importe
    return {
        "0062_0075": f"Ref: {row.get('Ref_Catastral', 'N/A')}",
        "0076": "A (Arrendamiento)", "0100": "SÍ" if tipo_arrendamiento == "Larga Duración" else "NO",
        "0101": dias_arrendado, "0102": round(ingresos_integros, 2),
        "0105": round(intereses, 2), "0106": round(gastos_reparacion, 2),
        "0107": round(total_gastos, 2),
        "0108": round(ibi_anual, 2), "0110": round(casilla_0110, 2),
        "0111": round(servicios, 2), "0112": round(gastos_juridicos, 2),
        "0113": round(amortizacion, 2), "0149": round(rendimiento_neto, 2),
        "0150": round(reduccion_importe, 2), "0153": round(retenciones, 2),
        "0152": round(rendimiento_final, 2), "reduccion_pct": int(reduccion_pct * 100)
    }

# ================================================================
# SECCIÓN 9 — FUNCIONES BLOQUE 5 (Macrofinanzas)
# calcular_amortizacion: simulador de hipoteca
# stress_test_euribor: impacto subida de tipos
# analisis_sensibilidad_renta: rentabilidad según variación de renta
# ================================================================
def calcular_amortizacion(principal, tasa_anual, plazo_años, modo="cuota_fija"):
    tasa_mensual = tasa_anual / 100 / 12
    num_cuotas = plazo_años * 12
    if modo == "cuota_fija":
        if tasa_mensual == 0:
            cuota_mensual = principal / num_cuotas
        else:
            cuota_mensual = principal * (tasa_mensual * (1 + tasa_mensual)**num_cuotas) / \
                           ((1 + tasa_mensual)**num_cuotas - 1)
    else:
        cuota_mensual = None
    tabla = []
    capital_pendiente = principal
    total_intereses = 0
    for mes in range(1, int(num_cuotas) + 1):
        if modo == "cuota_fija":
            interes = capital_pendiente * tasa_mensual
            capital = cuota_mensual - interes
            capital_pendiente -= capital
        else:
            capital = principal / num_cuotas
            interes = capital_pendiente * tasa_mensual
            cuota = capital + interes
            capital_pendiente -= capital
        total_intereses += interes
        tabla.append({
            "Mes": mes,
            "Cuota": cuota_mensual if modo == "cuota_fija" else interes + capital,
            "Capital": capital,
            "Intereses": interes,
            "Pendiente": max(0, capital_pendiente)
        })
    df_tabla = pd.DataFrame(tabla)
    return {
        "cuota_mensual": cuota_mensual if modo == "cuota_fija" else "variable",
        "total_intereses": round(total_intereses, 2),
        "total_pagado": round(principal + total_intereses, 2),
        "tabla": df_tabla
    }

def stress_test_euribor(saldo_actual, margen, euribor_base, plazo_restante_años):
    escenarios = {
        "Euríbor -1%": euribor_base - 1,
        "Euríbor actual": euribor_base,
        "Euríbor +1%": euribor_base + 1,
        "Euríbor +2%": euribor_base + 2,
        "Euríbor +3%": euribor_base + 3,
    }
    resultados = {}
    for escenario, tasa in escenarios.items():
        tasa_total = (tasa + margen) / 100
        if tasa_total == 0:
            cuota = saldo_actual / (plazo_restante_años * 12)
        else:
            cuota = saldo_actual * (tasa_total / 12 * (1 + tasa_total/12)**(plazo_restante_años*12)) / \
                    ((1 + tasa_total/12)**(plazo_restante_años*12) - 1)
        resultados[escenario] = {
            "tasa_total": round(tasa + margen, 2),
            "cuota_mensual": round(cuota, 2),
            "cuota_anual": round(cuota * 12, 2),
        }
    return resultados

def analisis_sensibilidad_renta(renta_actual, gastos_anuales, valor_construccion, variaciones=None):
    if variaciones is None:
        variaciones = [-15, -10, -5, 0, 5, 10, 15]
    escenarios = []
    for var_pct in variaciones:
        nueva_renta = renta_actual * (1 + var_pct / 100)
        ingresos_anuales = nueva_renta * 12
        neto_anual = ingresos_anuales - gastos_anuales
        rentabilidad = (neto_anual / valor_construccion * 100) if valor_construccion > 0 else 0
        escenarios.append({
            "Variación": f"{var_pct:+.0f}%",
            "Renta Mensual": f"{nueva_renta:.2f} €",
            "Ingresos Anuales": f"{ingresos_anuales:.2f} €",
            "Gastos Anuales": f"{gastos_anuales:.2f} €",
            "Neto Anual": f"{neto_anual:.2f} €",
            "Rentabilidad": f"{rentabilidad:.2f}%"
        })
    return pd.DataFrame(escenarios)

# ================================================================
# SECCIÓN 10 — GENERADOR DE PDF (Modelo 100)
# Genera el PDF de 2 páginas para el asesor fiscal
# No tocar salvo que quieras cambiar el diseño del PDF
# ================================================================
def generar_pdf_modelo100(inmueble_data, modelo):
    if not REPORTLAB_OK:
        return None
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    azul_oscuro = HexColor("#0F2744")
    azul_acento = HexColor("#185FA5")
    verde = HexColor("#1a7a40")
    gris_claro = HexColor("#F4F7FB")
    gris_borde = HexColor("#D0DFF0")
    ref = f"NC-{datetime.now().strftime('%Y')}-{inmueble_data['Nombre'][:3].upper()}"
    tipo_arr = str(inmueble_data.get("Tipo_Arrendamiento", "Larga Duracion"))

    # PÁGINA 1
    c.setFillColor(azul_oscuro)
    c.rect(0, h - 100, w, 100, fill=True, stroke=False)
    c.setFillColor(azul_acento)
    c.roundRect(30, h - 85, 55, 55, 6, fill=True, stroke=False)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(57.5, h - 65, "NC")
    c.setFont("Helvetica", 7)
    c.drawCentredString(57.5, h - 77, "CAPITAL")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, h - 50, "Nolasco Capital")
    c.setFont("Helvetica", 9)
    c.drawString(100, h - 65, "GRANADA  |  GESTION PATRIMONIAL INMOBILIARIA")
    c.setFont("Helvetica", 8)
    c.drawRightString(w - 30, h - 45, f"Ref: {ref}")
    c.drawRightString(w - 30, h - 57, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    c.drawRightString(w - 30, h - 69, f"Ejercicio: {datetime.now().year}")
    c.setStrokeColor(azul_acento)
    c.setLineWidth(3)
    c.line(0, h - 103, w, h - 103)

    y = h - 135
    c.setFillColor(azul_oscuro)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, y, "Modelo 100 - Rendimientos del Capital Inmobiliario")
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#5A7A9A"))
    c.drawString(30, y - 16, "Pre-relleno automatico IRPF  |  Verificado por propietario")

    y = y - 50
    c.setFillColor(gris_claro)
    c.roundRect(25, y - 75, w - 50, 75, 6, fill=True, stroke=False)
    c.setStrokeColor(gris_borde)
    c.roundRect(25, y - 75, w - 50, 75, 6, fill=False, stroke=True)
    c.setFillColor(azul_oscuro)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(35, y - 15, "Datos del Inmueble")
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#5A7A9A"))
    c.drawString(35, y - 32, "Inmueble: ")
    c.drawString(200, y - 32, "Ref. Catastral: ")
    c.drawString(370, y - 32, "Titular: ")
    c.setFillColor(azul_oscuro)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(87, y - 32, str(inmueble_data['Nombre']))
    c.drawString(275, y - 32, str(inmueble_data.get('Ref_Catastral', 'N/A')))
    c.drawString(408, y - 32, str(inmueble_data.get('Titular', 'Pedro Nolasco')))
    c.setFillColor(HexColor("#5A7A9A"))
    c.setFont("Helvetica", 9)
    c.drawString(35, y - 50, "Modalidad: ")
    c.drawString(200, y - 50, "NIF Inquilino: ")
    c.drawString(370, y - 50, "Dias arrendado: ")
    c.setFillColor(azul_oscuro)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(93, y - 50, tipo_arr)
    c.drawString(275, y - 50, str(inmueble_data.get('NIF_Inquilino', 'N/A')))
    c.drawString(452, y - 50, str(modelo['0101']))

    y = y - 100
    c.setFillColor(azul_oscuro)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y, "Casillas del Modelo 100")
    c.setStrokeColor(azul_acento)
    c.setLineWidth(2)
    c.line(30, y - 5, 220, y - 5)
    y = y - 25

    data = [
        ["Casilla", "Descripcion", "Valor", "Estado"],
        ["0062-0075", "Identificacion del inmueble", modelo["0062_0075"], "OK"],
        ["0076", "Clave de uso", modelo["0076"], "OK"],
        ["0100", "Reduccion vivienda habitual", modelo["0100"], "OK"],
        ["0101", "Dias arrendado", f"{modelo['0101']} dias", "OK"],
        ["0102", "Ingresos integros", f"{modelo['0102']:,.2f} EUR", "OK"],
        ["0105", "Intereses y financiacion", f"{modelo['0105']:,.2f} EUR", "OK"],
        ["0106", "Reparacion y conservacion", f"{modelo['0106']:,.2f} EUR", "OK"],
        ["0107", "TOTAL GASTOS DEDUCIBLES", f"{modelo['0107']:,.2f} EUR", "OK"],
        ["0108", "Tributos e IBI", f"{modelo['0108']:,.2f} EUR", "OK"],
        ["0110", "Comunidad, seguros, formalizacion", f"{modelo['0110']:,.2f} EUR", "OK"],
        ["0111", "Servicios y suministros", f"{modelo['0111']:,.2f} EUR", "OK"],
        ["0112", "Gastos juridicos", f"{modelo['0112']:,.2f} EUR", "OK"],
        ["0113", "Amortizacion (3%)", f"{modelo['0113']:,.2f} EUR", "OK"],
        ["0149", "RENDIMIENTO NETO", f"{modelo['0149']:,.2f} EUR", "OK"],
        ["0150", f"Reduccion {modelo['reduccion_pct']}%", f"-{modelo['0150']:,.2f} EUR", "OK"],
        ["0153", "Retenciones practicadas", f"{modelo['0153']:,.2f} EUR", "OK"],
        ["0152", "BASE IMPONIBLE FINAL", f"{modelo['0152']:,.2f} EUR", "OK"],
    ]
    t = Table(data, colWidths=[65, 230, 130, 50])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), azul_oscuro),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, gris_borde),
        ('LINEBELOW', (0, 0), (-1, 0), 2, azul_acento),
        ('ROWBACKGROUNDS', (0, 1), (-1, -4), [white, gris_claro]),
        ('BACKGROUND', (0, -4), (-1, -4), HexColor("#F0F8FF")),
        ('FONTNAME', (0, -4), (-1, -4), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -3), (-1, -3), HexColor("#FFF9E6")),
        ('FONTNAME', (0, -3), (-1, -3), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor("#D5F4E6")),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (2, -1), (2, -1), verde),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    t.wrapOn(c, w, h)
    t.drawOn(c, 30, y - len(data) * 20 - 10)
    y_after = y - len(data) * 20 - 30

    y_res = y_after - 20
    c.setFillColor(azul_acento)
    c.roundRect(25, y_res - 65, w - 50, 65, 6, fill=True, stroke=False)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y_res - 18, "RESUMEN FISCAL")
    c.setFont("Helvetica", 9)
    c.drawString(40, y_res - 35, f"Ingresos integros: {modelo['0102']:,.2f} EUR")
    c.drawString(220, y_res - 35, f"Total gastos: {modelo['0102'] - modelo['0149']:,.2f} EUR")
    c.drawString(430, y_res - 35, f"Reduccion: {modelo['reduccion_pct']}%")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y_res - 55, f"Base Imponible Final: {modelo['0152']:,.2f} EUR")

    # PÁGINA 2
    c.showPage()
    c.setFillColor(azul_oscuro)
    c.rect(0, h - 60, w, 60, fill=True, stroke=False)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, h - 38, "Nolasco Capital")
    c.setFont("Helvetica", 8)
    c.drawString(30, h - 50, f"Modelo 100 - {inmueble_data['Nombre']} | Ref: {ref}")
    c.drawRightString(w - 30, h - 38, "Pagina 2 de 2")
    c.setStrokeColor(azul_acento)
    c.setLineWidth(3)
    c.line(0, h - 63, w, h - 63)

    # Firma digital
    y_firma = h - 100
    c.setFillColor(azul_oscuro)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_firma, "Verificacion y Firma Digital")
    c.setStrokeColor(azul_acento)
    c.setLineWidth(2)
    c.line(30, y_firma - 5, 240, y_firma - 5)
    y_firma -= 30
    c.setFillColor(gris_claro)
    c.roundRect(25, y_firma - 90, (w - 50) / 2 - 10, 90, 6, fill=True, stroke=False)
    c.roundRect((w / 2) + 5, y_firma - 90, (w - 50) / 2 - 10, 90, 6, fill=True, stroke=False)
    c.setFillColor(azul_oscuro)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(35, y_firma - 15, "Propietario")
    c.setFont("Helvetica", 8)
    c.drawString(35, y_firma - 30, f"Nombre: {inmueble_data.get('Titular', 'Pedro Nolasco')}")
    c.drawString(35, y_firma - 44, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.setFillColor(verde)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(35, y_firma - 62, "VERIFICADO DIGITALMENTE")
    c.setFillColor(HexColor("#5A7A9A"))
    c.setFont("Helvetica", 7)
    c.drawString(35, y_firma - 75, f"Hash: NC{datetime.now().strftime('%Y%m%d%H%M')}{inmueble_data['Nombre'][:3].upper()}")
    c.setFillColor(azul_oscuro)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(w / 2 + 15, y_firma - 15, "Asesor Fiscal")
    c.setFont("Helvetica", 8)
    c.drawString(w / 2 + 15, y_firma - 30, "Nombre: ____________________________")
    c.drawString(w / 2 + 15, y_firma - 44, "Fecha:  ____________________________")
    c.drawString(w / 2 + 15, y_firma - 62, "Firma:  ____________________________")

    # Notas legales
    y_notas = y_firma - 130
    c.setFillColor(azul_oscuro)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, y_notas, "Notas Legales")
    c.setStrokeColor(azul_acento)
    c.setLineWidth(1)
    c.line(30, y_notas - 5, 130, y_notas - 5)
    notas = [
        "1. Este documento es orientativo y no sustituye el asesoramiento fiscal profesional.",
        "2. Los datos han sido pre-rellenados automaticamente desde la plataforma Nolasco Capital.",
        "3. El propietario es responsable de verificar la exactitud de todos los importes.",
        "4. Las reducciones aplicadas se basan en la normativa IRPF vigente (Ley 35/2006).",
        f"5. Modalidad de arrendamiento declarada: {tipo_arr}. Reduccion aplicada: {modelo['reduccion_pct']}%.",
        "6. La amortizacion se calcula al 3% sobre el valor de construccion (Art. 14 RIRPF).",
        "7. Documento generado electronicamente. No requiere firma manuscrita del propietario.",
        f"8. Referencia interna: {ref} | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
    ]
    c.setFont("Helvetica", 7)
    c.setFillColor(HexColor("#5A7A9A"))
    for i, nota in enumerate(notas):
        c.drawString(30, y_notas - 20 - (i * 13), nota)

    c.setFillColor(azul_oscuro)
    c.rect(0, 0, w, 30, fill=True, stroke=False)
    c.setFillColor(white)
    c.setFont("Helvetica", 7)
    c.drawString(30, 12, "Nolasco Capital  |  Granada  |  Gestion Patrimonial Inmobiliaria")
    c.drawRightString(w - 30, 12, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    c.save()
    buffer.seek(0)
    return buffer

# ================================================================
# PANTALLA 1 — TORRE DE CONTROL
# KPIs generales, rentabilidad por activo, lucro cesante, alertas
# ================================================================
if menu == "Torre de Control":
    st.markdown('<div class="brand-header">Torre de Control</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Rendimiento consolidado · Cartera Nolasco</div>', unsafe_allow_html=True)
    ing_b  = df_inm["Renta"].sum()
    gas_co = df_inm["Comunidad"].sum()
    gastos = gas_co + df_mov[(df_mov["Tipo"]=="Gasto")&(df_mov["Categoría"]!="Comunidad")]["Importe"].sum()
    neto   = ing_b - gastos
    margen = (neto/ing_b*100) if ing_b>0 else 0
    c1,c2,c3 = st.columns(3)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-label">Ingresos Brutos</div><div class="kpi-value" style="color:{GREEN};">{ing_b:,.0f} €</div><div class="kpi-sub">Renta mensual total</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-label">Gastos Operativos</div><div class="kpi-value" style="color:{RED};">−{gastos:,.0f} €</div><div class="kpi-sub">Comunidad + registrados</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card highlight"><div class="kpi-label">Beneficio Neto</div><div class="kpi-value">{neto:,.0f} €</div><div class="kpi-sub">Margen {margen:.1f}%</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Rentabilidad por Activo</div>', unsafe_allow_html=True)
    cols = st.columns(len(df_inm))
    for i, row in df_inm.iterrows():
        g_esp    = df_mov[(df_mov["Apartamento"]==row["Nombre"])&(df_mov["Tipo"]=="Gasto")&(df_mov["Categoría"]!="Comunidad")]["Importe"].sum()
        gastos_u = row["Comunidad"]+g_esp
        neto_u   = row["Renta"]-gastos_u
        rm       = tasacion(row)
        desv     = (row["Renta"]-rm)/rm*100
        pill_cls,_ = bench_pill(desv)
        zt = " 🔒" if str(row.get("Zona_Tensionada","N"))=="S" else ""
        with cols[i]:
            st.markdown(f"""<div class="asset-card"><div class="asset-top" style="background:{COLOR_TOPS[i%len(COLOR_TOPS)]};"></div><div class="asset-body"><div class="asset-name">{row["Nombre"]}{zt}</div><div class="asset-tenant">{row["Inquilino"]}</div><div class="asset-row"><span class="asset-ml">Renta</span><span class="asset-mv" style="color:{GREEN};">+{row["Renta"]:,.0f}€</span></div><div class="asset-row"><span class="asset-ml">Gastos</span><span class="asset-mv" style="color:{RED};">−{gastos_u:,.0f}€</span></div><div class="asset-div"></div><div class="asset-row"><span class="asset-ml">Neto</span><span class="asset-neto">{neto_u:,.0f}€</span></div><span class="pill {pill_cls}">{desv:+.1f}% mercado</span></div></div>""", unsafe_allow_html=True)
            if st.button("→ Ver ficha", key=f"card_{i}", use_container_width=True):
                st.session_state.menu = "Fichas (Benchmark)"
                st.session_state.ficha_sel = row["Nombre"]
                st.rerun()
    col_l,col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-title">Composición de Rentas</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Bar(x=df_inm["Renta"],y=df_inm["Nombre"],orientation="h",marker_color=COLOR_TOPS[:len(df_inm)],text=[f"{r:,.0f} €" for r in df_inm["Renta"]],textposition="outside"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=60,t=10,b=10),height=280,xaxis=dict(showgrid=False,visible=False),yaxis=dict(showgrid=False),font=dict(family="DM Sans",size=12))
        st.plotly_chart(fig,use_container_width=True)
    with col_r:
        st.markdown('<div class="section-title">Lucro Cesante Anual</div>', unsafe_allow_html=True)
        total_lc=0
        for _,row in df_inm.iterrows():
            rm=tasacion(row); pa=max(0,rm-row["Renta"])*12; total_lc+=pa
            if pa>0:
                dv=(row["Renta"]-rm)/rm*100; cv=RED if dv<-15 else AMBER
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:9px 12px;background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;margin-bottom:6px;"><span style="font-size:0.8rem;color:{TEXT_SEC};">{row["Nombre"]}</span><span style="font-size:0.9rem;font-weight:600;color:{cv};">−{pa:,.0f} €/año</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:11px 14px;background:{ACCENT};border-radius:8px;margin-top:4px;"><span style="font-size:0.72rem;font-weight:500;color:#B5D4F4;text-transform:uppercase;letter-spacing:0.06em;">Total pérdida anual</span><span style="font-size:1.3rem;font-weight:600;color:#fff;">−{total_lc:,.0f} €</span></div>', unsafe_allow_html=True)
    alertas = [(row["Nombre"],*alerta_vencimiento(row)) for _,row in df_inm.iterrows() if alerta_vencimiento(row)[0] in ("vencido","urgente","aviso")]
    if alertas:
        st.markdown('<div class="section-title">📅 Alertas de Contratos</div>', unsafe_allow_html=True)
        for nombre,tipo,msg in alertas:
            cls = "status-red" if tipo in ("vencido","urgente") else "status-yellow"
            st.markdown(f'<div class="{cls}" style="margin-bottom:6px;"><b>{nombre}</b> — {msg}</div>', unsafe_allow_html=True)

# ================================================================
# PANTALLA 2 — FICHAS BENCHMARK
# Análisis de mercado, motor de tasación, simulador de renta
# ================================================================
elif menu == "Fichas (Benchmark)":
    st.markdown('<div class="brand-header">Benchmark y Análisis Fiscal</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Análisis de mercado · Comparativa fiscal por modalidad</div>', unsafe_allow_html=True)
    default_idx = df_inm["Nombre"].tolist().index(st.session_state.ficha_sel) if st.session_state.ficha_sel in df_inm["Nombre"].tolist() else 0
    sel = st.selectbox("Inmueble a auditar:", df_inm["Nombre"].tolist(), index=default_idx)
    st.session_state.ficha_sel = sel
    f = df_inm[df_inm["Nombre"]==sel].iloc[0]
    renta_act = f["Renta"]; renta_mer = tasacion(f); desv = (renta_act-renta_mer)/renta_mer*100
    perdida_m = max(0,renta_mer-renta_act); perdida_a = perdida_m*12
    df_gf = df_mov[(df_mov["Apartamento"]==sel)&(df_mov["Tipo"]=="Gasto")&(df_mov["Categoría"]!="Comunidad")]
    gastos_u = f["Comunidad"]+df_gf["Importe"].sum()
    rent_bruta = (renta_act*12/f["Valor_Construccion"]*100) if f["Valor_Construccion"]>0 else 0
    rent_neta = ((renta_act-gastos_u)*12/f["Valor_Construccion"]*100) if f["Valor_Construccion"]>0 else 0
    tipo_arr = str(f.get("Tipo_Arrendamiento","Larga Duración"))
    zona_tens = str(f.get("Zona_Tensionada","N"))=="S"
    cochera_v = str(f.get("Cochera_Vinculada","N"))=="S"
    k1,k2,k3,k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-card"><div class="kpi-label">Renta Actual</div><div class="kpi-value" style="color:{GREEN};">{renta_act:,.0f} €</div><div class="kpi-sub">mensual</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><div class="kpi-label">Renta Tasada</div><div class="kpi-value" style="color:{TEXT_PRI};">{renta_mer:,.0f} €</div><div class="kpi-sub">motor CP + características</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card"><div class="kpi-label">Rentabilidad Bruta</div><div class="kpi-value" style="color:{ACCENT};">{rent_bruta:.1f}%</div><div class="kpi-sub">sobre valor construcción</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card highlight"><div class="kpi-label">Rentabilidad Neta</div><div class="kpi-value">{rent_neta:.1f}%</div><div class="kpi-sub">{tipo_arr}</div></div>', unsafe_allow_html=True)
    badges = []
    if zona_tens: badges.append(f'<span style="background:#FDECEA;color:#A32D2D;font-size:0.72rem;padding:3px 10px;border-radius:20px;font-weight:600;">🔒 Zona Tensionada</span>')
    if cochera_v: badges.append(f'<span style="background:#EDF7F1;color:#1a7a40;font-size:0.72rem;padding:3px 10px;border-radius:20px;font-weight:600;">🅿️ Cochera Vinculada</span>')
    tipo_color = {"Larga Duración":"#EAF3DE","Temporada":"#FFF9E6","Vacacional":"#FDECEA"}.get(tipo_arr,"#EAF3DE")
    tipo_texto = {"Larga Duración":"#3B6D11","Temporada":"#854F0B","Vacacional":"#A32D2D"}.get(tipo_arr,"#3B6D11")
    badges.append(f'<span style="background:{tipo_color};color:{tipo_texto};font-size:0.72rem;padding:3px 10px;border-radius:20px;font-weight:600;">📋 {tipo_arr}</span>')
    st.markdown("<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:1rem;'>"+"".join(badges)+"</div>", unsafe_allow_html=True)
    if zona_tens:
        st.markdown(f'<div class="status-red" style="margin-bottom:1rem;"><b>🔒 Zona de Mercado Tensionado</b><br>No puedes subir la renta por encima del índice legal.</div>', unsafe_allow_html=True)
    if not cochera_v and str(f.get("Parking","N"))=="S":
        st.markdown(f'<div class="status-yellow" style="margin-bottom:1rem;"><b>🅿️ Cochera Independiente</b><br>Tributa de forma separada. Revisar en declaración IRPF.</div>', unsafe_allow_html=True)
    tipo_v, msg_v = alerta_vencimiento(f)
    if tipo_v:
        cls_v = "status-red" if tipo_v in ("vencido","urgente") else ("status-yellow" if tipo_v=="aviso" else "status-green")
        st.markdown(f'<div class="{cls_v}" style="margin-bottom:1rem;"><b>📅 Contrato:</b> {msg_v}</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title">Renta Actual vs Tasada</div>', unsafe_allow_html=True)
        fig_bar = go.Figure(go.Bar(x=["Renta Actual","Renta Tasada"],y=[renta_act,renta_mer],marker_color=[ACCENT,"#D0DFF0"],text=[f"{renta_act:,.0f} €",f"{renta_mer:,.0f} €"],textposition="outside",width=0.4))
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=10,b=10),height=240,yaxis=dict(showgrid=False,visible=False),xaxis=dict(showgrid=False),font=dict(family="DM Sans",size=13),showlegend=False)
        st.plotly_chart(fig_bar,use_container_width=True)
    with c2:
        st.markdown('<div class="section-title">Estatus de Mercado</div>', unsafe_allow_html=True)
        if desv<-15:   clase,msg,icon="status-red","Rentabilidad Crítica","🔴"
        elif desv<-5:  clase,msg,icon="status-yellow","Margen de Mejora","🟡"
        else:          clase,msg,icon="status-green","Activo en Mercado","🟢"
        lucro_html=""
        if perdida_a>0:
            lucro_html=f'<div style="margin-top:12px;padding-top:12px;border-top:1px dashed rgba(0,0,0,0.15);"><span style="font-size:0.88rem;"><b>💸 Lucro Cesante:</b><br>Pérdida mensual: <b>{perdida_m:,.2f} €</b><br>Pérdida anualizada: <b style="color:{RED};font-size:1.15rem;">{perdida_a:,.2f} €/año</b></span></div>'
        st.markdown(f'<div class="{clase}"><b style="font-size:1.1rem;">{icon} {msg}</b><br>Desviación: <b>{desv:.1f}%</b>{lucro_html}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚖️ Comparativa Fiscal por Modalidad</div>', unsafe_allow_html=True)
    st.caption("Rentabilidad neta real tras aplicar reducción IRPF según tipo de arrendamiento")
    rto_neto = (renta_act-gastos_u)*12; tipo_irpf = 0.45
    modalidades = {"Larga Duración":{"reduccion":0.60,"iva":False},"Temporada":{"reduccion":0.00,"iva":False},"Vacacional":{"reduccion":0.00,"iva":True}}
    cf1,cf2,cf3 = st.columns(3); cols_fiscal = [cf1,cf2,cf3]; mejor_mod,mejor_rn = None,-99999
    for idx,(mod,params) in enumerate(modalidades.items()):
        red = params["reduccion"]; impuesto = max(0, rto_neto*(1-red)*tipo_irpf)
        rn_real = (rto_neto-impuesto)/f["Valor_Construccion"]*100 if f["Valor_Construccion"]>0 else 0
        if rn_real>mejor_rn: mejor_rn=rn_real; mejor_mod=mod
        es_actual = (mod==tipo_arr)
        borde = f"border:2px solid {ACCENT};" if es_actual else f"border:1px solid {BORDER};"
        iva_txt = "<br><span style='font-size:0.7rem;color:#854F0B;'>⚠️ Puede llevar IVA</span>" if params["iva"] else ""
        red_txt = f"Reducción IRPF: <b>{int(red*100)}%</b>" if red>0 else "Sin reducción fiscal"
        badge = "<div style='margin-top:8px;font-size:0.7rem;background:#EAF3DE;color:#3B6D11;padding:3px 8px;border-radius:20px;'>✅ Modalidad actual</div>" if es_actual else ""
        cols_fiscal[idx].markdown(f"""<div style="background:{CARD_BG};{borde}border-radius:10px;padding:1.1rem;text-align:center;"><div style="font-size:0.72rem;font-weight:600;color:{TEXT_SEC};text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">{mod}</div><div style="font-family:'DM Serif Display',serif;font-size:1.8rem;color:{ACCENT if es_actual else TEXT_PRI};">{rn_real:.1f}%</div><div style="font-size:0.7rem;color:{TEXT_SEC};margin-top:4px;">Rent. neta real/año</div><div style="font-size:0.75rem;color:{TEXT_PRI};margin-top:8px;">{red_txt}{iva_txt}</div><div style="font-size:0.7rem;color:{RED};margin-top:4px;">Impuesto est.: {impuesto:,.0f} €/año</div>{badge}</div>""", unsafe_allow_html=True)
    if mejor_mod:
        st.markdown(f'<div class="status-green" style="margin-top:1rem;"><b>💡 Recomendación IA:</b> La modalidad <b>{mejor_mod}</b> ofrece la mayor rentabilidad neta real ({mejor_rn:.1f}%).</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Simulador de Subida de Renta</div>', unsafe_allow_html=True)
    if zona_tens:
        max_renta = int(renta_act*1.03)
        st.warning(f"🔒 Zona tensionada: subida máxima al IPC (3%). Renta máxima: {max_renta:,.0f} €/mes")
        nueva_renta = st.slider("Ajusta la renta (€)", min_value=int(renta_act*0.9), max_value=max_renta, value=int(renta_act), step=10)
    else:
        nueva_renta = st.slider("Ajusta la renta mensual (€)", min_value=int(renta_act*0.8), max_value=int(renta_mer*1.2), value=int(renta_act), step=25)
    ganancia_m = nueva_renta-renta_act; ganancia_a = ganancia_m*12
    nueva_neta = ((nueva_renta-gastos_u)*12/f["Valor_Construccion"]*100) if f["Valor_Construccion"]>0 else 0
    s1,s2,s3 = st.columns(3)
    s1.metric("Nueva Renta", f"{nueva_renta:,.0f} €/mes", delta=f"{ganancia_m:+.0f} €")
    s2.metric("Impacto Anual", f"{ganancia_a:+,.0f} €/año")
    s3.metric("Nueva Rent. Neta", f"{nueva_neta:.1f}%", delta=f"{nueva_neta-rent_neta:+.1f}%")
    st.markdown('<div class="section-title">Comparativa de Activos — Renta vs Tasación</div>', unsafe_allow_html=True)
    rt = [tasacion(r) for _,r in df_inm.iterrows()]
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name="Renta Actual",x=df_inm["Nombre"],y=df_inm["Renta"],marker_color=ACCENT,text=[f"{r:,.0f}€" for r in df_inm["Renta"]],textposition="outside"))
    fig_comp.add_trace(go.Bar(name="Renta Tasada",x=df_inm["Nombre"],y=rt,marker_color="#D0DFF0",text=[f"{r:,.0f}€" for r in rt],textposition="outside"))
    fig_comp.update_layout(barmode="group",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=10,b=10),height=300,yaxis=dict(showgrid=False,visible=False),xaxis=dict(showgrid=False),font=dict(family="DM Sans",size=12),legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    st.plotly_chart(fig_comp,use_container_width=True)
    st.markdown('<div class="section-title">Análisis de Gastos Reales</div>', unsafe_allow_html=True)
    res = pd.concat([pd.DataFrame([{"Concepto":"Comunidad","Importe":f["Comunidad"],"Deducible":"S"}]),df_gf[["Concepto","Importe","Deducible"]]])
    st.dataframe(res.style.format({"Importe":"{:,.2f} €"}),hide_index=True,use_container_width=True)

# ================================================================
# PANTALLA 3 — AUDITORÍA IA DE MANTENIMIENTO
# Presupuestos urgente/medio/largo por inmueble
# ================================================================
elif menu == "Auditoría IA":
    st.markdown('<div class="brand-header">Auditoría de Mantenimiento</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Planificación de reformas · Costos e impacto por plazo</div>', unsafe_allow_html=True)
    datos_mantenimiento = {
        "Casa Abarqueros": {"urgente": {"total":4500,"items":[("Revisión estructura",2500,0.55),("Pintura fachada",1500,0.33),("Canalones",500,0.12)]},"medio": {"total":12000,"items":[("Tuberías",8000,0.67),("Electricidad",3500,0.29),("Calderas",600,0.05)]},"largo": {"total":8000,"items":[("Ventanas",5000,0.62),("Aislamiento",2500,0.31),("Cubierta",500,0.06)]}},
        "Paseo del Salón": {"urgente": {"total":3000,"items":[("Pinturas",1500,0.5),("Fontanería menor",1000,0.33),("Mantenimiento",500,0.17)]},"medio": {"total":7000,"items":[("Tuberías",4000,0.57),("Electricidad",2500,0.36),("Otros",500,0.07)]},"largo": {"total":4500,"items":[("Ventanas",2500,0.56),("Aislamiento",1500,0.33),("Cubierta",500,0.11)]}},
        "Huerto Unidad 1": {"urgente": {"total":2000,"items":[("Pintura",1000,0.5),("Reparaciones",800,0.4),("Otros",200,0.1)]},"medio": {"total":4500,"items":[("Tuberías",2500,0.56),("Electricidad",1500,0.33),("Otros",500,0.11)]},"largo": {"total":3000,"items":[("Ventanas",1800,0.6),("Aislamiento",1000,0.33),("Cubierta",200,0.07)]}},
        "Huerto Unidad 2": {"urgente": {"total":2000,"items":[("Pintura",1000,0.5),("Reparaciones",800,0.4),("Otros",200,0.1)]},"medio": {"total":4500,"items":[("Tuberías",2500,0.56),("Electricidad",1500,0.33),("Otros",500,0.11)]},"largo": {"total":3000,"items":[("Ventanas",1800,0.6),("Aislamiento",1000,0.33),("Cubierta",200,0.07)]}},
        "Huerto Unidad 3": {"urgente": {"total":1500,"items":[("Pintura",800,0.53),("Reparaciones",600,0.4),("Otros",100,0.07)]},"medio": {"total":4000,"items":[("Tuberías",2300,0.575),("Electricidad",1400,0.35),("Otros",300,0.075)]},"largo": {"total":2500,"items":[("Ventanas",1500,0.6),("Aislamiento",800,0.32),("Cubierta",200,0.08)]}},
        "Huerto Unidad 4": {"urgente": {"total":1000,"items":[("Pintura",600,0.6),("Reparaciones",300,0.3),("Otros",100,0.1)]},"medio": {"total":3500,"items":[("Tuberías",2000,0.57),("Electricidad",1200,0.34),("Otros",300,0.09)]},"largo": {"total":2000,"items":[("Ventanas",1200,0.6),("Aislamiento",600,0.3),("Cubierta",200,0.1)]}},
    }
    inmueble_sel_aud = st.selectbox("Selecciona inmueble a auditar:", df_inm["Nombre"].tolist(), key="aud_inmueble")
    if inmueble_sel_aud in datos_mantenimiento:
        row_aud = df_inm[df_inm["Nombre"]==inmueble_sel_aud].iloc[0]
        año_actual = datetime.now().year
        ant = año_actual - int(row_aud.get("Año_Reforma", año_actual))
        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        col_a1.metric("Construcción", int(row_aud.get("Año_Construccion", 0)))
        col_a2.metric("Última reforma", int(row_aud.get("Año_Reforma", 0)))
        col_a3.metric("Antigüedad", f"{ant} años")
        col_a4.metric("Estado", row_aud.get("Estado", "—"))
        st.markdown("---")
        datos_aud = datos_mantenimiento[inmueble_sel_aud]
        total_presupuesto = datos_aud["urgente"]["total"] + datos_aud["medio"]["total"] + datos_aud["largo"]["total"]
        def mostrar_seccion(plazo_label, color_hex, datos_plazo):
            col_sec1, col_sec2 = st.columns([3, 1])
            with col_sec1:
                st.markdown(f"### {plazo_label}")
            with col_sec2:
                st.markdown(f'<div style="font-family:\'DM Serif Display\',serif;font-size:1.5rem;color:{color_hex};font-weight:600;">{datos_plazo["total"]:,.0f}€</div>', unsafe_allow_html=True)
            cols_items = st.columns(len(datos_plazo["items"]))
            for idx_item, (nombre, monto, pct) in enumerate(datos_plazo["items"]):
                with cols_items[idx_item]:
                    st.markdown(f"""<div style="background:{color_hex};height:50px;border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:white;font-size:0.7rem;font-weight:600;padding:0.4rem;text-align:center;margin-bottom:0.5rem;"><span style="font-size:0.65rem;">{nombre}</span><span style="font-size:0.75rem;margin-top:2px;">{monto:,.0f}€</span></div>""", unsafe_allow_html=True)
                    st.caption(f"{pct*100:.0f}%")
            desglose = " • ".join([f"{n} ({m:,.0f}€)" for n, m, _ in datos_plazo["items"]])
            st.markdown(f'<div style="font-size:0.8rem;color:{TEXT_SEC};margin-top:0.5rem;">📊 {desglose}</div>', unsafe_allow_html=True)
            st.markdown("---")
        mostrar_seccion("🔴 URGENTE (0-6 meses)", RED, datos_aud["urgente"])
        mostrar_seccion("🟠 MEDIO (6-18 meses)", AMBER, datos_aud["medio"])
        mostrar_seccion("🟢 LARGO (18+ meses)", GREEN, datos_aud["largo"])
        st.markdown('<div class="section-title">💰 Resumen Presupuestario</div>', unsafe_allow_html=True)
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Inversión Total", f"{total_presupuesto:,.0f} €", "todas las categorías")
        col_res2.metric("Urgente + Medio", f"{datos_aud['urgente']['total'] + datos_aud['medio']['total']:,.0f} €", "próximos 18 meses")
        col_res3.metric("% sobre valor", f"{total_presupuesto/row_aud['Valor_Construccion']*100:.1f}%", f"de {row_aud['Valor_Construccion']:,.0f}€")
        st.markdown('<div class="section-title">📋 Recomendaciones</div>', unsafe_allow_html=True)
        if ant >= 8:
            st.markdown(f'<div class="status-red"><b>🚨 Reforma muy antigua</b><br>Con {ant} años desde la última reforma, las intervenciones urgentes son críticas.</div>', unsafe_allow_html=True)
        elif ant >= 5:
            st.markdown(f'<div class="status-yellow"><b>⚠️ Reforma antigua</b><br>Con {ant} años, planifica presupuesto para las intervenciones del plazo medio.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-green"><b>✅ Reforma reciente</b><br>Con {ant} años, el inmueble está en buen estado.</div>', unsafe_allow_html=True)
        tipo_v, msg_v = alerta_vencimiento(row_aud)
        if tipo_v in ("vencido", "urgente", "aviso") and ant >= 3:
            st.markdown(f'<div class="status-yellow" style="margin-top:0.8rem;"><b>🎯 Oportunidad de Negociación:</b><br>El contrato {msg_v.lower()}. Momento óptimo para renegociar.</div>', unsafe_allow_html=True)

# ================================================================
# PANTALLA 4 — DIARIO CONTABLE
# Registro de ingresos y gastos, parseo inteligente de texto
# ================================================================
elif menu == "Diario Contable":
    st.markdown('<div class="brand-header">Diario Contable</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Registro de operaciones · Ingresos · Gastos</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 Registro de Operaciones", "📥 Registrar Ingresos", "📤 Registrar Gastos"])
    with tab1:
        l_inm = df_inm["Nombre"].tolist()+["Global"]
        l_cat = ["Ingresos","Financiero","Tributario","Suministros","Seguros","Mantenimiento","Estructura","Comunidad","Otros"]
        l_con = ["Renta Mensual","Hipoteca (Intereses)","Hipoteca (Capital)","IBI","Comunidad Ordinaria","Seguro Hogar","Seguro Vida","Luz","Agua","Reparación","Sueldo Pedro"]
        config = {
            "Apartamento": st.column_config.SelectboxColumn("Inmueble",options=l_inm,required=True),
            "Concepto": st.column_config.SelectboxColumn("Concepto",options=l_con,required=True),
            "Categoría": st.column_config.SelectboxColumn("Categoría",options=l_cat,required=True),
            "Tipo": st.column_config.SelectboxColumn("Tipo",options=["Ingreso","Gasto"],required=True),
            "Deducible": st.column_config.SelectboxColumn("Fiscal",options=["S","N"],required=True),
            "Importe": st.column_config.NumberColumn("Importe (€)",format="%.2f",min_value=0),
        }
        df_ed = st.data_editor(df_mov,num_rows="dynamic",use_container_width=True,hide_index=True,column_config=config)
        t_ing = df_ed[df_ed["Tipo"]=="Ingreso"]["Importe"].sum()
        t_gas = df_ed[df_ed["Tipo"]=="Gasto"]["Importe"].sum()
        m1,m2,m3 = st.columns(3)
        m1.metric("Ingresos Registrados", f"{t_ing:,.2f} €")
        m2.metric("Gastos Registrados", f"−{t_gas:,.2f} €")
        m3.metric("Balance Total", f"{t_ing-t_gas:,.2f} €")
        if st.button("💾 Guardar Cambios", key="guardar_tabla"):
            df_ed.to_csv(DB_MOV,index=False); st.success("✓ Operaciones guardadas."); st.rerun()
    with tab2:
        st.markdown("### 📥 Registrar Ingresos del Mes")
        st.caption('Ejemplo: "Todos han pagado menos Abarqueros"')
        texto_ingresos = st.text_area("¿Quién ha pagado este mes?",placeholder="Todos han pagado menos Abarqueros...",height=90)
        if st.button("🔄 Procesar ingresos", type="primary", key="procesar_ing"):
            if texto_ingresos.strip():
                registros = parsear_ingresos(texto_ingresos, df_inm)
                if registros:
                    st.markdown("---")
                    st.markdown("**✓ Registros detectados — revisa antes de guardar:**")
                    for r in registros:
                        color = "#EDF7F1" if r["Estado"]=="Cobrado" else "#FDECEA"
                        bcolor = GREEN if r["Estado"]=="Cobrado" else RED
                        icon = "✅" if r["Estado"]=="Cobrado" else "⏳"
                        st.markdown(f"""<div style="background:{color};border-left:4px solid {bcolor};padding:0.8rem 1rem;border-radius:6px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;"><div><span style="font-weight:600;font-size:0.88rem;">{icon} {r['Apartamento']}</span><span style="font-size:0.75rem;color:{TEXT_SEC};margin-left:8px;">{r['Concepto']}</span></div><span style="font-family:'DM Serif Display',serif;font-size:1.1rem;color:{bcolor};">{r['Importe']:,.0f} €</span></div>""", unsafe_allow_html=True)
                    st.session_state["ingresos_pendientes"] = registros
            else:
                st.warning("Escribe una descripción primero")
        if "ingresos_pendientes" in st.session_state and st.session_state["ingresos_pendientes"]:
            if st.button("💾 Guardar todos en tabla", key="guardar_ingresos"):
                a_guardar = [r.copy() for r in st.session_state["ingresos_pendientes"]]
                for r in a_guardar:
                    r.pop("Estado", None)
                guardar_movimientos(a_guardar)
                st.session_state.pop("ingresos_pendientes")
                st.success("✅ Ingresos guardados correctamente"); st.rerun()
    with tab3:
        st.markdown("### 📤 Registrar Gasto")
        st.caption("Sube una factura (OCR próximamente) o describe el gasto manualmente")
        archivo = st.file_uploader("Adjunta factura PDF o foto", type=["pdf","jpg","png","jpeg"])
        if archivo:
            st.info("📝 Lectura automática de facturas — próximamente disponible.")
        concepto_gasto = st.text_input("Concepto", placeholder="Reparación lavadora Huerto 1...")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            inmueble_g = st.selectbox("Inmueble", ["— Selecciona —"]+df_inm["Nombre"].tolist(), key="inmg")
            importe_g = st.number_input("Importe (€)", min_value=0.0, step=0.01, format="%.2f")
        with col_g2:
            categoria_g = st.selectbox("Categoría", ["Mantenimiento","Suministros","Comunidad","Seguros","Tributario","Financiero","Otros"])
            deducible_g = st.selectbox("¿Es deducible?", ["S","N"])
        if st.button("💾 Guardar Gasto", type="primary", key="guardar_gasto"):
            if inmueble_g == "— Selecciona —":
                st.error("Selecciona un inmueble")
            elif importe_g <= 0:
                st.error("El importe debe ser mayor que 0")
            elif not concepto_gasto.strip():
                st.error("Escribe un concepto")
            else:
                nuevo = [{"Fecha":datetime.now().strftime("%Y-%m-%d"),"Apartamento":inmueble_g,"Concepto":concepto_gasto,"Categoría":categoria_g,"Tipo":"Gasto","Importe":importe_g,"Deducible":deducible_g}]
                guardar_movimientos(nuevo)
                st.success(f"✅ Gasto de {importe_g:.2f} € guardado en {inmueble_g}"); st.rerun()

# ================================================================
# PANTALLA 5 — SUMINISTROS
# Auditoría de potencia eléctrica, comparador de tarifas
# ================================================================
elif menu == "Suministros":
    st.markdown('<div class="brand-header">Optimización de Suministros</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Auditoría de potencia eléctrica · Comparador tarifario</div>', unsafe_allow_html=True)
    inmueble_sel = st.selectbox("Selecciona inmueble:", df_inm["Nombre"].tolist())
    f = df_inm[df_inm["Nombre"]==inmueble_sel].iloc[0]
    hab = int(f.get("Habitaciones",2))
    st.markdown('<div class="section-title">⚡ Auditoría de Potencia Contratada</div>', unsafe_allow_html=True)
    col1,col2 = st.columns(2)
    with col1:
        potencia_actual = st.number_input("Potencia contratada (kW)",min_value=1.0,max_value=30.0,value=4.4,step=0.1)
        tiene_ac = st.checkbox("¿Aire acondicionado?",value=True)
        tiene_vitro = st.checkbox("¿Vitrocerámica/inducción?",value=True)
        tiene_termo = st.checkbox("¿Termo eléctrico?",value=False)
        tiene_cargador = st.checkbox("¿Cargador vehículo eléctrico?",value=False)
    base_kw={1:2.3,2:3.3,3:3.3,4:4.4,5:5.5}.get(min(hab,5),4.4)
    extra=0.0
    if tiene_ac: extra+=2.0
    if tiene_vitro: extra+=1.5
    if tiene_termo: extra+=1.0
    if tiene_cargador: extra+=3.7
    POTENCIAS_REE=[1.15,2.3,3.45,4.6,5.75,6.9,8.05,9.2,10.35,11.5,14.49,17.25]
    pot_rec=next((p for p in POTENCIAS_REE if p>=base_kw+extra),17.25)
    coste_act=potencia_actual*42.0; coste_opt=pot_rec*42.0; ahorro=coste_act-coste_opt
    with col2:
        st.markdown(f"""<div style="background:{CARD_BG};border:1px solid {BORDER};border-radius:10px;padding:1.4rem;"><div class="kpi-label">Potencia recomendada</div><div style="font-family:'DM Serif Display',serif;font-size:2.2rem;color:{ACCENT};">{pot_rec} kW</div><div class="kpi-sub">Basado en {hab} hab. + equipos</div><hr style="border:0;border-top:1px solid {BORDER};margin:0.8rem 0;"><div style="display:flex;justify-content:space-between;margin-bottom:6px;"><span class="kpi-label">Coste actual/año</span><span style="font-size:0.9rem;font-weight:600;color:{RED};">{coste_act:,.0f} €</span></div><div style="display:flex;justify-content:space-between;"><span class="kpi-label">Coste óptimo/año</span><span style="font-size:0.9rem;font-weight:600;color:{GREEN};">{coste_opt:,.0f} €</span></div></div>""", unsafe_allow_html=True)
        cls_a="status-green" if ahorro>5 else ("status-red" if ahorro<-5 else "status-green")
        msg_a=f"✅ Ahorro potencial: {ahorro:,.0f} €/año · Bajar a {pot_rec} kW" if ahorro>5 else (f"⚠️ Potencia insuficiente · Subir a {pot_rec} kW" if ahorro<-5 else "✅ Potencia correctamente ajustada")
        st.markdown(f'<div class="{cls_a}" style="margin-top:0.8rem;">{msg_a}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Comparador Tarifa Fija vs Indexada</div>', unsafe_allow_html=True)
    tc1,tc2,tc3=st.columns(3)
    with tc1: kwh=st.number_input("Consumo mensual (kWh)",min_value=50,max_value=2000,value=200,step=10)
    with tc2: pfijo=st.number_input("Tarifa fija (€/kWh)",min_value=0.05,max_value=0.50,value=0.18,step=0.01,format="%.3f")
    with tc3: ppool=st.number_input("Pool PVPC (€/kWh)",min_value=0.02,max_value=0.40,value=0.12,step=0.01,format="%.3f")
    pind=ppool+0.04; cf_mes=kwh*pfijo; ci_mes=kwh*pind; dif_a=(cf_mes-ci_mes)*12
    fig_tar=go.Figure(go.Bar(x=["Tarifa Fija","Tarifa Indexada"],y=[cf_mes,ci_mes],marker_color=[ACCENT,"#639922"],text=[f"{cf_mes:.2f} €/mes",f"{ci_mes:.2f} €/mes"],textposition="outside",width=0.35))
    fig_tar.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=20,b=10),height=260,yaxis=dict(showgrid=False,visible=False),xaxis=dict(showgrid=False),font=dict(family="DM Sans",size=13),showlegend=False)
    st.plotly_chart(fig_tar,use_container_width=True)
    r1,r2,r3=st.columns(3)
    r1.metric("Coste fijo/mes",f"{cf_mes:.2f} €")
    r2.metric("Coste indexado/mes",f"{ci_mes:.2f} €",delta=f"{-(cf_mes-ci_mes):+.2f} €")
    r3.metric("Ahorro anual",f"{dif_a:+.0f} €")
    if dif_a>30: rec,cls_t=f"✅ Tarifa <b>indexada</b> más barata. Ahorro: <b>{dif_a:.0f} €/año</b>.","status-green"
    elif dif_a<-30: rec,cls_t="⚠️ Tarifa <b>fija</b> más económica con pool actual.","status-yellow"
    else: rec,cls_t="➡️ Diferencia marginal. Depende de tu tolerancia al riesgo.","status-yellow"
    st.markdown(f'<div class="{cls_t}" style="margin-top:0.5rem;">{rec}</div>', unsafe_allow_html=True)

# ================================================================
# PANTALLA 6 — FISCALIDAD (MODELO 100 IRPF)
# Pre-relleno automático de casillas, generador de PDF
# ================================================================
elif menu == "Fiscalidad":
    st.markdown('<div class="brand-header">Escudo Fiscal — Modelo 100</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Pre-relleno IRPF · Rendimientos de capital inmobiliario</div>', unsafe_allow_html=True)

    inmueble_fiscal = st.selectbox("Selecciona inmueble:", df_inm["Nombre"].tolist(), key="fiscal_inmueble")
    año_fiscal = st.selectbox("Ejercicio fiscal:", [2025, 2024, 2023], index=0, key="año_fiscal")
    f_fiscal = df_inm[df_inm["Nombre"] == inmueble_fiscal].iloc[0]
    modelo = calcular_modelo_100(f_fiscal, df_mov, año_fiscal=año_fiscal)

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ingresos Íntegros", f"{modelo['0102']:,.0f} €", "Casilla 0102")
    k2.metric("Total Gastos", f"{modelo['0102'] - modelo['0149']:,.0f} €", "Deducibles")
    k3.metric("Rendimiento Neto", f"{modelo['0149']:,.0f} €", "Casilla 0149")
    k4.metric("Base Imponible", f"{modelo['0152']:,.0f} €", f"Reducción {modelo['reduccion_pct']}%")

    st.markdown("---")
    st.markdown('<div class="section-title">📋 Casillas Modelo 100 — Verificar y Confirmar</div>', unsafe_allow_html=True)
    st.caption("Revisa cada casilla. Los valores están pre-rellenados desde tus datos.")

    # Tabla con DataFrame en lugar de HTML + checkboxes rotos
    casillas_data = [
        {"Casilla": "0062-0075", "Descripción": "Identificación del inmueble", "Valor": modelo["0062_0075"]},
        {"Casilla": "0076", "Descripción": "Clave de uso", "Valor": modelo["0076"]},
        {"Casilla": "0100", "Descripción": "Reducción vivienda habitual", "Valor": modelo["0100"]},
        {"Casilla": "0101", "Descripción": "Días arrendado", "Valor": f"{modelo['0101']} días"},
        {"Casilla": "0102", "Descripción": "Ingresos íntegros", "Valor": f"{modelo['0102']:,.2f} €"},
        {"Casilla": "0105", "Descripción": "Intereses y financiación", "Valor": f"{modelo['0105']:,.2f} €"},
        {"Casilla": "0106", "Descripción": "Reparación y conservación", "Valor": f"{modelo['0106']:,.2f} €"},
        {"Casilla": "0107", "Descripción": "TOTAL GASTOS DEDUCIBLES", "Valor": f"{modelo['0107']:,.2f} €"},
        {"Casilla": "0108", "Descripción": "Tributos e IBI", "Valor": f"{modelo['0108']:,.2f} €"},
        {"Casilla": "0110", "Descripción": "Comunidad, seguros, formalización", "Valor": f"{modelo['0110']:,.2f} €"},
        {"Casilla": "0111", "Descripción": "Servicios y suministros", "Valor": f"{modelo['0111']:,.2f} €"},
        {"Casilla": "0112", "Descripción": "Gastos jurídicos", "Valor": f"{modelo['0112']:,.2f} €"},
        {"Casilla": "0113", "Descripción": "Amortización (3%)", "Valor": f"{modelo['0113']:,.2f} €"},
        {"Casilla": "0149", "Descripción": "RENDIMIENTO NETO", "Valor": f"{modelo['0149']:,.2f} €"},
        {"Casilla": "0150", "Descripción": f"Reducción {modelo['reduccion_pct']}%", "Valor": f"-{modelo['0150']:,.2f} €"},
        {"Casilla": "0153", "Descripción": "Retenciones practicadas", "Valor": f"{modelo['0153']:,.2f} €"},
        {"Casilla": "0152", "Descripción": "BASE IMPONIBLE FINAL", "Valor": f"{modelo['0152']:,.2f} €"},
    ]

    df_casillas = pd.DataFrame(casillas_data)
    st.dataframe(df_casillas, use_container_width=True, hide_index=True, height=600)

    # Botón generar PDF
    st.markdown("---")
    if REPORTLAB_OK:
        if st.button("✅ Confirmar y Generar PDF", type="primary", use_container_width=True):
            pdf_buffer = generar_pdf_modelo100(f_fiscal, modelo)
            st.session_state["pdf_generado"] = pdf_buffer
            st.session_state["pdf_nombre"] = f"Modelo100_{inmueble_fiscal.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            st.success(f"✓ Modelo 100 confirmado para {inmueble_fiscal}")

        if "pdf_generado" in st.session_state and st.session_state.get("pdf_generado"):
            st.download_button(
                label="📥 Descargar PDF Modelo 100",
                data=st.session_state["pdf_generado"],
                file_name=st.session_state.get("pdf_nombre", "modelo100.pdf"),
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.warning("⚠️ Añade `reportlab` a requirements.txt para generar PDFs.")

    # Notas
    st.markdown('<div class="section-title">ℹ️ Información Importante</div>', unsafe_allow_html=True)
    cochera_txt = "Consolidada en arrendamiento principal" if f_fiscal.get("Cochera_Vinculada")=="S" else "Tributa independiente"
    st.markdown(f"""<div class="status-yellow"><b>⚠️ Antes de confirmar:</b><br>• Este pre-relleno es orientativo. Verifica con tu asesor fiscal.<br>• Cochera vinculada: {f_fiscal.get('Cochera_Vinculada','N')} — {cochera_txt}<br>• Modalidad: {f_fiscal.get('Tipo_Arrendamiento','Larga Duración')} — Reducción aplicable: {modelo['reduccion_pct']}%<br>• Los datos provienen de: Fichas de inmuebles + Diario Contable</div>""", unsafe_allow_html=True)

# ================================================================
# PANTALLA 7 — MACROFINANZAS (BLOQUE 5)
# Simulador amortización, stress test Euríbor, sensibilidad renta
# ================================================================
elif menu == "Macrofinanzas":
    st.markdown('<div class="brand-header">Macrofinanzas</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Simulador hipoteca · Stress test Euríbor · Análisis sensibilidad</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Simulador Amortización", "⚠️ Stress Test Euríbor", "📈 Sensibilidad Rentabilidad"])

    with tab1:
        st.markdown('<div class="section-title">Simulador de Amortización</div>', unsafe_allow_html=True)
        st.caption("Compara modalidades: cuota fija (método francés) vs capital fijo (método alemán)")
        inmuebles_con_hip = df_hip[df_hip["Principal"] > 0]["Inmueble"].tolist()
        if not inmuebles_con_hip:
            st.warning("⚠️ No hay hipotecas cargadas.")
        else:
            sel_hip = st.selectbox("Selecciona inmueble:", inmuebles_con_hip, key="hip_sel")
            hip_row = df_hip[df_hip["Inmueble"] == sel_hip].iloc[0]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                principal = st.number_input("Principal (€)", value=int(hip_row["Principal"]), min_value=0)
            with col2:
                tasa = st.number_input("Tasa (%)", value=float(hip_row["Tasa_Inicial"]), min_value=0.0, max_value=10.0, step=0.1)
            with col3:
                plazo = st.number_input("Plazo (años)", value=int(hip_row["Plazo_Años"]) if int(hip_row["Plazo_Años"]) > 0 else 20, min_value=1, max_value=50)
            with col4:
                modo = st.selectbox("Modalidad", ["Cuota Fija", "Capital Fijo"], key="modo_amort")
            modo_code = "cuota_fija" if modo == "Cuota Fija" else "capital_fijo"
            resultado = calcular_amortizacion(principal, tasa, plazo, modo_code)
            k1, k2, k3 = st.columns(3)
            cuota_val = resultado["cuota_mensual"]
            k1.metric("Cuota Mensual", f"{cuota_val:,.2f} €" if isinstance(cuota_val, float) else "Variable")
            k2.metric("Total Intereses", f"{resultado['total_intereses']:,.0f} €")
            k3.metric("Total Pagado", f"{resultado['total_pagado']:,.0f} €")
            tabla = resultado["tabla"].copy()
            tabla["Año"] = tabla["Mes"] // 12
            fig_amort = go.Figure()
            fig_amort.add_trace(go.Scatter(x=tabla["Año"], y=tabla["Pendiente"], mode="lines",
                name="Capital Pendiente", fill="tozeroy", line=dict(color=ACCENT)))
            fig_amort.add_trace(go.Scatter(x=tabla["Año"], y=tabla["Intereses"].cumsum(), mode="lines",
                name="Intereses Acumulados", line=dict(color=RED, dash="dash")))
            fig_amort.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10), height=300,
                font=dict(family="DM Sans", size=12), hovermode="x unified")
            st.plotly_chart(fig_amort, use_container_width=True)
            st.markdown("**Primeros y últimos 12 meses:**")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.caption("Primeros 12 meses")
                st.dataframe(tabla.head(12)[["Mes","Cuota","Capital","Intereses","Pendiente"]].style.format({
                    "Cuota":"{:,.2f} €","Capital":"{:,.2f} €","Intereses":"{:,.2f} €","Pendiente":"{:,.2f} €"
                }), use_container_width=True, hide_index=True)
            with col_t2:
                st.caption("Últimos 12 meses")
                st.dataframe(tabla.tail(12)[["Mes","Cuota","Capital","Intereses","Pendiente"]].style.format({
                    "Cuota":"{:,.2f} €","Capital":"{:,.2f} €","Intereses":"{:,.2f} €","Pendiente":"{:,.2f} €"
                }), use_container_width=True, hide_index=True)

    with tab2:
        st.markdown('<div class="section-title">Stress Test Euríbor</div>', unsafe_allow_html=True)
        st.caption("¿Cuánto sube tu cuota si el Euríbor sube 1%, 2% o 3%?")
        hips_variable = df_hip[(df_hip["Es_Variable"] == "S") & (df_hip["Principal"] > 0)]
        if hips_variable.empty:
            st.warning("⚠️ No hay hipotecas variables. Paseo del Salón tiene hipoteca variable de ejemplo.")
        else:
            sel_var = st.selectbox("Hipoteca variable:", hips_variable["Inmueble"].tolist(), key="hip_var")
            hip_var = hips_variable[hips_variable["Inmueble"] == sel_var].iloc[0]
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1:
                saldo = st.number_input("Saldo Actual (€)", value=int(hip_var["Saldo_Actual"]), min_value=0)
            with col_s2:
                margen = st.number_input("Margen (%)", value=float(hip_var["Margen"]), min_value=0.0, max_value=3.0, step=0.05)
            with col_s3:
                euribor_ahora = st.number_input("Euríbor Actual (%)", value=3.5, min_value=0.0, max_value=10.0, step=0.1)
            with col_s4:
                plazo_rest = st.number_input("Años Restantes", value=20, min_value=1, max_value=40)
            stress_results = stress_test_euribor(saldo, margen, euribor_ahora, plazo_rest)
            tabla_stress = []
            for escenario, datos in stress_results.items():
                tabla_stress.append({
                    "Escenario": escenario,
                    "Tasa Total": f"{datos['tasa_total']:.2f}%",
                    "Cuota Mensual": f"{datos['cuota_mensual']:,.2f} €",
                    "Cuota Anual": f"{datos['cuota_anual']:,.2f} €"
                })
            st.dataframe(pd.DataFrame(tabla_stress), use_container_width=True, hide_index=True)
            fig_stress = go.Figure(go.Bar(
                x=list(stress_results.keys()),
                y=[v["cuota_mensual"] for v in stress_results.values()],
                marker_color=[RED if k != "Euríbor actual" else ACCENT for k in stress_results.keys()],
                text=[f"{v['cuota_mensual']:,.0f} €" for v in stress_results.values()],
                textposition="outside"
            ))
            fig_stress.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10), height=300,
                font=dict(family="DM Sans", size=12), showlegend=False)
            st.plotly_chart(fig_stress, use_container_width=True)
            cuota_base = stress_results["Euríbor actual"]["cuota_mensual"]
            cuota_peligro = stress_results["Euríbor +2%"]["cuota_mensual"]
            impacto = cuota_peligro - cuota_base
            if impacto > 500:
                cls_r, msg_r = "status-red", f"🔴 RIESGO ALTO: Subida +2% = +{impacto:,.0f} €/mes. Considera pasar a tipo fijo."
            elif impacto > 200:
                cls_r, msg_r = "status-yellow", f"🟡 RIESGO MEDIO: Subida +2% = +{impacto:,.0f} €/mes. Monitorear."
            else:
                cls_r, msg_r = "status-green", f"🟢 RIESGO BAJO: Subida +2% = +{impacto:,.0f} €/mes. Asumible."
            st.markdown(f'<div class="{cls_r}">{msg_r}</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-title">Análisis de Sensibilidad</div>', unsafe_allow_html=True)
        st.caption("Cómo cambia la rentabilidad si subes o bajas la renta")
        sel_sens = st.selectbox("Inmueble:", df_inm["Nombre"].tolist(), key="sens_inmueble")
        row_sens = df_inm[df_inm["Nombre"] == sel_sens].iloc[0]
        gastos_esp = df_mov[(df_mov["Apartamento"] == sel_sens) & (df_mov["Tipo"] == "Gasto")]["Importe"].sum()
        comunidad_esp = float(row_sens.get("Comunidad", 0)) * 12
        gastos_anuales_sens = gastos_esp + comunidad_esp
        col_var1, col_var2 = st.columns(2)
        with col_var1:
            renta_sens = st.number_input("Renta Mensual (€)", value=float(row_sens["Renta"]), min_value=0.0)
        with col_var2:
            variaciones = st.multiselect("Variaciones a analizar (%)",
                options=[-15, -10, -5, 0, 5, 10, 15], default=[-10, -5, 0, 5, 10])
        if variaciones:
            tabla_sens = analisis_sensibilidad_renta(renta_sens, gastos_anuales_sens, float(row_sens["Valor_Construccion"]), variaciones)
            st.dataframe(tabla_sens, use_container_width=True, hide_index=True)
            datos_graf = []
            for var_pct in sorted(variaciones):
                nueva_renta = renta_sens * (1 + var_pct / 100)
                neto = (nueva_renta * 12 - gastos_anuales_sens)
                rent = (neto / float(row_sens["Valor_Construccion"]) * 100) if float(row_sens["Valor_Construccion"]) > 0 else 0
                datos_graf.append({"var": var_pct, "rent": rent})
            df_graf = pd.DataFrame(datos_graf)
            fig_sens = go.Figure(go.Scatter(x=df_graf["var"], y=df_graf["rent"],
                mode="lines+markers", line=dict(color=ACCENT, width=3),
                marker=dict(size=10), fill="tozeroy"))
            fig_sens.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10), height=300,
                xaxis_title="Variación Renta (%)", yaxis_title="Rentabilidad Neta (%)",
                font=dict(family="DM Sans", size=12))
            st.plotly_chart(fig_sens, use_container_width=True)

# ================================================================
# PANTALLA 8 — DATOS DE LA CARTERA
# Editor maestro de inmuebles y copias de seguridad
# ================================================================
elif menu == "Datos de la Cartera":
    st.markdown('<div class="brand-header">Datos de la Cartera</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Parámetros maestros y copias de seguridad</div>', unsafe_allow_html=True)
    st.info("ℹ️ Campos fiscales: NIF_Inquilino · Intereses_Hipoteca · IBI_Anual · Seguro_Anual · etc.")
    col_cfg = {
        "Tipo_Arrendamiento": st.column_config.SelectboxColumn("Tipo Arrend.",options=["Larga Duración","Temporada","Vacacional"],required=True),
        "Cochera_Vinculada": st.column_config.SelectboxColumn("Cochera Vinc.",options=["S","N"],required=True),
        "Zona_Tensionada": st.column_config.SelectboxColumn("Zona Tensión",options=["S","N"],required=True),
        "Estado": st.column_config.SelectboxColumn("Estado",options=["Reformado","Bueno","Regular"],required=True),
        "Mobiliario": st.column_config.SelectboxColumn("Mobiliario",options=["S","N"],required=True),
        "Parking": st.column_config.SelectboxColumn("Parking",options=["S","N"],required=True),
        "IBI_Anual": st.column_config.NumberColumn("IBI/año",format="%.0f €"),
        "Seguro_Anual": st.column_config.NumberColumn("Seguro/año",format="%.0f €"),
        "Intereses_Hipoteca": st.column_config.NumberColumn("Intereses Hip.",format="%.0f €"),
    }
    df_ed = st.data_editor(df_inm,num_rows="dynamic",use_container_width=True,hide_index=True,column_config=col_cfg)
    if st.button("✅ Actualizar Cartera"):
        df_ed.to_csv(DB_INM,index=False); st.success("✓ Datos actualizados."); st.rerun()
    st.markdown('<div class="section-title">Copias de Seguridad</div>', unsafe_allow_html=True)
    b1,b2=st.columns(2)
    with b1:
        with open(DB_INM,"rb") as fi: st.download_button("📥 Descargar Inmuebles",fi,"nolasco_inmuebles.csv","text/csv")
    with b2:
        with open(DB_MOV,"rb") as fm: st.download_button("📥 Descargar Movimientos",fm,"nolasco_movimientos.csv","text/csv")
