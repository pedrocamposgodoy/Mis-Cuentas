# ================================================================
# SECCIÓN 0 — IMPORTS Y LIBRERÍAS
# No tocar esto salvo que añadas una librería nueva
# ================================================================
import streamlit as st
import pandas as pd
import os
import io
import base64
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
# IMPORT MÓDULO B2B2C
# ================================================================
from asesoramiento_ia import render_asesor_ia, render_privacidad, render_diagnostico_inmueble

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
    background:transparent!important;border:none!important;color:#8ab4d4!important;
    font-family:'DM Sans',sans-serif!important;font-size:0.9rem!important;font-weight:400!important;
    text-align:left!important;padding:0.55rem 1rem!important;border-radius:0 6px 6px 0!important;
    width:100%!important;margin-bottom:2px!important;box-shadow:none!important;
    border-left:3px solid transparent!important;transition:all 0.15s ease!important;
}}
[data-testid="stSidebar"] .stButton>button:hover{{
    background:rgba(96,180,255,0.1)!important;color:#fff!important;
    border-left:3px solid rgba(96,180,255,0.4)!important;
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
# SECCIÓN 3 — BASE DE DATOS SUPABASE (Bloque 6)
# ================================================================
from supabase_db import (
    leer_inmuebles, leer_movimientos,
    guardar_inmuebles, eliminar_inmueble, guardar_movimientos_completo,
    agregar_movimientos, generar_csv_backup,
    login_usuario, registrar_usuario
)

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
# SECCIÓN 4 — AUTENTICACIÓN
# ================================================================
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# Si no está logueado, mostrar formulario de login
if not st.session_state.user_logged_in:
    st.markdown("<h1 style='text-align:center;color:#0F2744;'>🏠 Nolasco Capital</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;color:#185FA5;'>Gestión Patrimonial Inmobiliaria</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Iniciar Sesión", "📝 Registrarse"])
    
    with tab1:
        st.markdown("### Inicia sesión con tu cuenta")
        email_login = st.text_input("📧 Email", key="email_login")
        password_login = st.text_input("🔒 Contraseña", type="password", key="password_login")
        
        if st.button("🚀 Entrar", use_container_width=True):
            if email_login and password_login:
                result = login_usuario(email_login, password_login)
                if result['success']:
                    st.session_state.user_logged_in = True
                    st.session_state.user_id = result['user_id']
                    st.session_state.user_email = result['email']
                    # Limpiar datos del usuario anterior
                    if "df_inm_persistent" in st.session_state:
                        del st.session_state.df_inm_persistent
                    if "df_mov_persistent" in st.session_state:
                        del st.session_state.df_mov_persistent
                    st.success(f"✅ Bienvenido {result['email']}")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.warning("⚠️ Completa todos los campos")
    
    with tab2:
        st.markdown("### Crea tu cuenta nueva")
        email_reg = st.text_input("📧 Email", key="email_reg")
        password_reg = st.text_input("🔒 Contraseña", type="password", key="password_reg")
        password_reg2 = st.text_input("🔒 Repetir Contraseña", type="password", key="password_reg2")
        
        if st.button("📝 Registrarse", use_container_width=True):
            if email_reg and password_reg and password_reg2:
                if password_reg == password_reg2:
                    if len(password_reg) >= 6:
                        result = registrar_usuario(email_reg, password_reg)
                        if result['success']:
                            st.success("✅ Cuenta creada. Ahora inicia sesión.")
                        else:
                            st.error(f"❌ {result['error']}")
                    else:
                        st.warning("⚠️ La contraseña debe tener al menos 6 caracteres")
                else:
                    st.warning("⚠️ Las contraseñas no coinciden")
            else:
                st.warning("⚠️ Completa todos los campos")
    
    st.stop()

# ================================================================
# SECCIÓN 5 — CARGA DE DATOS DESDE SUPABASE
# ================================================================
if "df_inm_persistent" not in st.session_state:
    st.session_state.df_inm_persistent = leer_inmuebles(user_id=st.session_state.user_id)
if "df_mov_persistent" not in st.session_state:
    st.session_state.df_mov_persistent = leer_movimientos(user_id=st.session_state.user_id)

df_inm = st.session_state.df_inm_persistent
df_mov = st.session_state.df_mov_persistent

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
    ("📊", "Torre de Control",              "Core"),
    ("🏠", "Fichas (Benchmark)",            "Core"),
    ("📝", "Diario Contable",               "Core"),
    ("⚡", "Suministros",                   "Core"),
    ("💰", "Fiscalidad",                    "Core"),
    ("💎", "Macrofinanzas",                 "Core"),
    ("🧠", "Asesor Patrimonial IA",         "B2B2C"),
    ("🔒", "Privacidad y Consentimientos",  "B2B2C"),
    ("⚖️", "Legal",                         "Tools"),
    ("📂", "Datos de la Cartera",           "Config"),
]

with st.sidebar:
    # Logo y marca
    st.markdown("""
<div style='padding:1.4rem 1.4rem 1rem;'>
  <div style='font-family:"DM Serif Display",serif;font-size:1.5rem;color:#60B4FF;line-height:1.2;letter-spacing:0.01em;'>Nolasco Capital</div>
  <div style='font-size:0.6rem;letter-spacing:0.18em;text-transform:uppercase;color:#3a6a8a;margin-top:4px;'>Granada · Gestión Patrimonial</div>
</div>
<hr style='border:0;border-top:1px solid #1a3a5c;margin:0 0 0.6rem 0;'>
""", unsafe_allow_html=True)

    # Usuario logueado
    st.markdown(f"""
<div style='padding:0.5rem 1rem;background:rgba(96,180,255,0.1);border-radius:6px;margin:0 1rem 1rem;'>
    <div style='font-size:0.7rem;color:#3a6a8a;'>👤 Usuario</div>
    <div style='font-size:0.85rem;color:#fff;margin-top:2px;'>{st.session_state.user_email}</div>
</div>
""", unsafe_allow_html=True)
    
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.user_logged_in = False
        st.session_state.user_id = None
        st.session_state.user_email = None
        # Limpiar datos
        if "df_inm_persistent" in st.session_state:
            del st.session_state.df_inm_persistent
        if "df_mov_persistent" in st.session_state:
            del st.session_state.df_mov_persistent
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)

    def nav_group(label, grupo_id):
        st.markdown(f"<div style='font-size:0.58rem;letter-spacing:0.15em;text-transform:uppercase;color:#3a6a8a;padding:0.5rem 1rem 0.3rem;'>{label}</div>", unsafe_allow_html=True)
        for icon, page, grupo in PAGES:
            if grupo != grupo_id: continue
            is_active = st.session_state.menu == page
            if is_active:
                st.markdown(f"""
                <div style='background:rgba(96,180,255,0.15);border-left:3px solid #60B4FF;
                    padding:0.55rem 1rem;border-radius:0 6px 6px 0;margin-bottom:2px;
                    display:flex;align-items:center;gap:10px;'>
                    <span style='font-size:1rem;'>{icon}</span>
                    <span style='font-size:0.9rem;font-weight:600;color:#fff;'>{page}</span>
                </div>""", unsafe_allow_html=True)
            else:
                if st.button(f"{icon}  {page}", key=f"nav_{page}", use_container_width=True):
                    st.session_state.menu = page
                    st.rerun()

    nav_group("Gestión", "Core")
    st.markdown("<hr style='border:0;border-top:1px solid #1a3a5c;margin:0.5rem 0;'>", unsafe_allow_html=True)
    nav_group("Servicios IA", "B2B2C")
    st.markdown("<hr style='border:0;border-top:1px solid #1a3a5c;margin:0.5rem 0;'>", unsafe_allow_html=True)
    nav_group("Herramientas", "Tools")
    st.markdown("<hr style='border:0;border-top:1px solid #1a3a5c;margin:0.5rem 0;'>", unsafe_allow_html=True)
    nav_group("Configuración", "Config")

    st.markdown(f"""
    <hr style='border:0;border-top:1px solid #1a3a5c;margin:0.8rem 0 0.4rem;'>
    <div style='padding:0.3rem 1rem;font-size:0.68rem;color:#2a5070;'>
        {len(df_inm)} activos · {datetime.now().strftime('%b %Y')}
    </div>
    """, unsafe_allow_html=True)

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

def safe_float(value, default=0):
    """Convierte valor a float de forma segura, devuelve default si es None/NaN."""
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return float(default)
        return float(value)
    except:
        return float(default)

def tasacion(row):
    p  = PRECIOS_CP.get(str(row.get("CP","18005")),10.0)
    m2 = safe_float(row.get("M2_Construidos",80))
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
    agregar_movimientos(nuevos)
    df_nuevos = pd.DataFrame(nuevos)
    df_final = pd.concat([st.session_state.df_mov_persistent, df_nuevos], ignore_index=True)
    st.session_state.df_mov_persistent = df_final

