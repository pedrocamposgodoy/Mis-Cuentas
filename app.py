import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
from datetime import datetime, date

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

DB_INM = "nolasco_inmuebles_v11.csv"
DB_MOV = "nolasco_movimientos_v11.csv"

# COLUMNAS ACTUALIZADAS CON CAMPOS FISCALES
COLS_INM = [
    "Nombre","Inquilino","Renta","Renta_Mercado","Comunidad","Valor_Construccion",
    "Año_Reforma","Año_Construccion","Mobiliario","Tipo","Ref_Catastral","Titular",
    "M2_Construidos","Habitaciones","CP","Planta","Parking","Estado",
    "Tipo_Arrendamiento","Cochera_Vinculada","Zona_Tensionada",
    "Fecha_Inicio_Contrato","Fecha_Vencimiento_Contrato",
    # NUEVOS CAMPOS FISCALES
    "NIF_Inquilino","Intereses_Hipoteca","IBI_Anual","Seguro_Anual",
    "Gastos_Juridicos","Retenciones_IRPF","Gastos_Formalizacion",
    "Gastos_Pendientes_Años_Ant","Servicios_Suministros"
]

def inicializar_bd():
    if not os.path.exists(DB_INM):
        pd.DataFrame([
            {
                "Nombre":"Casa Abarqueros","Inquilino":"Victor Aguiluz","Renta":2200.0,"Renta_Mercado":2600.0,"Comunidad":193.76,
                "Valor_Construccion":150000.0,"Año_Reforma":2018,"Año_Construccion":1975,"Mobiliario":"S","Tipo":"Casa",
                "Ref_Catastral":"00XX0001","Titular":"Pedro Nolasco","M2_Construidos":180,"Habitaciones":5,"CP":"18001",
                "Planta":0,"Parking":"N","Estado":"Reformado","Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N",
                "Zona_Tensionada":"N","Fecha_Inicio_Contrato":"2022-01-01","Fecha_Vencimiento_Contrato":"2027-01-01",
                "NIF_Inquilino":"12345678A","Intereses_Hipoteca":0,"IBI_Anual":800,"Seguro_Anual":250,
                "Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0
            },
            {
                "Nombre":"Paseo del Salón","Inquilino":"Pool Despachos","Renta":1591.8,"Renta_Mercado":1650.0,"Comunidad":175.18,
                "Valor_Construccion":120000.0,"Año_Reforma":2020,"Año_Construccion":1990,"Mobiliario":"N","Tipo":"Piso",
                "Ref_Catastral":"00XX0002","Titular":"Pedro Nolasco","M2_Construidos":130,"Habitaciones":4,"CP":"18005",
                "Planta":3,"Parking":"S","Estado":"Bueno","Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"S",
                "Zona_Tensionada":"N","Fecha_Inicio_Contrato":"2021-06-01","Fecha_Vencimiento_Contrato":"2026-06-01",
                "NIF_Inquilino":"B87654321","Intereses_Hipoteca":0,"IBI_Anual":600,"Seguro_Anual":200,
                "Gastos_Juridicos":0,"Retenciones_IRPF":286.0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0
            },
            {
                "Nombre":"Huerto Unidad 1","Inquilino":"Alain","Renta":660.0,"Renta_Mercado":800.0,"Comunidad":74.62,
                "Valor_Construccion":45000.0,"Año_Reforma":2022,"Año_Construccion":2005,"Mobiliario":"S","Tipo":"Piso",
                "Ref_Catastral":"00XX0003","Titular":"Pedro Nolasco","M2_Construidos":60,"Habitaciones":2,"CP":"18008",
                "Planta":1,"Parking":"N","Estado":"Reformado","Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N",
                "Zona_Tensionada":"S","Fecha_Inicio_Contrato":"2023-03-01","Fecha_Vencimiento_Contrato":"2028-03-01",
                "NIF_Inquilino":"87654321B","Intereses_Hipoteca":0,"IBI_Anual":300,"Seguro_Anual":150,
                "Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0
            },
            {
                "Nombre":"Huerto Unidad 2","Inquilino":"Laura/Alex","Renta":800.0,"Renta_Mercado":800.0,"Comunidad":74.62,
                "Valor_Construccion":45000.0,"Año_Reforma":2022,"Año_Construccion":2005,"Mobiliario":"S","Tipo":"Piso",
                "Ref_Catastral":"00XX0004","Titular":"Pedro Nolasco","M2_Construidos":65,"Habitaciones":2,"CP":"18008",
                "Planta":2,"Parking":"N","Estado":"Reformado","Tipo_Arrendamiento":"Temporada","Cochera_Vinculada":"N",
                "Zona_Tensionada":"S","Fecha_Inicio_Contrato":"2024-09-01","Fecha_Vencimiento_Contrato":"2025-08-31",
                "NIF_Inquilino":"23456789C","Intereses_Hipoteca":0,"IBI_Anual":300,"Seguro_Anual":150,
                "Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0
            },
            {
                "Nombre":"Huerto Unidad 3","Inquilino":"Jose Manuel","Renta":850.0,"Renta_Mercado":800.0,"Comunidad":74.63,
                "Valor_Construccion":45000.0,"Año_Reforma":2021,"Año_Construccion":2005,"Mobiliario":"S","Tipo":"Piso",
                "Ref_Catastral":"00XX0005","Titular":"Pedro Nolasco","M2_Construidos":68,"Habitaciones":3,"CP":"18008",
                "Planta":3,"Parking":"N","Estado":"Bueno","Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N",
                "Zona_Tensionada":"N","Fecha_Inicio_Contrato":"2022-11-01","Fecha_Vencimiento_Contrato":"2027-11-01",
                "NIF_Inquilino":"34567890D","Intereses_Hipoteca":0,"IBI_Anual":300,"Seguro_Anual":150,
                "Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0
            },
            {
                "Nombre":"Huerto Unidad 4","Inquilino":"Pendiente","Renta":600.0,"Renta_Mercado":800.0,"Comunidad":74.62,
                "Valor_Construccion":45000.0,"Año_Reforma":2024,"Año_Construccion":2005,"Mobiliario":"S","Tipo":"Piso",
                "Ref_Catastral":"00XX0006","Titular":"Pedro Nolasco","M2_Construidos":62,"Habitaciones":2,"CP":"18008",
                "Planta":4,"Parking":"N","Estado":"Reformado","Tipo_Arrendamiento":"Vacacional","Cochera_Vinculada":"N",
                "Zona_Tensionada":"N","Fecha_Inicio_Contrato":"2025-01-01","Fecha_Vencimiento_Contrato":"2026-12-31",
                "NIF_Inquilino":"","Intereses_Hipoteca":0,"IBI_Anual":300,"Seguro_Anual":150,
                "Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0
            },
        ]).to_csv(DB_INM, index=False)
    else:
        df = pd.read_csv(DB_INM)
        defaults = {
            "Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N","Zona_Tensionada":"N",
            "Fecha_Inicio_Contrato":"2022-01-01","Fecha_Vencimiento_Contrato":"2027-01-01",
            "NIF_Inquilino":"","Intereses_Hipoteca":0,"IBI_Anual":0,"Seguro_Anual":0,
            "Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,
            "Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0
        }
        for c in COLS_INM:
            if c not in df.columns:
                df[c] = defaults.get(c,"")
        df.to_csv(DB_INM, index=False)

    if not os.path.exists(DB_MOV):
        pd.DataFrame([
            {"Fecha":"2026-04-01","Apartamento":"Casa Abarqueros","Concepto":"Renta Mensual","Categoría":"Ingresos","Tipo":"Ingreso","Importe":2200.00,"Deducible":"N"},
            {"Fecha":"2026-04-01","Apartamento":"Casa Abarqueros","Concepto":"Comunidad","Categoría":"Comunidad","Tipo":"Gasto","Importe":193.76,"Deducible":"S"},
        ]).to_csv(DB_MOV, index=False)