def parsear_ingresos(texto, df_inm_local):
    rentas  = dict(zip(df_inm_local["Nombre"], df_inm_local["Renta"]))
    nombres = df_inm_local["Nombre"].tolist()
    texto_l = texto.lower()
    registros = []
    hoy = datetime.now().strftime("%Y-%m-%d")
    mes = datetime.now().strftime("%B %Y")

    # Detectar qué inmuebles se mencionan en el texto
    def mencionado(nombre):
        partes = [nombre.lower()] + [p.lower() for p in nombre.split()]
        return any(p in texto_l for p in partes if len(p) > 2)

    mencionados = [n for n in nombres if mencionado(n)]

    # Palabras que indican que NO pagó
    palabras_negativas = ["no ", "pendiente", "falta", "sin pagar", "no ha", "no pagó", "no pago", "excepto", "menos"]
    es_negativo = any(p in texto_l for p in palabras_negativas)

    # CASO 1: "todos han pagado" → todos Cobrado
    if "todos" in texto_l and not es_negativo and not mencionados:
        for n in nombres:
            registros.append({"Fecha":hoy,"Apartamento":n,"Concepto":f"Renta {mes}","Categoría":"Ingresos","Tipo":"Ingreso","Importe":rentas.get(n,0),"Deducible":"S","Estado":"Cobrado"})

    # CASO 2: "todos menos X" / "todos excepto X" → todos Cobrado menos el mencionado
    elif "todos" in texto_l and mencionados:
        for n in nombres:
            estado = "Pendiente" if n in mencionados else "Cobrado"
            registros.append({"Fecha":hoy,"Apartamento":n,"Concepto":f"Renta {mes}","Categoría":"Ingresos","Tipo":"Ingreso","Importe":rentas.get(n,0),"Deducible":"S","Estado":estado})

    # CASO 3: "solo pagó X" / "ha pagado X" / "X ha pagado" → SOLO ese inmueble
    elif mencionados and not es_negativo:
        for n in mencionados:
            registros.append({"Fecha":hoy,"Apartamento":n,"Concepto":f"Renta {mes}","Categoría":"Ingresos","Tipo":"Ingreso","Importe":rentas.get(n,0),"Deducible":"S","Estado":"Cobrado"})

    # CASO 4: "X no ha pagado" / "falta X" → SOLO ese inmueble como Pendiente
    elif mencionados and es_negativo:
        for n in mencionados:
            registros.append({"Fecha":hoy,"Apartamento":n,"Concepto":f"Renta {mes}","Categoría":"Ingresos","Tipo":"Ingreso","Importe":rentas.get(n,0),"Deducible":"S","Estado":"Pendiente"})

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
    renta_mensual = safe_float(row.get("Renta", 0))
    ingresos_integros = renta_mensual * 12
    intereses = safe_float(row.get("Intereses_Hipoteca", 0))
    gastos_reparacion = df_mov_local[
        (df_mov_local["Apartamento"] == row["Nombre"]) &
        (df_mov_local["Tipo"] == "Gasto") &
        (df_mov_local["Categoría"].isin(["Mantenimiento", "Reparación"]))
    ]["Importe"].sum()
    ibi_anual = safe_float(row.get("IBI_Anual", 0))
    comunidad_anual = safe_float(row.get("Comunidad", 0)) * 12
    seguro_anual = safe_float(row.get("Seguro_Anual", 0))
    formalizacion = safe_float(row.get("Gastos_Formalizacion", 0))
    casilla_0110 = comunidad_anual + seguro_anual + formalizacion
    servicios = safe_float(row.get("Servicios_Suministros", 0))
    gastos_juridicos = safe_float(row.get("Gastos_Juridicos", 0))
    valor_construccion = safe_float(row.get("Valor_Construccion", 0))
    amortizacion = valor_construccion * 0.03
    gastos_años_ant = safe_float(row.get("Gastos_Pendientes_Años_Ant", 0))
    total_gastos = intereses + gastos_reparacion + ibi_anual + casilla_0110 + servicios + gastos_juridicos + amortizacion + gastos_años_ant
    rendimiento_neto = ingresos_integros - total_gastos
    tipo_arrendamiento = str(row.get("Tipo_Arrendamiento", "Larga Duración"))
    reduccion_pct = 0.60 if tipo_arrendamiento == "Larga Duración" else 0.00
    reduccion_importe = rendimiento_neto * reduccion_pct
    retenciones = safe_float(row.get("Retenciones_IRPF", 0))
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
def generar_contrato_larga_duracion(data):
    suministros_incluidos = []
    if data["incluye_luz"]: suministros_incluidos.append("electricidad")
    if data["incluye_gas"]: suministros_incluidos.append("gas")
    if data["incluye_agua"]: suministros_incluidos.append("agua")
    if data["incluye_internet"]: suministros_incluidos.append("internet")
    
    suministros_texto = ", ".join(suministros_incluidos) if suministros_incluidos else "ninguno"
    
    ipc_clausula = """ACTUALIZACIÓN DE RENTA: La renta se actualizará anualmente según la variación del Índice de Precios al Consumo (IPC) conforme al artículo 18 de la LAU.""" if data["ipc"] else """ACTUALIZACIÓN DE RENTA: La renta permanecerá fija durante toda la duración del contrato."""
    
    mascotas_clausula = f"""MASCOTAS: {data["mascotas"]}."""
    
    return f"""
══════════════════════════════════════════════════════════════
CONTRATO DE ARRENDAMIENTO DE VIVIENDA
Ley 29/1994 de Arrendamientos Urbanos (LAU)
══════════════════════════════════════════════════════════════

REUNIDOS

De una parte, ________________________, con DNI ______________, 
en calidad de ARRENDADOR.

De otra parte, ________________________, con DNI ______________, 
en calidad de ARRENDATARIO.

EXPONEN

PRIMERO.- Que el ARRENDADOR es propietario del inmueble sito en 
{data["direccion"]}, con referencia catastral {data["ref_catastral"]}, 
de {data["m2"]} m² construidos.

SEGUNDO.- Que ambas partes convienen formalizar el presente contrato 
de arrendamiento de vivienda conforme a las siguientes:

══════════════════════════════════════════════════════════════
CLÁUSULAS
══════════════════════════════════════════════════════════════

PRIMERA.- OBJETO DEL CONTRATO
El arrendador cede al arrendatario el uso y disfrute de la vivienda 
descrita, destinada a satisfacer la necesidad permanente de vivienda 
del arrendatario, conforme al artículo 2 de la LAU.

SEGUNDA.- DURACIÓN
El presente contrato tendrá una duración de {data["duracion_anos"]} años, 
comenzando el día ___/___/______ y finalizando el día ___/___/______.

Conforme al artículo 9 de la LAU, si a la finalización del plazo pactado 
el arrendatario permanece en el uso de la vivienda por un plazo de al menos 
quince días con conocimiento y sin oposición del arrendador, el contrato se 
entenderá prorrogado por plazos anuales hasta un máximo de tres años más, 
salvo que el arrendatario manifieste su voluntad de no renovar con treinta 
días de antelación.

TERCERA.- RENTA
La renta mensual pactada es de {data["renta"]:,.2f} EUROS ({data["renta"]:,.2f}€), 
que el arrendatario abonará mediante transferencia bancaria antes del día 5 
de cada mes en la cuenta facilitada por el arrendador.

{ipc_clausula}

CUARTA.- FIANZA
El arrendatario deposita en este acto la cantidad de {data["importe_fianza"]:,.2f} 
EUROS ({data["importe_fianza"]:,.2f}€), equivalente a {data["fianza_meses"]} {"mes" if data["fianza_meses"] == 1 else "meses"} 
de renta, en concepto de fianza, conforme al artículo 36 de la LAU.

Esta fianza será depositada por el arrendador en el organismo competente de 
la Comunidad Autónoma y le será devuelta al arrendatario al término del 
contrato, previa deducción de los gastos que procedan por deterioros 
imputables al arrendatario o por rentas pendientes.

QUINTA.- SUMINISTROS Y SERVICIOS
Los suministros incluidos en la renta son: {suministros_texto}.

Los demás suministros y servicios (agua, gas, electricidad, internet, 
comunidad de propietarios, etc.) que no estén incluidos serán de cuenta 
del arrendatario, quien deberá contratar directamente con las compañías 
suministradoras y abonar puntualmente los recibos correspondientes.

SEXTA.- GASTOS DE COMUNIDAD E IBI
Los gastos de comunidad de propietarios, IBI y demás impuestos que graven 
directamente la vivienda serán de cuenta del arrendador, salvo pacto expreso 
en contrario.

SÉPTIMA.- OBRAS Y REPARACIONES
Serán de cuenta del arrendador las reparaciones necesarias para conservar 
la vivienda en las condiciones de habitabilidad, salvo cuando el deterioro 
sea imputable al arrendatario (artículo 21 LAU).

El arrendatario no podrá realizar obras sin consentimiento escrito del 
arrendador.

OCTAVA.- CESIÓN Y SUBARRIENDO
El arrendatario no podrá subarrendar ni ceder el contrato sin consentimiento 
escrito del arrendador (artículo 8 LAU).

NOVENA.- {mascotas_clausula}

DÉCIMA.- RESOLUCIÓN DEL CONTRATO
El contrato podrá resolverse por las causas previstas en el artículo 27 de la LAU:
- Falta de pago de la renta
- Falta de pago de la fianza
- Subarriendo o cesión no autorizados
- Daños causados dolosamente en la finca
- Realización de actividades molestas, insalubres, nocivas o peligrosas

DECIMOPRIMERA.- DESISTIMIENTO DEL ARRENDATARIO
Transcurridos al menos seis meses de contrato, el arrendatario podrá desistir 
del contrato notificándolo al arrendador con al menos treinta días de antelación 
(artículo 11 LAU). Si el arrendatario desiste antes de transcurridos cinco años, 
deberá indemnizar al arrendador con una cantidad equivalente a una mensualidad 
por cada año que reste hasta completar cinco años, prorrateándose por meses los 
períodos inferiores al año.

DECIMOSEGUNDA.- NOTIFICACIONES
Las notificaciones se realizarán en los domicilios indicados por las partes, 
salvo que se comunique por escrito un cambio de domicilio.

DECIMOTERCERA.- LEGISLACIÓN APLICABLE Y JURISDICCIÓN
El presente contrato se rige por la Ley 29/1994 de Arrendamientos Urbanos y 
disposiciones complementarias. Para cuantas cuestiones pudieran derivarse del 
presente contrato, las partes se someten a los Juzgados y Tribunales de la 
ciudad de Granada.

══════════════════════════════════════════════════════════════

Y en prueba de conformidad, firman el presente contrato por duplicado 
ejemplar en el lugar y fecha indicados.

Granada, a ___ de ______________ de 20__


EL ARRENDADOR                           EL ARRENDATARIO


_____________________                   _____________________
Fdo.: [Nombre]                          Fdo.: [Nombre]
DNI: [DNI]                              DNI: [DNI]

══════════════════════════════════════════════════════════════
Contrato generado con Nolasco Capital - Herramientas Legales
Documento orientativo LAU 29/1994 - Consulte con abogado
══════════════════════════════════════════════════════════════
"""

def generar_contrato_temporada(data):
    suministros_incluidos = []
    if data["incluye_luz"]: suministros_incluidos.append("electricidad")
    if data["incluye_gas"]: suministros_incluidos.append("gas")
    if data["incluye_agua"]: suministros_incluidos.append("agua")
    if data["incluye_internet"]: suministros_incluidos.append("internet")
    
    suministros_texto = ", ".join(suministros_incluidos) if suministros_incluidos else "ninguno"
    
    return f"""
══════════════════════════════════════════════════════════════
CONTRATO DE ARRENDAMIENTO DE TEMPORADA
Ley 29/1994 de Arrendamientos Urbanos (LAU) - Art. 3
══════════════════════════════════════════════════════════════

REUNIDOS

De una parte, ________________________, con DNI ______________, 
en calidad de ARRENDADOR.

De otra parte, ________________________, con DNI ______________, 
en calidad de ARRENDATARIO.

EXPONEN

PRIMERO.- Que el ARRENDADOR es propietario del inmueble sito en 
{data["direccion"]}, con referencia catastral {data["ref_catastral"]}, 
de {data["m2"]} m² construidos.

SEGUNDO.- Que el ARRENDATARIO precisa el uso temporal de la vivienda 
por motivos de [estudios/trabajo temporal/turismo/otros], NO siendo 
esta su vivienda habitual permanente.

TERCERO.- Que ambas partes convienen formalizar el presente contrato 
de arrendamiento de temporada conforme a las siguientes:

══════════════════════════════════════════════════════════════
CLÁUSULAS
══════════════════════════════════════════════════════════════

PRIMERA.- NATURALEZA DEL CONTRATO
El presente es un contrato de arrendamiento para uso distinto del de 
vivienda habitual, regulado por el artículo 3 de la LAU y el Código Civil.

SEGUNDA.- DURACIÓN
El contrato tendrá una duración de {data["duracion_meses"]} {"mes" if data["duracion_meses"] == 1 else "meses"}, 
comenzando el día ___/___/______ y finalizando el día ___/___/______.

A la finalización del plazo, el contrato se extinguirá automáticamente 
SIN PRÓRROGA OBLIGATORIA, debiendo el arrendatario desalojar la vivienda.

TERCERA.- RENTA
La renta mensual pactada es de {data["renta"]:,.2f} EUROS ({data["renta"]:,.2f}€), 
que el arrendatario abonará mediante transferencia bancaria antes del día 5 
de cada mes.

La renta permanecerá fija durante toda la duración del contrato.

CUARTA.- FIANZA
El arrendatario deposita en este acto la cantidad de {data["importe_fianza"]:,.2f} 
EUROS ({data["importe_fianza"]:,.2f}€) en concepto de fianza.

Esta fianza le será devuelta al arrendatario al término del contrato, previa 
deducción de los gastos que procedan por deterioros o rentas pendientes.

QUINTA.- SUMINISTROS Y SERVICIOS
Los suministros incluidos en la renta son: {suministros_texto}.

Los demás suministros serán de cuenta del arrendatario.

SEXTA.- FINALIZACIÓN
A la finalización del plazo, el arrendatario se compromete a entregar la 
vivienda en las mismas condiciones en que la recibió, salvo el desgaste 
por uso normal.

SÉPTIMA.- LEGISLACIÓN APLICABLE
El presente contrato se rige por el artículo 3 de la LAU 29/1994 y 
el Código Civil.

══════════════════════════════════════════════════════════════

Y en prueba de conformidad, firman el presente contrato en el lugar 
y fecha indicados.

Granada, a ___ de ______________ de 20__


EL ARRENDADOR                           EL ARRENDATARIO


_____________________                   _____________________
Fdo.: [Nombre]                          Fdo.: [Nombre]
DNI: [DNI]                              DNI: [DNI]

══════════════════════════════════════════════════════════════
Contrato generado con Nolasco Capital - Herramientas Legales
Documento orientativo LAU 29/1994 - Consulte con abogado
══════════════════════════════════════════════════════════════
"""

def generar_contrato_habitacion(data):
    return f"""
══════════════════════════════════════════════════════════════
CONTRATO DE ARRENDAMIENTO DE HABITACIÓN
Ley 29/1994 de Arrendamientos Urbanos (LAU)
══════════════════════════════════════════════════════════════

REUNIDOS

De una parte, ________________________, con DNI ______________, 
en calidad de ARRENDADOR.

De otra parte, ________________________, con DNI ______________, 
en calidad de ARRENDATARIO.

EXPONEN

PRIMERO.- Que el ARRENDADOR es titular del derecho de uso de la vivienda 
sita en {data["direccion"]}, referencia catastral {data["ref_catastral"]}.

SEGUNDO.- Que el ARRENDADOR cede en arrendamiento una HABITACIÓN de la 
vivienda, manteniendo el uso compartido de las zonas comunes (cocina, 
baño, salón).

TERCERO.- Que ambas partes convienen formalizar el presente contrato 
conforme a las siguientes:

══════════════════════════════════════════════════════════════
CLÁUSULAS
══════════════════════════════════════════════════════════════

PRIMERA.- OBJETO
El arrendador cede al arrendatario el uso de UNA HABITACIÓN de aproximadamente 
_____ m², con derecho a uso compartido de zonas comunes (cocina, baño, salón).

SEGUNDA.- DURACIÓN
El contrato tendrá una duración de {data["duracion_meses"]} {"mes" if data["duracion_meses"] == 1 else "meses"}, 
comenzando el día ___/___/______ y finalizando el día ___/___/______.

TERCERA.- RENTA
La renta mensual es de {data["renta"]:,.2f} EUROS ({data["renta"]:,.2f}€), 
que incluye el uso de la habitación y zonas comunes.

Los suministros (agua, luz, gas, internet) están INCLUIDOS en la renta.

CUARTA.- FIANZA
Fianza: {data["importe_fianza"]:,.2f} EUROS.

QUINTA.- NORMAS DE CONVIVENCIA
- Respetar los horarios de descanso (silencio de 23:00 a 8:00h)
- Mantener las zonas comunes limpias y ordenadas
- No realizar fiestas o ruidos molestos
- Avisar con antelación de visitas que pernocten

SEXTA.- DESISTIMIENTO
Cualquiera de las partes podrá desistir del contrato con 30 días de preaviso.

══════════════════════════════════════════════════════════════

Granada, a ___ de ______________ de 20__


EL ARRENDADOR                           EL ARRENDATARIO


_____________________                   _____________________

══════════════════════════════════════════════════════════════
Contrato generado con Nolasco Capital - Herramientas Legales
══════════════════════════════════════════════════════════════
"""
if menu == "Torre de Control":
    # Si no hay inmuebles, redirigir a Cartera
    if df_inm.empty:
        st.markdown("## 🏠 Bienvenido a Nolasco Capital")
        st.info("📭 Aún no tienes inmuebles registrados. Ve a **Datos de Cartera** en el menú lateral para añadir tu primer inmueble.")
        st.stop()
    else:
        pass
    st.markdown('<div class="brand-header">Torre de Control</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Rendimiento consolidado · Cartera Nolasco</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════
    # CHATBOT COMPACTO — TARJETA PLEGABLE
    # ═══════════════════════════════════════════════════════════
    
    # Calcular métricas REALES desde el Diario Contable
    total_ingresos_registrados = df_mov[df_mov["Tipo"]=="Ingreso"]["Importe"].sum()
    total_gastos_registrados = df_mov[df_mov["Tipo"]=="Gasto"]["Importe"].sum()
    balance_real = total_ingresos_registrados - total_gastos_registrados
    num_inmuebles = len(df_inm)
    margen_real = (balance_real / total_ingresos_registrados * 100) if total_ingresos_registrados > 0 else 0
    
    # Valores teóricos (para comparación)
    ing_b_teorico  = df_inm["Renta"].sum()
    
    # DEBUG: Mostrar info de carga de datos
    st.caption(f"🔍 Debug: {len(df_mov)} operaciones cargadas | Ingresos: {total_ingresos_registrados:,.0f}€ | Gastos: {total_gastos_registrados:,.0f}€")
    
    # Detectar alertas y oportunidades
    alertas_pendientes = []
    oportunidades = []
    
    # 1. Ingresos no registrados
    if total_ingresos_registrados < ing_b_teorico * 0.5:
        alertas_pendientes.append(f"Registra los cobros del mes en el Diario Contable (esperados: {ing_b_teorico:,.0f}€)")
    
    # 2. Contratos próximos a vencer
    for _, row in df_inm.iterrows():
        tipo_alert, msg = alerta_vencimiento(row)
        if tipo_alert in ["vencido", "urgente"]:
            dias = dias_para_vencimiento(row.get("Fecha_Vencimiento_Contrato"))
            if dias and dias < 60:
                alertas_pendientes.append(f"{row['Nombre']}: Contrato vence en {abs(dias)} días")
    
    # 3. Rentas por debajo del mercado
    for _, row in df_inm.iterrows():
        rm = tasacion(row)
        desv = (safe_float(row.get("Renta",0)) - rm) / rm * 100
        if desv < -10:
            potencial = (rm - safe_float(row.get("Renta",0)))
            oportunidades.append(f"{row['Nombre']} está {abs(desv):.0f}% bajo mercado → Puedes subir {potencial:,.0f}€/mes")
    
    # 4. Margen bajo
    if margen_real < 50 and margen_real > 0:
        oportunidades.append(f"Margen ajustado ({margen_real:.1f}%). Revisa gastos en Suministros")
    
    # Estado general basado en DATOS REALES
    if balance_real > 0 and margen_real > 70:
        estado_corto = "✅ Todo excelente"
        estado_largo = f"**Genial!** Has registrado **{total_ingresos_registrados:,.0f}€** de ingresos contra **{total_gastos_registrados:,.0f}€** de gastos = **{balance_real:,.0f}€** de balance neto con un margen excelente del **{margen_real:.1f}%**."
    elif balance_real > 0 and margen_real > 50:
        estado_corto = "✅ Todo bien"
        estado_largo = f"**Bien!** Balance real: **{balance_real:,.0f}€** ({total_ingresos_registrados:,.0f}€ ingresos - {total_gastos_registrados:,.0f}€ gastos) con **{margen_real:.1f}%** de margen."
    elif balance_real > 0:
        estado_corto = "⚠️ Margen ajustado"
        estado_largo = f"Balance positivo de **{balance_real:,.0f}€**, pero el margen es ajustado (**{margen_real:.1f}%**). Ingresos: {total_ingresos_registrados:,.0f}€ | Gastos: {total_gastos_registrados:,.0f}€"
    else:
        estado_corto = "⚠️ Revisar gastos"
        estado_largo = f"**Atención:** Balance negativo de **{balance_real:,.0f}€**. Gastos ({total_gastos_registrados:,.0f}€) superan ingresos ({total_ingresos_registrados:,.0f}€)."
    
    # Inicializar estado de expansión
    if "chatbot_expandido" not in st.session_state:
        st.session_state.chatbot_expandido = False
    
    # Mostrar tarjeta plegable
    with st.container():
        # Header con robot e info
        col_robot, col_info, col_toggle = st.columns([1.2, 3.8, 1])
        
        with col_robot:
            # Robot científico animado en Canvas
            robot_html = """
            <div style="width:120px;height:130px;margin:0 auto;">
            <canvas id="robotCanvas" style="display:block;width:100%;height:auto;border-radius:12px;"></canvas>
            <script>
            (function(){
            const cv=document.getElementById('robotCanvas');
            if(!cv||cv.dataset.init)return;
            cv.dataset.init='1';
            const cx=cv.getContext('2d');
            cv.width=240;cv.height=260;
            let T=0;
            function rr(x,y,w,h,r){cx.beginPath();cx.moveTo(x+r,y);cx.lineTo(x+w-r,y);cx.quadraticCurveTo(x+w,y,x+w,y+r);cx.lineTo(x+w,y+h-r);cx.quadraticCurveTo(x+w,y+h,x+w-r,y+h);cx.lineTo(x+r,y+h);cx.quadraticCurveTo(x,y+h,x,y+h-r);cx.lineTo(x,y+r);cx.quadraticCurveTo(x,y,x+r,y);cx.closePath();}
            function drawBg(){const g=cx.createRadialGradient(120,100,20,120,130,160);g.addColorStop(0,'#e8f6ff');g.addColorStop(1,'#bcd8f0');cx.fillStyle=g;cx.fillRect(0,0,240,260);}
            function drawBody(bx,by){cx.save();cx.translate(bx,by);const bg=cx.createLinearGradient(0,-30,0,30);bg.addColorStop(0,'#90c8f0');bg.addColorStop(0.5,'#4080c0');bg.addColorStop(1,'#2060a0');cx.fillStyle=bg;rr(-25,-30,50,60,12);cx.fill();cx.strokeStyle='rgba(255,255,255,0.2)';cx.lineWidth=1;cx.stroke();cx.restore();}
            function drawHead(hx,hy){cx.save();cx.translate(hx,hy);const hg=cx.createRadialGradient(-10,-15,5,0,0,50);hg.addColorStop(0,'#b8e0ff');hg.addColorStop(0.6,'#5090c8');hg.addColorStop(1,'#2060a0');cx.fillStyle=hg;cx.beginPath();cx.arc(0,0,45,0,Math.PI*2);cx.fill();cx.strokeStyle='rgba(255,255,255,0.25)';cx.lineWidth=2;cx.stroke();const blink=Math.abs(Math.sin(T*0.0008));const lookX=Math.sin(T*0.002)*3;function eye(ex,ey){const eg=cx.createRadialGradient(ex,ey,1,ex,ey,12);eg.addColorStop(0,'rgba(80,210,255,0.6)');eg.addColorStop(1,'rgba(80,210,255,0)');cx.fillStyle=eg;cx.beginPath();cx.ellipse(ex,ey,12,12*blink,0,0,Math.PI*2);cx.fill();const ig=cx.createRadialGradient(ex-2+lookX,ey-2,0.5,ex+lookX,ey,8);ig.addColorStop(0,'#b8f0ff');ig.addColorStop(0.4,'#30b8f0');ig.addColorStop(1,'#03284a');cx.fillStyle=ig;cx.beginPath();cx.ellipse(ex,ey,8,8*blink,0,0,Math.PI*2);cx.fill();cx.fillStyle='#020c18';cx.beginPath();cx.ellipse(ex+lookX*0.5,ey,4,4*blink,0,0,Math.PI*2);cx.fill();if(blink>0.4){cx.fillStyle='rgba(255,255,255,0.85)';cx.beginPath();cx.ellipse(ex-3,ey-3,2,1.5,-0.4,0,Math.PI*2);cx.fill();}}
            eye(-14,-8);eye(14,-8);const smile=Math.sin(T*0.002)*2;cx.strokeStyle='rgba(80,210,255,0.7)';cx.lineWidth=2;cx.lineCap='round';cx.beginPath();cx.moveTo(-12,12+smile);cx.quadraticCurveTo(0,20+smile,12,12+smile);cx.stroke();cx.restore();}
            function drawAntenna(ax,ay){cx.save();cx.translate(ax,ay);const wb=Math.sin(T*0.004)*6;cx.strokeStyle='#5090c8';cx.lineWidth=2;cx.lineCap='round';cx.beginPath();cx.moveTo(0,0);cx.quadraticCurveTo(wb*0.5,-15,wb,-30);cx.stroke();const p=5+Math.sin(T*0.008)*2;const pg=cx.createRadialGradient(wb,-35,0.5,wb,-35,p+5);pg.addColorStop(0,'rgba(80,210,255,0.7)');pg.addColorStop(1,'rgba(80,210,255,0)');cx.fillStyle=pg;cx.beginPath();cx.arc(wb,-35,p+5,0,Math.PI*2);cx.fill();const bg=cx.createRadialGradient(wb-2,-37,0.5,wb,-35,p);bg.addColorStop(0,'#ffffff');bg.addColorStop(0.3,'#90e0ff');bg.addColorStop(1,'#1890e0');cx.fillStyle=bg;cx.beginPath();cx.arc(wb,-35,p,0,Math.PI*2);cx.fill();cx.restore();}
            function frame(){drawBg();const bob=Math.sin(T*0.004)*3;drawBody(120,150+bob);drawHead(120,100+bob);drawAntenna(120,70+bob);T+=16;requestAnimationFrame(frame);}
            frame();
            })();
            </script>
            </div>
            """
            st.components.v1.html(robot_html, height=135)
        
        with col_info:
            st.markdown(f"""
            <div style="padding-top:30px;">
                <span style="font-weight:600;color:{TEXT_PRI};font-size:1.1rem;">Resumen IA</span>
                <span style="color:{TEXT_SEC};font-size:0.95rem;"> │ </span>
                <span style="font-size:0.95rem;color:{TEXT_PRI};">{estado_corto}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col_toggle:
            st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
            if st.button("▼" if not st.session_state.chatbot_expandido else "▲", key="toggle_chatbot", use_container_width=True):
                st.session_state.chatbot_expandido = not st.session_state.chatbot_expandido
                st.rerun()
    
    # Mostrar contenido expandido si está activo
    if st.session_state.chatbot_expandido:
        with st.container():
            st.markdown(f"""
            <div style="background:{CARD_BG};border:1px solid {ACCENT};border-left:4px solid {ACCENT};border-radius:8px;padding:1rem;margin-bottom:1.5rem;margin-top:-0.5rem;">
                <div style="font-size:0.9rem;color:{TEXT_PRI};line-height:1.6;margin-bottom:12px;">
                    {estado_largo}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if alertas_pendientes:
                st.markdown("**📋 Pendientes:**")
                for alerta in alertas_pendientes[:3]:
                    st.markdown(f"• {alerta}")
                st.markdown("")
            
            if oportunidades:
                st.markdown("**💡 Oportunidades:**")
                for oport in oportunidades[:3]:
                    st.markdown(f"• {oport}")
                st.markdown("")
            
            if not alertas_pendientes and not oportunidades:
                st.success("✅ Todo está en orden. Continúa registrando movimientos para optimizar deducciones fiscales.")

    st.markdown("---")
    
    # KPIs principales - MOSTRAR INGRESOS REALES REGISTRADOS
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-label">Ingresos Registrados</div><div class="kpi-value" style="color:{GREEN};">{total_ingresos_registrados:,.0f} €</div><div class="kpi-sub">Total cobrado real</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-label">Gastos Registrados</div><div class="kpi-value" style="color:{RED};">−{total_gastos_registrados:,.0f} €</div><div class="kpi-sub">Total pagado real</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card highlight"><div class="kpi-label">Balance Real</div><div class="kpi-value">{balance_real:,.0f} €</div><div class="kpi-sub">Ingresos - Gastos</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Rentabilidad por Activo</div>', unsafe_allow_html=True)
    if df_inm.empty:
        st.info("📭 No tienes inmuebles registrados. Ve a **Cartera** para añadir tu primer inmueble.")
    else:
        cols = st.columns(len(df_inm))
        for i, row in df_inm.iterrows():
            g_esp    = df_mov[(df_mov["Apartamento"]==row["Nombre"])&(df_mov["Tipo"]=="Gasto")&(df_mov["Categoría"]!="Comunidad")]["Importe"].sum()
            comunidad = safe_float(row.get("Comunidad",0)) if pd.notna(row.get("Comunidad", 0)) else 0
            gastos_u = comunidad + g_esp
            neto_u   = safe_float(row.get("Renta",0))-gastos_u
            rm       = tasacion(row)
            desv     = (safe_float(row.get("Renta",0))-rm)/rm*100
            pill_cls,_ = bench_pill(desv)
            zt = " 🔒" if str(row.get("Zona_Tensionada","N"))=="S" else ""
            with cols[i]:
                st.markdown(f"""<div class="asset-card"><div class="asset-top" style="background:{COLOR_TOPS[i%len(COLOR_TOPS)]};"></div><div class="asset-body"><div class="asset-name">{row["Nombre"]}{zt}</div><div class="asset-tenant">{row["Inquilino"]}</div><div class="asset-row"><span class="asset-ml">Renta</span><span class="asset-mv" style="color:{GREEN};">+{safe_float(row.get("Renta",0)):,.0f}€</span></div><div class="asset-row"><span class="asset-ml">Gastos</span><span class="asset-mv" style="color:{RED};">−{gastos_u:,.0f}€</span></div><div class="asset-div"></div><div class="asset-row"><span class="asset-ml">Neto</span><span class="asset-neto">{neto_u:,.0f}€</span></div><span class="pill {pill_cls}">{desv:+.1f}% mercado</span></div></div>""", unsafe_allow_html=True)
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
            rm=tasacion(row); pa=max(0,rm-safe_float(row.get("Renta",0)))*12; total_lc+=pa
            if pa>0:
                dv=(safe_float(row.get("Renta",0))-rm)/rm*100; cv=RED if dv<-15 else AMBER
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:9px 12px;background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;margin-bottom:6px;"><span style="font-size:0.8rem;color:{TEXT_SEC};">{row["Nombre"]}</span><span style="font-size:0.9rem;font-weight:600;color:{cv};">−{pa:,.0f} €/año</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:11px 14px;background:{ACCENT};border-radius:8px;margin-top:4px;"><span style="font-size:0.72rem;font-weight:500;color:#B5D4F4;text-transform:uppercase;letter-spacing:0.06em;">Total pérdida anual</span><span style="font-size:1.3rem;font-weight:600;color:#fff;">−{total_lc:,.0f} €</span></div>', unsafe_allow_html=True)
    
    # Gráfico histórico últimos 12 meses
    st.markdown('<div class="section-title">📈 Evolución Últimos 12 Meses</div>', unsafe_allow_html=True)
    
    # Generar datos históricos agregando movimientos por mes
    df_mov["Fecha"] = pd.to_datetime(df_mov["Fecha"], errors="coerce")
    df_mov_12m = df_mov[df_mov["Fecha"].notna()].copy()
    df_mov_12m["Mes"] = df_mov_12m["Fecha"].dt.to_period("M")
    
    # Agrupar por mes
    ingresos_mes = df_mov_12m[df_mov_12m["Tipo"]=="Ingreso"].groupby("Mes")["Importe"].sum()
    gastos_mes   = df_mov_12m[df_mov_12m["Tipo"]=="Gasto"].groupby("Mes")["Importe"].sum()
    
    # Últimos 12 meses
    hoy = pd.Period(datetime.now(), freq="M")
    meses = [hoy - i for i in range(11, -1, -1)]
    meses_str = [str(m) for m in meses]
    
    ing_data = [ingresos_mes.get(m, 0) for m in meses]
    gas_data = [gastos_mes.get(m, 0) for m in meses]
    neto_data = [i - g for i, g in zip(ing_data, gas_data)]
    
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Scatter(x=meses_str, y=ing_data, mode='lines+markers', name='Ingresos', 
        line=dict(color=GREEN, width=3), marker=dict(size=7)))
    fig_hist.add_trace(go.Scatter(x=meses_str, y=gas_data, mode='lines+markers', name='Gastos', 
        line=dict(color=RED, width=3), marker=dict(size=7)))
    fig_hist.add_trace(go.Scatter(x=meses_str, y=neto_data, mode='lines+markers', name='Neto', 
        line=dict(color=ACCENT, width=3, dash='dot'), marker=dict(size=7)))
    
    fig_hist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10,r=10,t=10,b=40), height=280,
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", title=""),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", title="€"),
        font=dict(family="DM Sans", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    st.plotly_chart(fig_hist, use_container_width=True)
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
    
    # Navegación con botones prev/next
    lista_inmuebles = df_inm["Nombre"].tolist()
    default_idx = lista_inmuebles.index(st.session_state.ficha_sel) if st.session_state.ficha_sel in lista_inmuebles else 0
    
    col_nav1, col_nav2, col_nav3 = st.columns([1, 6, 1])
    with col_nav1:
        if st.button("←", key="prev_inmueble", use_container_width=True, disabled=(default_idx == 0)):
            st.session_state.ficha_sel = lista_inmuebles[default_idx - 1]
            st.rerun()
    with col_nav2:
        sel = st.selectbox("Inmueble a auditar:", lista_inmuebles, index=default_idx, label_visibility="collapsed")
        st.session_state.ficha_sel = sel
    with col_nav3:
        if st.button("→", key="next_inmueble", use_container_width=True, disabled=(default_idx == len(lista_inmuebles) - 1)):
            st.session_state.ficha_sel = lista_inmuebles[default_idx + 1]
            st.rerun()
    
    f = df_inm[df_inm["Nombre"]==sel].iloc[0]
    renta_act = safe_float(f.get("Renta",0)); renta_mer = tasacion(f); desv = (renta_act-renta_mer)/renta_mer*100
    perdida_m = max(0,renta_mer-renta_act); perdida_a = perdida_m*12
    df_gf = df_mov[(df_mov["Apartamento"]==sel)&(df_mov["Tipo"]=="Gasto")&(df_mov["Categoría"]!="Comunidad")]
    gastos_u = (safe_float(f.get("Comunidad",0)) if pd.notna(f.get("Comunidad", 0)) else 0) + df_gf["Importe"].sum()
    rent_bruta = (renta_act*12/safe_float(f.get("Valor_Construccion",0))*100) if safe_float(f.get("Valor_Construccion",0))>0 else 0
    rent_neta = ((renta_act-gastos_u)*12/safe_float(f.get("Valor_Construccion",0))*100) if safe_float(f.get("Valor_Construccion",0))>0 else 0
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
        rn_real = (rto_neto-impuesto)/safe_float(f.get("Valor_Construccion",0))*100 if safe_float(f.get("Valor_Construccion",0))>0 else 0
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
    nueva_neta = ((nueva_renta-gastos_u)*12/safe_float(f.get("Valor_Construccion",0))*100) if safe_float(f.get("Valor_Construccion",0))>0 else 0
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
    res = pd.concat([pd.DataFrame([{"Concepto":"Comunidad","Importe":safe_float(f.get("Comunidad",0)) if pd.notna(f.get("Comunidad",0)) else 0,"Deducible":"S"}]),df_gf[["Concepto","Importe","Deducible"]]])
    st.dataframe(res.style.format({"Importe":"{:,.2f} €"}),hide_index=True,use_container_width=True)

# ================================================================
# PANTALLA 3 — AUDITORÍA IA DE MANTENIMIENTO
# Diseño acordeón compacto - sin colores llamativos
# ================================================================
    st.markdown('<div class="brand-header">Auditoría de Mantenimiento</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Planificación de reformas por inmueble</div>', unsafe_allow_html=True)
    
    # Generar datos dinámicamente desde el CSV
    # Función para calcular costes estimados según años reforma
    def calcular_costes_reforma(años_reforma, valor_construccion):
        if años_reforma >= 8:
            return {"urgente": valor_construccion * 0.03, "medio": valor_construccion * 0.08, "largo": valor_construccion * 0.05}
        elif años_reforma >= 5:
            return {"urgente": valor_construccion * 0.02, "medio": valor_construccion * 0.05, "largo": valor_construccion * 0.04}
        else:
            return {"urgente": valor_construccion * 0.01, "medio": valor_construccion * 0.03, "largo": valor_construccion * 0.02}
    
    def desc_reforma(años_reforma):
        if años_reforma >= 8:
            return "Pintura exterior + tuberías + electricidad"
        elif años_reforma >= 5:
            return "Pintura + revisión instalaciones"
        else:
            return "Mantenimiento preventivo"
    
    año_actual = datetime.now().year
    datos_mantenimiento = {}
    for _, row in df_inm.iterrows():
        nombre = row["Nombre"]
        reforma = int(row.get("Año_Reforma", año_actual))
        años = año_actual - reforma
        costes = calcular_costes_reforma(años, safe_float(row.get("Valor_Construccion",0)))
        datos_mantenimiento[nombre] = {
            "urgente": round(costes["urgente"]),
            "medio": round(costes["medio"]),
            "largo": round(costes["largo"]),
            "reforma": reforma,
            "desc": desc_reforma(años)
        }
    
    # Inicializar estado de expansión
    if "auditoria_expandido" not in st.session_state:
        st.session_state.auditoria_expandido = {}
    
    # Función para determinar urgencia
    def get_urgencia(reforma_año):
        años = datetime.now().year - reforma_año
        if años >= 8:
            return "🔴 Urgente", RED
        elif años >= 5:
            return "🟡 Medio", AMBER
        else:
            return "🟢 Largo", GREEN
    
    # Mostrar cada inmueble como acordeón
    for nombre, datos in datos_mantenimiento.items():
        if nombre not in df_inm["Nombre"].tolist():
            continue
            
        urgencia_label, urgencia_color = get_urgencia(datos["reforma"])
        años = datetime.now().year - datos["reforma"]
        total = datos["urgente"] + datos["medio"] + datos["largo"]
        
        # Estado de expansión para este inmueble
        expandido = st.session_state.auditoria_expandido.get(nombre, False)
        
        # Header del acordeón
        col_header, col_btn = st.columns([5, 1])
        with col_header:
            st.markdown(f"""
            <div style="background:{CARD_BG};border:1px solid {BORDER};border-radius:6px;padding:0.7rem 1rem;margin-bottom:0.5rem;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div style="flex:1;">
                        <span style="font-weight:600;color:{TEXT_PRI};font-size:1.23rem;">{nombre}</span>
                        <span style="color:{TEXT_SEC};font-size:1.04rem;margin-left:12px;">{urgencia_label} • {total:,.0f}€</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_btn:
            if st.button("▼" if not expandido else "▲", key=f"toggle_audit_{nombre}", use_container_width=True):
                st.session_state.auditoria_expandido[nombre] = not expandido
                st.rerun()
        
        # Contenido expandido
        if expandido:
            with st.container():
                st.markdown(f"""
                <div style="background:{CARD_BG};border:1px solid {BORDER};border-left:3px solid {urgencia_color};border-radius:6px;padding:1rem;margin-bottom:1rem;margin-top:-0.3rem;">
                    <div style="font-size:1.14rem;color:{TEXT_PRI};line-height:1.7;">
                        <div style="margin-bottom:8px;"><b>Reforma:</b> {datos["reforma"]} ({años} años)</div>
                        <div style="margin-bottom:8px;"><b>Urgencia:</b> {datos["desc"]}</div>
                        <div style="margin-bottom:8px;"><b>Presupuesto:</b> {total:,.0f}€</div>
                        <div style="margin-top:12px;padding-top:12px;border-top:1px dashed {BORDER};">
                            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;font-size:1.1rem;">
                                <div>
                                    <div style="color:{TEXT_SEC};font-size:0.98rem;">Urgente (0-6m)</div>
                                    <div style="font-weight:600;color:{RED};">{datos["urgente"]:,.0f}€</div>
                                </div>
                                <div>
                                    <div style="color:{TEXT_SEC};font-size:0.98rem;">Medio (6-18m)</div>
                                    <div style="font-weight:600;color:{AMBER};">{datos["medio"]:,.0f}€</div>
                                </div>
                                <div>
                                    <div style="color:{TEXT_SEC};font-size:0.98rem;">Largo (18+m)</div>
                                    <div style="font-weight:600;color:{GREEN};">{datos["largo"]:,.0f}€</div>
                                </div>
                            </div>
                        </div>
                        <div style="margin-top:12px;padding-top:12px;border-top:1px dashed {BORDER};font-size:1.07rem;color:{TEXT_SEC};">
                            <b>Recomendación:</b> {"Actuar en próximos 3 meses — reforma muy antigua" if años >= 8 else ("Planifica presupuesto para plazo medio" if años >= 5 else "Inmueble en buen estado")}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ================================================================
# PANTALLA 4 — DIARIO CONTABLE
# Registro de ingresos y gastos, parseo inteligente de texto
# ================================================================
elif menu == "Diario Contable":
    st.markdown('<div class="brand-header">Diario Contable</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Registro de operaciones · Ingresos · Gastos</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 Registro de Operaciones", "📥 Registrar Ingresos", "📤 Registrar Gastos"])
    with tab1:
        # Filtros de fecha
        col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
        with col_f1:
            años_disponibles = sorted(pd.to_datetime(df_mov["Fecha"], errors="coerce").dt.year.dropna().unique(), reverse=True)
            año_filtro = st.selectbox("📅 Año", ["Todos"] + [int(a) for a in años_disponibles], key="filtro_año")
        with col_f2:
            meses_nombres = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            mes_filtro = st.selectbox("📅 Mes", meses_nombres, key="filtro_mes")
        with col_f3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("🔄 Limpiar", use_container_width=True, key="limpiar_filtros"):
                st.session_state.filtro_año = "Todos"
                st.session_state.filtro_mes = "Todos"
                st.rerun()
        
        # Aplicar filtros
        df_filtrado = df_mov.copy()
        df_filtrado["Fecha"] = pd.to_datetime(df_filtrado["Fecha"], errors="coerce")
        
        if año_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Fecha"].dt.year == año_filtro]
        
        if mes_filtro != "Todos":
            mes_num = meses_nombres.index(mes_filtro)
            df_filtrado = df_filtrado[df_filtrado["Fecha"].dt.month == mes_num]
        
        # Mostrar contador
        st.caption(f"📊 Mostrando {len(df_filtrado)} de {len(df_mov)} operaciones")
        
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
        df_ed = st.data_editor(df_filtrado,num_rows="dynamic",use_container_width=True,hide_index=True,column_config=config)
        t_ing = df_ed[df_ed["Tipo"]=="Ingreso"]["Importe"].sum()
        t_gas = df_ed[df_ed["Tipo"]=="Gasto"]["Importe"].sum()
        m1,m2,m3 = st.columns(3)
        m1.metric("Ingresos Registrados", f"{t_ing:,.2f} €")
        m2.metric("Gastos Registrados", f"−{t_gas:,.2f} €")
        m3.metric("Balance Total", f"{t_ing-t_gas:,.2f} €")
        if st.button("💾 Guardar Cambios", key="guardar_tabla"):
            # CRÍTICO: No sobrescribir todo el DataFrame, solo actualizar las filas editadas
            # Si hay filtros activos, df_ed solo contiene las filas visibles
            # Necesitamos merge con el DataFrame completo
            
            if año_filtro != "Todos" or mes_filtro != "Todos":
                # Hay filtros activos - hacer merge inteligente
                # Eliminar del DataFrame completo las filas que estaban en el filtro
                df_completo = st.session_state.df_mov_persistent.copy()
                df_completo["Fecha"] = pd.to_datetime(df_completo["Fecha"], errors="coerce")
                
                # Crear máscara de las filas que NO estaban en el filtro
                mascara = pd.Series([True] * len(df_completo))
                if año_filtro != "Todos":
                    mascara = mascara & (df_completo["Fecha"].dt.year != año_filtro)
                if mes_filtro != "Todos":
                    mes_num = meses_nombres.index(mes_filtro)
                    mascara = mascara & (df_completo["Fecha"].dt.month != mes_num)
                
                # Combinar: filas NO filtradas + filas editadas
                df_final = pd.concat([df_completo[mascara], df_ed], ignore_index=True)
                df_final = df_final.sort_values("Fecha", ascending=False).reset_index(drop=True)
            else:
                # No hay filtros - df_ed contiene todo
                df_final = df_ed
            
            st.session_state.df_mov_persistent = df_final
            guardar_movimientos_completo(df_final)
            
            total_movs = len(st.session_state.df_mov_persistent)
            total_ingresos = st.session_state.df_mov_persistent[st.session_state.df_mov_persistent["Tipo"]=="Ingreso"]["Importe"].sum()
            
            st.success(f"✓ Guardado: {total_movs} operaciones | Ingresos totales: {total_ingresos:,.0f}€")
            st.rerun()
    with tab2:
        st.markdown("### 📥 Registrar Ingresos del Mes")
        st.caption("Escribe con tus propias palabras quién ha pagado este mes")
        
        # BOTÓN RÁPIDO: Registrar todas las rentas
        col_quick1, col_quick2 = st.columns([2, 1])
        with col_quick1:
            st.markdown(f"""<div class="status-green" style="font-size:0.8rem;">
            <b>Ejemplos que entiendo:</b><br>
            · "Ha pagado solo Huerto 1"<br>
            · "Todos han pagado"<br>
            · "Todos han pagado menos Abarqueros"<br>
            · "Falta Huerto 2 por pagar"<br>
            · "Han pagado Huerto 1 y Huerto 3"
            </div>""", unsafe_allow_html=True)
        with col_quick2:
            if st.button("⚡ Registrar TODAS las rentas", type="primary", use_container_width=True, key="registrar_todas_rentas"):
                # Registrar automáticamente todos los inmuebles
                hoy = datetime.now().strftime("%Y-%m-%d")
                nuevos_ingresos = []
                for _, inm in df_inm.iterrows():
                    nuevos_ingresos.append({
                        "Fecha": hoy,
                        "Apartamento": inm["Nombre"],
                        "Concepto": "Renta Mensual",
                        "Categoría": "Ingresos",
                        "Tipo": "Ingreso",
                        "Importe": inm["Renta"],
                        "Deducible": "N"
                    })
                
                # Añadir al DataFrame
                df_nuevos = pd.DataFrame(nuevos_ingresos)
                df_completo = pd.concat([st.session_state.df_mov_persistent, df_nuevos], ignore_index=True)
                
                # Convertir Fecha a datetime antes de ordenar
                df_completo["Fecha"] = pd.to_datetime(df_completo["Fecha"], errors="coerce")
                df_completo = df_completo.sort_values("Fecha", ascending=False).reset_index(drop=True)
                # Volver a convertir a string para guardar en CSV
                df_completo["Fecha"] = df_completo["Fecha"].dt.strftime("%Y-%m-%d")
                
                st.session_state.df_mov_persistent = df_completo
                guardar_movimientos_completo(df_completo)
                
                total_registrado = df_nuevos["Importe"].sum()
                st.success(f"✓ Registradas {len(nuevos_ingresos)} rentas por {total_registrado:,.0f}€")
                
                if st.button("🔄 Ir a Torre de Control", key="go_to_dashboard"):
                    st.session_state.menu = "Torre de Control"
                    st.rerun()

        texto_ingresos = st.text_area("¿Quién ha pagado este mes?", placeholder="Ha pagado solo Huerto 1...", height=90, key="txt_ingresos")

        if st.button("🔍 Interpretar", type="primary", key="procesar_ing"):
            if texto_ingresos.strip():
                registros = parsear_ingresos(texto_ingresos, df_inm)
                if registros:
                    st.session_state["ingresos_pendientes"] = registros
                    st.session_state["ingresos_editados"] = registros.copy()
                else:
                    st.warning("⚠️ No entendí quién pagó. Prueba con: 'Ha pagado Huerto 1' o 'Todos han pagado'")
            else:
                st.warning("Escribe algo primero")

        if "ingresos_pendientes" in st.session_state and st.session_state["ingresos_pendientes"]:
            st.markdown("---")
            st.markdown("**✏️ Revisa y corrige si es necesario — luego guarda:**")

            registros = st.session_state["ingresos_pendientes"]

            # Mostrar cada registro como fila editable
            editados = []
            for i, r in enumerate(registros):
                color = "#EDF7F1" if r["Estado"] == "Cobrado" else "#FDECEA"
                bcolor = GREEN if r["Estado"] == "Cobrado" else RED
                icon = "✅" if r["Estado"] == "Cobrado" else "⏳"

                with st.container():
                    st.markdown(f'<div style="background:{color};border-left:4px solid {bcolor};padding:0.6rem 1rem;border-radius:6px;margin-bottom:4px;"><b>{icon} {r["Apartamento"]}</b></div>', unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([2, 1, 1])
                    with c1:
                        nuevo_importe = st.number_input("Importe (€)", value=float(r["Importe"]), min_value=0.0, step=10.0, key=f"imp_{i}", label_visibility="collapsed")
                    with c2:
                        nuevo_estado = st.selectbox("Estado", ["Cobrado", "Pendiente"], index=0 if r["Estado"] == "Cobrado" else 1, key=f"est_{i}", label_visibility="collapsed")
                    with c3:
                        incluir = st.checkbox("Incluir", value=True, key=f"inc_{i}")

                    if incluir:
                        fila = r.copy()
                        fila["Importe"] = nuevo_importe
                        fila["Estado"] = nuevo_estado
                        editados.append(fila)

            st.session_state["ingresos_editados"] = editados

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("💾 Guardar", type="primary", key="guardar_ingresos"):
                    a_guardar = [r.copy() for r in st.session_state.get("ingresos_editados", [])]
                    for r in a_guardar:
                        r.pop("Estado", None)
                    if a_guardar:
                        guardar_movimientos(a_guardar)
                        st.session_state.pop("ingresos_pendientes", None)
                        st.session_state.pop("ingresos_editados", None)
                        st.success(f"✅ {len(a_guardar)} ingreso(s) guardados correctamente")
                        st.rerun()
                    else:
                        st.warning("No has seleccionado ningún registro")
            with col_btn2:
                if st.button("🗑️ Cancelar", key="cancelar_ingresos"):
                    st.session_state.pop("ingresos_pendientes", None)
                    st.session_state.pop("ingresos_editados", None)
                    st.rerun()
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
# Gestión de inmuebles con vista de cards + formulario organizado
# ================================================================
elif menu == "Datos de la Cartera":
    st.markdown('<div class="brand-header">Datos de la Cartera</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Gestión de inmuebles · Backups · Configuración</div>', unsafe_allow_html=True)

    # Inicializar estados de sesión
    if "modo_cartera" not in st.session_state:
        st.session_state.modo_cartera = "lista"  # lista, editar, nuevo
    if "inmueble_editando" not in st.session_state:
        st.session_state.inmueble_editando = None

    # Botones superiores
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    with col_btn1:
        if st.button("📋 Ver Lista", key="btn_lista", use_container_width=True):
            st.session_state.modo_cartera = "lista"
            st.rerun()
    with col_btn2:
        if st.button("➕ Añadir Inmueble", key="btn_nuevo", use_container_width=True):
            st.session_state.modo_cartera = "nuevo"
            st.session_state.inmueble_editando = None
            st.rerun()
    with col_btn3:
        if st.button("📊 Ver Tabla Completa", key="btn_tabla", use_container_width=True):
            st.session_state.modo_cartera = "tabla"
            st.rerun()
    with col_btn4:
        if st.button("💾 Backups", key="btn_backup", use_container_width=True):
            st.session_state.modo_cartera = "backup"
            st.rerun()

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════
    # MODO: LISTA DE INMUEBLES (cards)
    # ═══════════════════════════════════════════════════════════
    if st.session_state.modo_cartera == "lista":
        st.markdown(f'<div class="section-title">🏠 Mis Inmuebles ({len(df_inm)})</div>', unsafe_allow_html=True)
        
        for idx, row in df_inm.iterrows():
            with st.container():
                col_info, col_btn = st.columns([4, 1])
                
                with col_info:
                    st.markdown(f"""
                    <div style="background:{CARD_BG};border:1px solid {BORDER};border-radius:10px;padding:1rem;margin-bottom:0.8rem;">
                        <div style="display:flex;justify-content:space-between;align-items:start;">
                            <div>
                                <div style="font-size:1.1rem;font-weight:600;color:{TEXT_PRI};margin-bottom:4px;">🏠 {row['Nombre']}</div>
                                <div style="font-size:0.85rem;color:{TEXT_SEC};">👤 {row.get('Inquilino', 'Sin inquilino')} · 📍 CP {row.get('CP', 'N/A')}</div>
                                <div style="margin-top:8px;font-size:0.82rem;">
                                    <span style="background:#EDF7F1;color:#3B6D11;padding:3px 8px;border-radius:4px;margin-right:4px;">💰 {row['Renta']:,.0f} €/mes</span>
                                    <span style="background:#F0F6FF;color:{ACCENT};padding:3px 8px;border-radius:4px;margin-right:4px;">📐 {row.get('M2_Construidos', 'N/A')} m²</span>
                                    <span style="background:#FFF9E6;color:#854F0B;padding:3px 8px;border-radius:4px;">🛏️ {row.get('Habitaciones', 'N/A')} hab</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_btn:
                    if st.button("✏️ Editar", key=f"edit_{idx}", use_container_width=True):
                        st.session_state.modo_cartera = "editar"
                        st.session_state.inmueble_editando = idx
                        st.rerun()
                    if st.button("🗑️", key=f"del_{idx}", use_container_width=True):
                        if len(st.session_state.df_inm_persistent) > 1:
                            # Eliminar de session_state
                            df_nuevo = st.session_state.df_inm_persistent.drop(idx).reset_index(drop=True)
                            st.session_state.df_inm_persistent = df_nuevo
                            guardar_inmuebles(df_nuevo, user_id=st.session_state.user_id)
                            st.success(f"✓ {row['Nombre']} eliminado")
                            st.rerun()
                        else:
                            st.error("No puedes eliminar el último inmueble")

    # ═══════════════════════════════════════════════════════════
    # MODO: FORMULARIO (EDITAR O NUEVO)
    # ═══════════════════════════════════════════════════════════
    elif st.session_state.modo_cartera in ["editar", "nuevo"]:
        es_nuevo = st.session_state.modo_cartera == "nuevo"
        titulo = "➕ Añadir Inmueble Nuevo" if es_nuevo else f"✏️ Editar: {df_inm.iloc[st.session_state.inmueble_editando]['Nombre']}"
        
        st.markdown(f'<div class="section-title">{titulo}</div>', unsafe_allow_html=True)

        # Obtener datos actuales si es edición
        if es_nuevo:
            datos = {col: DEFAULTS_FISCAL.get(col, "") for col in COLS_INM}
        else:
            datos = df_inm.iloc[st.session_state.inmueble_editando].to_dict()

        # Helper para convertir valores a float de forma segura
        def safe_float(val, default=0.0):
            try:
                if pd.isna(val) or val in [None, "", "nan", "NaN", "None"]:
                    return default
                result = float(val)
                # Si el resultado es negativo o 0 y el default es mayor, usar default
                if result <= 0 and default > 0:
                    return default
                return result
            except (ValueError, TypeError):
                return default

        def safe_int(val, default=0):
            try:
                if pd.isna(val) or val in [None, "", "nan", "NaN", "None"]:
                    return default
                result = int(float(val))  # float primero por si viene "2.0"
                if result <= 0 and default > 0:
                    return default
                return result
            except (ValueError, TypeError):
                return default

        def safe_index(options, val, default=0):
            """Devuelve el índice de val en options, o default si no existe"""
            try:
                return options.index(val) if val in options else default
            except (ValueError, TypeError):
                return default

        with st.form("form_inmueble"):
            st.markdown("### 📋 Datos Básicos")
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre del Inmueble *", value=datos.get("Nombre", ""), placeholder="Ej: Casa Abarqueros")
                inquilino = st.text_input("Inquilino", value=datos.get("Inquilino", ""), placeholder="Nombre del inquilino")
                renta = st.number_input("Renta Mensual (€) *", value=safe_float(datos.get("Renta"), 0.0), min_value=0.0, step=50.0)
            with col2:
                renta_mercado = st.number_input("Renta de Mercado (€)", value=safe_float(datos.get("Renta_Mercado"), 0.0), min_value=0.0, step=50.0)
                comunidad = st.number_input("Comunidad Mensual (€)", value=safe_float(datos.get("Comunidad"), 0.0), min_value=0.0, step=10.0)
                valor_construccion = st.number_input("Valor Construcción (€) *", value=safe_float(datos.get("Valor_Construccion"), 0.0), min_value=0.0, step=1000.0)

            st.markdown("### 🏠 Características")
            col3, col4, col5 = st.columns(3)
            with col3:
                m2 = st.number_input("M² Construidos *", value=safe_float(datos.get("M2_Construidos"), 80.0), min_value=10.0, step=5.0)
                habitaciones = st.number_input("Habitaciones *", value=safe_int(datos.get("Habitaciones"), 2), min_value=1, max_value=10)
                planta = st.number_input("Planta", value=safe_int(datos.get("Planta"), 1), min_value=0, max_value=20)
            with col4:
                cp = st.text_input("Código Postal *", value=str(datos.get("CP", "18005")), max_chars=5)
                tipo = st.selectbox("Tipo", ["Piso", "Casa", "Estudio", "Local"], index=safe_index(["Piso", "Casa", "Estudio", "Local"], datos.get("Tipo"), 0))
                estado = st.selectbox("Estado", ["Reformado", "Bueno", "Regular"], index=safe_index(["Reformado", "Bueno", "Regular"], datos.get("Estado"), 1))
            with col5:
                mobiliario = st.selectbox("Mobiliario", ["S", "N"], index=0 if datos.get("Mobiliario") == "S" else 1)
                parking = st.selectbox("Parking", ["S", "N"], index=0 if datos.get("Parking") == "S" else 1)
                año_construccion = st.number_input("Año Construcción", value=safe_int(datos.get("Año_Construccion"), 2000), min_value=1900, max_value=2030)

            st.markdown("### 📝 Información Adicional")
            col6, col7 = st.columns(2)
            with col6:
                ref_catastral = st.text_input("Ref. Catastral", value=datos.get("Ref_Catastral", ""), placeholder="00XX00000")
                titular = st.text_input("Titular", value=datos.get("Titular", ""), placeholder="Nombre del propietario")
                año_reforma = st.number_input("Año Última Reforma", value=safe_int(datos.get("Año_Reforma"), 2020), min_value=1900, max_value=2030)
            with col7:
                tipo_arrendamiento = st.selectbox("Tipo Arrendamiento", ["Larga Duración", "Temporada", "Vacacional"], 
                    index=safe_index(["Larga Duración", "Temporada", "Vacacional"], datos.get("Tipo_Arrendamiento"), 0))
                cochera_vinculada = st.selectbox("Cochera Vinculada", ["N", "S"], index=0 if datos.get("Cochera_Vinculada") == "N" else 1)
                zona_tensionada = st.selectbox("Zona Tensionada", ["N", "S"], index=0 if datos.get("Zona_Tensionada") == "N" else 1)

            st.markdown("### 💰 Datos Fiscales")
            col8, col9, col10 = st.columns(3)
            with col8:
                nif_inquilino = st.text_input("NIF Inquilino", value=datos.get("NIF_Inquilino", ""), placeholder="12345678A")
                ibi_anual = st.number_input("IBI Anual (€)", value=safe_float(datos.get("IBI_Anual"), 0.0), min_value=0.0, step=10.0)
            with col9:
                seguro_anual = st.number_input("Seguro Anual (€)", value=safe_float(datos.get("Seguro_Anual"), 0.0), min_value=0.0, step=10.0)
                intereses_hipoteca = st.number_input("Intereses Hipoteca (€)", value=safe_float(datos.get("Intereses_Hipoteca"), 0.0), min_value=0.0, step=100.0)
            with col10:
                gastos_juridicos = st.number_input("Gastos Jurídicos (€)", value=safe_float(datos.get("Gastos_Juridicos"), 0.0), min_value=0.0, step=10.0)
                retenciones_irpf = st.number_input("Retenciones IRPF (€)", value=safe_float(datos.get("Retenciones_IRPF"), 0.0), min_value=0.0, step=10.0)

            st.markdown("### 📅 Contrato")
            col11, col12 = st.columns(2)
            with col11:
                fecha_inicio = st.date_input("Fecha Inicio Contrato", value=pd.to_datetime(datos.get("Fecha_Inicio_Contrato", "2024-01-01")).date() if pd.notna(datos.get("Fecha_Inicio_Contrato")) else date(2024, 1, 1))
            with col12:
                fecha_vencimiento = st.date_input("Fecha Vencimiento Contrato", value=pd.to_datetime(datos.get("Fecha_Vencimiento_Contrato", "2025-12-31")).date() if pd.notna(datos.get("Fecha_Vencimiento_Contrato")) else date(2025, 12, 31))

            col_otros1, col_otros2 = st.columns(2)
            with col_otros1:
                gastos_formalizacion = st.number_input("Gastos Formalización (€)", value=safe_float(datos.get("Gastos_Formalizacion"), 0.0), min_value=0.0, step=10.0)
            with col_otros2:
                gastos_pend_años_ant = st.number_input("Gastos Pend. Años Ant. (€)", value=safe_float(datos.get("Gastos_Pendientes_Años_Ant"), 0.0), min_value=0.0, step=10.0)

            servicios_suministros = st.number_input("Servicios y Suministros (€)", value=safe_float(datos.get("Servicios_Suministros"), 0.0), min_value=0.0, step=10.0)

            st.markdown("---")
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button("💾 Guardar Inmueble", type="primary", use_container_width=True)
            with col_cancel:
                cancelled = st.form_submit_button("❌ Cancelar", use_container_width=True)

            if submitted:
                if not nombre.strip():
                    st.error("El nombre del inmueble es obligatorio")
                elif renta <= 0:
                    st.error("La renta debe ser mayor que 0")
                elif valor_construccion <= 0:
                    st.error("El valor de construcción debe ser mayor que 0")
                else:
                    nuevo_inmueble = {
                        "Nombre": nombre, "Inquilino": inquilino, "Renta": renta, "Renta_Mercado": renta_mercado,
                        "Comunidad": comunidad, "Valor_Construccion": valor_construccion, "Año_Reforma": año_reforma,
                        "Año_Construccion": año_construccion, "Mobiliario": mobiliario, "Tipo": tipo,
                        "Ref_Catastral": ref_catastral, "Titular": titular, "M2_Construidos": m2,
                        "Habitaciones": habitaciones, "CP": cp, "Planta": planta, "Parking": parking,
                        "Estado": estado, "Tipo_Arrendamiento": tipo_arrendamiento,
                        "Cochera_Vinculada": cochera_vinculada, "Zona_Tensionada": zona_tensionada,
                        "Fecha_Inicio_Contrato": fecha_inicio.strftime("%Y-%m-%d"),
                        "Fecha_Vencimiento_Contrato": fecha_vencimiento.strftime("%Y-%m-%d"),
                        "NIF_Inquilino": nif_inquilino, "Intereses_Hipoteca": intereses_hipoteca,
                        "IBI_Anual": ibi_anual, "Seguro_Anual": seguro_anual, "Gastos_Juridicos": gastos_juridicos,
                        "Retenciones_IRPF": retenciones_irpf, "Gastos_Formalizacion": gastos_formalizacion,
                        "Gastos_Pendientes_Años_Ant": gastos_pend_años_ant, "Servicios_Suministros": servicios_suministros
                    }

                    if es_nuevo:
                        df_nuevo = pd.concat([st.session_state.df_inm_persistent, pd.DataFrame([nuevo_inmueble])], ignore_index=True)
                        st.session_state.df_inm_persistent = df_nuevo
                        guardar_inmuebles(df_nuevo, user_id=st.session_state.user_id)
                        st.toast(f"✅ '{nombre}' guardado en Supabase", icon="✅")
                        st.success(f"✅ Inmueble '{nombre}' añadido correctamente")
                        import time; time.sleep(1.5)
                    else:
                        for col, val in nuevo_inmueble.items():
                            st.session_state.df_inm_persistent.at[st.session_state.inmueble_editando, col] = val
                        guardar_inmuebles(st.session_state.df_inm_persistent, user_id=st.session_state.user_id)
                        st.toast(f"✅ '{nombre}' actualizado en Supabase", icon="✅")
                        st.success(f"✅ Inmueble '{nombre}' actualizado correctamente")
                        import time; time.sleep(1.5)
                    
                    st.session_state.modo_cartera = "lista"
                    st.rerun()

            if cancelled:
                st.session_state.modo_cartera = "lista"
                st.rerun()

    # ═══════════════════════════════════════════════════════════
    # MODO: TABLA COMPLETA (data_editor original)
    # ═══════════════════════════════════════════════════════════
    elif st.session_state.modo_cartera == "tabla":
        st.markdown('<div class="section-title">📊 Tabla Completa de Datos</div>', unsafe_allow_html=True)
        st.warning("⚠️ Vista avanzada — solo para usuarios experimentados")
        
        col_cfg = {
            "Tipo_Arrendamiento": st.column_config.SelectboxColumn("Tipo Arrend.", options=["Larga Duración", "Temporada", "Vacacional"], required=True),
            "Cochera_Vinculada": st.column_config.SelectboxColumn("Cochera Vinc.", options=["S", "N"], required=True),
            "Zona_Tensionada": st.column_config.SelectboxColumn("Zona Tensión", options=["S", "N"], required=True),
            "Estado": st.column_config.SelectboxColumn("Estado", options=["Reformado", "Bueno", "Regular"], required=True),
            "Mobiliario": st.column_config.SelectboxColumn("Mobiliario", options=["S", "N"], required=True),
            "Parking": st.column_config.SelectboxColumn("Parking", options=["S", "N"], required=True),
            "IBI_Anual": st.column_config.NumberColumn("IBI/año", format="%.0f €"),
            "Seguro_Anual": st.column_config.NumberColumn("Seguro/año", format="%.0f €"),
            "Intereses_Hipoteca": st.column_config.NumberColumn("Intereses Hip.", format="%.0f €"),
        }
        df_ed = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True, hide_index=True, column_config=col_cfg)
        if st.button("✅ Guardar Cambios de Tabla", type="primary"):
            st.session_state.df_inm_persistent = df_ed
            guardar_inmuebles(df_ed, user_id=st.session_state.user_id)
            st.success("✓ Datos actualizados.")
            st.rerun()

    # ═══════════════════════════════════════════════════════════
    # MODO: BACKUPS
    # ═══════════════════════════════════════════════════════════
    elif st.session_state.modo_cartera == "backup":
        st.markdown('<div class="section-title">💾 Copias de Seguridad</div>', unsafe_allow_html=True)
        st.info("💡 Descarga tus datos regularmente para no perder información")
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.download_button("📥 Descargar Inmuebles (CSV)", generar_csv_backup(st.session_state.df_inm_persistent, "inmuebles"), "nolasco_inmuebles_backup.csv", "text/csv", use_container_width=True)
        with col_b2:
            st.download_button("📥 Descargar Movimientos (CSV)", generar_csv_backup(st.session_state.df_mov_persistent, "movimientos"), "nolasco_movimientos_backup.csv", "text/csv", use_container_width=True)

        st.markdown("---")
        st.markdown("### 📤 Restaurar desde Backup")
        st.caption("Próximamente: podrás subir CSVs para restaurar datos")
        uploaded_inm = st.file_uploader("Subir Inmuebles (CSV)", type=["csv"], key="upload_inm")
        if uploaded_inm:
            st.info("📝 Función de restauración — disponible en Bloque 6")

# ================================================================
# PANTALLA 9 — ASESOR PATRIMONIAL IA
# Flujo: Radar → Matriz → Árbol de Decisión → Proyección
# ================================================================
# ================================================================
# SECCIÓN B2B2C — ASESOR PATRIMONIAL IA
# ================================================================
elif menu == "Asesor Patrimonial IA":
    st.markdown(f"""
    <div style='background:{SIDEBAR_BG};padding:20px 24px 16px;
        border-radius:12px;margin-bottom:24px;
        border-left:4px solid {ACCENT};'>
        <h2 style='color:white;margin:0;font-size:22px'>
            🧠 Asesor Patrimonial IA
        </h2>
        <p style='color:#8899AA;margin:6px 0 0;font-size:14px'>
            Analizamos tu cartera y te conectamos con inmobiliarias cuando lo necesitas.
            Tú controlas tus datos en todo momento.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if df_inm.empty:
        st.info("📭 Añade inmuebles en 'Datos de la Cartera' para usar el Asesor.")
    else:
        datos_propietario = {
            "nombre":   st.session_state.get("user_nombre", ""),
            "email":    st.session_state.get("user_email", st.session_state.user_email or ""),
            "telefono": st.session_state.get("user_telefono", ""),
        }
        render_asesor_ia(
            user_id=st.session_state.user_id,
            df_inmuebles=df_inm,
            datos_propietario=datos_propietario
        )

# FUNCIONES GENERADORAS DE CONTRATOS (antes de la sección Legal)
# ================================================================

# ================================================================
# SECCIÓN B2B2C — PRIVACIDAD Y CONSENTIMIENTOS (RGPD)
# ================================================================
elif menu == "Privacidad y Consentimientos":
    st.markdown(f"""
    <div style='background:{SIDEBAR_BG};padding:20px 24px 16px;
        border-radius:12px;margin-bottom:24px;
        border-left:4px solid #0F6E56;'>
        <h2 style='color:white;margin:0;font-size:22px'>
            🔒 Privacidad y Consentimientos
        </h2>
        <p style='color:#8899AA;margin:6px 0 0;font-size:14px'>
            Gestiona quién tiene acceso a tus datos y revoca permisos en cualquier momento.
        </p>
    </div>
    """, unsafe_allow_html=True)
    render_privacidad(user_id=st.session_state.user_id)

# ================================================================
# LEGAL — GENERADOR DE CONTRATOS
# ================================================================
elif menu == "Legal":
    st.markdown('<div class="brand-header">⚖️ HERRAMIENTAS LEGALES</div>', unsafe_allow_html=True)
    
    # Estilo CSS específico para Legal
    st.markdown("""
    <style>
    .legal-card {
        background: linear-gradient(135deg, #1a3a5c 0%, #2d5a8c 100%);
        border: 2px solid #c9a85c;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(26, 58, 92, 0.15);
    }
    .legal-title {
        color: #c9a85c;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .legal-subtitle {
        color: #e8f2ff;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .contract-card {
        background: white;
        border: 2px solid #e0e7ef;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .contract-card:hover {
        border-color: #c9a85c;
        box-shadow: 0 4px 12px rgba(201, 168, 92, 0.2);
        transform: translateY(-2px);
    }
    .contract-card.selected {
        border-color: #c9a85c;
        background: #fffbf0;
        border-width: 3px;
    }
    .contract-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .contract-name {
        color: #1a3a5c;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.3rem;
    }
    .contract-desc {
        color: #4a5568;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    .legal-section {
        background: #f8fafb;
        border-left: 4px solid #1a3a5c;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1.5rem 0;
    }
    .legal-label {
        color: #1a3a5c;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    .disclaimer {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-left: 4px solid #ff9800;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 2rem;
        color: #856404;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header principal
    st.markdown("""
    <div class="legal-card">
        <div class="legal-title">📋 GENERADOR DE CONTRATOS DE ARRENDAMIENTO</div>
        <div class="legal-subtitle">Genera contratos conformes a LAU 29/1994 con tus datos precargados</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar estado
    if "tipo_contrato_seleccionado" not in st.session_state:
        st.session_state.tipo_contrato_seleccionado = None
    
    # PASO 1: Selección de tipo de contrato
    st.markdown('<div class="legal-section">', unsafe_allow_html=True)
    st.markdown('<div class="legal-label">🏛️ SELECCIONA EL TIPO DE CONTRATO</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📜\n\n**LARGA DURACIÓN**\n\nVivienda habitual\nLAU Art. 9", 
                     key="btn_larga", use_container_width=True,
                     type="primary" if st.session_state.tipo_contrato_seleccionado == "larga" else "secondary"):
            st.session_state.tipo_contrato_seleccionado = "larga"
            st.rerun()
    
    with col2:
        if st.button("⏰\n\n**TEMPORADA**\n\nTurístico o estudios\n≤12 meses", 
                     key="btn_temp", use_container_width=True,
                     type="primary" if st.session_state.tipo_contrato_seleccionado == "temporada" else "secondary"):
            st.session_state.tipo_contrato_seleccionado = "temporada"
            st.rerun()
    
    with col3:
        if st.button("🛏️\n\n**HABITACIÓN**\n\nSubarrienda habitación\nLAU parcial", 
                     key="btn_hab", use_container_width=True,
                     type="primary" if st.session_state.tipo_contrato_seleccionado == "habitacion" else "secondary"):
            st.session_state.tipo_contrato_seleccionado = "habitacion"
            st.rerun()
    
    # Mostrar formulario solo si hay tipo seleccionado
    if st.session_state.tipo_contrato_seleccionado:
        tipo = st.session_state.tipo_contrato_seleccionado
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # PASO 2: Seleccionar inmueble
        st.markdown('<div class="legal-section">', unsafe_allow_html=True)
        st.markdown('<div class="legal-label">📍 INMUEBLE</div>', unsafe_allow_html=True)
        inmueble_seleccionado = st.selectbox(
            "Selecciona el inmueble",
            options=df_inm["Nombre"].tolist(),
            key="inmueble_legal",
            label_visibility="collapsed"
        )
        
        # Obtener datos del inmueble
        inm_data = df_inm[df_inm["Nombre"] == inmueble_seleccionado].iloc[0]
        st.caption(f"📍 Ref. Catastral: {inm_data.get('Ref_Catastral', 'N/A')} | {inm_data.get('M2_Construidos', 0)}m²")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # PASO 3: Duración
        st.markdown('<div class="legal-section">', unsafe_allow_html=True)
        st.markdown('<div class="legal-label">⏳ DURACIÓN</div>', unsafe_allow_html=True)
        
        col_dur1, col_dur2 = st.columns(2)
        with col_dur1:
            if tipo == "larga":
                duracion_anos = st.selectbox("Años", options=[1, 2, 3, 4, 5], index=2, key="dur_anos")
                duracion_meses = 0
            else:
                duracion_meses = st.selectbox("Meses", options=list(range(1, 13)), index=5, key="dur_meses")
                duracion_anos = 0
        
        with col_dur2:
            st.caption("✓ Larga duración: 1-5 años" if tipo == "larga" else "✓ Temporada: máximo 12 meses")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # PASO 4: Condiciones económicas
        st.markdown('<div class="legal-section">', unsafe_allow_html=True)
        st.markdown('<div class="legal-label">💰 CONDICIONES ECONÓMICAS</div>', unsafe_allow_html=True)
        
        renta = inm_data.get("Renta", 0)
        st.write(f"**Renta mensual:** {renta:,.0f}€ _(precargado desde tu cartera)_")
        
        tipo_fianza = st.radio(
            "Fianza",
            options=["1 mes", "2 meses", "Sin fianza"],
            index=1 if tipo == "larga" else 0,
            horizontal=True,
            key="fianza_tipo"
        )
        
        if "Sin fianza" in tipo_fianza:
            importe_fianza = 0
        elif "1 mes" in tipo_fianza:
            importe_fianza = renta
        else:
            importe_fianza = renta * 2
        
        st.caption(f"💵 Importe fianza: {importe_fianza:,.0f}€")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # PASO 5: Suministros
        st.markdown('<div class="legal-section">', unsafe_allow_html=True)
        st.markdown('<div class="legal-label">⚡ SUMINISTROS</div>', unsafe_allow_html=True)
        
        col_sum1, col_sum2 = st.columns(2)
        with col_sum1:
            incluye_luz = st.checkbox("⚡ Incluye electricidad", key="sum_luz")
            incluye_gas = st.checkbox("🔥 Incluye gas", key="sum_gas")
        with col_sum2:
            incluye_internet = st.checkbox("📡 Incluye internet", key="sum_int")
            incluye_agua = st.checkbox("💧 Incluye agua _(no recomendado)_", key="sum_agua")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # PASO 6: Opciones adicionales
        st.markdown('<div class="legal-section">', unsafe_allow_html=True)
        st.markdown('<div class="legal-label">📊 ACTUALIZACIÓN Y OPCIONES</div>', unsafe_allow_html=True)
        
        ipc_anual = st.checkbox("✓ Actualización anual según IPC", value=True, key="ipc")
        
        mascotas = st.radio(
            "🐕 Mascotas",
            options=["Permitidas", "No permitidas", "A consultar"],
            index=1,
            horizontal=True,
            key="mascotas"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # GENERAR CONTRATO
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚖️ GENERAR CONTRATO", type="primary", use_container_width=True, key="generar_contrato"):
            # Aquí generaremos el contrato
            st.success("✅ Contrato generado correctamente")
            
            # Preparar datos para el template
            contrato_data = {
                "tipo": tipo,
                "inmueble": inmueble_seleccionado,
                "direccion": "Calle ejemplo, 1",  # TODO: añadir campo dirección en CSV
                "ref_catastral": inm_data.get('Ref_Catastral', 'N/A'),
                "m2": inm_data.get('M2_Construidos', 0),
                "renta": renta,
                "duracion_anos": duracion_anos,
                "duracion_meses": duracion_meses,
                "fianza_meses": 0 if "Sin" in tipo_fianza else (1 if "1 mes" in tipo_fianza else 2),
                "importe_fianza": importe_fianza,
                "incluye_luz": incluye_luz,
                "incluye_gas": incluye_gas,
                "incluye_internet": incluye_internet,
                "incluye_agua": incluye_agua,
                "ipc": ipc_anual,
                "mascotas": mascotas
            }
            
            # Generar contrato según tipo
            if tipo == "larga":
                contrato_texto = generar_contrato_larga_duracion(contrato_data)
            elif tipo == "temporada":
                contrato_texto = generar_contrato_temporada(contrato_data)
            else:
                contrato_texto = generar_contrato_habitacion(contrato_data)
            
            # Generar PDF
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import cm
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
                from io import BytesIO
                
                # Crear PDF en memoria
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                       leftMargin=2*cm, rightMargin=2*cm,
                                       topMargin=2*cm, bottomMargin=2*cm)
                
                # Estilos
                styles = getSampleStyleSheet()
                
                # Estilo título
                titulo_style = ParagraphStyle(
                    'TituloLegal',
                    parent=styles['Heading1'],
                    fontSize=16,
                    textColor='#1a3a5c',
                    alignment=TA_CENTER,
                    spaceAfter=20
                )
                
                # Estilo cuerpo
                cuerpo_style = ParagraphStyle(
                    'CuerpoLegal',
                    parent=styles['Normal'],
                    fontSize=10,
                    alignment=TA_JUSTIFY,
                    leading=14,
                    spaceAfter=10
                )
                
                # Estilo cláusula
                clausula_style = ParagraphStyle(
                    'ClausulaLegal',
                    parent=styles['Normal'],
                    fontSize=10,
                    fontName='Helvetica-Bold',
                    spaceAfter=8
                )
                
                # Construir documento
                story = []
                
                # Parsear el texto y crear párrafos
                lineas = contrato_texto.strip().split('\n')
                for linea in lineas:
                    linea = linea.strip()
                    if not linea:
                        story.append(Spacer(1, 0.3*cm))
                    elif '═' in linea:
                        story.append(Spacer(1, 0.5*cm))
                    elif linea.isupper() and len(linea) < 80:
                        # Título
                        story.append(Paragraph(linea, titulo_style))
                    elif linea.endswith('.-'):
                        # Cláusula
                        story.append(Paragraph(linea, clausula_style))
                    else:
                        # Cuerpo normal
                        story.append(Paragraph(linea, cuerpo_style))
                
                # Generar PDF
                doc.build(story)
                pdf_bytes = buffer.getvalue()
                buffer.close()
                
                pdf_disponible = True
                
            except ImportError:
                pdf_disponible = False
                pdf_bytes = None
            
            # Mostrar preview
            with st.expander("📄 PREVIEW DEL CONTRATO", expanded=True):
                st.text(contrato_texto)
            
            # Botones de descarga
            col_down1, col_down2 = st.columns(2)
            
            with col_down1:
                if pdf_disponible:
                    st.download_button(
                        label="📥 Descargar PDF (recomendado)",
                        data=pdf_bytes,
                        file_name=f"contrato_{tipo}_{inmueble_seleccionado.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary"
                    )
                else:
                    st.warning("⚠️ Instala `reportlab` para generar PDFs")
            
            with col_down2:
                st.download_button(
                    label="📥 Descargar TXT (alternativo)",
                    data=contrato_texto,
                    file_name=f"contrato_{tipo}_{inmueble_seleccionado.replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
    
    # Disclaimer legal
    st.markdown("""
    <div class="disclaimer">
        <strong>⚠️ AVISO LEGAL</strong><br>
        Este generador crea contratos orientativos basados en la Ley de Arrendamientos Urbanos (LAU 29/1994).<br>
        <strong>NO sustituye asesoramiento legal profesional.</strong> Consulte con un abogado antes de firmar.<br>
        El contenido generado es informativo y no vinculante.
    </div>
    """, unsafe_allow_html=True)