inicializar_bd()
df_inm = pd.read_csv(DB_INM)
df_mov = pd.read_csv(DB_MOV)

if "menu" not in st.session_state:      st.session_state.menu = "Torre de Control"
if "ficha_sel" not in st.session_state: st.session_state.ficha_sel = None

PAGES = [
    ("📊","Torre de Control"),
    ("🏠","Fichas (Benchmark)"),
    ("🤖","Auditoría IA"),
    ("📝","Diario Contable"),
    ("⚡","Suministros"),
    ("💰","Fiscalidad"),
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

# ─── HELPERS ─────────────────────────────────
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
    """Añade registros nuevos al CSV de movimientos"""
    df_actual = pd.read_csv(DB_MOV)
    df_nuevos = pd.DataFrame(nuevos)
    df_final  = pd.concat([df_actual, df_nuevos], ignore_index=True)
    df_final.to_csv(DB_MOV, index=False)

def parsear_ingresos(texto, df_inm_local):
    """Detecta qué inmuebles han pagado a partir de texto libre"""
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

def calcular_dias_arrendado(row):
    """Calcula días arrendado en el año actual"""
    try:
        inicio = datetime.strptime(str(row.get("Fecha_Inicio_Contrato","")), "%Y-%m-%d").date()
        fin    = datetime.strptime(str(row.get("Fecha_Vencimiento_Contrato","")), "%Y-%m-%d").date()
        hoy    = date.today()
        año_actual = hoy.year
        
        inicio_año = date(año_actual, 1, 1)
        fin_año    = date(año_actual, 12, 31)
        
        inicio_efectivo = max(inicio, inicio_año)
        fin_efectivo    = min(fin, fin_año, hoy)
        
        if inicio_efectivo > fin_efectivo:
            return 0
        return (fin_efectivo - inicio_efectivo).days + 1
    except:
        return 365

def calcular_modelo_100(row, df_mov_local):
    """Calcula todas las casillas del Modelo 100 para un inmueble"""
    
    # CASILLA 0101: Días arrendado
    dias_arrendado = calcular_dias_arrendado(row)
    
    # CASILLA 0102: Ingresos íntegros
    renta_mensual = float(row.get("Renta", 0))
    ingresos_integros = renta_mensual * 12
    
    # CASILLA 0105: Intereses hipoteca
    intereses = float(row.get("Intereses_Hipoteca", 0))
    
    # CASILLA 0106: Reparación y conservación
    gastos_reparacion = df_mov_local[
        (df_mov_local["Apartamento"] == row["Nombre"]) &
        (df_mov_local["Tipo"] == "Gasto") &
        (df_mov_local["Categoría"].isin(["Mantenimiento", "Reparación"]))
    ]["Importe"].sum()
    
    # CASILLA 0108: IBI y tasas
    ibi_anual = float(row.get("IBI_Anual", 0))
    
    # CASILLA 0110: Comunidad + seguros + formalización
    comunidad_anual = float(row.get("Comunidad", 0)) * 12
    seguro_anual = float(row.get("Seguro_Anual", 0))
    formalizacion = float(row.get("Gastos_Formalizacion", 0))
    casilla_0110 = comunidad_anual + seguro_anual + formalizacion
    
    # CASILLA 0111: Servicios y suministros
    servicios = float(row.get("Servicios_Suministros", 0))
    
    # CASILLA 0112: Gastos jurídicos
    gastos_juridicos = float(row.get("Gastos_Juridicos", 0))
    
    # CASILLA 0113: Amortización (3% valor construcción)
    valor_construccion = float(row.get("Valor_Construccion", 0))
    amortizacion = valor_construccion * 0.03
    
    # SUMA TOTAL GASTOS
    total_gastos = (intereses + gastos_reparacion + ibi_anual + casilla_0110 + 
                   servicios + gastos_juridicos + amortizacion)
    
    # CASILLA 0149: Rendimiento neto
    rendimiento_neto = ingresos_integros - total_gastos
    
    # CASILLA 0150: Reducción por modalidad
    tipo_arrendamiento = str(row.get("Tipo_Arrendamiento", "Larga Duración"))
    if tipo_arrendamiento == "Larga Duración":
        reduccion_pct = 0.60
    else:
        reduccion_pct = 0.00
    
    reduccion_importe = rendimiento_neto * reduccion_pct
    
    # CASILLA 0153: Retenciones
    retenciones = float(row.get("Retenciones_IRPF", 0))
    
    # CASILLA 0154: Rendimiento neto reducido
    rendimiento_final = rendimiento_neto - reduccion_importe
    
    return {
        "0062_0075": f"Ref: {row.get('Ref_Catastral', 'N/A')}",
        "0076": "A (Arrendamiento)",
        "0100": "SÍ" if tipo_arrendamiento == "Larga Duración" else "NO",
        "0101": dias_arrendado,
        "0102": round(ingresos_integros, 2),
        "0105": round(intereses, 2),
        "0106": round(gastos_reparacion, 2),
        "0108": round(ibi_anual, 2),
        "0110": round(casilla_0110, 2),
        "0111": round(servicios, 2),
        "0112": round(gastos_juridicos, 2),
        "0113": round(amortizacion, 2),
        "0149": round(rendimiento_neto, 2),
        "0150": round(reduccion_importe, 2),
        "0153": round(retenciones, 2),
        "0154": round(rendimiento_final, 2),
        "reduccion_pct": int(reduccion_pct * 100)
    }

# ══════════════════════════════════════════════
# TORRE DE CONTROL
# ══════════════════════════════════════════════
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
            st.markdown(f"""
<div class="asset-card">
  <div class="asset-top" style="background:{COLOR_TOPS[i%len(COLOR_TOPS)]};"></div>
  <div class="asset-body">
    <div class="asset-name">{row["Nombre"]}{zt}</div>
    <div class="asset-tenant">{row["Inquilino"]}</div>
    <div class="asset-row"><span class="asset-ml">Renta</span><span class="asset-mv" style="color:{GREEN};">+{row["Renta"]:,.0f}€</span></div>
    <div class="asset-row"><span class="asset-ml">Gastos</span><span class="asset-mv" style="color:{RED};">−{gastos_u:,.0f}€</span></div>
    <div class="asset-div"></div>
    <div class="asset-row"><span class="asset-ml">Neto</span><span class="asset-neto">{neto_u:,.0f}€</span></div>
    <span class="pill {pill_cls}">{desv:+.1f}% mercado</span>
  </div>
</div>""", unsafe_allow_html=True)
            if st.button("→ Ver ficha", key=f"card_{i}", use_container_width=True):
                st.session_state.menu = "Fichas (Benchmark)"
                st.session_state.ficha_sel = row["Nombre"]
                st.rerun()

    col_l,col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-title">Composición de Rentas</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Bar(x=df_inm["Renta"],y=df_inm["Nombre"],orientation="h",
            marker_color=COLOR_TOPS[:len(df_inm)],
            text=[f"{r:,.0f} €" for r in df_inm["Renta"]],textposition="outside"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10,r=60,t=10,b=10),height=280,
            xaxis=dict(showgrid=False,visible=False),yaxis=dict(showgrid=False),
            font=dict(family="DM Sans",size=12))
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

# ══════════════════════════════════════════════
# FICHAS BENCHMARK
# ══════════════════════════════════════════════
elif menu == "Fichas (Benchmark)":
    st.markdown('<div class="brand-header">Benchmark y Análisis Fiscal</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Análisis de mercado · Comparativa fiscal por modalidad</div>', unsafe_allow_html=True)

    default_idx = df_inm["Nombre"].tolist().index(st.session_state.ficha_sel) \
        if st.session_state.ficha_sel in df_inm["Nombre"].tolist() else 0
    sel = st.selectbox("Inmueble a auditar:", df_inm["Nombre"].tolist(), index=default_idx)
    st.session_state.ficha_sel = sel
    f = df_inm[df_inm["Nombre"]==sel].iloc[0]

    renta_act = f["Renta"]
    renta_mer = tasacion(f)
    desv      = (renta_act-renta_mer)/renta_mer*100
    perdida_m = max(0,renta_mer-renta_act)
    perdida_a = perdida_m*12
    df_gf     = df_mov[(df_mov["Apartamento"]==sel)&(df_mov["Tipo"]=="Gasto")&(df_mov["Categoría"]!="Comunidad")]
    gastos_u  = f["Comunidad"]+df_gf["Importe"].sum()
    rent_bruta= (renta_act*12/f["Valor_Construccion"]*100) if f["Valor_Construccion"]>0 else 0
    rent_neta = ((renta_act-gastos_u)*12/f["Valor_Construccion"]*100) if f["Valor_Construccion"]>0 else 0
    tipo_arr  = str(f.get("Tipo_Arrendamiento","Larga Duración"))
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
        fig_bar = go.Figure(go.Bar(x=["Renta Actual","Renta Tasada"],y=[renta_act,renta_mer],
            marker_color=[ACCENT,"#D0DFF0"],text=[f"{renta_act:,.0f} €",f"{renta_mer:,.0f} €"],
            textposition="outside",width=0.4))
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10,r=10,t=10,b=10),height=240,
            yaxis=dict(showgrid=False,visible=False),xaxis=dict(showgrid=False),
            font=dict(family="DM Sans",size=13),showlegend=False)
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
    rto_neto    = (renta_act-gastos_u)*12
    tipo_irpf   = 0.45
    modalidades = {"Larga Duración":{"reduccion":0.60,"iva":False},"Temporada":{"reduccion":0.00,"iva":False},"Vacacional":{"reduccion":0.00,"iva":True}}
    cf1,cf2,cf3 = st.columns(3)
    cols_fiscal = [cf1,cf2,cf3]
    mejor_mod,mejor_rn = None,-99999

    for idx,(mod,params) in enumerate(modalidades.items()):
        red      = params["reduccion"]
        impuesto = max(0, rto_neto*(1-red)*tipo_irpf)
        rn_real  = (rto_neto-impuesto)/f["Valor_Construccion"]*100 if f["Valor_Construccion"]>0 else 0
        if rn_real>mejor_rn: mejor_rn=rn_real; mejor_mod=mod
        es_actual = (mod==tipo_arr)
        borde = f"border:2px solid {ACCENT};" if es_actual else f"border:1px solid {BORDER};"
        iva_txt = "<br><span style='font-size:0.7rem;color:#854F0B;'>⚠️ Puede llevar IVA</span>" if params["iva"] else ""
        red_txt = f"Reducción IRPF: <b>{int(red*100)}%</b>" if red>0 else "Sin reducción fiscal"
        badge   = "<div style='margin-top:8px;font-size:0.7rem;background:#EAF3DE;color:#3B6D11;padding:3px 8px;border-radius:20px;'>✅ Modalidad actual</div>" if es_actual else ""
        cols_fiscal[idx].markdown(f"""
<div style="background:{CARD_BG};{borde}border-radius:10px;padding:1.1rem;text-align:center;">
  <div style="font-size:0.72rem;font-weight:600;color:{TEXT_SEC};text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">{mod}</div>
  <div style="font-family:'DM Serif Display',serif;font-size:1.8rem;color:{ACCENT if es_actual else TEXT_PRI};">{rn_real:.1f}%</div>
  <div style="font-size:0.7rem;color:{TEXT_SEC};margin-top:4px;">Rent. neta real/año</div>
  <div style="font-size:0.75rem;color:{TEXT_PRI};margin-top:8px;">{red_txt}{iva_txt}</div>
  <div style="font-size:0.7rem;color:{RED};margin-top:4px;">Impuesto est.: {impuesto:,.0f} €/año</div>
  {badge}
</div>""", unsafe_allow_html=True)

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
    s1.metric("Nueva Renta",      f"{nueva_renta:,.0f} €/mes", delta=f"{ganancia_m:+.0f} €")
    s2.metric("Impacto Anual",    f"{ganancia_a:+,.0f} €/año")
    s3.metric("Nueva Rent. Neta", f"{nueva_neta:.1f}%", delta=f"{nueva_neta-rent_neta:+.1f}%")

    st.markdown('<div class="section-title">Comparativa de Activos — Renta vs Tasación</div>', unsafe_allow_html=True)
    rt = [tasacion(r) for _,r in df_inm.iterrows()]
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name="Renta Actual",x=df_inm["Nombre"],y=df_inm["Renta"],marker_color=ACCENT,text=[f"{r:,.0f}€" for r in df_inm["Renta"]],textposition="outside"))
    fig_comp.add_trace(go.Bar(name="Renta Tasada",x=df_inm["Nombre"],y=rt,marker_color="#D0DFF0",text=[f"{r:,.0f}€" for r in rt],textposition="outside"))
    fig_comp.update_layout(barmode="group",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10,r=10,t=10,b=10),height=300,
        yaxis=dict(showgrid=False,visible=False),xaxis=dict(showgrid=False),
        font=dict(family="DM Sans",size=12),
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    st.plotly_chart(fig_comp,use_container_width=True)

    st.markdown('<div class="section-title">Análisis de Gastos Reales</div>', unsafe_allow_html=True)
    res = pd.concat([pd.DataFrame([{"Concepto":"Comunidad","Importe":f["Comunidad"],"Deducible":"S"}]),df_gf[["Concepto","Importe","Deducible"]]])
    st.dataframe(res.style.format({"Importe":"{:,.2f} €"}),hide_index=True,use_container_width=True)

# ══════════════════════════════════════════════
# AUDITORÍA IA
# ══════════════════════════════════════════════
elif menu == "Auditoría IA":
    st.markdown('<div class="brand-header">Auditoría de Mantenimiento</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Planificación de reformas · Costos e impacto por plazo</div>', unsafe_allow_html=True)

    datos_mantenimiento = {
        "Casa Abarqueros": {
            "urgente": {"total":4500,"items":[("Revisión estructura",2500,0.55),("Pintura fachada",1500,0.33),("Canalones",500,0.12)]},
            "medio":   {"total":12000,"items":[("Tuberías",8000,0.67),("Electricidad",3500,0.29),("Calderas",600,0.05)]},
            "largo":   {"total":8000,"items":[("Ventanas",5000,0.62),("Aislamiento",2500,0.31),("Cubierta",500,0.06)]}
        },
        "Paseo del Salón": {
            "urgente": {"total":3000,"items":[("Pinturas",1500,0.5),("Fontanería menor",1000,0.33),("Mantenimiento",500,0.17)]},
            "medio":   {"total":7000,"items":[("Tuberías",4000,0.57),("Electricidad",2500,0.36),("Otros",500,0.07)]},
            "largo":   {"total":4500,"items":[("Ventanas",2500,0.56),("Aislamiento",1500,0.33),("Cubierta",500,0.11)]}
        },
        "Huerto Unidad 1": {
            "urgente": {"total":2000,"items":[("Pintura",1000,0.5),("Reparaciones",800,0.4),("Otros",200,0.1)]},
            "medio":   {"total":4500,"items":[("Tuberías",2500,0.56),("Electricidad",1500,0.33),("Otros",500,0.11)]},
            "largo":   {"total":3000,"items":[("Ventanas",1800,0.6),("Aislamiento",1000,0.33),("Cubierta",200,0.07)]}
        },
        "Huerto Unidad 2": {
            "urgente": {"total":2000,"items":[("Pintura",1000,0.5),("Reparaciones",800,0.4),("Otros",200,0.1)]},
            "medio":   {"total":4500,"items":[("Tuberías",2500,0.56),("Electricidad",1500,0.33),("Otros",500,0.11)]},
            "largo":   {"total":3000,"items":[("Ventanas",1800,0.6),("Aislamiento",1000,0.33),("Cubierta",200,0.07)]}
        },
        "Huerto Unidad 3": {
            "urgente": {"total":1500,"items":[("Pintura",800,0.53),("Reparaciones",600,0.4),("Otros",100,0.07)]},
            "medio":   {"total":4000,"items":[("Tuberías",2300,0.575),("Electricidad",1400,0.35),("Otros",300,0.075)]},
            "largo":   {"total":2500,"items":[("Ventanas",1500,0.6),("Aislamiento",800,0.32),("Cubierta",200,0.08)]}
        },
        "Huerto Unidad 4": {
            "urgente": {"total":1000,"items":[("Pintura",600,0.6),("Reparaciones",300,0.3),("Otros",100,0.1)]},
            "medio":   {"total":3500,"items":[("Tuberías",2000,0.57),("Electricidad",1200,0.34),("Otros",300,0.09)]},
            "largo":   {"total":2000,"items":[("Ventanas",1200,0.6),("Aislamiento",600,0.3),("Cubierta",200,0.1)]}
        }
    }

    inmueble_sel_aud = st.selectbox("Selecciona inmueble a auditar:", df_inm["Nombre"].tolist(), key="aud_inmueble")
    
    if inmueble_sel_aud in datos_mantenimiento:
        row_aud = df_inm[df_inm["Nombre"]==inmueble_sel_aud].iloc[0]
        año_actual = datetime.now().year
        ant = año_actual - int(row_aud.get("Año_Reforma", año_actual))
        
        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        col_a1.metric("Construcción", int(row_aud.get("Año_Construccion", "—")))
        col_a2.metric("Última reforma", int(row_aud.get("Año_Reforma", "—")))
        col_a3.metric("Antigüedad", f"{ant} años")
        col_a4.metric("Estado", row_aud.get("Estado", "—"))
        
        st.markdown("---")
        
        datos_aud = datos_mantenimiento[inmueble_sel_aud]
        total_presupuesto = datos_aud["urgente"]["total"] + datos_aud["medio"]["total"] + datos_aud["largo"]["total"]
        
        def mostrar_seccion(plazo_label, plazo_key, emoji, color_hex, datos_plazo):
            col_sec1, col_sec2 = st.columns([3, 1])
            with col_sec1:
                st.markdown(f"### {emoji} {plazo_label}")
            with col_sec2:
                st.markdown(f'<div style="font-family:\'DM Serif Display\',serif;font-size:1.5rem;color:{color_hex};font-weight:600;">{datos_plazo["total"]:,.0f}€</div>', unsafe_allow_html=True)
            
            cols_items = st.columns(len(datos_plazo["items"]))
            for idx, (nombre, monto, pct) in enumerate(datos_plazo["items"]):
                with cols_items[idx]:
                    st.markdown(f"""
<div style="background:{color_hex};height:50px;border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:white;font-size:0.7rem;font-weight:600;padding:0.4rem;text-align:center;margin-bottom:0.5rem;">
  <span style="font-size:0.65rem;">{nombre}</span>
  <span style="font-size:0.75rem;margin-top:2px;">{monto:,.0f}€</span>
</div>""", unsafe_allow_html=True)
                    st.caption(f"{pct*100:.0f}%")
            
            desglose = " • ".join([f"{n} ({m:,.0f}€)" for n, m, _ in datos_plazo["items"]])
            st.markdown(f'<div style="font-size:0.8rem;color:{TEXT_SEC};margin-top:0.5rem;">📊 {desglose}</div>', unsafe_allow_html=True)
            st.markdown("---")
        
        mostrar_seccion("🔴 URGENTE (0-6 meses)", "urgente", "🔴", RED, datos_aud["urgente"])
        mostrar_seccion("🟠 MEDIO (6-18 meses)", "medio", "🟠", AMBER, datos_aud["medio"])
        mostrar_seccion("🟢 LARGO (18+ meses)", "largo", "🟢", GREEN, datos_aud["largo"])
        
        st.markdown('<div class="section-title">💰 Resumen Presupuestario</div>', unsafe_allow_html=True)
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Inversión Total", f"{total_presupuesto:,.0f} €", "todas las categorías")
        col_res2.metric("Urgente + Medio", f"{datos_aud['urgente']['total'] + datos_aud['medio']['total']:,.0f} €", "próximos 18 meses")
        col_res3.metric("% sobre valor", f"{total_presupuesto/row_aud['Valor_Construccion']*100:.1f}%", f"de {row_aud['Valor_Construccion']:,.0f}€")
        
        st.markdown('<div class="section-title">📋 Recomendaciones</div>', unsafe_allow_html=True)
        if ant >= 8:
            st.markdown(f'<div class="status-red"><b>🚨 Reforma muy antigua</b><br>Con {ant} años desde la última reforma, las intervenciones urgentes son críticas para mantener el valor del inmueble.</div>', unsafe_allow_html=True)
        elif ant >= 5:
            st.markdown(f'<div class="status-yellow"><b>⚠️ Reforma antigua</b><br>Con {ant} años, planifica presupuesto para las intervenciones del plazo medio en los próximos 12 meses.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-green"><b>✅ Reforma reciente</b><br>Con {ant} años, el inmueble está en buen estado. Mantén un seguimiento preventivo.</div>', unsafe_allow_html=True)
        
        tipo_v, msg_v = alerta_vencimiento(row_aud)
        if tipo_v in ("vencido", "urgente", "aviso") and ant >= 3:
            st.markdown(f'<div class="status-yellow" style="margin-top:0.8rem;"><b>🎯 Oportunidad de Negociación:</b><br>El contrato {msg_v.lower()}. Con {ant} años desde reforma, este es el momento óptimo para renegociar renta + reformas con el inquilino.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# DIARIO CONTABLE
# ══════════════════════════════════════════════
elif menu == "Diario Contable":
    st.markdown('<div class="brand-header">Diario Contable</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Registro de operaciones · Ingresos · Gastos</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Registro de Operaciones", "📥 Registrar Ingresos", "📤 Registrar Gastos"])

    with tab1:
        l_inm = df_inm["Nombre"].tolist()+["Global"]
        l_cat = ["Ingresos","Financiero","Tributario","Suministros","Seguros","Mantenimiento","Estructura","Comunidad","Otros"]
        l_con = ["Renta Mensual","Hipoteca (Intereses)","Hipoteca (Capital)","IBI","Comunidad Ordinaria","Seguro Hogar","Seguro Vida","Luz","Agua","Reparación","Sueldo Pedro"]
        config = {
            "Apartamento": st.column_config.SelectboxColumn("Inmueble",  options=l_inm,required=True),
            "Concepto":    st.column_config.SelectboxColumn("Concepto",  options=l_con,required=True),
            "Categoría":   st.column_config.SelectboxColumn("Categoría", options=l_cat,required=True),
            "Tipo":        st.column_config.SelectboxColumn("Tipo",      options=["Ingreso","Gasto"],required=True),
            "Deducible":   st.column_config.SelectboxColumn("Fiscal",    options=["S","N"],required=True),
            "Importe":     st.column_config.NumberColumn("Importe (€)",  format="%.2f",min_value=0),
        }
        df_ed = st.data_editor(df_mov,num_rows="dynamic",use_container_width=True,hide_index=True,column_config=config)
        t_ing = df_ed[df_ed["Tipo"]=="Ingreso"]["Importe"].sum()
        t_gas = df_ed[df_ed["Tipo"]=="Gasto"]["Importe"].sum()
        m1,m2,m3 = st.columns(3)
        m1.metric("Ingresos Registrados", f"{t_ing:,.2f} €")
        m2.metric("Gastos Registrados",   f"−{t_gas:,.2f} €")
        m3.metric("Balance Total",        f"{t_ing-t_gas:,.2f} €")
        if st.button("💾 Guardar Cambios", key="guardar_tabla"):
            df_ed.to_csv(DB_MOV,index=False); st.success("✓ Operaciones guardadas."); st.rerun()

    with tab2:
        st.markdown("### 📥 Registrar Ingresos del Mes")
        st.markdown("Escribe de forma natural quién ha pagado y quién no")
        st.caption('Ejemplo: "Todos han pagado menos Abarqueros" · "Solo pagaron Huerto 1 y Salón"')

        texto_ingresos = st.text_area(
            "¿Quién ha pagado este mes?",
            placeholder="Todos han pagado menos Abarqueros...",
            height=90
        )

        if st.button("🔄 Procesar ingresos", type="primary", key="procesar_ing"):
            if texto_ingresos.strip():
                registros = parsear_ingresos(texto_ingresos, df_inm)
                if registros:
                    st.markdown("---")
                    st.markdown("**✓ Registros detectados — revisa antes de guardar:**")
                    for r in registros:
                        color  = "#EDF7F1" if r["Estado"]=="Cobrado" else "#FDECEA"
                        bcolor = GREEN if r["Estado"]=="Cobrado" else RED
                        icon   = "✅" if r["Estado"]=="Cobrado" else "⏳"
                        st.markdown(f"""
<div style="background:{color};border-left:4px solid {bcolor};padding:0.8rem 1rem;border-radius:6px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;">
  <div>
    <span style="font-weight:600;font-size:0.88rem;">{icon} {r['Apartamento']}</span>
    <span style="font-size:0.75rem;color:{TEXT_SEC};margin-left:8px;">{r['Concepto']}</span>
  </div>
  <span style="font-family:'DM Serif Display',serif;font-size:1.1rem;color:{bcolor};">{r['Importe']:,.0f} €</span>
</div>""", unsafe_allow_html=True)

                    st.session_state["ingresos_pendientes"] = registros
            else:
                st.warning("Escribe una descripción primero")

        if "ingresos_pendientes" in st.session_state and st.session_state["ingresos_pendientes"]:
            if st.button("💾 Guardar todos en tabla", key="guardar_ingresos"):
                a_guardar = [r for r in st.session_state["ingresos_pendientes"]]
                for r in a_guardar:
                    r.pop("Estado", None)
                guardar_movimientos(a_guardar)
                st.session_state.pop("ingresos_pendientes")
                st.success("✅ Ingresos guardados correctamente")
                st.rerun()

    with tab3:
        st.markdown("### 📤 Registrar Gasto")
        st.caption("Sube una factura (OCR próximamente) o describe el gasto manualmente")

        archivo = st.file_uploader("Adjunta factura PDF o foto", type=["pdf","jpg","png","jpeg"])
        if archivo:
            st.info("📝 Lectura automática de facturas — próximamente disponible. Completa los datos manualmente.")

        st.markdown("**Describe el gasto:**")
        concepto_gasto = st.text_input("Concepto", placeholder="Reparación lavadora Huerto 1...")

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            inmueble_g = st.selectbox("Inmueble", ["— Selecciona —"]+df_inm["Nombre"].tolist(), key="inmg")
            importe_g  = st.number_input("Importe (€)", min_value=0.0, step=0.01, format="%.2f")
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
                nuevo = [{
                    "Fecha":      datetime.now().strftime("%Y-%m-%d"),
                    "Apartamento":inmueble_g,
                    "Concepto":   concepto_gasto,
                    "Categoría":  categoria_g,
                    "Tipo":       "Gasto",
                    "Importe":    importe_g,
                    "Deducible":  deducible_g,
                }]
                guardar_movimientos(nuevo)
                st.success(f"✅ Gasto de {importe_g:.2f} € guardado en {inmueble_g}")
                st.rerun()

# ══════════════════════════════════════════════
# SUMINISTROS
# ══════════════════════════════════════════════
elif menu == "Suministros":
    st.markdown('<div class="brand-header">Optimización de Suministros</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Auditoría de potencia eléctrica · Comparador tarifario</div>', unsafe_allow_html=True)

    inmueble_sel = st.selectbox("Selecciona inmueble:", df_inm["Nombre"].tolist())
    f   = df_inm[df_inm["Nombre"]==inmueble_sel].iloc[0]
    hab = int(f.get("Habitaciones",2))

    st.markdown('<div class="section-title">⚡ Auditoría de Potencia Contratada</div>', unsafe_allow_html=True)
    col1,col2 = st.columns(2)
    with col1:
        potencia_actual = st.number_input("Potencia contratada (kW)",min_value=1.0,max_value=30.0,value=4.4,step=0.1)
        tiene_ac       = st.checkbox("¿Aire acondicionado?",value=True)
        tiene_vitro    = st.checkbox("¿Vitrocerámica/inducción?",value=True)
        tiene_termo    = st.checkbox("¿Termo eléctrico?",value=False)
        tiene_cargador = st.checkbox("¿Cargador vehículo eléctrico?",value=False)

    base_kw={1:2.3,2:3.3,3:3.3,4:4.4,5:5.5}.get(min(hab,5),4.4)
    extra=0.0
    if tiene_ac:       extra+=2.0
    if tiene_vitro:    extra+=1.5
    if tiene_termo:    extra+=1.0
    if tiene_cargador: extra+=3.7
    POTENCIAS_REE=[1.15,2.3,3.45,4.6,5.75,6.9,8.05,9.2,10.35,11.5,14.49,17.25]
    pot_rec=next((p for p in POTENCIAS_REE if p>=base_kw+extra),17.25)
    coste_act=potencia_actual*42.0; coste_opt=pot_rec*42.0; ahorro=coste_act-coste_opt

    with col2:
        st.markdown(f"""<div style="background:{CARD_BG};border:1px solid {BORDER};border-radius:10px;padding:1.4rem;">
            <div class="kpi-label">Potencia recomendada</div>
            <div style="font-family:'DM Serif Display',serif;font-size:2.2rem;color:{ACCENT};">{pot_rec} kW</div>
            <div class="kpi-sub">Basado en {hab} hab. + equipos</div>
            <hr style="border:0;border-top:1px solid {BORDER};margin:0.8rem 0;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;"><span class="kpi-label">Coste actual/año</span><span style="font-size:0.9rem;font-weight:600;color:{RED};">{coste_act:,.0f} €</span></div>
            <div style="display:flex;justify-content:space-between;"><span class="kpi-label">Coste óptimo/año</span><span style="font-size:0.9rem;font-weight:600;color:{GREEN};">{coste_opt:,.0f} €</span></div>
        </div>""", unsafe_allow_html=True)
        cls_a="status-green" if ahorro>5 else ("status-red" if ahorro<-5 else "status-green")
        msg_a=f"✅ Ahorro potencial: {ahorro:,.0f} €/año · Bajar a {pot_rec} kW" if ahorro>5 else (f"⚠️ Potencia insuficiente · Subir a {pot_rec} kW" if ahorro<-5 else "✅ Potencia correctamente ajustada")
        st.markdown(f'<div class="{cls_a}" style="margin-top:0.8rem;">{msg_a}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 Comparador Tarifa Fija vs Indexada</div>', unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1: kwh=st.number_input("Consumo mensual (kWh)",min_value=50,max_value=2000,value=200,step=10)
    with c2: pfijo=st.number_input("Tarifa fija (€/kWh)",min_value=0.05,max_value=0.50,value=0.18,step=0.01,format="%.3f")
    with c3: ppool=st.number_input("Pool PVPC (€/kWh)",min_value=0.02,max_value=0.40,value=0.12,step=0.01,format="%.3f",help="Histórico 2024 ≈ 0.08–0.14 €/kWh")
    pind=ppool+0.04; cf_mes=kwh*pfijo; ci_mes=kwh*pind; dif_a=(cf_mes-ci_mes)*12
    fig_tar=go.Figure(go.Bar(x=["Tarifa Fija","Tarifa Indexada"],y=[cf_mes,ci_mes],marker_color=[ACCENT,"#639922"],
        text=[f"{cf_mes:.2f} €/mes",f"{ci_mes:.2f} €/mes"],textposition="outside",width=0.35))
    fig_tar.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10,r=10,t=20,b=10),height=260,
        yaxis=dict(showgrid=False,visible=False),xaxis=dict(showgrid=False),
        font=dict(family="DM Sans",size=13),showlegend=False)
    st.plotly_chart(fig_tar,use_container_width=True)
    r1,r2,r3=st.columns(3)
    r1.metric("Coste fijo/mes",f"{cf_mes:.2f} €")
    r2.metric("Coste indexado/mes",f"{ci_mes:.2f} €",delta=f"{-(cf_mes-ci_mes):+.2f} €")
    r3.metric("Ahorro anual",f"{dif_a:+.0f} €")
    if dif_a>30:    rec,cls=f"✅ Tarifa <b>indexada</b> más barata. Ahorro: <b>{dif_a:.0f} €/año</b>.","status-green"
    elif dif_a<-30: rec,cls="⚠️ Tarifa <b>fija</b> más económica con pool actual.","status-yellow"
    else:           rec,cls="➡️ Diferencia marginal. Depende de tu tolerancia al riesgo.","status-yellow"
    st.markdown(f'<div class="{cls}" style="margin-top:0.5rem;">{rec}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# FISCALIDAD — MODELO 100
# ══════════════════════════════════════════════
elif menu == "Fiscalidad":
    st.markdown('<div class="brand-header">Escudo Fiscal — Modelo 100</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Pre-relleno IRPF · Rendimientos de capital inmobiliario</div>', unsafe_allow_html=True)

    inmueble_fiscal = st.selectbox("Selecciona inmueble:", df_inm["Nombre"].tolist(), key="fiscal_inmueble")
    f_fiscal = df_inm[df_inm["Nombre"] == inmueble_fiscal].iloc[0]
    
    # Calcular Modelo 100
    modelo = calcular_modelo_100(f_fiscal, df_mov)
    
    # KPIs superiores
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ingresos Íntegros", f"{modelo['0102']:,.0f} €", "Casilla 0102")
    k2.metric("Total Gastos", f"{modelo['0102'] - modelo['0149']:,.0f} €", "Deducibles")
    k3.metric("Rendimiento Neto", f"{modelo['0149']:,.0f} €", "Casilla 0149")
    k4.metric("Base Imponible", f"{modelo['0154']:,.0f} €", f"Reducción {modelo['reduccion_pct']}%")
    
    st.markdown("---")
    st.markdown('<div class="section-title">📋 Casillas Modelo 100 — Verificar y Confirmar</div>', unsafe_allow_html=True)
    st.caption("Revisa cada casilla y marca como verificada. Los valores están pre-rellenados desde tus datos.")
    
    # Inicializar estado de checkboxes
    if "casillas_verificadas" not in st.session_state:
        st.session_state.casillas_verificadas = {}
    
    # Tabla estilo Modelo 100
    tabla_html = f"""
    <style>
    .tabla-modelo {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        background: white;
        border-radius: 8px;
        overflow: hidden;
    }}
    .tabla-modelo th {{
        background: #0F2744;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: 600;
    }}
    .tabla-modelo td {{
        padding: 12px;
        border-bottom: 1px solid #e0e0e0;
    }}
    .tabla-modelo tr:hover {{
        background: #f9f9f9;
    }}
    .casilla-col {{
        width: 80px;
        background: #f5f5f5;
        font-weight: 600;
        color: #0F2744;
    }}
    .valor-col {{
        text-align: right;
        font-weight: 600;
        color: #185FA5;
        width: 120px;
    }}
    .check-col {{
        text-align: center;
        width: 50px;
    }}
    </style>
    
    <table class="tabla-modelo">
    <thead>
        <tr>
            <th>Casilla</th>
            <th>Descripción</th>
            <th>Valor</th>
            <th>✓</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td class="casilla-col">0062-0075</td>
            <td>Identificación del inmueble</td>
            <td class="valor-col">{modelo['0062_0075']}</td>
            <td class="check-col">__CHECK_0__</td>
        </tr>
        <tr>
            <td class="casilla-col">0076</td>
            <td>Clave de uso</td>
            <td class="valor-col">{modelo['0076']}</td>
            <td class="check-col">__CHECK_1__</td>
        </tr>
        <tr>
            <td class="casilla-col">0100</td>
            <td>Reducción vivienda habitual</td>
            <td class="valor-col">{modelo['0100']}</td>
            <td class="check-col">__CHECK_2__</td>
        </tr>
        <tr>
            <td class="casilla-col">0101</td>
            <td>Días arrendado</td>
            <td class="valor-col">{modelo['0101']} días</td>
            <td class="check-col">__CHECK_3__</td>
        </tr>
        <tr style="background: #f0f8ff;">
            <td class="casilla-col" style="font-weight: bold;">0102</td>
            <td style="font-weight: bold;">Ingresos íntegros</td>
            <td class="valor-col" style="color: #27ae60; font-weight: bold;">{modelo['0102']:,.2f} €</td>
            <td class="check-col">__CHECK_4__</td>
        </tr>
        <tr>
            <td class="casilla-col">0105</td>
            <td>Intereses y financiación</td>
            <td class="valor-col">{modelo['0105']:,.2f} €</td>
            <td class="check-col">__CHECK_5__</td>
        </tr>
        <tr>
            <td class="casilla-col">0106</td>
            <td>Reparación y conservación</td>
            <td class="valor-col">{modelo['0106']:,.2f} €</td>
            <td class="check-col">__CHECK_6__</td>
        </tr>
        <tr>
            <td class="casilla-col">0108</td>
            <td>Tributos e IBI</td>
            <td class="valor-col">{modelo['0108']:,.2f} €</td>
            <td class="check-col">__CHECK_7__</td>
        </tr>
        <tr>
            <td class="casilla-col">0110</td>
            <td>Comunidad, seguros, formalización</td>
            <td class="valor-col">{modelo['0110']:,.2f} €</td>
            <td class="check-col">__CHECK_8__</td>
        </tr>
        <tr>
            <td class="casilla-col">0111</td>
            <td>Servicios y suministros</td>
            <td class="valor-col">{modelo['0111']:,.2f} €</td>
            <td class="check-col">__CHECK_9__</td>
        </tr>
        <tr>
            <td class="casilla-col">0112</td>
            <td>Gastos jurídicos</td>
            <td class="valor-col">{modelo['0112']:,.2f} €</td>
            <td class="check-col">__CHECK_10__</td>
        </tr>
        <tr>
            <td class="casilla-col">0113</td>
            <td>Amortización (3%)</td>
            <td class="valor-col">{modelo['0113']:,.2f} €</td>
            <td class="check-col">__CHECK_11__</td>
        </tr>
        <tr style="background: #f0f8ff; font-weight: bold;">
            <td class="casilla-col">0149</td>
            <td>Rendimiento neto</td>
            <td class="valor-col" style="color: #185FA5;">{modelo['0149']:,.2f} €</td>
            <td class="check-col">__CHECK_12__</td>
        </tr>
        <tr style="background: #f0f8ff; font-weight: bold;">
            <td class="casilla-col">0150</td>
            <td>Reducción {modelo['reduccion_pct']}%</td>
            <td class="valor-col" style="color: #f39c12;">-{modelo['0150']:,.2f} €</td>
            <td class="check-col">__CHECK_13__</td>
        </tr>
        <tr style="background: #f0f8ff; font-weight: bold;">
            <td class="casilla-col">0153</td>
            <td>Retenciones practicadas</td>
            <td class="valor-col">{modelo['0153']:,.2f} €</td>
            <td class="check-col">__CHECK_14__</td>
        </tr>
        <tr style="background: #d5f4e6; font-weight: bold;">
            <td class="casilla-col">0154</td>
            <td>BASE IMPONIBLE FINAL</td>
            <td class="valor-col" style="color: #27ae60;">{modelo['0154']:,.2f} €</td>
            <td class="check-col">__CHECK_15__</td>
        </tr>
    </tbody>
    </table>
    """
    
    # Reemplazar placeholders con checkboxes reales
    cols_check = st.columns(16)
    checks_html = tabla_html
    for i in range(16):
        with cols_check[i]:
            key = f"check_{inmueble_fiscal}_{i}"
            if key not in st.session_state.casillas_verificadas:
                st.session_state.casillas_verificadas[key] = False
            checked = st.checkbox("", key=key, label_visibility="collapsed")
            check_symbol = "✅" if checked else "☐"
            checks_html = checks_html.replace(f"__CHECK_{i}__", check_symbol, 1)
    
    st.markdown(checks_html, unsafe_allow_html=True)
    
    # Barra de progreso
    total_checks = 16
    verificadas = sum([1 for k, v in st.session_state.casillas_verificadas.items() if inmueble_fiscal in k and v])
    progreso = int((verificadas / total_checks) * 100)
    
    st.markdown("---")
    col_p1, col_p2 = st.columns([3, 1])
    with col_p1:
        st.progress(progreso / 100)
    with col_p2:
        st.markdown(f"**{verificadas} de {total_checks} verificadas** ({progreso}%)")
    
    # Botones de acción
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("✅ Confirmar Todas y Generar PDF", type="primary", use_container_width=True):
            st.success(f"✓ Modelo 100 confirmado para {inmueble_fiscal}")
            st.info("📄 Generación de PDF — Próximamente disponible")
    with col_b2:
        if st.button("📊 Ver Resumen Completo", use_container_width=True):
            st.info("Vista de resumen consolidado de todos los inmuebles — Próximamente")
    
    # Notas importantes
    st.markdown('<div class="section-title">ℹ️ Información Importante</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="status-yellow">
<b>⚠️ Antes de confirmar:</b><br>
• Este pre-relleno es orientativo. Verifica con tu asesor fiscal.<br>
• Cochera vinculada: {f_fiscal.get('Cochera_Vinculada','N')} — {'Consolidada en arrendamiento principal' if f_fiscal.get('Cochera_Vinculada')=='S' else 'Tributa independiente'}<br>
• Modalidad: {f_fiscal.get('Tipo_Arrendamiento','Larga Duración')} — Reducción aplicable: {modelo['reduccion_pct']}%<br>
• Los datos provienen de: Fichas de inmuebles + Diario Contable
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# DATOS DE LA CARTERA
# ══════════════════════════════════════════════
elif menu == "Datos de la Cartera":
    st.markdown('<div class="brand-header">Datos de la Cartera</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Parámetros maestros y copias de seguridad</div>', unsafe_allow_html=True)
    st.info("ℹ️ Campos fiscales añadidos: NIF_Inquilino · Intereses_Hipoteca · IBI_Anual · Seguro_Anual · etc.")

    col_cfg = {
        "Tipo_Arrendamiento": st.column_config.SelectboxColumn("Tipo Arrend.",options=["Larga Duración","Temporada","Vacacional"],required=True),
        "Cochera_Vinculada":  st.column_config.SelectboxColumn("Cochera Vinc.",options=["S","N"],required=True),
        "Zona_Tensionada":    st.column_config.SelectboxColumn("Zona Tensión", options=["S","N"],required=True),
        "Estado":             st.column_config.SelectboxColumn("Estado",       options=["Reformado","Bueno","Regular"],required=True),
        "Mobiliario":         st.column_config.SelectboxColumn("Mobiliario",   options=["S","N"],required=True),
        "Parking":            st.column_config.SelectboxColumn("Parking",      options=["S","N"],required=True),
        "IBI_Anual":          st.column_config.NumberColumn("IBI/año", format="%.0f €"),
        "Seguro_Anual":       st.column_config.NumberColumn("Seguro/año", format="%.0f €"),
        "Intereses_Hipoteca": st.column_config.NumberColumn("Intereses Hip.", format="%.0f €"),
    }
    df_ed = st.data_editor(df_inm,num_rows="dynamic",use_container_width=True,hide_index=True,column_config=col_cfg)
    if st.button("✅ Actualizar Cartera"):
        df_ed.to_csv(DB_INM,index=False); st.success("✓ Datos actualizados."); st.rerun()

    st.markdown('<div class="section-title">Copias de Seguridad</div>', unsafe_allow_html=True)
    b1,b2=st.columns(2)
    with b1:
        with open(DB_INM,"rb") as fi: st.download_button("📥 Descargar Inmuebles",fi,"nolasco_inmuebles.csv","text/csv")
    with b2:
        with open(DB_MOV,"rb") as fm: st.download_button("📥 Descargar Movimientos",fm,"nolasco_movimientos.csv","tex
