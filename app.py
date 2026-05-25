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
from cashflow_module import render_cashflow
from kpi_renderer import render_kpi_row

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
from sabio_patrimonial import render_sabio, limpiar_insight_seccion

# ================================================================
# SECCIÓN 1 — CONFIGURACIÓN Y COLORES
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
# SECCIÓN 2 — ESTILOS CSS (Design System Nolasco Capital)
# ================================================================
from nolasco_styles import inject_global_css
APP = "capital"
inject_global_css(APP)

# CSS adicional para botones de navegación del sidebar
st.markdown("""
<style>
[data-testid="stSidebar"] button[kind="secondary"] {
    background: transparent !important;
    border: none !important;
    color: rgba(255,255,255,0.82) !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.45rem 0.8rem !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] button[kind="secondary"] p {
    color: rgba(255,255,255,0.82) !important;
    font-size: 0.92rem !important;
}
</style>
""", unsafe_allow_html=True)

# ================================================================
# SECCIÓN 3 — BASE DE DATOS SUPABASE
# ================================================================
from supabase_db import (
    leer_inmuebles, leer_movimientos,
    guardar_inmuebles, eliminar_inmueble, guardar_movimientos_completo,
    agregar_movimientos, generar_csv_backup,
    login_usuario, registrar_usuario,
    leer_gastos_recurrentes, guardar_gasto_recurrente,
    actualizar_gasto_recurrente, eliminar_gasto_recurrente,
    generar_codigo_acceso, obtener_codigo_activo, revocar_codigo_acceso,
    upsert_inmueble, guardar_logo_usuario, leer_logo_usuario, health_check,
    subir_factura, obtener_url_factura, eliminar_factura,
    actualizar_estado_fiscal_movimiento,
    leer_perfil_usuario, guardar_perfil_usuario,
    cambiar_contrasena, cambiar_email,
    leer_plantillas_factura, guardar_plantilla_factura,
    leer_facturas_emitidas, crear_factura_emitida,
    actualizar_estado_factura, guardar_pdf_factura,
    crear_factura_rectificativa
)

COLS_INM = [
    "Nombre","Inquilino","Renta","Renta_Mercado","Comunidad","Valor_Construccion",
    "Año_Reforma","Año_Construccion","Mobiliario","Tipo","Ref_Catastral","Titular",
    "M2_Construidos","Habitaciones","CP","Planta","Parking","Estado",
    "Tipo_Arrendamiento","Cochera_Vinculada","Zona_Tensionada",
    "Fecha_Inicio_Contrato","Fecha_Vencimiento_Contrato",
    "NIF_Inquilino","Intereses_Hipoteca","IBI_Anual","Seguro_Anual",
    "Gastos_Juridicos","Retenciones_IRPF","Gastos_Formalizacion",
    "Fecha_Adquisicion","Precio_Compra","Impuestos_Compra","Gastos_Compra",
    "Valor_Catastral","Valor_Catastral_Piso","Pct_Suelo","Pct_Construccion",
    "Valor_Real_Construccion","Amortizacion_Fiscal","Seguro_Vida",
    "Gasto_Ascensor","Ref_Catastral_Cochera","IBI_Cocheras","Comunidad_Cocheras",
    "IVA_Aplicable","Tipo_IVA","Retencion_IRPF_Pct","Dias_Arrendados_Anio",
    "Gastos_Pendientes_Años_Ant","Servicios_Suministros"
]

DEFAULTS_FISCAL = {
    "Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N","Zona_Tensionada":"N",
    "Fecha_Inicio_Contrato":"2022-01-01","Fecha_Vencimiento_Contrato":"2027-01-01",
    "NIF_Inquilino":"","Intereses_Hipoteca":0,"IBI_Anual":0,"Seguro_Anual":0,
    "Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,
    "Fecha_Adquisicion":None,"Precio_Compra":0,"Impuestos_Compra":0,"Gastos_Compra":0,
    "Valor_Catastral":0,"Valor_Catastral_Piso":0,"Pct_Suelo":0.25,"Pct_Construccion":0.75,
    "Valor_Real_Construccion":0,"Amortizacion_Fiscal":0,"Seguro_Vida":0,
    "Gasto_Ascensor":0,"Ref_Catastral_Cochera":"","IBI_Cocheras":0,"Comunidad_Cocheras":0,
    "IVA_Aplicable":False,"Tipo_IVA":21,"Retencion_IRPF_Pct":0,"Dias_Arrendados_Anio":365,
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
if "filtro_año" not in st.session_state:
    st.session_state.filtro_año = "Todos"
if "filtro_mes" not in st.session_state:
    st.session_state.filtro_mes = "Todos"

if not st.session_state.user_logged_in:
    st.markdown("""
<style>
.stApp { background: #0F2744 !important; }
.login-card {
    background: white; border-radius: 16px; padding: 2.5rem 2.5rem 2rem;
    max-width: 480px; margin: 4rem auto 0; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.login-title { font-family: 'DM Serif Display', Georgia, serif; font-size: 2rem; color: #0F2744; margin-bottom: 0.2rem; }
.login-sub { font-size: 0.68rem; letter-spacing: 0.18em; text-transform: uppercase; color: #5A7A9A; border-bottom: 2px solid #185FA5; padding-bottom: 0.8rem; margin-bottom: 1.2rem; }
.login-desc { font-size: 0.9rem; color: #3a5a7a; margin-bottom: 1.5rem; line-height: 1.5; }
div[data-testid="stTextInput"] label { font-size: 0.65rem !important; letter-spacing: 0.12em !important; text-transform: uppercase !important; color: #5A7A9A !important; font-weight: 600 !important; }
div[data-testid="stTextInput"] input { border: 1.5px solid #D0DFF0 !important; border-radius: 8px !important; padding: 0.6rem 0.8rem !important; font-size: 0.95rem !important; }
div[data-testid="stTextInput"] input:focus { border-color: #185FA5 !important; box-shadow: 0 0 0 3px rgba(24,95,165,0.1) !important; }
div.stButton > button { background: #185FA5 !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 0.7rem !important; font-size: 1rem !important; font-weight: 600 !important; width: 100% !important; margin-top: 0.5rem !important; }
div.stButton > button:hover { background: #0F4A8A !important; }
</style>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="login-card">
  <div class="login-title">Nolasco Capital</div>
  <div class="login-sub">Granada · Tu Patrimonio Inmobiliario</div>
  <div class="login-desc">Gestiona tu cartera, descubre cuánto pierdes frente al mercado y simula tus impuestos. <strong>Gratis siempre.</strong></div>
</div>
""", unsafe_allow_html=True)

    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        if "login_modo" not in st.session_state:
            st.session_state.login_modo = "login"

        if st.session_state.login_modo == "login":
            email_login    = st.text_input("Email", key="email_login", placeholder="tu@email.com")
            password_login = st.text_input("Contraseña", type="password", key="password_login", placeholder="••••••••")
            if st.button("🚀 Iniciar sesión", use_container_width=True):
                if email_login and password_login:
                    result = login_usuario(email_login, password_login)
                    if result['success']:
                        st.session_state.user_logged_in = True
                        st.session_state.user_id = result['user_id']
                        st.session_state.user_email = result['email']
                        for k in ["df_inm_persistent","df_mov_persistent","sidebar_logo_bytes","supabase_ok","df_gastos_rec","datos_propietario","perfil_datos"]:
                            if k in st.session_state: del st.session_state[k]
                        st.success(f"✅ Bienvenido {result['email']}")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")
                else:
                    st.warning("⚠️ Completa todos los campos")
            st.markdown("<div style='text-align:center;margin-top:1rem;font-size:0.85rem;color:#8ab4d4;'>¿Sin cuenta?</div>", unsafe_allow_html=True)
            if st.button("Regístrate gratis →", use_container_width=False, key="ir_registro"):
                st.session_state.login_modo = "registro"; st.rerun()
        else:
            st.markdown("<div style='font-size:1rem;font-weight:600;color:white;margin-bottom:1rem;'>Crear cuenta nueva</div>", unsafe_allow_html=True)
            email_reg     = st.text_input("Email", key="email_reg", placeholder="tu@email.com")
            password_reg  = st.text_input("Contraseña", type="password", key="password_reg", placeholder="••••••••")
            password_reg2 = st.text_input("Repetir Contraseña", type="password", key="password_reg2", placeholder="••••••••")
            if st.button("Crear cuenta", use_container_width=True):
                if email_reg and password_reg and password_reg2:
                    if password_reg == password_reg2:
                        if len(password_reg) >= 6:
                            result = registrar_usuario(email_reg, password_reg)
                            if result['success']:
                                st.success("✅ Cuenta creada. Ahora inicia sesión.")
                                st.session_state.login_modo = "login"; st.rerun()
                            else:
                                st.error(f"❌ {result['error']}")
                        else:
                            st.warning("⚠️ La contraseña debe tener al menos 6 caracteres")
                    else:
                        st.warning("⚠️ Las contraseñas no coinciden")
                else:
                    st.warning("⚠️ Completa todos los campos")
            if st.button("← Volver al login", use_container_width=False, key="ir_login"):
                st.session_state.login_modo = "login"; st.rerun()

    st.stop()

# ================================================================
# SECCIÓN 5 — CARGA DE DATOS DESDE SUPABASE
# ================================================================
if "df_inm_persistent" not in st.session_state:
    st.session_state.df_inm_persistent = leer_inmuebles(user_id=st.session_state.user_id)

# ── Health check Supabase (una vez por sesión) ─────────────────
if "supabase_ok" not in st.session_state:
    hc = health_check()
    st.session_state["supabase_ok"] = hc["ok"]
    if not hc["ok"]:
        st.error(f"⚠️ Sin conexión con Supabase: {hc.get('error','')}. Los datos no se guardarán.")
        st.stop()

# Cargar logo desde Supabase Storage (una vez por sesión)
if "sidebar_logo_bytes" not in st.session_state:
    logo_cargado = leer_logo_usuario(st.session_state.user_id)
    if logo_cargado:
        st.session_state["sidebar_logo_bytes"] = logo_cargado
if "df_mov_persistent" not in st.session_state:
    st.session_state.df_mov_persistent = leer_movimientos(user_id=st.session_state.user_id)

df_inm = st.session_state.df_inm_persistent
df_mov = st.session_state.df_mov_persistent
_sin_inmuebles = df_inm is None or len(df_inm) == 0

# ================================================================
# SECCIÓN 5B — DATOS DE HIPOTECAS
# Hipotecas cargadas desde Supabase por user_id
# ================================================================
def _cargar_hipotecas_supabase():
    from supabase_db import leer_hipotecas
    uid = st.session_state.get("user_id", "")
    df = leer_hipotecas(uid) if uid else pd.DataFrame()
    # Normalizar columnas para compatibilidad con el resto del código
    col_map = {
        "inmueble": "Inmueble", "principal": "Principal",
        "tasa_inicial": "Tasa_Inicial", "plazo_años": "Plazo_Años",
        "fecha_inicio": "Fecha_Inicio", "es_variable": "Es_Variable",
        "indice_variable": "Indice_Variable", "margen": "Margen",
        "saldo_actual": "Saldo_Actual"
    }
    if not df.empty:
        df = df.rename(columns=col_map)
    else:
        df = pd.DataFrame(columns=list(col_map.values()) + ["id"])
    return df

if "df_hip" not in st.session_state:
    st.session_state.df_hip = _cargar_hipotecas_supabase()
df_hip = st.session_state.df_hip

if "menu" not in st.session_state:      st.session_state.menu = "Torre de Control"
if "ficha_sel" not in st.session_state:  st.session_state.ficha_sel = None

# ================================================================
# SECCIÓN 6 — MENÚ DE NAVEGACIÓN
# Para añadir pantalla: agrega ("🔑", "Nombre", "Grupo") aquí
# ================================================================
PAGES = [
    ("📊", "Torre de Control",              "Core"),
    ("🏠", "Fichas (Benchmark)",            "Core"),
    ("📥", "Ingresos · Rentas",             "Core"),
    ("📝", "Gastos",                         "Core"),
    ("💵", "Cash Flow",                     "Core"),
    ("⚡", "Suministros",                   "Core"),
    ("💰", "Fiscalidad",                    "Core"),
    ("💎", "Macrofinanzas",                 "Core"),
    ("🧠", "Asesor Patrimonial IA",         "B2B2C"),
    ("🔒", "Privacidad y Consentimientos",  "B2B2C"),
    ("🔗", "Compartir con Asesor",           "B2B2C"),
    ("⚖️", "Legal",                         "Tools"),
    ("📂", "Datos de la Cartera",           "Config"),
    ("👤", "Mi Perfil",                     "Config"),
]

with st.sidebar:
    # ── LOGO (solo lectura — editar en Mi Perfil) ──────────────
    logo_bytes = st.session_state.get("sidebar_logo_bytes")
    if logo_bytes:
        st.image(logo_bytes, use_container_width=True)

    st.markdown("""
<div style='padding:0.8rem 1.4rem 1rem;'>
  <div style='font-family:"DM Serif Display",serif;font-size:1.5rem;color:#FFFFFF;line-height:1.2;'>Nolasco Capital</div>
  <div style='font-size:0.6rem;letter-spacing:0.18em;text-transform:uppercase;color:rgba(255,255,255,0.45);margin-top:4px;'>Granada · Gestión Patrimonial</div>
</div>
<hr style='border:0;border-top:1px solid rgba(255,255,255,0.1);margin:0 0 0.6rem 0;'>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div style='padding:0.5rem 1rem;background:rgba(255,255,255,0.07);border-radius:6px;margin:0 1rem 1rem;'>
    <div style='font-size:0.7rem;color:rgba(255,255,255,0.45);'>👤 Usuario</div>
    <div style='font-size:0.85rem;color:#fff;margin-top:2px;'>{st.session_state.user_email}</div>
</div>
""", unsafe_allow_html=True)

    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.user_logged_in = False
        st.session_state.user_id = None
        st.session_state.user_email = None
        for k in ["df_inm_persistent","df_mov_persistent","sidebar_logo_bytes"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    def nav_group(label, grupo_id):
        st.markdown(f"<div style='font-size:0.62rem;letter-spacing:0.15em;text-transform:uppercase;color:rgba(255,255,255,0.4);padding:0.5rem 1rem 0.3rem;'>{label}</div>", unsafe_allow_html=True)
        for icon, page, grupo in PAGES:
            if grupo != grupo_id: continue
            is_active = st.session_state.menu == page
            if is_active:
                st.markdown(f"""<div style='background:rgba(96,180,255,0.18);border-left:3px solid #60B4FF;
                    padding:0.55rem 1rem;border-radius:0 6px 6px 0;margin-bottom:2px;
                    display:flex;align-items:center;gap:10px;'>
                    <span style='font-size:1.05rem;'>{icon}</span>
                    <span style='font-size:0.95rem;font-weight:700;color:#FFFFFF;'>{page}</span>
                </div>""", unsafe_allow_html=True)
            else:
                if st.button(f"{icon}  {page}", key=f"nav_{page}", use_container_width=True):
                    st.session_state.menu = page; st.rerun()

    nav_group("Gestión", "Core")
    st.markdown("<hr style='border:0;border-top:1px solid rgba(255,255,255,0.08);margin:0.5rem 0;'>", unsafe_allow_html=True)
    nav_group("Servicios IA", "B2B2C")
    st.markdown("<hr style='border:0;border-top:1px solid rgba(255,255,255,0.08);margin:0.5rem 0;'>", unsafe_allow_html=True)
    nav_group("Herramientas", "Tools")
    st.markdown("<hr style='border:0;border-top:1px solid rgba(255,255,255,0.08);margin:0.5rem 0;'>", unsafe_allow_html=True)
    nav_group("Configuración", "Config")

    st.markdown(f"""
    <hr style='border:0;border-top:1px solid rgba(255,255,255,0.08);margin:0.8rem 0 0.4rem;'>
    <div style='padding:0.3rem 1rem;font-size:0.68rem;color:rgba(255,255,255,0.3);'>
        {len(df_inm)} activos · {datetime.now().strftime('%b %Y')}
    </div>""", unsafe_allow_html=True)

menu = st.session_state.menu

# ================================================================
# SECCIÓN 7 — FUNCIONES AUXILIARES GLOBALES
# ⚠️  safe_float definida UNA SOLA VEZ aquí — no duplicar
# bench_pill, safe_float, safe_int, safe_index, tasacion,
# alerta_vencimiento, guardar_movimientos, parsear_ingresos
# ================================================================
def safe_float(value, default=0):
    """Convierte valor a float de forma segura. Única definición global."""
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return float(default)
        return float(value)
    except:
        return float(default)

def safe_int(val, default=0):
    """Convierte valor a int de forma segura."""
    try:
        if pd.isna(val) or val in [None, "", "nan", "NaN", "None"]:
            return default
        return int(float(val))
    except (ValueError, TypeError):
        return default

def safe_index(options, val, default=0):
    """Devuelve el índice de val en options, o default si no existe."""
    try:
        return options.index(val) if val in options else default
    except (ValueError, TypeError):
        return default

def bench_pill(desv):
    if desv < -15: return "pill-red","🔴"
    if desv < -5:  return "pill-amber","🟡"
    return "pill-green","🟢"

PRECIOS_CP = {
    "18001":12.5,"18002":11.8,"18003":10.2,"18004":10.8,"18005":11.2,
    "18006":10.0,"18007":9.5,"18008":10.4,"18009":8.2,"18010":9.8,
    "18011":10.1,"18012":9.6,"18013":9.0,"18014":9.3,"18015":8.8
}

def tasacion(row):
    p   = PRECIOS_CP.get(str(row.get("CP","18005")),10.0)
    m2  = safe_float(row.get("M2_Construidos",80))
    am  = 1.05 if row.get("Mobiliario")=="S" else 1.0
    ap  = 1.04 if row.get("Parking")=="S" else 1.0
    ae  = {"Reformado":1.08,"Bueno":1.0,"Regular":0.92}.get(row.get("Estado","Bueno"),1.0)
    pl  = int(row.get("Planta",1))
    apl = 0.95 if pl==0 else (1.03 if pl>=3 else 1.0)
    h   = int(row.get("Habitaciones",2))
    ah  = 1.05 if h>=4 else (0.97 if h==1 else 1.0)
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
    user_id = st.session_state.get("user_id", "")
    agregar_movimientos(nuevos, user_id)
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

    def mencionado(nombre):
        partes = [nombre.lower()] + [p.lower() for p in nombre.split()]
        return any(p in texto_l for p in partes if len(p) > 2)

    mencionados = [n for n in nombres if mencionado(n)]
    palabras_negativas = ["no ","pendiente","falta","sin pagar","no ha","no pagó","no pago","excepto","menos"]
    es_negativo = any(p in texto_l for p in palabras_negativas)

    if "todos" in texto_l and not es_negativo and not mencionados:
        for n in nombres:
            registros.append({"Fecha":hoy,"Apartamento":n,"Concepto":f"Renta {mes}","Categoría":"Ingresos","Tipo":"Ingreso","Importe":rentas.get(n,0),"Deducible":"S","Estado":"Cobrado"})
    elif "todos" in texto_l and mencionados:
        for n in nombres:
            estado = "Pendiente" if n in mencionados else "Cobrado"
            registros.append({"Fecha":hoy,"Apartamento":n,"Concepto":f"Renta {mes}","Categoría":"Ingresos","Tipo":"Ingreso","Importe":rentas.get(n,0),"Deducible":"S","Estado":estado})
    elif mencionados and not es_negativo:
        for n in mencionados:
            registros.append({"Fecha":hoy,"Apartamento":n,"Concepto":f"Renta {mes}","Categoría":"Ingresos","Tipo":"Ingreso","Importe":rentas.get(n,0),"Deducible":"S","Estado":"Cobrado"})
    elif mencionados and es_negativo:
        for n in mencionados:
            registros.append({"Fecha":hoy,"Apartamento":n,"Concepto":f"Renta {mes}","Categoría":"Ingresos","Tipo":"Ingreso","Importe":rentas.get(n,0),"Deducible":"S","Estado":"Pendiente"})
    return registros

# ================================================================
# SECCIÓN 8 — FUNCIONES FISCALES (Modelo 100 IRPF)
# ================================================================
def calcular_dias_arrendado(row, año_fiscal=None):
    try:
        inicio = datetime.strptime(str(row.get("Fecha_Inicio_Contrato","")), "%Y-%m-%d").date()
        fin    = datetime.strptime(str(row.get("Fecha_Vencimiento_Contrato","")), "%Y-%m-%d").date()
        hoy    = date.today()
        año_actual = año_fiscal if año_fiscal else hoy.year - 1 if hoy.month < 7 else hoy.year
        inicio_año = date(año_actual, 1, 1)
        fin_año    = date(año_actual, 12, 31)
        inicio_efectivo = max(inicio, inicio_año)
        fin_efectivo    = min(fin, fin_año)
        if inicio_efectivo > fin_efectivo: return 0
        return (fin_efectivo - inicio_efectivo).days + 1
    except:
        return 365

def calcular_modelo_100(row, df_mov_local, año_fiscal=None, tipo_cuenta=None):
    # Si no se pasa tipo_cuenta, leer del perfil en session_state
    if tipo_cuenta is None:
        import streamlit as _st
        _perfil = _st.session_state.get("perfil_datos", {})
        tipo_cuenta = _perfil.get("tipo_cuenta", "particular")
    import re as _re2
    dias_arrendado = int(safe_float(row.get("Dias_Arrendados_Anio", 365)))
    if dias_arrendado <= 0: dias_arrendado = 365
    factor_dias = min(dias_arrendado, 365) / 365
    renta_mensual = safe_float(row.get("Renta", 0))
    ingresos_integros = round(renta_mensual * 12 * factor_dias, 2)
    intereses = round(safe_float(row.get("Intereses_Hipoteca", 0)) * factor_dias, 2)
    gastos_reparacion = round(df_mov_local[
        (df_mov_local["Apartamento"] == row["Nombre"]) &
        (df_mov_local["Tipo"] == "Gasto") &
        (df_mov_local["Categoría"].isin(["Mantenimiento", "Reparación"]))
    ]["Importe"].sum() * factor_dias, 2)
    ibi_anual = round(safe_float(row.get("IBI_Anual", 0)) * factor_dias, 2)
    comunidad_anual = safe_float(row.get("Comunidad", 0)) * 12
    seguro_hogar    = safe_float(row.get("Seguro_Anual", 0))
    seguro_vida     = safe_float(row.get("Seguro_Vida", 0))
    gasto_ascensor  = safe_float(row.get("Gasto_Ascensor", 0))
    formalizacion   = safe_float(row.get("Gastos_Formalizacion", 0))
    casilla_0110 = round((comunidad_anual + seguro_hogar + seguro_vida + gasto_ascensor + formalizacion) * factor_dias, 2)
    servicios = round(safe_float(row.get("Servicios_Suministros", 0)) * factor_dias, 2)
    gastos_juridicos = round(safe_float(row.get("Gastos_Juridicos", 0)) * factor_dias, 2)
    precio_compra    = safe_float(row.get("Precio_Compra", 0))
    impuestos_compra = safe_float(row.get("Impuestos_Compra", 0))
    gastos_compra_v  = safe_float(row.get("Gastos_Compra", 0))
    valor_catastral  = safe_float(row.get("Valor_Catastral", 0))
    pct_construccion = safe_float(row.get("Pct_Construccion", 0.75))
    titular_str = str(row.get("Titular", "100"))
    _m = _re2.search(r'(\d+(?:\.\d+)?)', titular_str)
    pct_titular = float(_m.group(1)) / 100 if _m else 1.0
    if pct_titular > 1: pct_titular = pct_titular / 100
    base_compra = precio_compra + impuestos_compra + gastos_compra_v
    if base_compra == 0: base_compra = safe_float(row.get("Valor_Construccion", 0))
    base_amortizacion = max(base_compra, valor_catastral) * pct_construccion
    amortizacion = round(base_amortizacion * 0.03 * pct_titular * factor_dias, 2)
    gastos_años_ant = round(safe_float(row.get("Gastos_Pendientes_Años_Ant", 0)), 2)
    total_gastos = round(intereses + gastos_reparacion + ibi_anual + casilla_0110 +
                         servicios + gastos_juridicos + amortizacion + gastos_años_ant, 2)
    rendimiento_neto = round(ingresos_integros - total_gastos, 2)
    tipo_arrendamiento = str(row.get("Tipo_Arrendamiento", "Larga Duración"))
    retenciones = safe_float(row.get("Retenciones_IRPF", 0))

    # ── Rama IS (Sociedad Patrimonial) ──────────────────────────
    if tipo_cuenta == "sociedad":
        reduccion_pct     = 0.00  # Sin reducción en IS
        reduccion_importe = 0.00
        rendimiento_final = round(rendimiento_neto, 2)
        cuota_is          = round(max(rendimiento_final * 0.25, 0), 2)
        return {
            "0062_0075":      f"Ref: {row.get('Ref_Catastral', 'N/A')}",
            "0076":           "A (Arrendamiento)",
            "0100":           "SÍ" if tipo_arrendamiento == "Larga Duración" else "NO",
            "0101":           dias_arrendado,
            "0102":           ingresos_integros,
            "0105":           intereses,
            "0106":           gastos_reparacion,
            "0107":           total_gastos,
            "0108":           ibi_anual,
            "0110":           casilla_0110,
            "0111":           servicios,
            "0112":           gastos_juridicos,
            "0113":           amortizacion,
            "0113_detalle":   f"MAX({base_compra:,.0f}€ compra, {valor_catastral:,.0f}€ catastral) × {pct_construccion*100:.0f}% × 3% × {pct_titular*100:.0f}%",
            "0149":           rendimiento_neto,
            "0150":           reduccion_importe,
            "0152":           rendimiento_final,
            "0153":           round(retenciones, 2),
            "reduccion_pct":  0,
            "nota_reduccion": "ℹ️ Sociedad Patrimonial: IS al 25% sin reducción por arrendamiento",
            "iva_aplicable":  bool(row.get("IVA_Aplicable", False)),
            "tipo_arrendamiento": tipo_arrendamiento,
            # Casillas específicas Modelo 200
            "m200_318":       ingresos_integros,
            "m200_319":       total_gastos,
            "m200_320":       amortizacion,
            "m200_399":       rendimiento_final,
            "cuota_is_25":    cuota_is,
            "modo_fiscal":    "IS",
        }

    # ── Rama IRPF (Particular) — comportamiento original ────────
    reduccion_pct = 0.60 if tipo_arrendamiento == "Larga Duración" else 0.00
    reduccion_importe = round(rendimiento_neto * reduccion_pct, 2)
    rendimiento_final = round(rendimiento_neto - reduccion_importe, 2)
    return {
        "0062_0075":     f"Ref: {row.get('Ref_Catastral', 'N/A')}",
        "0076":          "A (Arrendamiento)",
        "0100":          "SÍ" if tipo_arrendamiento == "Larga Duración" else "NO",
        "0101":          dias_arrendado,
        "0102":          ingresos_integros,
        "0105":          intereses,
        "0106":           gastos_reparacion,
        "0107":          total_gastos,
        "0108":          ibi_anual,
        "0110":          casilla_0110,
        "0111":          servicios,
        "0112":          gastos_juridicos,
        "0113":          amortizacion,
        "0113_detalle":  f"MAX({base_compra:,.0f}€ compra, {valor_catastral:,.0f}€ catastral) × {pct_construccion*100:.0f}% × 3% × {pct_titular*100:.0f}%",
        "0149":          rendimiento_neto,
        "0150":          reduccion_importe,
        "0152":          rendimiento_final,
        "0153":          round(retenciones, 2),
        "reduccion_pct": int(reduccion_pct * 100),
        "nota_reduccion":"⚠️ Reducción 60% orientativa — validar con asesor según ingresos totales contribuyente",
        "iva_aplicable": bool(row.get("IVA_Aplicable", False)),
        "tipo_arrendamiento": tipo_arrendamiento,
        "modo_fiscal":   "IRPF",
    }

# ================================================================
# SECCIÓN 9 — FUNCIONES MACROFINANZAS
# calcular_amortizacion, stress_test_euribor, analisis_sensibilidad_renta
# ================================================================
def calcular_amortizacion(principal, tasa_anual, plazo_años, modo="cuota_fija"):
    tasa_mensual = tasa_anual / 100 / 12
    num_cuotas = plazo_años * 12
    if modo == "cuota_fija":
        cuota_mensual = principal / num_cuotas if tasa_mensual == 0 else \
            principal * (tasa_mensual * (1+tasa_mensual)**num_cuotas) / ((1+tasa_mensual)**num_cuotas - 1)
    else:
        cuota_mensual = None
    tabla = []; capital_pendiente = principal; total_intereses = 0
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
        tabla.append({"Mes":mes,"Cuota":cuota_mensual if modo=="cuota_fija" else interes+capital,"Capital":capital,"Intereses":interes,"Pendiente":max(0,capital_pendiente)})
    return {"cuota_mensual":cuota_mensual if modo=="cuota_fija" else "variable","total_intereses":round(total_intereses,2),"total_pagado":round(principal+total_intereses,2),"tabla":pd.DataFrame(tabla)}

def stress_test_euribor(saldo_actual, margen, euribor_base, plazo_restante_años):
    escenarios = {"Euríbor -1%":euribor_base-1,"Euríbor actual":euribor_base,"Euríbor +1%":euribor_base+1,"Euríbor +2%":euribor_base+2,"Euríbor +3%":euribor_base+3}
    resultados = {}
    for escenario, tasa in escenarios.items():
        tasa_total = (tasa + margen) / 100
        cuota = saldo_actual / (plazo_restante_años*12) if tasa_total==0 else \
            saldo_actual * (tasa_total/12 * (1+tasa_total/12)**(plazo_restante_años*12)) / ((1+tasa_total/12)**(plazo_restante_años*12)-1)
        resultados[escenario] = {"tasa_total":round(tasa+margen,2),"cuota_mensual":round(cuota,2),"cuota_anual":round(cuota*12,2)}
    return resultados

def analisis_sensibilidad_renta(renta_actual, gastos_anuales, valor_construccion, variaciones=None):
    if variaciones is None: variaciones = [-15,-10,-5,0,5,10,15]
    escenarios = []
    for var_pct in variaciones:
        nueva_renta = renta_actual * (1 + var_pct/100)
        ingresos_anuales = nueva_renta * 12
        neto_anual = ingresos_anuales - gastos_anuales
        rentabilidad = (neto_anual / valor_construccion * 100) if valor_construccion > 0 else 0
        escenarios.append({"Variación":f"{var_pct:+.0f}%","Renta Mensual":f"{nueva_renta:.2f} €","Ingresos Anuales":f"{ingresos_anuales:.2f} €","Gastos Anuales":f"{gastos_anuales:.2f} €","Neto Anual":f"{neto_anual:.2f} €","Rentabilidad":f"{rentabilidad:.2f}%"})
    return pd.DataFrame(escenarios)

# ================================================================
# SECCIÓN 10 — GENERADOR DE PDF (Modelo 100)
# ================================================================
def _generar_pdf_factura(perfil: dict, datos: dict, numero: str, es_rectificativa: bool = False):
    """Genera PDF de factura de renta al estilo Nolasco Capital."""
    if not REPORTLAB_OK:
        return None
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.colors import HexColor, white
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.platypus import Table, TableStyle

        buffer = io.BytesIO()
        c = rl_canvas.Canvas(buffer, pagesize=A4)
        w, h = A4
        azul   = HexColor("#0F2744")
        acento = HexColor("#185FA5")
        gris   = HexColor("#F4F7FB")
        borde  = HexColor("#D0DFF0")
        verde  = HexColor("#1a7a40")
        rojo   = HexColor("#C0392B")

        # ── CABECERA ────────────────────────────────────────────
        c.setFillColor(azul); c.rect(0, h-100, w, 100, fill=True, stroke=False)
        c.setFillColor(acento); c.roundRect(30, h-85, 55, 55, 6, fill=True, stroke=False)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 22); c.drawCentredString(57.5, h-65, "NC")
        c.setFont("Helvetica", 7); c.drawCentredString(57.5, h-77, "CAPITAL")
        c.setFont("Helvetica-Bold", 20); c.drawString(100, h-50, "Nolasco Capital")
        c.setFont("Helvetica", 9); c.drawString(100, h-65, "GRANADA  |  GESTIÓN PATRIMONIAL INMOBILIARIA")
        c.setFont("Helvetica", 8)
        c.drawRightString(w-30, h-45, f"Nº: {numero}")
        c.drawRightString(w-30, h-57, f"Fecha: {datos.get('fecha','')}")
        c.drawRightString(w-30, h-69, f"Vencimiento: {datos.get('vencimiento','')}")
        c.setStrokeColor(acento); c.setLineWidth(3); c.line(0, h-103, w, h-103)

        # ── TÍTULO ──────────────────────────────────────────────
        y = h-130
        c.setFillColor(azul); c.setFont("Helvetica-Bold", 14)
        _titulo_pdf = "FACTURA RECTIFICATIVA" if es_rectificativa else "FACTURA"
        c.drawString(30, y, _titulo_pdf)
        c.setFont("Helvetica", 9); c.setFillColor(HexColor("#5A7A9A"))
        c.drawString(30, y-16, f"Arrendamiento inmobiliario — {datos.get('concepto','')}")

        # ── BLOQUE EMISOR / RECEPTOR ────────────────────────────
        y -= 45
        # Emisor
        c.setFillColor(gris); c.roundRect(25, y-90, (w-60)/2-5, 90, 5, fill=True, stroke=False)
        c.setStrokeColor(borde); c.roundRect(25, y-90, (w-60)/2-5, 90, 5, fill=False, stroke=True)
        c.setFillColor(azul); c.setFont("Helvetica-Bold", 9); c.drawString(35, y-14, "EMISOR (Arrendador)")
        c.setFont("Helvetica", 8); c.setFillColor(HexColor("#333333"))
        c.drawString(35, y-28, perfil.get("nombre_fiscal",""))
        c.drawString(35, y-40, f"NIF: {perfil.get('nif','')}")
        c.drawString(35, y-52, perfil.get("direccion",""))
        c.drawString(35, y-64, f"{perfil.get('cp','')} {perfil.get('ciudad','')}")
        if perfil.get("telefono"): c.drawString(35, y-76, f"Tel: {perfil.get('telefono','')}")

        # Receptor
        mid = 30 + (w-60)/2 + 5
        c.setFillColor(HexColor("#FFFDF0")); c.roundRect(mid, y-90, (w-60)/2-5, 90, 5, fill=True, stroke=False)
        c.setStrokeColor(borde); c.roundRect(mid, y-90, (w-60)/2-5, 90, 5, fill=False, stroke=True)
        c.setFillColor(azul); c.setFont("Helvetica-Bold", 9); c.drawString(mid+10, y-14, "RECEPTOR (Arrendatario)")
        c.setFont("Helvetica", 8); c.setFillColor(HexColor("#333333"))
        c.drawString(mid+10, y-28, datos.get("inquilino",""))
        c.drawString(mid+10, y-40, f"NIF: {datos.get('nif_inquilino','')}")
        dir_inq = datos.get("direccion_inquilino","")
        # Dividir dirección en dos líneas si es larga
        if len(dir_inq) > 45:
            c.drawString(mid+10, y-52, dir_inq[:45])
            c.drawString(mid+10, y-64, dir_inq[45:90])
        else:
            c.drawString(mid+10, y-52, dir_inq)

        # ── TABLA CONCEPTOS ─────────────────────────────────────
        y -= 110
        c.setFillColor(azul); c.setFont("Helvetica-Bold", 11)
        c.drawString(30, y, "Detalle de la factura")
        c.setStrokeColor(acento); c.setLineWidth(2); c.line(30, y-4, 230, y-4)
        y -= 20

        data_tabla = [
            ["Concepto", "Precio ud.", "Unidades", "Subtotal", "IVA", "Retención", "Total"],
            [
                datos.get("concepto",""),
                f"{datos.get('base_imponible',0):,.2f}€",
                "1",
                f"{datos.get('base_imponible',0):,.2f}€",
                f"{datos.get('pct_iva',0):.0f}%",
                f"-{datos.get('pct_retencion',0):.0f}%",
                f"{datos.get('total',0):,.2f}€"
            ]
        ]
        t = Table(data_tabla, colWidths=[165,55,45,55,30,45,55])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),azul),
            ("TEXTCOLOR",(0,0),(-1,0),white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,0),8),
            ("FONTNAME",(0,1),(-1,-1),"Helvetica"),
            ("FONTSIZE",(0,1),(-1,-1),8),
            ("ALIGN",(1,0),(-1,-1),"RIGHT"),
            ("GRID",(0,0),(-1,-1),0.4,borde),
            ("LINEBELOW",(0,0),(-1,0),2,acento),
            ("BACKGROUND",(0,1),(-1,-1),gris),
            ("TOPPADDING",(0,0),(-1,-1),5),
            ("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),6),
        ]))
        t.wrapOn(c, w, h); t.drawOn(c, 25, y-35)
        y -= 55

        # ── RESUMEN FISCAL ──────────────────────────────────────
        y -= 20
        resumen = [
            ["Base Imponible", f"{datos.get('base_imponible',0):,.2f} €"],
            [f"IVA {datos.get('pct_iva',0):.0f}%", f"{datos.get('importe_iva',0):,.2f} €"],
            [f"Retención {datos.get('pct_retencion',0):.0f}%", f"−{datos.get('importe_retencion',0):,.2f} €"],
            ["TOTAL", f"{datos.get('total',0):,.2f} €"],
        ]
        tabla_res = Table(resumen, colWidths=[150, 100])
        tabla_res.setStyle(TableStyle([
            ("FONTNAME",(0,0),(-1,-2),"Helvetica"),
            ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),9),
            ("ALIGN",(1,0),(1,-1),"RIGHT"),
            ("GRID",(0,0),(-1,-1),0.4,borde),
            ("BACKGROUND",(0,-1),(-1,-1),acento),
            ("TEXTCOLOR",(0,-1),(-1,-1),white),
            ("TOPPADDING",(0,0),(-1,-1),5),
            ("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),8),
        ]))
        tabla_res.wrapOn(c, w, h)
        tabla_res.drawOn(c, w-285, y-80)
        y -= 100

        # ── CONDICIONES DE PAGO ─────────────────────────────────
        if perfil.get("iban"):
            y -= 20
            c.setFillColor(gris); c.roundRect(25, y-45, w-50, 45, 5, fill=True, stroke=False)
            c.setStrokeColor(borde); c.roundRect(25, y-45, w-50, 45, 5, fill=False, stroke=True)
            c.setFillColor(azul); c.setFont("Helvetica-Bold", 9)
            c.drawString(35, y-14, "Condiciones de pago")
            c.setFont("Helvetica", 8); c.setFillColor(HexColor("#333333"))
            c.drawString(35, y-28, "TRANSFERENCIA BANCARIA A CUENTA:")
            c.setFont("Helvetica-Bold", 9)
            c.drawString(35, y-40, f"Nº: {perfil.get('iban','')}")

        # ── FOOTER ──────────────────────────────────────────────
        c.setFillColor(azul); c.rect(0, 0, w, 30, fill=True, stroke=False)
        c.setFillColor(white); c.setFont("Helvetica", 7)
        c.drawString(30, 11, "Nolasco Capital  |  Granada  |  Gestión Patrimonial Inmobiliaria")
        c.drawRightString(w-30, 11, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        c.save()
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error generando PDF factura: {e}")
        return None


def generar_pdf_modelo100(inmueble_data, modelo):
    if not REPORTLAB_OK: return None
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    azul_oscuro = HexColor("#0F2744"); azul_acento = HexColor("#185FA5")
    verde = HexColor("#1a7a40"); naranja = HexColor("#B45309")
    gris_claro = HexColor("#F4F7FB"); gris_borde = HexColor("#D0DFF0"); amarillo = HexColor("#FFF9E6")
    ref = f"NC-{datetime.now().strftime('%Y')}-{inmueble_data['Nombre'][:3].upper()}"
    tipo_arr = str(inmueble_data.get("Tipo_Arrendamiento","Larga Duracion"))
    dias_arr = int(safe_float(inmueble_data.get("Dias_Arrendados_Anio",365)))
    # Cabecera
    c.setFillColor(azul_oscuro); c.rect(0,h-100,w,100,fill=True,stroke=False)
    c.setFillColor(azul_acento); c.roundRect(30,h-85,55,55,6,fill=True,stroke=False)
    c.setFillColor(white); c.setFont("Helvetica-Bold",22); c.drawCentredString(57.5,h-65,"NC")
    c.setFont("Helvetica",7); c.drawCentredString(57.5,h-77,"CAPITAL")
    c.setFont("Helvetica-Bold",20); c.drawString(100,h-50,"Nolasco Capital")
    c.setFont("Helvetica",9); c.drawString(100,h-65,"GRANADA  |  GESTION PATRIMONIAL INMOBILIARIA")
    c.setFont("Helvetica",8)
    c.drawRightString(w-30,h-45,f"Ref: {ref}"); c.drawRightString(w-30,h-57,f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    c.drawRightString(w-30,h-69,f"Ejercicio: {datetime.now().year}")
    c.setStrokeColor(azul_acento); c.setLineWidth(3); c.line(0,h-103,w,h-103)
    # Título
    y = h-130; c.setFillColor(azul_oscuro); c.setFont("Helvetica-Bold",13)
    c.drawString(30,y,"Modelo 100 - Rendimientos del Capital Inmobiliario")
    c.setFont("Helvetica",9); c.setFillColor(HexColor("#5A7A9A"))
    c.drawString(30,y-15,"Datos informativos para el asesor fiscal | Pendiente validacion profesional")
    # Datos inmueble
    y -= 45; c.setFillColor(gris_claro); c.roundRect(25,y-70,w-50,70,6,fill=True,stroke=False)
    c.setStrokeColor(gris_borde); c.roundRect(25,y-70,w-50,70,6,fill=False,stroke=True)
    c.setFillColor(azul_oscuro); c.setFont("Helvetica-Bold",10); c.drawString(35,y-14,"Datos del Inmueble")
    labels1=[("Inmueble:",35,str(inmueble_data["Nombre"])),("Ref. Catastral:",200,str(inmueble_data.get("Ref_Catastral","N/A"))),("Titular:",390,str(inmueble_data.get("Titular","N/A")))]
    labels2=[("Modalidad:",35,tipo_arr),("NIF Inquilino:",200,str(inmueble_data.get("NIF_Inquilino","N/A"))),("Dias arrendados:",390,f"{dias_arr} dias")]
    c.setFont("Helvetica",8); c.setFillColor(HexColor("#5A7A9A"))
    for lbl,x,_ in labels1: c.drawString(x,y-30,lbl)
    for lbl,x,_ in labels2: c.drawString(x,y-48,lbl)
    c.setFillColor(azul_oscuro); c.setFont("Helvetica-Bold",8)
    for lbl,x,val in labels1: c.drawString(x+60,y-30,val)
    for lbl,x,val in labels2: c.drawString(x+65,y-48,val)
    # Tabla casillas
    y -= 95; c.setFillColor(azul_oscuro); c.setFont("Helvetica-Bold",11)
    c.drawString(30,y,"Casillas del Modelo 100")
    c.setStrokeColor(azul_acento); c.setLineWidth(2); c.line(30,y-4,230,y-4); y -= 22
    amort_detalle = modelo.get("0113_detalle","")
    data = [
        ["Casilla","Descripcion","Importe (EUR)","Nota para asesor"],
        ["0101","Dias arrendado en el ano",f"{modelo['0101']} dias",""],
        ["0102","Ingresos integros",f"{modelo['0102']:,.2f}",""],
        ["0105","Intereses hipoteca/financiacion",f"{modelo['0105']:,.2f}","Solo intereses, no capital"],
        ["0106","Reparacion y conservacion",f"{modelo['0106']:,.2f}","Del diario contable"],
        ["0108","Tributos e IBI",f"{modelo['0108']:,.2f}",""],
        ["0110","Comunidad + Seguros + Ascensor",f"{modelo['0110']:,.2f}","Hogar + vida + comunidad"],
        ["0111","Servicios y suministros",f"{modelo['0111']:,.2f}",""],
        ["0112","Gastos juridicos",f"{modelo['0112']:,.2f}",""],
        ["0113","Amortizacion fiscal (3%)",f"{modelo['0113']:,.2f}",amort_detalle[:40] if amort_detalle else ""],
        ["0107","TOTAL GASTOS DEDUCIBLES",f"{modelo['0107']:,.2f}",""],
        ["0149","RENDIMIENTO NETO",f"{modelo['0149']:,.2f}",""],
        ["0150",f"Reduccion {modelo['reduccion_pct']}% (orientativa)",f"-{modelo['0150']:,.2f}","VALIDAR con asesor"],
        ["0152","RENDIMIENTO NETO REDUCIDO",f"{modelo['0152']:,.2f}","VALIDAR con asesor"],
        ["0153","Retenciones practicadas",f"{modelo['0153']:,.2f}",""],
    ]
    t = Table(data, colWidths=[58,165,90,152])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),azul_oscuro),("TEXTCOLOR",(0,0),(-1,0),white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),8),
        ("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,1),(-1,-1),7.5),
        ("ALIGN",(2,1),(2,-1),"RIGHT"),("FONTNAME",(0,1),(0,-1),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),0.4,gris_borde),("LINEBELOW",(0,0),(-1,0),2,azul_acento),
        ("ROWBACKGROUNDS",(0,1),(-1,-5),[white,gris_claro]),
        ("BACKGROUND",(0,-4),(-1,-4),HexColor("#F0F8FF")),("FONTNAME",(0,-4),(-1,-4),"Helvetica-Bold"),
        ("BACKGROUND",(0,-3),(-1,-3),amarillo),("FONTNAME",(0,-3),(-1,-3),"Helvetica-Bold"),
        ("TEXTCOLOR",(3,-3),(3,-3),naranja),
        ("BACKGROUND",(0,-2),(-1,-2),HexColor("#FFF0DC")),("FONTNAME",(0,-2),(-1,-2),"Helvetica-Bold"),
        ("TEXTCOLOR",(3,-2),(3,-2),naranja),("BACKGROUND",(0,-1),(-1,-1),gris_claro),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),6),
    ]))
    t.wrapOn(c,w,h); t.drawOn(c,25,y-len(data)*19-5)
    y_after = y-len(data)*19-20
    # Aviso
    y_av = y_after-15; c.setFillColor(amarillo); c.roundRect(25,y_av-55,w-50,55,5,fill=True,stroke=False)
    c.setStrokeColor(naranja); c.setLineWidth(1); c.roundRect(25,y_av-55,w-50,55,5,fill=False,stroke=True)
    c.setFillColor(naranja); c.setFont("Helvetica-Bold",9)
    c.drawString(35,y_av-14,"IMPORTANTE: Documento informativo — pendiente validacion por asesor fiscal")
    c.setFont("Helvetica",8); c.setFillColor(HexColor("#5A4A00"))
    c.drawString(35,y_av-28,"Reduccion 60% (cas. 0150): orientativa. Depende de los ingresos totales del contribuyente.")
    c.drawString(35,y_av-40,"Amortizacion: MAX(precio compra, catastral) x % construccion x 3%. Verificar datos catastrales.")
    if modelo.get("iva_aplicable"): c.drawString(35,y_av-52,"IVA: Este inmueble tributa por Modelo 303 (IVA). No incluido en este Modelo 100.")
    # Página 2
    c.showPage()
    c.setFillColor(azul_oscuro); c.rect(0,h-60,w,60,fill=True,stroke=False)
    c.setFillColor(white); c.setFont("Helvetica-Bold",14); c.drawString(30,h-38,"Nolasco Capital")
    c.setFont("Helvetica",8); c.drawString(30,h-50,f"Modelo 100 - {inmueble_data['Nombre']} | Ref: {ref}")
    c.drawRightString(w-30,h-38,"Pagina 2 de 2")
    c.setStrokeColor(azul_acento); c.setLineWidth(3); c.line(0,h-63,w,h-63)
    y_firma = h-110; c.setFillColor(azul_oscuro); c.setFont("Helvetica-Bold",11)
    c.drawString(30,y_firma,"Verificacion y Firma")
    # Bloque propietario
    c.setFillColor(gris_claro); c.roundRect(25,y_firma-95,(w-60)/2,80,5,fill=True,stroke=False)
    c.setStrokeColor(gris_borde); c.roundRect(25,y_firma-95,(w-60)/2,80,5,fill=False,stroke=True)
    c.setFillColor(azul_oscuro); c.setFont("Helvetica-Bold",9); c.drawString(35,y_firma-22,"Propietario")
    c.setFont("Helvetica",8); c.drawString(35,y_firma-38,f"Nombre: {inmueble_data.get('Titular','Pedro Nolasco')}")
    c.drawString(35,y_firma-52,f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.setFillColor(verde); c.setFont("Helvetica-Bold",9); c.drawString(35,y_firma-68,"DATOS VERIFICADOS")
    c.setFont("Helvetica",7); c.setFillColor(HexColor("#5A7A9A"))
    c.drawString(35,y_firma-80,f"Hash: NC{datetime.now().strftime('%Y%m%d%H%M')}{inmueble_data['Nombre'][:3].upper()}")
    # Bloque asesor
    mid = 30+(w-60)/2+10
    c.setFillColor(HexColor("#FFFDF0")); c.roundRect(mid,y_firma-95,(w-60)/2,80,5,fill=True,stroke=False)
    c.setStrokeColor(naranja); c.roundRect(mid,y_firma-95,(w-60)/2,80,5,fill=False,stroke=True)
    c.setFillColor(azul_oscuro); c.setFont("Helvetica-Bold",9); c.drawString(mid+10,y_firma-22,"Asesor Fiscal")
    c.setFont("Helvetica",8); c.setFillColor(naranja); c.drawString(mid+10,y_firma-38,"PENDIENTE VALIDACION")
    c.setFillColor(HexColor("#5A7A9A"))
    c.drawString(mid+10,y_firma-52,"Nombre: ____________________________")
    c.drawString(mid+10,y_firma-66,"Fecha:  ____________________________")
    c.drawString(mid+10,y_firma-80,"Firma:  ____________________________")
    # Notas legales
    y_notas = y_firma-120; c.setFillColor(azul_oscuro); c.setFont("Helvetica-Bold",10)
    c.drawString(30,y_notas,"Notas Legales"); c.setStrokeColor(azul_acento); c.setLineWidth(1.5)
    c.line(30,y_notas-4,140,y_notas-4)
    notas = [
        "1. Este documento es INFORMATIVO y no sustituye el asesoramiento fiscal profesional.",
        "2. Los datos han sido pre-rellenados automaticamente desde Nolasco Capital.",
        "3. La reduccion del 60% (casilla 0150) es orientativa y depende de los ingresos totales",
        "   del contribuyente. Debe ser validada y aplicada por el asesor fiscal.",
        "4. La amortizacion fiscal se calcula como: MAX(precio compra total, valor catastral)",
        "   x porcentaje de construccion x 3% x porcentaje de titularidad (Art. 14 RIRPF).",
        "5. Los dias de arrendamiento (casilla 0101) afectan proporcionalmente a todos los gastos.",
        f"6. Modalidad declarada: {tipo_arr}. Dias arrendados: {dias_arr}.",
        "7. Si el inmueble esta arrendado a una empresa, el IVA tributa en Modelo 303.",
        f"8. Referencia interna: {ref} | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
    ]
    c.setFont("Helvetica",7.5); yn = y_notas-18
    for nota in notas:
        c.setFillColor(HexColor("#333333")); c.drawString(30,yn,nota); yn -= 13
    # Footer
    c.setFillColor(azul_oscuro); c.rect(0,0,w,30,fill=True,stroke=False)
    c.setFillColor(white); c.setFont("Helvetica",7)
    c.drawString(30,11,"Nolasco Capital  |  Granada  |  Gestion Patrimonial Inmobiliaria")
    c.drawRightString(w-30,11,f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.save(); buffer.seek(0)
    return buffer

# ================================================================
# SECCIÓN 11 — GENERADORES DE CONTRATOS LAU
# generar_contrato_larga_duracion, _temporada, _habitacion
# ================================================================
def generar_contrato_larga_duracion(data):
    suministros = [k for k,v in [("electricidad",data["incluye_luz"]),("gas",data["incluye_gas"]),("agua",data["incluye_agua"]),("internet",data["incluye_internet"])] if v]
    s_txt = ", ".join(suministros) if suministros else "ninguno"
    ipc_cl = "La renta se actualizará anualmente según IPC conforme al artículo 18 de la LAU." if data["ipc"] else "La renta permanecerá fija durante toda la duración del contrato."
    return f"""
══════════════════════════════════════════════════════════════
CONTRATO DE ARRENDAMIENTO DE VIVIENDA
Ley 29/1994 de Arrendamientos Urbanos (LAU)
══════════════════════════════════════════════════════════════
ARRENDADOR: ________________________, DNI ____________
ARRENDATARIO: ________________________, DNI ____________

INMUEBLE: {data["direccion"]} · Ref. Catastral: {data["ref_catastral"]} · {data["m2"]} m²

CLÁUSULAS

PRIMERA.- OBJETO: Vivienda habitual (Art. 2 LAU).
SEGUNDA.- DURACIÓN: {data["duracion_anos"]} años.
TERCERA.- RENTA: {data["renta"]:,.2f} €/mes. {ipc_cl}
CUARTA.- FIANZA: {data["importe_fianza"]:,.2f} € ({data["fianza_meses"]} mes/es) conforme Art. 36 LAU.
QUINTA.- SUMINISTROS incluidos en renta: {s_txt}.
SEXTA.- GASTOS COMUNIDAD e IBI: a cargo del arrendador.
SÉPTIMA.- OBRAS: reparaciones necesarias a cargo del arrendador (Art. 21 LAU).
OCTAVA.- CESIÓN/SUBARRIENDO: no permitidos sin consentimiento escrito (Art. 8 LAU).
NOVENA.- MASCOTAS: {data["mascotas"]}.
DÉCIMA.- LEGISLACIÓN: LAU 29/1994. Juzgados de Granada.

Granada, a ___ de ______________ de 20__

EL ARRENDADOR ___________________   EL ARRENDATARIO ___________________

══════════════════════════════════════════════════════════════
Generado con Nolasco Capital · Documento orientativo LAU 29/1994 · Consulte con abogado
══════════════════════════════════════════════════════════════
"""

def generar_contrato_temporada(data):
    suministros = [k for k,v in [("electricidad",data["incluye_luz"]),("gas",data["incluye_gas"]),("agua",data["incluye_agua"]),("internet",data["incluye_internet"])] if v]
    s_txt = ", ".join(suministros) if suministros else "ninguno"
    return f"""
══════════════════════════════════════════════════════════════
CONTRATO DE ARRENDAMIENTO DE TEMPORADA
Ley 29/1994 de Arrendamientos Urbanos (LAU) · Art. 3
══════════════════════════════════════════════════════════════
ARRENDADOR: ________________________, DNI ____________
ARRENDATARIO: ________________________, DNI ____________

INMUEBLE: {data["direccion"]} · Ref. Catastral: {data["ref_catastral"]} · {data["m2"]} m²
Uso distinto de vivienda habitual permanente (Art. 3 LAU y Código Civil).

CLÁUSULAS

PRIMERA.- DURACIÓN: {data["duracion_meses"]} mes/es. Extinción automática SIN PRÓRROGA OBLIGATORIA.
SEGUNDA.- RENTA: {data["renta"]:,.2f} €/mes. Fija durante toda la duración.
TERCERA.- FIANZA: {data["importe_fianza"]:,.2f} €.
CUARTA.- SUMINISTROS incluidos: {s_txt}.
QUINTA.- ENTREGA: inmueble en las mismas condiciones al término.

Granada, a ___ de ______________ de 20__

EL ARRENDADOR ___________________   EL ARRENDATARIO ___________________

══════════════════════════════════════════════════════════════
Generado con Nolasco Capital · Consulte con abogado
══════════════════════════════════════════════════════════════
"""

def generar_contrato_habitacion(data):
    return f"""
══════════════════════════════════════════════════════════════
CONTRATO DE ARRENDAMIENTO DE HABITACIÓN
══════════════════════════════════════════════════════════════
ARRENDADOR: ________________________, DNI ____________
ARRENDATARIO: ________________________, DNI ____________

INMUEBLE: {data["direccion"]} · Ref. Catastral: {data["ref_catastral"]}

CLÁUSULAS

PRIMERA.- OBJETO: cesión de UNA HABITACIÓN. Uso compartido de zonas comunes.
SEGUNDA.- DURACIÓN: {data["duracion_meses"]} mes/es.
TERCERA.- RENTA: {data["renta"]:,.2f} €/mes. Suministros incluidos.
CUARTA.- FIANZA: {data["importe_fianza"]:,.2f} €.
QUINTA.- NORMAS: silencio 23:00-8:00h. Zonas comunes limpias. Avisar de visitas que pernocten.
SEXTA.- DESISTIMIENTO: 30 días de preaviso por cualquiera de las partes.

Granada, a ___ de ______________ de 20__

EL ARRENDADOR ___________________   EL ARRENDATARIO ___________________

══════════════════════════════════════════════════════════════
Generado con Nolasco Capital · Consulte con abogado
══════════════════════════════════════════════════════════════
"""

# ================================================================
# ================================================================
# PANTALLAS — LÓGICA DE NAVEGACIÓN
# Cada elif es una pantalla independiente y autónoma
# ================================================================
# ================================================================

# ================================================================
# PANTALLA: TORRE DE CONTROL
# Deps: df_inm, df_mov, tasacion(), alerta_vencimiento()
# ================================================================
if menu == "Torre de Control":
    if df_inm.empty:
        st.markdown("## 🏠 Bienvenido a Nolasco Capital")
        st.info("📭 Aún no tienes inmuebles registrados. Ve a **Datos de Cartera** para añadir tu primer inmueble.")
        st.stop()

    # ── Detectar modo fiscal ──────────────────────────────────────
    _perfil_tc = st.session_state.get("perfil_datos", {})
    if not _perfil_tc:
        from supabase_db import leer_perfil_usuario
        _perfil_tc = leer_perfil_usuario(st.session_state.get("user_id","")) or {}
    _es_sociedad_tc = _perfil_tc.get("tipo_cuenta","particular") == "sociedad"
    _nom_soc_tc = _perfil_tc.get("nombre_sociedad","Sociedad Patrimonial")

    if _es_sociedad_tc:
        st.markdown(f'<div class="nc-brand-header">Torre de Control IS</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="nc-brand-sub">🏢 {_nom_soc_tc} · Impuesto de Sociedades · Modelo 200</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="nc-brand-header">Torre de Control</div>', unsafe_allow_html=True)
        st.markdown('<div class="nc-brand-sub">Rendimiento consolidado · Cartera Nolasco</div>', unsafe_allow_html=True)

    # Ingresos = facturas emitidas cobradas (nueva tabla) + ingresos en movimientos (legacy)
    _df_facs_tc = leer_facturas_emitidas(st.session_state.user_id)
    _ing_facturas = _df_facs_tc[_df_facs_tc["estado"]=="cobrada"]["total"].sum() if not _df_facs_tc.empty else 0
    _ing_movimientos = df_mov[df_mov["Tipo"]=="Ingreso"]["Importe"].sum()
    total_ingresos_registrados = _ing_facturas + _ing_movimientos
    total_gastos_registrados   = df_mov[df_mov["Tipo"]=="Gasto"]["Importe"].sum()
    balance_real  = total_ingresos_registrados - total_gastos_registrados
    margen_real   = (balance_real / total_ingresos_registrados * 100) if total_ingresos_registrados > 0 else 0

    mes_actual  = datetime.now().month
    anio_actual = datetime.now().year
    df_mov_fecha = df_mov.copy()
    df_mov_fecha["Fecha"] = pd.to_datetime(df_mov_fecha["Fecha"], errors="coerce")
    df_mes = df_mov_fecha[(df_mov_fecha["Fecha"].dt.month==mes_actual)&(df_mov_fecha["Fecha"].dt.year==anio_actual)]
    ing_mes_real = df_mes[df_mes["Tipo"]=="Ingreso"]["Importe"].sum()
    gas_mes_real = df_mes[df_mes["Tipo"]=="Gasto"]["Importe"].sum()
    bal_mes_real = ing_mes_real - gas_mes_real

    ing_previsto = df_inm["Renta"].apply(lambda x: safe_float(x)).sum()
    gas_previsto = (
        df_inm["Comunidad"].apply(lambda x: safe_float(x)).sum() +
        df_inm["IBI_Anual"].apply(lambda x: safe_float(x)).sum()/12 +
        df_inm["Seguro_Anual"].apply(lambda x: safe_float(x)).sum()/12 +
        df_inm["Intereses_Hipoteca"].apply(lambda x: safe_float(x)).sum()
    )
    bal_previsto = ing_previsto - gas_previsto
    ing_pct = min(int(ing_mes_real/ing_previsto*100),100) if ing_previsto>0 else 0
    gas_pct = min(int(gas_mes_real/gas_previsto*100),100) if gas_previsto>0 else 0
    bal_pct = min(int(bal_mes_real/bal_previsto*100),100) if bal_previsto>0 else 0
    ing_desv = ing_mes_real - ing_previsto
    gas_desv = gas_mes_real - gas_previsto
    bal_desv = bal_mes_real - bal_previsto

    # Alertas robot mini
    alertas_criticas = []; alertas_medias = []
    for _, row in df_inm.iterrows():
        tipo_alert, msg = alerta_vencimiento(row)
        if tipo_alert in ("vencido","urgente"): alertas_criticas.append(f"{row['Nombre']}: {msg}")
        elif tipo_alert == "aviso": alertas_medias.append(f"{row['Nombre']}: {msg}")
    for _, row in df_inm.iterrows():
        rm = tasacion(row); desv_r = (safe_float(row.get("Renta",0))-rm)/rm*100 if rm>0 else 0
        if desv_r < -15:
            perdida = rm - safe_float(row.get("Renta",0))
            alertas_criticas.append(f"{row['Nombre']}: renta {abs(desv_r):.0f}% bajo mercado — pérdida {perdida:,.0f}€/mes")
        elif desv_r < -5:
            alertas_medias.append(f"{row['Nombre']}: renta {abs(desv_r):.0f}% bajo mercado")

    if alertas_criticas or alertas_medias:
        alerta_txt = alertas_criticas[0] if alertas_criticas else alertas_medias[0]
        es_critica = bool(alertas_criticas)
        borde_color = "#C0392B" if es_critica else "#F39C12"
        fondo_color = "#FDECEA" if es_critica else "#FFF9E6"
        texto_color = "#C0392B" if es_critica else "#854F0B"
        extra = f"<span style='font-size:0.75rem;color:{borde_color};margin-left:8px;'>+{len(alertas_criticas)-1} alertas más</span>" if len(alertas_criticas)>1 else ""
        col_robot, col_alerta = st.columns([1, 11])
        with col_robot:
            if st.button("🤖", key="btn_robot_torre", help="Abrir Sabio IA", use_container_width=True):
                st.session_state["sabio_torre_abierto"] = True
        with col_alerta:
            st.markdown(f"""
            <div style="position:relative;background:{fondo_color};border:1px solid {borde_color};
                        border-radius:10px;padding:9px 14px;margin-top:4px;">
              <span style="font-size:0.85rem;font-weight:600;color:{texto_color};">
                {"🚨" if es_critica else "⚠️"} {alerta_txt}
              </span>{extra}
            </div>""", unsafe_allow_html=True)

    # ── KPIs — bifurcación IS / IRPF ─────────────────────────────
    st.markdown('<div style="font-size:0.75rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#9CA3AF;margin:20px 0 12px;">Acumulado del año en curso</div>', unsafe_allow_html=True)

    if _es_sociedad_tc:
        # ── Calcular KPIs societarios ─────────────────────────────
        _intereses_tc  = df_inm["Intereses_Hipoteca"].apply(lambda x: safe_float(x)).sum()
        _amort_tc      = df_inm["Amortizacion_Fiscal"].apply(lambda x: safe_float(x)).sum()
        _gas_op_tc     = total_gastos_registrados - _intereses_tc - _amort_tc
        _ebitda_tc     = total_ingresos_registrados - _gas_op_tc
        _resultado_tc  = total_ingresos_registrados - total_gastos_registrados
        _is_tc         = round(max(_resultado_tc * 0.25, 0), 0)

        # DSCR — cuota anual desde hipotecas
        _df_hip_tc = _cargar_hipotecas_supabase() if "df_hip" not in st.session_state else st.session_state.df_hip
        _cuota_anual_tc = 0
        _saldo_deuda_tc = 0
        if not _df_hip_tc.empty:
            for _, _h in _df_hip_tc.iterrows():
                _p  = safe_float(_h.get("Principal", 0))
                _r  = safe_float(_h.get("Tasa_Inicial", 0)) / 100 / 12
                _n  = int(safe_float(_h.get("Plazo_Años", 20))) * 12
                if _r > 0 and _n > 0:
                    _cuota_m = _p * (_r * (1+_r)**_n) / ((1+_r)**_n - 1)
                else:
                    _cuota_m = _p / _n if _n > 0 else 0
                _cuota_anual_tc += _cuota_m * 12
                _saldo_deuda_tc += safe_float(_h.get("Saldo_Actual", 0)) or _p

        _cash_flow_tc = _ebitda_tc - _is_tc - _cuota_anual_tc
        _dscr_tc      = round(_ebitda_tc / _cuota_anual_tc, 2) if _cuota_anual_tc > 0 else 0
        _dscr_color   = RED if _dscr_tc < 1.20 and _dscr_tc > 0 else GREEN if _dscr_tc >= 1.20 else AMBER

        # ROI y LTV
        _inversion_tc = (
            df_inm["Precio_Compra"].apply(lambda x: safe_float(x)).sum() +
            df_inm["Impuestos_Compra"].apply(lambda x: safe_float(x)).sum() +
            df_inm["Gastos_Compra"].apply(lambda x: safe_float(x)).sum()
        )
        _roi_tc = round(_resultado_tc / _inversion_tc * 100, 1) if _inversion_tc > 0 else 0
        _val_cat_tc = df_inm["Valor_Catastral"].apply(lambda x: safe_float(x)).sum()
        _ltv_tc = round(_saldo_deuda_tc / _val_cat_tc * 100, 1) if _val_cat_tc > 0 else 0
        _ltv_color = RED if _ltv_tc > 70 else AMBER if _ltv_tc > 50 else GREEN

        # Banner DSCR si < 1.20
        if _dscr_tc > 0 and _dscr_tc < 1.20:
            st.markdown(f"""
            <div style="background:#FDECEA;border:1px solid #C0392B;border-radius:10px;
                        padding:10px 16px;margin-bottom:12px;">
              <span style="font-size:0.85rem;font-weight:700;color:#C0392B;">
                🚨 DSCR {_dscr_tc:.2f} — Por debajo del umbral bancario (1.20).
                La sociedad no genera suficiente EBITDA para cubrir 1.2× las cuotas hipotecarias.
              </span>
            </div>""", unsafe_allow_html=True)

        # Fila 1 — Resultados
        render_kpi_row([
            {"label": "EBITDA Inmobiliario",
             "value": f"{_ebitda_tc:,.0f} €",
             "color": GREEN,
             "subtitle": "Ingresos − Gastos operativos"},
            {"label": "IS Estimado 25%",
             "value": f"−{_is_tc:,.0f} €",
             "color": RED,
             "subtitle": "Cuota IS orientativa"},
            {"label": "Cash Flow Neto",
             "value": f"{_cash_flow_tc:,.0f} €",
             "color": ACCENT if _cash_flow_tc >= 0 else RED,
             "subtitle": "EBITDA − IS − cuotas hipoteca"},
        ])
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        # Fila 2 — Ratios
        render_kpi_row([
            {"label": f"DSCR {'⚠️' if _dscr_tc < 1.20 and _dscr_tc > 0 else '✅'}",
             "value": f"{_dscr_tc:.2f}×" if _dscr_tc > 0 else "Sin datos",
             "color": _dscr_color,
             "subtitle": "EBITDA / cuota anual · min. 1.20"},
            {"label": "ROI Societario",
             "value": f"{_roi_tc:.1f}%",
             "color": GREEN if _roi_tc > 5 else AMBER,
             "subtitle": "Resultado / inversión total"},
            {"label": f"LTV Cartera {'⚠️' if _ltv_tc > 70 else ''}",
             "value": f"{_ltv_tc:.1f}%" if _ltv_tc > 0 else "Sin datos",
             "color": _ltv_color,
             "subtitle": "Deuda / valor catastral"},
        ])

    else:
        render_kpi_row([
            {
                "label": "Ingresos Registrados",
                "value": f"{total_ingresos_registrados:,.0f} €",
                "color": GREEN,
                "subtitle": "Total cobrado acumulado"
            },
            {
                "label": "Gastos Registrados",
                "value": f"−{total_gastos_registrados:,.0f} €",
                "color": RED,
                "subtitle": "Total pagado acumulado"
            },
            {
                "label": "Balance Real",
                "value": f"{balance_real:,.0f} €",
                "color": ACCENT,
                "subtitle": f"Margen {margen_real:.0f}%"
            }
        ])

    nombre_mes = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][mes_actual-1]
    def _color_desv(val, invertido=False):
        if invertido: return GREEN if val<=0 else RED
        return GREEN if val>=0 else RED
    def _flecha(val, invertido=False):
        if invertido: return "▼" if val<=0 else "▲"
        return "▲" if val>=0 else "▼"
    def _barra(pct, color):
        return f'<div style="height:5px;background:#D0DFF0;border-radius:4px;overflow:hidden;margin:4px 0 2px 0;"><div style="width:{pct}%;height:100%;background:{color};border-radius:4px;"></div></div>'

    _titulo_panel_mes = f"Previsión vs Real — {nombre_mes} {anio_actual}"
    if _es_sociedad_tc:
        _titulo_panel_mes += " · IS 25%"
    st.markdown(f'<div class="nc-section-title">{_titulo_panel_mes}</div>', unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    p1.markdown(f"""<div class="nc-kpi"><div class="nc-kpi__label">Ingresos {nombre_mes}</div>
      <div style="display:flex;align-items:baseline;gap:8px;"><div class="nc-kpi__value" style="color:{GREEN};font-size:1.5rem;">{ing_mes_real:,.0f} €</div><div style="font-size:0.8rem;color:{TEXT_SEC};">de {ing_previsto:,.0f} €</div></div>
      {_barra(ing_pct,GREEN)}<div style="display:flex;justify-content:space-between;"><span style="font-size:0.7rem;color:{TEXT_SEC};">{ing_pct}% completado</span><span style="font-size:0.78rem;font-weight:600;color:{_color_desv(ing_desv)};">{_flecha(ing_desv)} {abs(ing_desv):,.0f} €</span></div></div>""", unsafe_allow_html=True)
    p2.markdown(f"""<div class="nc-kpi"><div class="nc-kpi__label">Gastos {nombre_mes}</div>
      <div style="display:flex;align-items:baseline;gap:8px;"><div class="nc-kpi__value" style="color:{RED};font-size:1.5rem;">{gas_mes_real:,.0f} €</div><div style="font-size:0.8rem;color:{TEXT_SEC};">de {gas_previsto:,.0f} €</div></div>
      {_barra(gas_pct,RED)}<div style="display:flex;justify-content:space-between;"><span style="font-size:0.7rem;color:{TEXT_SEC};">{gas_pct}% ejecutado</span><span style="font-size:0.78rem;font-weight:600;color:{_color_desv(gas_desv,invertido=True)};">{_flecha(gas_desv,invertido=True)} {abs(gas_desv):,.0f} €</span></div></div>""", unsafe_allow_html=True)
    p3.markdown(f"""<div class="nc-kpi" style="border-left:3px solid {ACCENT};"><div class="nc-kpi__label">Balance {nombre_mes}</div>
      <div style="display:flex;align-items:baseline;gap:8px;"><div class="nc-kpi__value" style="color:{ACCENT};font-size:1.5rem;">{bal_mes_real:,.0f} €</div><div style="font-size:0.8rem;color:{TEXT_SEC};">de {bal_previsto:,.0f} €</div></div>
      {_barra(bal_pct,ACCENT)}<div style="display:flex;justify-content:space-between;"><span style="font-size:0.7rem;color:{TEXT_SEC};">{bal_pct}% del objetivo</span><span style="font-size:0.78rem;font-weight:600;color:{_color_desv(bal_desv)};">{_flecha(bal_desv)} {abs(bal_desv):,.0f} €</span></div></div>""", unsafe_allow_html=True)

    # Tarjetas casita
    _titulo_activos = "Rentabilidad por Activo IS — [399] Resultado por inmueble" if _es_sociedad_tc else "Rentabilidad por Activo"
    st.markdown(f'<div class="nc-section-title">{_titulo_activos}</div>', unsafe_allow_html=True)
    def _roof_color(row):
        texto = str(row.get("Nombre","")).lower()+" "+str(row.get("Tipo",row.get("Tipo_Arrendamiento",""))).lower()
        if any(x in texto for x in ["despacho","oficina","comercial","local","salón","salon","coworking"]): return "#185FA5","Despacho"
        if any(x in texto for x in ["casa","chalet","adosado","unifamiliar","abarqueros","villa"]): return "#6B2737","Casa"
        if any(x in texto for x in ["cochera","garaje","parking","trastero"]): return "#4A5568","Garaje"
        return "#B8924A","Apartamento"

    st.markdown("""<style>
    .casita-body{background:var(--background-color,#fff);border:0.5px solid rgba(0,0,0,0.1);border-top:none;border-radius:0 0 12px 12px;padding:12px 12px 10px;box-sizing:border-box;}
    .c-name{font-size:13px;font-weight:600;margin:0 0 2px;line-height:1.3;} .c-tenant{font-size:11px;color:#888;margin:0 0 10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
    .c-row{display:flex;justify-content:space-between;margin-bottom:4px;} .c-lbl{font-size:11px;color:#888;} .c-div{height:0.5px;background:rgba(0,0,0,0.08);margin:7px 0;}
    .c-pill{border-radius:6px;padding:3px 8px;text-align:center;font-size:11px;margin:8px 0 10px;display:block;}
    .c-pos{color:#1a7a40;font-size:12px;font-weight:600;} .c-neg{color:#a32d2d;font-size:12px;font-weight:600;} .c-neu{font-size:13px;font-weight:600;}
    .pill-pos{background:#eaf3de;color:#3b6d11;} .pill-neg{background:#ffebeb;color:#a32d2d;} .pill-neu{background:#f4f4f4;color:#666;}
    </style>""", unsafe_allow_html=True)

    MAX_COLS = 4
    inmuebles_list = list(df_inm.iterrows())
    for fila_start in range(0, len(inmuebles_list), MAX_COLS):
        fila_rows = inmuebles_list[fila_start:fila_start+MAX_COLS]
        cols = st.columns(MAX_COLS)
        for col_idx, (i, row) in enumerate(fila_rows):
            g_esp    = df_mov[(df_mov["Apartamento"]==row["Nombre"])&(df_mov["Tipo"]=="Gasto")&(df_mov["Categoría"]!="Comunidad")]["Importe"].sum()
            comunidad= safe_float(row.get("Comunidad",0)) if pd.notna(row.get("Comunidad",0)) else 0
            gastos_u = comunidad + g_esp
            neto_u   = safe_float(row.get("Renta",0)) - gastos_u
            rm       = tasacion(row)
            desv     = (safe_float(row.get("Renta",0))-rm)/rm*100 if rm else 0
            zt       = " 🔒" if str(row.get("Zona_Tensionada","N"))=="S" else ""
            roof_col, tipo_label = _roof_color(row)
            if desv>5:   pill_cls,desv_txt="pill-pos",f"+{desv:.1f}% mercado"
            elif desv<-5: pill_cls,desv_txt="pill-neg",f"{desv:.1f}% mercado"
            else:         pill_cls,desv_txt="pill-neu",f"{desv:+.1f}% mercado"
            neto_col = "#1a7a40" if neto_u>=0 else "#a32d2d"
            with cols[col_idx]:
                st.markdown(f"""<svg viewBox="0 0 200 52" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;margin-bottom:-1px;" preserveAspectRatio="none">
                  <polygon points="100,4 196,52 4,52" fill="{roof_col}"/>
                  <text x="100" y="40" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="500" fill="white" opacity="0.95">{tipo_label}</text>
                  <text x="100" y="20" text-anchor="middle" font-family="sans-serif" font-size="13" fill="white" opacity="0.6">⌂</text>
                </svg>
                <div class="casita-body">
                  <p class="c-name">{row["Nombre"]}{zt}</p>
                  <p class="c-tenant">{row.get("Inquilino","—")}</p>
                  <div class="c-row"><span class="c-lbl">Renta</span><span class="c-pos">+{safe_float(row.get("Renta",0)):,.0f}€</span></div>
                  <div class="c-row"><span class="c-lbl">Gastos</span><span class="c-neg">−{gastos_u:,.0f}€</span></div>
                  <div class="c-div"></div>
                  <div class="c-row"><span class="c-lbl">Neto</span><span class="c-neu" style="color:{neto_col};">{neto_u:,.0f}€</span></div>
                  <span class="c-pill {pill_cls}">{desv_txt}</span>
                </div>""", unsafe_allow_html=True)
                if st.button("→ Ver ficha", key=f"card_{fila_start}_{col_idx}", use_container_width=True):
                    st.session_state.menu="Fichas (Benchmark)"; st.session_state.ficha_sel=row["Nombre"]; st.rerun()

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="nc-section-title">Composición de Rentas</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Bar(x=df_inm["Renta"],y=df_inm["Nombre"],orientation="h",marker_color=COLOR_TOPS[:len(df_inm)],text=[f"{r:,.0f} €" for r in df_inm["Renta"]],textposition="outside"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=60,t=10,b=10),height=280,xaxis=dict(showgrid=False,visible=False),yaxis=dict(showgrid=False),font=dict(family="DM Sans",size=12))
        st.plotly_chart(fig,use_container_width=True)
    with col_r:
        st.markdown('<div class="nc-section-title">Lucro Cesante Anual</div>', unsafe_allow_html=True)
        total_lc=0
        for _,row in df_inm.iterrows():
            rm=tasacion(row); pa=max(0,rm-safe_float(row.get("Renta",0)))*12; total_lc+=pa
            if pa>0:
                dv=(safe_float(row.get("Renta",0))-rm)/rm*100 if rm else 0; cv=RED if dv<-15 else AMBER
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:9px 12px;background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;margin-bottom:6px;"><span style="font-size:0.8rem;color:{TEXT_SEC};">{row["Nombre"]}</span><span style="font-size:0.9rem;font-weight:600;color:{cv};">−{pa:,.0f} €/año</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:11px 14px;background:{ACCENT};border-radius:8px;margin-top:4px;"><span style="font-size:0.72rem;font-weight:500;color:#B5D4F4;text-transform:uppercase;letter-spacing:0.06em;">Total pérdida anual</span><span style="font-size:1.3rem;font-weight:600;color:#fff;">−{total_lc:,.0f} €</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="nc-section-title">📈 Evolución Últimos 12 Meses</div>', unsafe_allow_html=True)
    df_mov["Fecha"] = pd.to_datetime(df_mov["Fecha"], errors="coerce")
    df_mov_12m = df_mov[df_mov["Fecha"].notna()].copy()
    df_mov_12m["Mes"] = df_mov_12m["Fecha"].dt.to_period("M")
    ingresos_mes = df_mov_12m[df_mov_12m["Tipo"]=="Ingreso"].groupby("Mes")["Importe"].sum()
    gastos_mes   = df_mov_12m[df_mov_12m["Tipo"]=="Gasto"].groupby("Mes")["Importe"].sum()
    hoy = pd.Period(datetime.now(), freq="M")
    meses = [hoy-i for i in range(11,-1,-1)]; meses_str=[str(m) for m in meses]
    ing_data=[ingresos_mes.get(m,0) for m in meses]; gas_data=[gastos_mes.get(m,0) for m in meses]
    neto_data=[i-g for i,g in zip(ing_data,gas_data)]
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Scatter(x=meses_str,y=ing_data,mode='lines+markers',name='Ingresos',line=dict(color=GREEN,width=3),marker=dict(size=7)))
    fig_hist.add_trace(go.Scatter(x=meses_str,y=gas_data,mode='lines+markers',name='Gastos',line=dict(color=RED,width=3),marker=dict(size=7)))
    fig_hist.add_trace(go.Scatter(x=meses_str,y=neto_data,mode='lines+markers',name='Neto',line=dict(color=ACCENT,width=3,dash='dot'),marker=dict(size=7)))
    fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=10,b=40),height=280,xaxis=dict(showgrid=True,gridcolor="rgba(0,0,0,0.05)"),yaxis=dict(showgrid=True,gridcolor="rgba(0,0,0,0.05)",title="€"),font=dict(family="DM Sans",size=11),legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="center",x=0.5),hovermode="x unified")
    st.plotly_chart(fig_hist,use_container_width=True)

    alertas = [(row["Nombre"],*alerta_vencimiento(row)) for _,row in df_inm.iterrows() if alerta_vencimiento(row)[0] in ("vencido","urgente","aviso")]
    if alertas:
        st.markdown('<div class="nc-section-title">📅 Alertas de Contratos</div>', unsafe_allow_html=True)
        for nombre,tipo,msg in alertas:
            cls = "status-red" if tipo in ("vencido","urgente") else "status-yellow"
            st.markdown(f'<div class="{cls}" style="margin-bottom:6px;"><b>{nombre}</b> — {msg}</div>', unsafe_allow_html=True)

    # ── SABIO IA — Torre de Control (activado por botón robot) ──
    contexto_torre = {
        "total_ingresos": total_ingresos_registrados,
        "total_gastos": total_gastos_registrados,
        "balance": balance_real,
        "margen_pct": margen_real,
        "alertas_criticas": alertas_criticas,
        "alertas_medias": alertas_medias,
        "num_inmuebles": len(df_inm),
    }
    sabio_abierto = st.session_state.get("sabio_torre_abierto", False)
    with st.expander("🧠 Sabio Patrimonial IA", expanded=sabio_abierto):
        if sabio_abierto:
            st.session_state["sabio_torre_abierto"] = False
        render_sabio("torre", contexto_torre)

# ================================================================
# PANTALLA: FICHAS (BENCHMARK)
# Análisis de mercado, motor de tasación, simulador de renta
# Deps: df_inm, df_mov, tasacion(), alerta_vencimiento(), safe_float()
# ================================================================
elif menu == "Fichas (Benchmark)":
    if _sin_inmuebles:
        st.info("📭 Sin inmuebles registrados. Ve a **Datos de Cartera** para añadir el primero."); st.stop()
    st.markdown('<div class="nc-brand-header">Benchmark y Análisis Fiscal</div>', unsafe_allow_html=True)
    st.markdown('<div class="nc-brand-sub">Análisis de mercado · Comparativa fiscal por modalidad</div>', unsafe_allow_html=True)

    lista_inmuebles = df_inm["Nombre"].tolist()
    default_idx = lista_inmuebles.index(st.session_state.ficha_sel) if st.session_state.ficha_sel in lista_inmuebles else 0
    col_nav1, col_nav2, col_nav3 = st.columns([1,6,1])
    with col_nav1:
        if st.button("←", key="prev_inmueble", use_container_width=True, disabled=(default_idx==0)):
            st.session_state.ficha_sel=lista_inmuebles[default_idx-1]; st.rerun()
    with col_nav2:
        sel = st.selectbox("Inmueble a auditar:", lista_inmuebles, index=default_idx, label_visibility="collapsed")
        st.session_state.ficha_sel = sel
    with col_nav3:
        if st.button("→", key="next_inmueble", use_container_width=True, disabled=(default_idx==len(lista_inmuebles)-1)):
            st.session_state.ficha_sel=lista_inmuebles[default_idx+1]; st.rerun()

    f = df_inm[df_inm["Nombre"]==sel].iloc[0]
    renta_act=safe_float(f.get("Renta",0)); renta_mer=tasacion(f)
    desv=(renta_act-renta_mer)/renta_mer*100 if renta_mer else 0
    perdida_m=max(0,renta_mer-renta_act); perdida_a=perdida_m*12
    df_gf=df_mov[(df_mov["Apartamento"]==sel)&(df_mov["Tipo"]=="Gasto")&(df_mov["Categoría"]!="Comunidad")]
    gastos_u=(safe_float(f.get("Comunidad",0)) if pd.notna(f.get("Comunidad",0)) else 0)+df_gf["Importe"].sum()
    rent_bruta=(renta_act*12/safe_float(f.get("Valor_Construccion",0))*100) if safe_float(f.get("Valor_Construccion",0))>0 else 0
    rent_neta=((renta_act-gastos_u)*12/safe_float(f.get("Valor_Construccion",0))*100) if safe_float(f.get("Valor_Construccion",0))>0 else 0
    tipo_arr=str(f.get("Tipo_Arrendamiento","Larga Duración")); zona_tens=str(f.get("Zona_Tensionada","N"))=="S"; cochera_v=str(f.get("Cochera_Vinculada","N"))=="S"

    # KPIs de Fichas — nuevo estilo grande y prominente
    st.markdown('<div style="margin:24px 0 16px;"></div>', unsafe_allow_html=True)

    # ── KPIs IS si es sociedad ────────────────────────────────────
    _perfil_fic = st.session_state.get("perfil_datos", {})
    _es_soc_fic = _perfil_fic.get("tipo_cuenta","particular") == "sociedad"

    if _es_soc_fic:
        # Calcular KPIs IS de este inmueble
        _renta_anual_fic   = renta_act * 12
        _ibi_fic     = safe_float(f.get("IBI_Anual", 0))
        _seguro_fic  = safe_float(f.get("Seguro_Anual", 0))
        _com_fic     = safe_float(f.get("Comunidad", 0)) * 12
        _int_fic     = safe_float(f.get("Intereses_Hipoteca", 0))
        _amort_fic   = safe_float(f.get("Amortizacion_Fiscal", 0))
        _rep_fic     = df_gf["Importe"].sum()
        _gas_op_fic  = _ibi_fic + _seguro_fic + _com_fic + _rep_fic  # operativos excl. intereses y amort
        _gas_tot_fic = _gas_op_fic + _int_fic + _amort_fic
        _ebitda_fic  = _renta_anual_fic - _gas_op_fic
        _resultado_fic = _renta_anual_fic - _gas_tot_fic
        _is_fic      = round(max(_resultado_fic * 0.25, 0), 0)
        # ROI
        _precio_fic  = safe_float(f.get("Precio_Compra", 0)) + safe_float(f.get("Impuestos_Compra", 0)) + safe_float(f.get("Gastos_Compra", 0))
        _roi_fic     = round(_resultado_fic / _precio_fic * 100, 1) if _precio_fic > 0 else 0
        # Cobertura hipoteca: renta anual / cuota anual
        _df_hip_fic  = st.session_state.get("df_hip", pd.DataFrame())
        _cuota_fic   = 0
        if not _df_hip_fic.empty:
            _match = _df_hip_fic[_df_hip_fic["Inmueble"].str.lower()==str(sel).lower()]
            if not _match.empty:
                _hrow   = _match.iloc[0]
                _p_h    = safe_float(_hrow.get("Principal", 0))
                _r_h    = safe_float(_hrow.get("Tasa_Inicial", 0)) / 100 / 12
                _n_h    = int(safe_float(_hrow.get("Plazo_Años", 20))) * 12
                if _r_h > 0 and _n_h > 0:
                    _cuota_fic = _p_h * (_r_h*(1+_r_h)**_n_h) / ((1+_r_h)**_n_h-1) * 12
                elif _n_h > 0:
                    _cuota_fic = _p_h / _n_h * 12
        _cobertura_fic = round(_renta_anual_fic / _cuota_fic, 2) if _cuota_fic > 0 else 0
        _cob_color = RED if 0 < _cobertura_fic < 1.20 else GREEN if _cobertura_fic >= 1.20 else AMBER

        # Badge IS
        st.markdown(
            '<div style="display:inline-block;background:#0d1a0d;border:1px solid #059669;'
            'border-radius:6px;padding:4px 12px;font-size:12px;color:#059669;margin-bottom:10px;">'
            '🏢 Modo IS · Sociedad Patrimonial · 25%</div>',
            unsafe_allow_html=True)

        render_kpi_row([
            {"label": "EBITDA del activo",
             "value": f"{_ebitda_fic:,.0f} €",
             "color": GREEN if _ebitda_fic >= 0 else RED,
             "subtitle": "Renta − gastos operativos"},
            {"label": "IS estimado 25%",
             "value": f"−{_is_fic:,.0f} €",
             "color": RED,
             "subtitle": "[562] Cuota IS orientativa"},
            {"label": "ROI del activo",
             "value": f"{_roi_fic:.1f}%" if _precio_fic > 0 else "Sin precio",
             "color": GREEN if _roi_fic > 5 else AMBER,
             "subtitle": "Resultado / inversión"},
            {"label": f"Cobertura hipoteca {'✅' if _cobertura_fic >= 1.20 else '⚠️' if _cobertura_fic > 0 else ''}",
             "value": f"{_cobertura_fic:.2f}×" if _cobertura_fic > 0 else "Sin hipoteca",
             "color": _cob_color,
             "subtitle": "Renta anual / cuota anual"},
        ])
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    render_kpi_row([
        {
            "label": "Renta Actual",
            "value": f"{renta_act:,.0f} €",
            "color": GREEN,
            "subtitle": "mensual"
        },
        {
            "label": "Renta Tasada",
            "value": f"{renta_mer:,.0f} €",
            "color": "#9CA3AF",
            "subtitle": "motor CP + características"
        },
        {
            "label": "Rentabilidad Bruta",
            "value": f"{rent_bruta:.1f}%",
            "color": ACCENT,
            "subtitle": "sobre valor construcción"
        },
        {
            "label": "Rentabilidad Neta",
            "value": f"{rent_neta:.1f}%",
            "color": ACCENT,
            "subtitle": tipo_arr
        }
    ])

    badges=[]
    if zona_tens: badges.append('<span style="background:#FDECEA;color:#A32D2D;font-size:0.72rem;padding:3px 10px;border-radius:20px;font-weight:600;">🔒 Zona Tensionada</span>')
    if cochera_v: badges.append('<span style="background:#EDF7F1;color:#1a7a40;font-size:0.72rem;padding:3px 10px;border-radius:20px;font-weight:600;">🅿️ Cochera Vinculada</span>')
    tipo_color={"Larga Duración":"#EAF3DE","Temporada":"#FFF9E6","Vacacional":"#FDECEA"}.get(tipo_arr,"#EAF3DE")
    tipo_texto={"Larga Duración":"#3B6D11","Temporada":"#854F0B","Vacacional":"#A32D2D"}.get(tipo_arr,"#3B6D11")
    badges.append(f'<span style="background:{tipo_color};color:{tipo_texto};font-size:0.72rem;padding:3px 10px;border-radius:20px;font-weight:600;">📋 {tipo_arr}</span>')
    st.markdown("<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:1rem;'>"+"".join(badges)+"</div>",unsafe_allow_html=True)

    if zona_tens: st.markdown(f'<div class="status-red" style="margin-bottom:1rem;"><b>🔒 Zona Tensionada</b><br>No puedes subir la renta por encima del índice legal.</div>',unsafe_allow_html=True)
    if not cochera_v and str(f.get("Parking","N"))=="S": st.markdown(f'<div class="status-yellow" style="margin-bottom:1rem;"><b>🅿️ Cochera Independiente</b><br>Tributa de forma separada. Revisar en declaración IRPF.</div>',unsafe_allow_html=True)
    tipo_v,msg_v=alerta_vencimiento(f)
    if tipo_v:
        cls_v="status-red" if tipo_v in ("vencido","urgente") else ("status-yellow" if tipo_v=="aviso" else "status-green")
        st.markdown(f'<div class="{cls_v}" style="margin-bottom:1rem;"><b>📅 Contrato:</b> {msg_v}</div>',unsafe_allow_html=True)

    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="nc-section-title">Renta Actual vs Tasada</div>',unsafe_allow_html=True)
        fig_bar=go.Figure(go.Bar(x=["Renta Actual","Renta Tasada"],y=[renta_act,renta_mer],marker_color=[ACCENT,"#D0DFF0"],text=[f"{renta_act:,.0f} €",f"{renta_mer:,.0f} €"],textposition="outside",width=0.4))
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=10,b=10),height=240,yaxis=dict(showgrid=False,visible=False),xaxis=dict(showgrid=False),font=dict(family="DM Sans",size=13),showlegend=False)
        st.plotly_chart(fig_bar,use_container_width=True)
    with c2:
        st.markdown('<div class="nc-section-title">Estatus de Mercado</div>',unsafe_allow_html=True)
        if desv<-15:   clase,msg,icon="status-red","Rentabilidad Crítica","🔴"
        elif desv<-5:  clase,msg,icon="status-yellow","Margen de Mejora","🟡"
        else:          clase,msg,icon="status-green","Activo en Mercado","🟢"
        lucro_html=""
        if perdida_a>0: lucro_html=f'<div style="margin-top:12px;padding-top:12px;border-top:1px dashed rgba(0,0,0,0.15);"><span style="font-size:0.88rem;"><b>💸 Lucro Cesante:</b><br>Pérdida mensual: <b>{perdida_m:,.2f} €</b><br>Pérdida anualizada: <b style="color:{RED};font-size:1.15rem;">{perdida_a:,.2f} €/año</b></span></div>'
        st.markdown(f'<div class="{clase}"><b style="font-size:1.1rem;">{icon} {msg}</b><br>Desviación: <b>{desv:.1f}%</b>{lucro_html}</div>',unsafe_allow_html=True)

    if _es_soc_fic:
        # ── Análisis Fiscal IS — Sociedad Patrimonial ─────────────
        st.markdown('<div class="nc-section-title">🏛️ Análisis Fiscal IS — Sociedad Patrimonial</div>', unsafe_allow_html=True)
        st.caption("Impuesto de Sociedades 25% · Sin reducción arrendamiento · Doble imposición si distribuyes dividendos")

        _rto_sin = _renta_anual_fic                          # sin deducir gastos
        _rto_con = _renta_anual_fic - _gas_tot_fic           # con todos los gastos
        _is_sin  = round(max(_rto_sin * 0.25, 0), 2)
        _is_con  = round(max(_rto_con * 0.25, 0), 2)
        _neto_sin = round(_rto_sin - _is_sin, 2)
        _neto_con = round(_rto_con - _is_con, 2)
        _div_sin  = round(max(_neto_sin * 0.19, 0), 2)       # retención dividendos 19%
        _div_con  = round(max(_neto_con * 0.19, 0), 2)
        _final_sin = round(_neto_sin - _div_sin, 2)
        _final_con = round(_neto_con - _div_con, 2)
        _ahorro_is = round(_is_sin - _is_con, 2)

        cf1, cf2, cf3 = st.columns(3)
        for _col, _titulo, _rto, _is_v, _neto, _div, _final, _es_actual in [
            (cf1, "Sin gastos deducidos", _rto_sin, _is_sin, _neto_sin, _div_sin, _final_sin, False),
            (cf2, "Con gastos deducidos", _rto_con, _is_con, _neto_con, _div_con, _final_con, True),
        ]:
            _borde = f"border:2px solid {ACCENT};" if _es_actual else f"border:1px solid #E5E7EB;"
            _col.markdown(f"""
            <div style="background:#FAFAFA;{_borde}border-radius:10px;padding:1rem;text-align:center;">
              <div style="font-size:0.72rem;font-weight:700;color:#6B7280;text-transform:uppercase;
                          letter-spacing:0.06em;margin-bottom:10px;">{_titulo}</div>
              <div style="font-size:0.75rem;color:#6B7280;margin-bottom:2px;">[399] Resultado neto</div>
              <div style="font-size:1.5rem;font-weight:800;color:{ACCENT};">{_rto:,.0f} €</div>
              <div style="height:1px;background:#E5E7EB;margin:10px 0;"></div>
              <div style="font-size:0.75rem;color:#6B7280;">[562] IS 25%</div>
              <div style="font-size:1.2rem;font-weight:700;color:{RED};">−{_is_v:,.0f} €</div>
              <div style="font-size:0.75rem;color:#6B7280;margin-top:8px;">Neto tras IS</div>
              <div style="font-size:1.1rem;font-weight:700;color:#059669;">{_neto:,.0f} €</div>
              <div style="height:1px;background:#E5E7EB;margin:10px 0;"></div>
              <div style="font-size:0.72rem;color:#6B7280;">Si distribuyes dividendos (19%)</div>
              <div style="font-size:0.95rem;font-weight:600;color:{RED};">−{_div:,.0f} €</div>
              <div style="font-size:0.75rem;color:#6B7280;margin-top:6px;">Neto final al socio</div>
              <div style="font-size:1.3rem;font-weight:800;color:#059669;">{_final:,.0f} €</div>
            </div>""", unsafe_allow_html=True)

        cf3.markdown(f"""
        <div style="background:#0d1a0d;border:1px solid #059669;border-radius:10px;
                    padding:1rem;text-align:center;">
          <div style="font-size:0.72rem;font-weight:700;color:#059669;text-transform:uppercase;
                      letter-spacing:0.06em;margin-bottom:10px;">💡 Ahorro fiscal</div>
          <div style="font-size:0.75rem;color:#6B7280;">Deduciendo gastos ahorras en IS</div>
          <div style="font-size:1.8rem;font-weight:900;color:#059669;">{_ahorro_is:,.0f} €</div>
          <div style="height:1px;background:#1a3a1a;margin:10px 0;"></div>
          <div style="font-size:0.72rem;color:#6B7280;">Tipo efectivo IS</div>
          <div style="font-size:1.2rem;font-weight:700;color:#059669;">
            {round(_is_con/_rto_con*100,1) if _rto_con>0 else 0:.1f}%
          </div>
          <div style="font-size:0.72rem;color:#6B7280;margin-top:8px;">
            ⚠️ Sin reducción 60% arrendamiento<br>
            (Art. 23.2 LIRPF no aplica a sociedades)
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#FFF9E6;border:1px solid #D97706;border-radius:8px;
                    padding:10px 16px;margin-top:12px;font-size:0.82rem;color:#854F0B;">
          <b>⚠️ Doble imposición:</b> El beneficio tributa al 25% en IS y si lo distribuyes como dividendo
          tributa de nuevo al 19% (tipo general ahorro IRPF). Tipo efectivo total:
          <b>{round((1-(1-0.25)*(1-0.19))*100,1)}%</b>.
          Valora si compensa reinvertir en la sociedad vs distribuir.
        </div>""", unsafe_allow_html=True)

    else:
        st.markdown('<div class="nc-section-title">⚖️ Comparativa Fiscal por Modalidad</div>',unsafe_allow_html=True)
        st.caption("Rentabilidad neta real tras aplicar reducción IRPF según tipo de arrendamiento")
        rto_neto=(renta_act-gastos_u)*12; tipo_irpf=0.45
        modalidades={"Larga Duración":{"reduccion":0.60,"iva":False},"Temporada":{"reduccion":0.00,"iva":False},"Vacacional":{"reduccion":0.00,"iva":True}}
        cf1,cf2,cf3=st.columns(3); cols_fiscal=[cf1,cf2,cf3]; mejor_mod,mejor_rn=None,-99999
        for idx,(mod,params) in enumerate(modalidades.items()):
            red=params["reduccion"]; impuesto=max(0,rto_neto*(1-red)*tipo_irpf)
            rn_real=(rto_neto-impuesto)/safe_float(f.get("Valor_Construccion",0))*100 if safe_float(f.get("Valor_Construccion",0))>0 else 0
            if rn_real>mejor_rn: mejor_rn=rn_real; mejor_mod=mod
            es_actual=(mod==tipo_arr); borde=f"border:2px solid {ACCENT};" if es_actual else f"border:1px solid {BORDER};"
            iva_txt="<br><span style='font-size:0.7rem;color:#854F0B;'>⚠️ Puede llevar IVA</span>" if params["iva"] else ""
            red_txt=f"Reducción IRPF: <b>{int(red*100)}%</b>" if red>0 else "Sin reducción fiscal"
            badge="<div style='margin-top:8px;font-size:0.7rem;background:#EAF3DE;color:#3B6D11;padding:3px 8px;border-radius:20px;'>✅ Modalidad actual</div>" if es_actual else ""
            cols_fiscal[idx].markdown(f"""<div style="background:{CARD_BG};{borde}border-radius:10px;padding:1.1rem;text-align:center;"><div style="font-size:0.72rem;font-weight:600;color:{TEXT_SEC};text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">{mod}</div><div style="font-family:'DM Serif Display',serif;font-size:1.8rem;color:{ACCENT if es_actual else TEXT_PRI};">{rn_real:.1f}%</div><div style="font-size:0.7rem;color:{TEXT_SEC};margin-top:4px;">Rent. neta real/año</div><div style="font-size:0.75rem;color:{TEXT_PRI};margin-top:8px;">{red_txt}{iva_txt}</div><div style="font-size:0.7rem;color:{RED};margin-top:4px;">Impuesto est.: {impuesto:,.0f} €/año</div>{badge}</div>""",unsafe_allow_html=True)
        if mejor_mod: st.markdown(f'<div class="status-green" style="margin-top:1rem;"><b>💡 Recomendación IA:</b> La modalidad <b>{mejor_mod}</b> ofrece la mayor rentabilidad neta real ({mejor_rn:.1f}%).</div>',unsafe_allow_html=True)

    st.markdown('<div class="nc-section-title">Simulador de Subida de Renta</div>',unsafe_allow_html=True)
    if zona_tens:
        max_renta=int(renta_act*1.03); st.warning(f"🔒 Zona tensionada: subida máxima al IPC (3%). Renta máxima: {max_renta:,.0f} €/mes")
        nueva_renta=st.slider("Ajusta la renta (€)",min_value=int(renta_act*0.9),max_value=max_renta,value=int(renta_act),step=10)
    else:
        nueva_renta=st.slider("Ajusta la renta mensual (€)",min_value=int(renta_act*0.8),max_value=int(renta_mer*1.2),value=int(renta_act),step=25)
    ganancia_m=nueva_renta-renta_act; ganancia_a=ganancia_m*12
    nueva_neta=((nueva_renta-gastos_u)*12/safe_float(f.get("Valor_Construccion",0))*100) if safe_float(f.get("Valor_Construccion",0))>0 else 0
    s1,s2,s3=st.columns(3)
    s1.metric("Nueva Renta",f"{nueva_renta:,.0f} €/mes",delta=f"{ganancia_m:+.0f} €")
    s2.metric("Impacto Anual",f"{ganancia_a:+,.0f} €/año")
    s3.metric("Nueva Rent. Neta",f"{nueva_neta:.1f}%",delta=f"{nueva_neta-rent_neta:+.1f}%")

    st.markdown('<div class="nc-section-title">Comparativa de Activos — Renta vs Tasación</div>',unsafe_allow_html=True)
    rt=[tasacion(r) for _,r in df_inm.iterrows()]
    fig_comp=go.Figure()
    fig_comp.add_trace(go.Bar(name="Renta Actual",x=df_inm["Nombre"],y=df_inm["Renta"],marker_color=ACCENT,text=[f"{r:,.0f}€" for r in df_inm["Renta"]],textposition="outside"))
    fig_comp.add_trace(go.Bar(name="Renta Tasada",x=df_inm["Nombre"],y=rt,marker_color="#D0DFF0",text=[f"{r:,.0f}€" for r in rt],textposition="outside"))
    fig_comp.update_layout(barmode="group",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=10,b=10),height=300,yaxis=dict(showgrid=False,visible=False),xaxis=dict(showgrid=False),font=dict(family="DM Sans",size=12),legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    st.plotly_chart(fig_comp,use_container_width=True)

    st.markdown('<div class="nc-section-title">Análisis de Gastos Reales</div>',unsafe_allow_html=True)
    res=pd.concat([pd.DataFrame([{"Concepto":"Comunidad","Importe":safe_float(f.get("Comunidad",0)) if pd.notna(f.get("Comunidad",0)) else 0,"Deducible":"S"}]),df_gf[["Concepto","Importe","Deducible"]]])
    st.dataframe(res.style.format({"Importe":"{:,.2f} €"}),hide_index=True,use_container_width=True)

    # ── SABIO PATRIMONIAL — Fichas ──────────────────────────────
    _tipo_v, _msg_v = alerta_vencimiento(f)
    contexto_fichas = {
        "inmueble":             str(f.get("Nombre", "")),
        "tipo":                 str(f.get("Tipo", "")),
        "renta_actual":         safe_float(f.get("Renta", 0)),
        "renta_tasada_mercado": renta_mer,
        "desviacion_mercado_pct": round(desv, 1),
        "perdida_mensual":      round(perdida_m, 0),
        "perdida_anual":        round(perdida_a, 0),
        "comunidad_mensual":    safe_float(f.get("Comunidad", 0)),
        "gastos_totales":       round(gastos_u, 0),
        "rentabilidad_bruta":   round(rent_bruta, 2),
        "rentabilidad_neta":    round(rent_neta, 2),
        "fecha_inicio":         str(f.get("Fecha_Inicio_Contrato", "")),
        "fecha_vencimiento":    str(f.get("Fecha_Vencimiento_Contrato", "")),
        "tipo_arrendamiento":   tipo_arr,
        "zona_tensionada":      "Sí" if zona_tens else "No",
        "inquilino":            str(f.get("Inquilino", "")),
        "m2":                   safe_float(f.get("M2_Construidos", 0)),
        "estado":               str(f.get("Estado", "")),
        "cp":                   str(f.get("CP", "")),
        "ibi_anual":            safe_float(f.get("IBI_Anual", 0)),
        "intereses_hipoteca":   safe_float(f.get("Intereses_Hipoteca", 0)),
        "seguro_anual":         safe_float(f.get("Seguro_Anual", 0)),
        "alerta_vencimiento":   _msg_v if _tipo_v else "Sin alerta",
    }
    if st.session_state.get("sabio_prev_ficha") != f.get("Nombre"):
        limpiar_insight_seccion("fichas")
        st.session_state["sabio_prev_ficha"] = f.get("Nombre")
    render_sabio("fichas", contexto_fichas)

# ================================================================
# PANTALLA: AUDITORÍA DE MANTENIMIENTO
# ⚠️  SEPARADA de Fichas — era código huérfano en el original
# Deps: df_inm, safe_float()
# ================================================================
elif menu == "Auditoría Mantenimiento":
    if _sin_inmuebles:
        st.info("📭 Sin inmuebles. Ve a **Datos de Cartera**."); st.stop()
    st.markdown('<div class="nc-brand-header">Auditoría de Mantenimiento</div>',unsafe_allow_html=True)
    st.markdown('<div class="nc-brand-sub">Planificación de reformas por inmueble</div>',unsafe_allow_html=True)

    def calcular_costes_reforma(años, vc):
        if años>=8:   return {"urgente":vc*0.03,"medio":vc*0.08,"largo":vc*0.05}
        elif años>=5: return {"urgente":vc*0.02,"medio":vc*0.05,"largo":vc*0.04}
        else:         return {"urgente":vc*0.01,"medio":vc*0.03,"largo":vc*0.02}

    def desc_reforma(años):
        if años>=8:   return "Pintura exterior + tuberías + electricidad"
        elif años>=5: return "Pintura + revisión instalaciones"
        else:         return "Mantenimiento preventivo"

    año_actual=datetime.now().year
    datos_mant={}
    for _,row in df_inm.iterrows():
        nombre=row["Nombre"]; reforma=int(row.get("Año_Reforma",año_actual)); años=año_actual-reforma
        costes=calcular_costes_reforma(años,safe_float(row.get("Valor_Construccion",0)))
        datos_mant[nombre]={"urgente":round(costes["urgente"]),"medio":round(costes["medio"]),"largo":round(costes["largo"]),"reforma":reforma,"años":años,"desc":desc_reforma(años)}

    if "auditoria_expandido" not in st.session_state: st.session_state.auditoria_expandido={}

    def get_urgencia(reforma_año):
        años=datetime.now().year-reforma_año
        if años>=8: return "🔴 Urgente",RED
        elif años>=5: return "🟡 Medio",AMBER
        else: return "🟢 Largo",GREEN

    for nombre,datos in datos_mant.items():
        if nombre not in df_inm["Nombre"].tolist(): continue
        urgencia_label,urgencia_color=get_urgencia(datos["reforma"])
        total=datos["urgente"]+datos["medio"]+datos["largo"]
        expandido=st.session_state.auditoria_expandido.get(nombre,False)
        col_header,col_btn=st.columns([5,1])
        with col_header:
            st.markdown(f"""<div style="background:{CARD_BG};border:1px solid {BORDER};border-radius:6px;padding:0.7rem 1rem;margin-bottom:0.5rem;">
                <span style="font-weight:600;color:{TEXT_PRI};font-size:1.1rem;">{nombre}</span>
                <span style="color:{TEXT_SEC};font-size:0.95rem;margin-left:12px;">{urgencia_label} · {total:,.0f}€</span>
            </div>""",unsafe_allow_html=True)
        with col_btn:
            if st.button("▼" if not expandido else "▲",key=f"toggle_audit_{nombre}",use_container_width=True):
                st.session_state.auditoria_expandido[nombre]=not expandido; st.rerun()
        if expandido:
            st.markdown(f"""<div style="background:{CARD_BG};border:1px solid {BORDER};border-left:3px solid {urgencia_color};border-radius:6px;padding:1rem;margin-bottom:1rem;">
                <div><b>Reforma:</b> {datos["reforma"]} ({datos["años"]} años) · <b>Descripción:</b> {datos["desc"]}</div>
                <div style="margin-top:12px;padding-top:12px;border-top:1px dashed {BORDER};display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;">
                    <div><div style="color:{TEXT_SEC};font-size:0.9rem;">Urgente (0-6m)</div><div style="font-weight:600;color:{RED};">{datos["urgente"]:,.0f}€</div></div>
                    <div><div style="color:{TEXT_SEC};font-size:0.9rem;">Medio (6-18m)</div><div style="font-weight:600;color:{AMBER};">{datos["medio"]:,.0f}€</div></div>
                    <div><div style="color:{TEXT_SEC};font-size:0.9rem;">Largo (18+m)</div><div style="font-weight:600;color:{GREEN};">{datos["largo"]:,.0f}€</div></div>
                </div>
                <div style="margin-top:10px;color:{TEXT_SEC};font-size:0.85rem;">
                    <b>Recomendación:</b> {"Actuar en próximos 3 meses" if datos["años"]>=8 else ("Planifica presupuesto a medio plazo" if datos["años"]>=5 else "Inmueble en buen estado — mantenimiento preventivo")}
                </div>
            </div>""",unsafe_allow_html=True)

# ================================================================
# PANTALLA: DIARIO CONTABLE
# Registro de ingresos y gastos, parseo inteligente de texto
# Deps: df_inm, df_mov, guardar_movimientos(), parsear_ingresos()
# ================================================================
elif menu == "Gastos":
    st.markdown('<div class="nc-brand-header">Gastos</div>',unsafe_allow_html=True)
    st.markdown('<div class="nc-brand-sub">Registro de gastos · Facturas recibidas</div>',unsafe_allow_html=True)
    tab1,tab2,tab3=st.tabs(["📋 Registro de Gastos","📤 Registrar Gasto","💳 Gastos Fijos"])

    with tab1:
        # ── IMPORTS LOCALES ────────────────────────────────────────────
        uid_dc = st.session_state.get("user_id", "")

        # ── LISTAS GLOBALES ────────────────────────────────────────────
        l_inm  = df_inm["Nombre"].tolist() + ["Global"]
        l_cat  = ["Ingresos","Financiero","Tributario","Suministros","Seguros",
                  "Mantenimiento","Estructura","Comunidad","Otros"]
        meses_nombres = ["Todos","Enero","Febrero","Marzo","Abril","Mayo","Junio",
                         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

        # ── ESTILOS TARJETAS ───────────────────────────────────────────
        st.markdown("""
<style>
.dc-card{background:#fff;border:1px solid #D0DFF0;border-radius:12px 12px 0 0;
         padding:14px 18px;margin-bottom:0;transition:border-color .15s;
         border-bottom:none;}
.dc-card:hover{border-color:#185FA5;}
.dc-tag-ing{background:#EAF3DE;color:#27500A;font-size:11px;padding:2px 8px;
            border-radius:20px;font-weight:600;}
.dc-tag-gas{background:#FDECEA;color:#7F1D1D;font-size:11px;padding:2px 8px;
            border-radius:20px;font-weight:600;}
.dc-tag-ok {background:#EAF3DE;color:#27500A;font-size:11px;padding:2px 7px;border-radius:20px;}
.dc-tag-warn{background:#FFF9E6;color:#854F0B;font-size:11px;padding:2px 7px;border-radius:20px;}
.dc-tag-val{background:#E6F1FB;color:#0C447C;font-size:11px;padding:2px 7px;border-radius:20px;}
.dc-importe-ing{font-size:1.15rem;font-weight:700;color:#1a7a40;}
.dc-importe-gas{font-size:1.15rem;font-weight:700;color:#C0392B;}
.dc-label{font-size:0.68rem;color:#5A7A9A;text-transform:uppercase;letter-spacing:.06em;}

/* Expander pegado a la tarjeta — aspecto acordeón */
.dc-card + div [data-testid="stExpander"] {
    border:1px solid #D0DFF0 !important;
    border-top:none !important;
    border-radius:0 0 12px 12px !important;
    margin-bottom:12px !important;
    margin-top:0 !important;
}
.dc-card + div [data-testid="stExpander"] > div:first-child {
    border-radius:0 0 12px 12px !important;
    padding:6px 18px !important;
    background:#F8FAFC !important;
    border-top:1px dashed #D0DFF0 !important;
}
/* Ocultar el label vacío del expander */
.dc-card + div [data-testid="stExpander"] summary p {display:none !important;}
/* Flecha centrada */
.dc-card + div [data-testid="stExpander"] summary {
    justify-content:center !important;
    min-height:28px !important;
}
</style>""", unsafe_allow_html=True)

        # ── FILTROS ────────────────────────────────────────────────────
        col_titulo, col_modo = st.columns([5, 1])
        with col_titulo:
            st.markdown(
                "<div style='font-size:0.72rem;font-weight:600;letter-spacing:0.08em;"
                "text-transform:uppercase;color:#9CA3AF;margin-bottom:4px;'>"
                "Vista de operaciones</div>", unsafe_allow_html=True)
        with col_modo:
            modo_diario = st.radio("Modo", ["📋 Tarjetas","⚙️ Tabla"],
                                   horizontal=True, key="modo_diario",
                                   label_visibility="collapsed")

        # Fila de filtros
        ff1,ff2,ff3,ff4,ff5,ff6 = st.columns([1.2,1.2,2,2,1.5,0.7])
        with ff1:
            años_disp = sorted(pd.to_datetime(df_mov["Fecha"],errors="coerce")
                               .dt.year.dropna().unique(), reverse=True)
            f_año = st.selectbox("Año",["Todos"]+[int(a) for a in años_disp], key="dc_año")
        with ff2:
            f_mes = st.selectbox("Mes", meses_nombres, key="dc_mes")
        with ff3:
            f_inm = st.selectbox("Inmueble",["Todos"]+df_inm["Nombre"].tolist(), key="dc_inm")
        with ff4:
            f_buscar = st.text_input("Buscar", placeholder="Reparación, comunidad...",
                                     key="dc_buscar", label_visibility="visible")
        with ff5:
            f_tipo = st.selectbox("Tipo",["Todos","Ingreso","Gasto"], key="dc_tipo")
        with ff6:
            st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
            if st.button("🔄", use_container_width=True, key="dc_limpiar", help="Limpiar filtros"):
                for k in ["dc_año","dc_mes","dc_inm","dc_buscar","dc_tipo"]:
                    if k in st.session_state: del st.session_state[k]
                st.rerun()

        # ── APLICAR FILTROS ────────────────────────────────────────────
        df_f = df_mov.copy()
        df_f["Fecha"] = pd.to_datetime(df_f["Fecha"], errors="coerce")
        if f_año  != "Todos": df_f = df_f[df_f["Fecha"].dt.year == int(f_año)]
        if f_mes  != "Todos": df_f = df_f[df_f["Fecha"].dt.month == meses_nombres.index(f_mes)]
        if f_inm  != "Todos": df_f = df_f[df_f["Apartamento"] == f_inm]
        if f_tipo != "Todos": df_f = df_f[df_f["Tipo"] == f_tipo]
        if f_buscar.strip():
            df_f = df_f[df_f["Concepto"].str.contains(f_buscar.strip(),case=False,na=False)]
        df_f = df_f.sort_values("Fecha", ascending=False).reset_index(drop=True)

        # ── RESUMEN 3 CARDS ────────────────────────────────────────────
        t_ing = df_f[df_f["Tipo"]=="Ingreso"]["Importe"].sum()
        t_gas = df_f[df_f["Tipo"]=="Gasto"]["Importe"].sum()
        bal   = t_ing - t_gas
        bal_c = GREEN if bal >= 0 else RED
        rc1,rc2,rc3,rc4 = st.columns(4)
        rc1.markdown(f"<div style='background:{CARD_BG};border:1px solid {BORDER};"
                     f"border-top:3px solid {GREEN};border-radius:10px;padding:.7rem;"
                     f"text-align:center;margin:8px 0;'>"
                     f"<div class='dc-label'>Ingresos</div>"
                     f"<div style='font-size:1.1rem;font-weight:700;color:{GREEN};'>+{t_ing:,.0f} €</div>"
                     f"</div>", unsafe_allow_html=True)
        rc2.markdown(f"<div style='background:{CARD_BG};border:1px solid {BORDER};"
                     f"border-top:3px solid {RED};border-radius:10px;padding:.7rem;"
                     f"text-align:center;margin:8px 0;'>"
                     f"<div class='dc-label'>Gastos</div>"
                     f"<div style='font-size:1.1rem;font-weight:700;color:{RED};'>−{t_gas:,.0f} €</div>"
                     f"</div>", unsafe_allow_html=True)
        rc3.markdown(f"<div style='background:{CARD_BG};border:1px solid {BORDER};"
                     f"border-top:3px solid {bal_c};border-radius:10px;padding:.7rem;"
                     f"text-align:center;margin:8px 0;'>"
                     f"<div class='dc-label'>Balance</div>"
                     f"<div style='font-size:1.1rem;font-weight:700;color:{bal_c};'>{bal:+,.0f} €</div>"
                     f"</div>", unsafe_allow_html=True)
        n_sf = len(df_f[df_f.get("tiene_factura", pd.Series([False]*len(df_f),dtype=bool)) == False]) if "tiene_factura" in df_f.columns else 0
        rc4.markdown(f"<div style='background:{CARD_BG};border:1px solid {BORDER};"
                     f"border-top:3px solid {AMBER};border-radius:10px;padding:.7rem;"
                     f"text-align:center;margin:8px 0;'>"
                     f"<div class='dc-label'>Sin factura</div>"
                     f"<div style='font-size:1.1rem;font-weight:700;color:{AMBER};'>{n_sf}</div>"
                     f"</div>", unsafe_allow_html=True)

        st.caption(f"📊 {len(df_f)} operaciones" +
                   (f" de {len(df_mov)} totales" if len(df_f) != len(df_mov) else ""))
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # ==============================================================
        # MODO TARJETAS
        # ==============================================================
        if modo_diario == "📋 Tarjetas":

            if df_f.empty:
                st.info("No hay operaciones con los filtros seleccionados.")
            else:
                # Paginación — 20 por página para no sobrecargar
                PAGE_SIZE = 20
                total_pags = max(1, (len(df_f) - 1) // PAGE_SIZE + 1)
                if "dc_pag" not in st.session_state: st.session_state.dc_pag = 1
                # Resetear página si cambian filtros
                _filtro_hash = f"{f_año}{f_mes}{f_inm}{f_buscar}{f_tipo}"
                if st.session_state.get("dc_filtro_hash") != _filtro_hash:
                    st.session_state.dc_pag = 1
                    st.session_state.dc_filtro_hash = _filtro_hash

                pag_actual = st.session_state.dc_pag
                df_pag = df_f.iloc[(pag_actual-1)*PAGE_SIZE : pag_actual*PAGE_SIZE]

                for idx, row in df_pag.iterrows():
                    es_ing  = str(row.get("Tipo","")) == "Ingreso"
                    importe = float(row.get("Importe", 0))
                    fecha_s = row["Fecha"].strftime("%d/%m/%Y") if pd.notna(row["Fecha"]) else "—"
                    concepto = str(row.get("Concepto","—"))
                    inmueble = str(row.get("Apartamento","—"))
                    categoria = str(row.get("Categoría","—"))
                    deducible = str(row.get("Deducible","N"))
                    tiene_fac = bool(row.get("tiene_factura", False))
                    estado_fis = str(row.get("estado_fiscal","pendiente"))
                    mov_id = row.get("id", None)

                    # Badge de estado factura
                    if estado_fis == "validado":
                        badge_fac = "<span class='dc-tag-val'>✅ Validado</span>"
                    elif tiene_fac:
                        badge_fac = "<span class='dc-tag-ok'>📄 Con factura</span>"
                    else:
                        badge_fac = "<span class='dc-tag-warn'>⚠️ Sin factura</span>"

                    tag_tipo = (f"<span class='dc-tag-ing'>Ingreso</span>" if es_ing
                                else f"<span class='dc-tag-gas'>Gasto</span>")
                    imp_html = (f"<span class='dc-importe-ing'>+{importe:,.2f} €</span>" if es_ing
                                else f"<span class='dc-importe-gas'>−{importe:,.2f} €</span>")
                    ded_txt = "✅ Deducible" if deducible == "S" else "—"

                    # Cabecera de tarjeta siempre visible
                    st.markdown(f"""
<div class="dc-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div style="flex:1;min-width:0;">
      <div style="font-size:0.72rem;color:{TEXT_SEC};margin-bottom:3px;">
        📅 {fecha_s} &nbsp;·&nbsp; 🏠 {inmueble}
      </div>
      <div style="font-size:0.97rem;font-weight:600;color:{TEXT_PRI};
                  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                  max-width:480px;margin-bottom:6px;">{concepto}</div>
      <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
        {tag_tipo}
        <span style="font-size:11px;color:{TEXT_SEC};">{categoria}</span>
        <span style="font-size:11px;color:{TEXT_SEC};">{ded_txt}</span>
        {badge_fac}
      </div>
    </div>
    <div style="text-align:right;padding-left:16px;flex-shrink:0;">
      {imp_html}
    </div>
  </div>
</div>""", unsafe_allow_html=True)

                    # Panel expandible
                    # Key dinámica — cambia tras acción, fuerza expander cerrado
                    _render_v = st.session_state.get("dc_render_v", 0)
                    with st.expander("",
                                     expanded=False,
                                     key=f"exp_{idx}_{_render_v}"):
                        col_det, col_fac = st.columns([1, 1])

                        with col_det:
                            st.markdown(f"**Categoría:** {categoria}")
                            st.markdown(f"**Tipo:** {'Ingreso' if es_ing else 'Gasto'}")
                            st.markdown(f"**Deducible:** {ded_txt}")
                            st.markdown(f"**Estado fiscal:** {estado_fis}")

                            # Edición rápida de campos
                            st.markdown("---")
                            nuevo_concepto = st.text_input("Concepto",
                                value=concepto, key=f"ed_con_{idx}")
                            nuevo_importe  = st.number_input("Importe (€)",
                                value=importe, min_value=0.0, step=1.0,
                                key=f"ed_imp_{idx}", format="%.2f")
                            nueva_cat = st.selectbox("Categoría", l_cat,
                                index=l_cat.index(categoria) if categoria in l_cat else 0,
                                key=f"ed_cat_{idx}")
                            nuevo_ded = st.selectbox("Deducible", ["S","N"],
                                index=0 if deducible=="S" else 1,
                                key=f"ed_ded_{idx}")

                            ce1, ce2 = st.columns(2)
                            with ce1:
                                if st.button("💾 Guardar cambios",
                                             key=f"btn_guardar_{idx}",
                                             use_container_width=True):
                                    if mov_id is not None:
                                        import requests as _req
                                        from supabase_db import SUPABASE_URL, SUPABASE_KEY
                                        _h = {
                                            "apikey": SUPABASE_KEY,
                                            "Authorization": f"Bearer {st.session_state.get('access_token', SUPABASE_KEY)}",
                                            "Content-Type": "application/json",
                                            "Prefer": "return=minimal"
                                        }
                                        _r = _req.patch(
                                            f"{SUPABASE_URL}/rest/v1/movimientos"
                                            f"?id=eq.{mov_id}&user_id=eq.{uid_dc}",
                                            headers=_h,
                                            json={"concepto": nuevo_concepto,
                                                  "importe": nuevo_importe,
                                                  "categoria": nueva_cat,
                                                  "deducible": nuevo_ded},
                                            timeout=10
                                        )
                                        if _r.status_code in (200, 204):
                                            st.success("✅ Guardado")
                                            st.session_state.df_mov_persistent = leer_movimientos(uid_dc)
                                            st.session_state["dc_render_v"] = st.session_state.get("dc_render_v",0)+1
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Error {_r.status_code}")
                                    else:
                                        st.warning("⚠️ Este movimiento no tiene id en Supabase. Usa el modo Tabla para editarlo.")

                            with ce2:
                                if st.button("🗑️ Eliminar",
                                             key=f"btn_del_{idx}",
                                             use_container_width=True,
                                             type="secondary"):
                                    if mov_id is not None:
                                        import requests as _req
                                        from supabase_db import SUPABASE_URL, SUPABASE_KEY
                                        _h = {
                                            "apikey": SUPABASE_KEY,
                                            "Authorization": f"Bearer {st.session_state.get('access_token', SUPABASE_KEY)}",
                                            "Content-Type": "application/json"
                                        }
                                        _r = _req.delete(
                                            f"{SUPABASE_URL}/rest/v1/movimientos"
                                            f"?id=eq.{mov_id}&user_id=eq.{uid_dc}",
                                            headers=_h, timeout=10
                                        )
                                        if _r.status_code in (200, 204):
                                            st.success("✅ Eliminado")
                                            st.session_state.df_mov_persistent = leer_movimientos(uid_dc)
                                            st.session_state["dc_render_v"] = st.session_state.get("dc_render_v",0)+1
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Error {_r.status_code}")
                                    else:
                                        st.warning("⚠️ Sin id — usa modo Tabla.")

                        with col_fac:
                            st.markdown("**📄 Factura**")

                            if tiene_fac and row.get("factura_url"):
                                # Ya tiene factura — mostrar opciones
                                url_firmada = obtener_url_factura(uid_dc, str(row["factura_url"]))
                                if url_firmada:
                                    st.markdown(
                                        f"<a href='{url_firmada}' target='_blank' "
                                        f"style='display:inline-block;background:#E6F1FB;"
                                        f"color:#0C447C;padding:6px 14px;border-radius:6px;"
                                        f"font-size:13px;font-weight:600;text-decoration:none;"
                                        f"border:1px solid #B5D4F4;'>👁️ Ver PDF</a>",
                                        unsafe_allow_html=True
                                    )
                                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

                                # Cambiar estado fiscal
                                nuevo_estado = st.selectbox(
                                    "Estado fiscal",
                                    ["con_factura","validado","pendiente"],
                                    index=["con_factura","validado","pendiente"].index(estado_fis)
                                          if estado_fis in ["con_factura","validado","pendiente"] else 0,
                                    key=f"est_{idx}"
                                )
                                if st.button("💾 Actualizar estado",
                                             key=f"btn_est_{idx}",
                                             use_container_width=True):
                                    if mov_id and actualizar_estado_fiscal_movimiento(uid_dc, mov_id, nuevo_estado):
                                        st.success("✅ Estado actualizado")
                                        st.session_state.df_mov_persistent = leer_movimientos(uid_dc)
                                        st.session_state["dc_render_v"] = st.session_state.get("dc_render_v",0)+1
                                        st.rerun()
                                    else:
                                        st.error("❌ Error actualizando estado")

                                # Eliminar factura
                                if st.button("🗑️ Quitar factura",
                                             key=f"btn_delfac_{idx}",
                                             use_container_width=True):
                                    if mov_id:
                                        ok_del = eliminar_factura(uid_dc, mov_id, str(row["factura_url"]))
                                        if ok_del:
                                            st.success("✅ Factura eliminada")
                                            st.session_state.df_mov_persistent = leer_movimientos(uid_dc)
                                            st.session_state["dc_render_v"] = st.session_state.get("dc_render_v",0)+1
                                            st.rerun()
                                        else:
                                            st.error("❌ Error eliminando factura")
                            else:
                                # Sin factura — uploader
                                st.markdown(
                                    "<div style='background:#FFF9E6;border:1px solid #F39C12;"
                                    "border-radius:8px;padding:10px 12px;font-size:12px;"
                                    "color:#854F0B;margin-bottom:10px;'>"
                                    "⚠️ Sin factura. Súbela para que sea deducible.</div>",
                                    unsafe_allow_html=True
                                )
                                archivo = st.file_uploader(
                                    "Subir factura (PDF, JPG, PNG)",
                                    type=["pdf","jpg","jpeg","png"],
                                    key=f"fac_{idx}",
                                    label_visibility="collapsed"
                                )
                                if archivo and mov_id:
                                    ext = archivo.name.split(".")[-1].lower()
                                    if st.button("📤 Subir factura",
                                                 key=f"btn_up_{idx}",
                                                 use_container_width=True,
                                                 type="primary"):
                                        with st.spinner("Subiendo..."):
                                            res = subir_factura(uid_dc, mov_id,
                                                                archivo.read(), ext)
                                        if res["ok"]:
                                            st.success("✅ Factura subida correctamente")
                                            st.session_state.df_mov_persistent = leer_movimientos(uid_dc)
                                            st.session_state["dc_render_v"] = st.session_state.get("dc_render_v",0)+1
                                            st.rerun()
                                        else:
                                            st.error(f"❌ {res['error']}")
                                elif archivo and not mov_id:
                                    st.warning("⚠️ Este movimiento no tiene id. Guarda primero desde modo Tabla.")

                # ── PAGINACIÓN ─────────────────────────────────────────
                if total_pags > 1:
                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                    pp1,pp2,pp3 = st.columns([1,3,1])
                    with pp1:
                        if pag_actual > 1:
                            if st.button("← Anterior", use_container_width=True, key="dc_prev"):
                                st.session_state.dc_pag -= 1; st.rerun()
                    with pp2:
                        st.markdown(
                            f"<div style='text-align:center;font-size:0.8rem;color:{TEXT_SEC};"
                            f"padding-top:8px;'>Página {pag_actual} de {total_pags}"
                            f" · {len(df_f)} operaciones</div>",
                            unsafe_allow_html=True
                        )
                    with pp3:
                        if pag_actual < total_pags:
                            if st.button("Siguiente →", use_container_width=True, key="dc_next"):
                                st.session_state.dc_pag += 1; st.rerun()

        # ==============================================================
        # MODO TABLA (avanzado — data_editor completo)
        # ==============================================================
        else:
            # Filtros extra en modo tabla
            ft1, ft2 = st.columns(2)
            with ft1:
                f_cat2 = st.selectbox("Categoría",["Todas"]+l_cat, key="dc_cat")
            with ft2:
                f_ded2 = st.selectbox("Deducible",["Todos","S","N"], key="dc_ded")

            df_t = df_f.copy()
            if f_cat2 != "Todas": df_t = df_t[df_t["Categoría"] == f_cat2]
            if f_ded2 != "Todos": df_t = df_t[df_t["Deducible"] == f_ded2]

            cols_tabla = [c for c in
                ["Fecha","Apartamento","Concepto","Categoría","Tipo","Importe","Deducible"]
                if c in df_t.columns]
            df_tabla = df_t[cols_tabla].copy()

            config_tabla = {
                "Fecha":      st.column_config.DateColumn("📅 Fecha", format="DD/MM/YYYY"),
                "Apartamento":st.column_config.SelectboxColumn("🏠 Inmueble",
                               options=l_inm, required=True),
                "Concepto":   st.column_config.TextColumn("📝 Concepto", width="large"),
                "Categoría":  st.column_config.SelectboxColumn("🗂 Categoría",
                               options=l_cat, required=True),
                "Tipo":       st.column_config.SelectboxColumn("↕ Tipo",
                               options=["Ingreso","Gasto"], required=True),
                "Importe":    st.column_config.NumberColumn("💶 Importe (€)",
                               format="%.2f €", min_value=0),
                "Deducible":  st.column_config.SelectboxColumn("✅ Fiscal",
                               options=["S","N"], required=True),
            }

            df_ed = st.data_editor(
                df_tabla, num_rows="dynamic", use_container_width=True,
                hide_index=True, column_config=config_tabla, key="tabla_completa"
            )

            # KPIs modo tabla
            t_ing_t = df_ed[df_ed["Tipo"]=="Ingreso"]["Importe"].sum()
            t_gas_t = df_ed[df_ed["Tipo"]=="Gasto"]["Importe"].sum()
            ded_t   = df_ed[(df_ed["Tipo"]=="Gasto")&(df_ed["Deducible"]=="S")]["Importe"].sum()
            pct_d   = (ded_t/t_gas_t*100) if t_gas_t>0 else 0
            k1,k2,k3,k4 = st.columns(4)
            for _c, _l, _v, _col in [
                (k1,"Ingresos",   f"+{t_ing_t:,.0f} €", GREEN),
                (k2,"Gastos",     f"−{t_gas_t:,.0f} €", RED),
                (k3,"Deducibles", f"{ded_t:,.0f} €",    ACCENT),
                (k4,"% Deducible",f"{pct_d:.0f}%",      ACCENT),
            ]:
                _c.markdown(
                    f"<div style='background:{CARD_BG};border:1px solid {BORDER};"
                    f"border-top:3px solid {_col};border-radius:10px;padding:.7rem;"
                    f"text-align:center;margin:8px 0;'>"
                    f"<div class='dc-label'>{_l}</div>"
                    f"<div style='font-size:1rem;font-weight:700;color:{_col};'>{_v}</div>"
                    f"</div>", unsafe_allow_html=True)

            # Botón guardar modo tabla
            st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
            if st.button("💾 Guardar Cambios", type="primary",
                         use_container_width=True, key="guardar_tabla"):
                # Validaciones
                df_val = df_ed.copy()
                df_val = df_val[~(df_val["Importe"].isna() &
                                  df_val["Concepto"].isna() &
                                  df_val["Apartamento"].isna())]
                df_val["Importe"] = pd.to_numeric(df_val["Importe"],errors="coerce").fillna(0)
                filas_malas = []
                for _col in ["Fecha","Apartamento","Tipo","Importe"]:
                    if _col in df_val.columns:
                        _mask = df_val[_col].isna()|(df_val[_col].astype(str).str.strip()=="")
                        filas_malas += df_val[_mask].index.tolist()
                if filas_malas:
                    st.warning(f"⚠️ {len(set(filas_malas))} fila(s) incompletas.")
                elif len(df_val[df_val["Importe"]<=0]) > 0:
                    st.warning("⚠️ Hay importes en 0 o negativos.")
                else:
                    # Reconstruir con filtros activos
                    if any(v != d for v, d in [(f_año,"Todos"),(f_mes,"Todos"),
                                               (f_inm,"Todos"),(f_tipo,"Todos"),
                                               (f_cat2,"Todas"),(f_ded2,"Todos")]):
                        df_comp = st.session_state.df_mov_persistent.copy()
                        df_comp["Fecha"] = pd.to_datetime(df_comp["Fecha"],errors="coerce")
                        mask = pd.Series([True]*len(df_comp))
                        if f_año  != "Todos": mask = mask&(df_comp["Fecha"].dt.year!=int(f_año))
                        if f_mes  != "Todos": mask = mask&(df_comp["Fecha"].dt.month!=meses_nombres.index(f_mes))
                        if f_inm  != "Todos": mask = mask&(df_comp["Apartamento"]!=f_inm)
                        if f_tipo != "Todos": mask = mask&(df_comp["Tipo"]!=f_tipo)
                        if f_cat2 != "Todas": mask = mask&(df_comp.get("Categoría",pd.Series())!=f_cat2)
                        if f_ded2 != "Todos": mask = mask&(df_comp.get("Deducible",pd.Series())!=f_ded2)
                        df_final = pd.concat([df_comp[mask],df_val],ignore_index=True)
                        df_final = df_final.sort_values("Fecha",ascending=False).reset_index(drop=True)
                    else:
                        df_final = df_val
                    st.session_state.df_mov_persistent = df_final
                    ok = guardar_movimientos_completo(df_final, user_id=uid_dc)
                    if ok:
                        n  = len(df_final)
                        ti = df_final[df_final["Tipo"]=="Ingreso"]["Importe"].sum()
                        tg = df_final[df_final["Tipo"]=="Gasto"]["Importe"].sum()
                        st.success(f"✅ Guardado: {n} ops · Ingresos {ti:,.0f} € · Gastos {tg:,.0f} €")
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar en Supabase. Inténtalo de nuevo.")

    with tab2:
        if "gasto_guardado" not in st.session_state: st.session_state.gasto_guardado=False
        if st.session_state.gasto_guardado:
            st.success("✅ Gasto guardado correctamente.")
            if st.button("➕ Registrar otro gasto",key="nuevo_gasto"):
                st.session_state.gasto_guardado=False; st.rerun()
        else:
            st.markdown("### 📤 Registrar Gasto")
            archivo=st.file_uploader("Adjunta factura PDF o foto",type=["pdf","jpg","png","jpeg"])
            if archivo: st.info("📝 Lectura automática de facturas — próximamente disponible.")
            concepto_gasto=st.text_input("Concepto",placeholder="Reparación lavadora Huerto 1...")
            col_g1,col_g2=st.columns(2)
            with col_g1:
                inmueble_g=st.selectbox("Inmueble",["— Selecciona —"]+df_inm["Nombre"].tolist(),key="inmg")
                importe_g=st.number_input("Importe (€)",min_value=0.0,step=0.01,format="%.2f")
            with col_g2:
                categoria_g=st.selectbox("Categoría",["Mantenimiento","Suministros","Comunidad","Seguros","Tributario","Financiero","Otros"])
                deducible_g=st.selectbox("¿Es deducible?",["S","N"])
            if st.button("💾 Guardar Gasto",type="primary",key="guardar_gasto"):
                if inmueble_g=="— Selecciona —": st.error("Selecciona un inmueble")
                elif importe_g<=0: st.error("El importe debe ser mayor que 0")
                elif not concepto_gasto.strip(): st.error("Escribe un concepto")
                else:
                    nuevo=[{"Fecha":datetime.now().strftime("%Y-%m-%d"),"Apartamento":inmueble_g,"Concepto":concepto_gasto,"Categoría":categoria_g,"Tipo":"Gasto","Importe":importe_g,"Deducible":deducible_g}]
                    guardar_movimientos(nuevo)
                    st.session_state.df_mov_persistent=leer_movimientos(st.session_state.get("user_id",""))
                    st.session_state.gasto_guardado=True; st.rerun()

    with tab3:
        st.markdown('<div class="nc-section-title">💳 Gastos Fijos Mensuales</div>',unsafe_allow_html=True)
        uid=st.session_state.get("user_id","")
        if "df_gf" not in st.session_state or st.session_state.get("reload_gf",False):
            st.session_state.df_gf=leer_gastos_recurrentes(uid); st.session_state.reload_gf=False
        df_gf=st.session_state.df_gf
        df_gf_activos=df_gf[df_gf["activo"]==True].reset_index(drop=True) if not df_gf.empty else pd.DataFrame()
        sub1,sub2=st.tabs(["📋 Registrar este mes","⚙️ Gestionar gastos fijos"])

        with sub1:
            st.caption("Marca los gastos que quieres registrar este mes y pulsa Registrar.")
            if df_gf_activos.empty:
                st.info("No tienes gastos fijos configurados. Ve a ⚙️ Gestionar para añadirlos.")
            else:
                mes_actual=datetime.now().month; año_actual=datetime.now().year
                df_mes=df_mov[(pd.to_datetime(df_mov["Fecha"],errors="coerce").dt.month==mes_actual)&(pd.to_datetime(df_mov["Fecha"],errors="coerce").dt.year==año_actual)&(df_mov["Tipo"]=="Gasto")]
                col_apt="Inmueble" if "Inmueble" in df_mes.columns else "Apartamento"
                conceptos_mes=set(df_mes[col_apt].astype(str)+"|"+df_mes["Concepto"].astype(str))
                seleccionados=[]; total_sel=0.0
                for i,row in df_gf_activos.iterrows():
                    clave=f"{row['inmueble']}|{row['concepto']}"; ya_registrado=clave in conceptos_mes
                    c_check,c_info,c_imp,c_est=st.columns([0.5,4,1.5,1.5])
                    with c_check:
                        if ya_registrado: st.checkbox("",value=False,disabled=True,key=f"gf_reg_{i}")
                        else:
                            if st.checkbox("",value=True,key=f"gf_reg_{i}"): seleccionados.append(row); total_sel+=float(row["importe"])
                    with c_info: st.markdown(f"**{row['concepto']}** — *{row['inmueble']}* · {row['categoria']}")
                    with c_imp: st.markdown(f"<div style='text-align:right;font-weight:600;padding-top:0.5rem;'>{float(row['importe']):,.2f} €</div>",unsafe_allow_html=True)
                    with c_est:
                        if ya_registrado: st.markdown("<div style='color:#1a7a40;font-size:0.8rem;padding-top:0.6rem;'>✅ Registrado</div>",unsafe_allow_html=True)
                        else: st.markdown("<div style='color:#5A7A9A;font-size:0.8rem;padding-top:0.6rem;'>Pendiente</div>",unsafe_allow_html=True)
                st.divider()
                cr1,cr2=st.columns([3,1])
                with cr1: st.markdown(f"**{len(seleccionados)} seleccionados** · Total: **{total_sel:,.2f} €**")
                with cr2:
                    if st.button("💾 Registrar seleccionados",type="primary",use_container_width=True,disabled=len(seleccionados)==0,key="btn_reg_gf"):
                        nuevos=[{"Fecha":datetime.now().strftime("%Y-%m-%d"),"Apartamento":r["inmueble"],"Concepto":r["concepto"],"Categoría":r["categoria"],"Tipo":"Gasto","Importe":float(r["importe"]),"Deducible":r.get("deducible","S")} for r in seleccionados]
                        guardar_movimientos(nuevos); st.session_state.df_mov_persistent=leer_movimientos(uid)
                        st.success(f"✅ {len(nuevos)} gastos registrados por {total_sel:,.2f} €"); st.rerun()

        with sub2:
            st.caption("Añade, edita o desactiva tus gastos fijos.")
            with st.expander("➕ Añadir nuevo gasto fijo"):
                na1,na2=st.columns(2)
                with na1:
                    nv_inm=st.selectbox("Inmueble",df_inm["Nombre"].tolist(),key="nv_inm")
                    nv_con=st.text_input("Concepto",placeholder="Ej: Seguro hogar",key="nv_con")
                with na2:
                    nv_cat=st.selectbox("Categoría",["Comunidad","Financiero","Seguros","Mantenimiento","Suministros","Tributario","Otros"],key="nv_cat")
                    nv_imp=st.number_input("Importe (€/mes)",min_value=0.01,step=0.01,format="%.2f",key="nv_imp")
                nv_ded=st.selectbox("¿Deducible?",["S","N"],key="nv_ded")
                if st.button("💾 Guardar nuevo gasto fijo",key="btn_add_gf"):
                    if nv_con.strip() and nv_imp>0:
                        ok=guardar_gasto_recurrente(uid,nv_inm,nv_con.strip(),nv_cat,nv_imp,nv_ded)
                        if ok: st.success(f"✅ Añadido: {nv_con} — {nv_imp:.2f} €/mes"); st.session_state.reload_gf=True; st.rerun()
                        else: st.error("❌ Error al guardar.")
                    else: st.warning("⚠️ Completa concepto e importe.")
            if df_gf.empty:
                st.info("No hay gastos fijos configurados.")
            else:
                st.markdown("**Gastos configurados:**")
                for _,row in df_gf.iterrows():
                    gid=int(row["id"]); activo=bool(row["activo"])
                    g1,g2,g3,g4,g5=st.columns([2.5,2,1.2,1,1])
                    with g1: nuevo_concepto=st.text_input("",value=row["concepto"],key=f"gf_con_{gid}",label_visibility="collapsed")
                    with g2: st.markdown(f"<div style='padding-top:0.55rem;color:#5A7A9A;font-size:0.85rem;'>{row['inmueble']}</div>",unsafe_allow_html=True)
                    with g3: nuevo_imp=st.number_input("",value=float(row["importe"]),min_value=0.01,step=0.01,format="%.2f",key=f"gf_imp_{gid}",label_visibility="collapsed")
                    with g4:
                        if st.button("💾" if activo else "🔄",key=f"gf_upd_{gid}"):
                            actualizar_gasto_recurrente(gid,importe=nuevo_imp,concepto=nuevo_concepto,activo=True)
                            st.session_state.reload_gf=True; st.rerun()
                    with g5:
                        if activo:
                            if st.button("⏸️",key=f"gf_des_{gid}"):
                                actualizar_gasto_recurrente(gid,activo=False); st.session_state.reload_gf=True; st.rerun()
                        else:
                            st.markdown("<div style='color:#C0392B;font-size:0.75rem;padding-top:0.6rem;'>Inactivo</div>",unsafe_allow_html=True)
                            if st.button("🗑️",key=f"gf_del_{gid}"):
                                eliminar_gasto_recurrente(gid); st.session_state.reload_gf=True; st.rerun()

# ================================================================
# PANTALLA: CASH FLOW
# Módulo completo — cashflow_module.py
# ================================================================
elif menu == "Cash Flow":
    df_gastos_rec_cf = leer_gastos_recurrentes(user_id=st.session_state.user_id)
    render_cashflow(df_mov, df_inm, df_gastos_rec_cf, safe_float)
# ================================================================
# PANTALLA: SUMINISTROS
# Auditoría de potencia eléctrica, comparador de tarifas
# Deps: df_inm, safe_float()
# ================================================================
elif menu == "Suministros":
    st.markdown('<div class="nc-brand-header">Optimización de Suministros</div>',unsafe_allow_html=True)
    st.markdown('<div class="nc-brand-sub">Auditoría de potencia eléctrica · Comparador tarifario</div>',unsafe_allow_html=True)
    inmueble_sel=st.selectbox("Selecciona inmueble:",df_inm["Nombre"].tolist())
    f=df_inm[df_inm["Nombre"]==inmueble_sel].iloc[0]; hab=int(f.get("Habitaciones",2))
    st.markdown('<div class="nc-section-title">⚡ Auditoría de Potencia Contratada</div>',unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        potencia_actual=st.number_input("Potencia contratada (kW)",min_value=1.0,max_value=30.0,value=4.4,step=0.1)
        tiene_ac=st.checkbox("¿Aire acondicionado?",value=True); tiene_vitro=st.checkbox("¿Vitrocerámica/inducción?",value=True)
        tiene_termo=st.checkbox("¿Termo eléctrico?",value=False); tiene_cargador=st.checkbox("¿Cargador vehículo eléctrico?",value=False)
    base_kw={1:2.3,2:3.3,3:3.3,4:4.4,5:5.5}.get(min(hab,5),4.4); extra=0.0
    if tiene_ac: extra+=2.0
    if tiene_vitro: extra+=1.5
    if tiene_termo: extra+=1.0
    if tiene_cargador: extra+=3.7
    POTENCIAS_REE=[1.15,2.3,3.45,4.6,5.75,6.9,8.05,9.2,10.35,11.5,14.49,17.25]
    pot_rec=next((p for p in POTENCIAS_REE if p>=base_kw+extra),17.25)
    coste_act=potencia_actual*42.0; coste_opt=pot_rec*42.0; ahorro=coste_act-coste_opt
    with col2:
        st.markdown(f"""<div style="background:{CARD_BG};border:1px solid {BORDER};border-radius:10px;padding:1.4rem;">
            <div class="nc-kpi__label">Potencia recomendada</div>
            <div style="font-family:'DM Serif Display',serif;font-size:2.2rem;color:{ACCENT};">{pot_rec} kW</div>
            <div class="nc-kpi__sub">Basado en {hab} hab. + equipos</div>
            <hr style="border:0;border-top:1px solid {BORDER};margin:0.8rem 0;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;"><span class="nc-kpi__label">Coste actual/año</span><span style="font-size:0.9rem;font-weight:600;color:{RED};">{coste_act:,.0f} €</span></div>
            <div style="display:flex;justify-content:space-between;"><span class="nc-kpi__label">Coste óptimo/año</span><span style="font-size:0.9rem;font-weight:600;color:{GREEN};">{coste_opt:,.0f} €</span></div>
        </div>""",unsafe_allow_html=True)
        cls_a="status-green" if ahorro>5 else ("status-red" if ahorro<-5 else "status-green")
        msg_a=f"✅ Ahorro potencial: {ahorro:,.0f} €/año · Bajar a {pot_rec} kW" if ahorro>5 else (f"⚠️ Potencia insuficiente · Subir a {pot_rec} kW" if ahorro<-5 else "✅ Potencia correctamente ajustada")
        st.markdown(f'<div class="{cls_a}" style="margin-top:0.8rem;">{msg_a}</div>',unsafe_allow_html=True)

    st.markdown('<div class="nc-section-title">📊 Comparador Tarifa Fija vs Indexada</div>',unsafe_allow_html=True)
    tc1,tc2,tc3=st.columns(3)
    with tc1: kwh=st.number_input("Consumo mensual (kWh)",min_value=50,max_value=2000,value=200,step=10)
    with tc2: pfijo=st.number_input("Tarifa fija (€/kWh)",min_value=0.05,max_value=0.50,value=0.18,step=0.01,format="%.3f")
    with tc3: ppool=st.number_input("Pool PVPC (€/kWh)",min_value=0.02,max_value=0.40,value=0.12,step=0.01,format="%.3f")
    pind=ppool+0.04; cf_mes=kwh*pfijo; ci_mes=kwh*pind; dif_a=(cf_mes-ci_mes)*12
    fig_tar=go.Figure(go.Bar(x=["Tarifa Fija","Tarifa Indexada"],y=[cf_mes,ci_mes],marker_color=[ACCENT,"#639922"],text=[f"{cf_mes:.2f} €/mes",f"{ci_mes:.2f} €/mes"],textposition="outside",width=0.35))
    fig_tar.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=20,b=10),height=260,yaxis=dict(showgrid=False,visible=False),xaxis=dict(showgrid=False),font=dict(family="DM Sans",size=13),showlegend=False)
    st.plotly_chart(fig_tar,use_container_width=True)
    r1,r2,r3=st.columns(3)
    r1.metric("Coste fijo/mes",f"{cf_mes:.2f} €"); r2.metric("Coste indexado/mes",f"{ci_mes:.2f} €",delta=f"{-(cf_mes-ci_mes):+.2f} €"); r3.metric("Ahorro anual",f"{dif_a:+.0f} €")
    if dif_a>30: rec,cls_t=f"✅ Tarifa <b>indexada</b> más barata. Ahorro: <b>{dif_a:.0f} €/año</b>.","status-green"
    elif dif_a<-30: rec,cls_t="⚠️ Tarifa <b>fija</b> más económica con pool actual.","status-yellow"
    else: rec,cls_t="➡️ Diferencia marginal. Depende de tu tolerancia al riesgo.","status-yellow"
    st.markdown(f'<div class="{cls_t}" style="margin-top:0.5rem;">{rec}</div>',unsafe_allow_html=True)

# ================================================================
# PANTALLA: FISCALIDAD (MODELO 100 IRPF)
# Delegado a fiscal_export.py
# Deps: df_inm, df_mov, safe_float(), calcular_modelo_100()
# ================================================================
elif menu == "Fiscalidad":
    if _sin_inmuebles:
        st.info("📭 Sin inmuebles registrados. Ve a **Datos de Cartera** para añadir el primero."); st.stop()
    # Cargar perfil desde Supabase si no está en session_state
    if "perfil_datos" not in st.session_state or not st.session_state.perfil_datos:
        st.session_state.perfil_datos = leer_perfil_usuario(st.session_state.get("user_id", ""))
    _perfil_fiscal = st.session_state.perfil_datos or {}
    _tipo_cuenta   = _perfil_fiscal.get("tipo_cuenta", "particular")

    if _tipo_cuenta == "sociedad":
        _nom_soc = _perfil_fiscal.get("nombre_sociedad", "Sociedad Patrimonial")
        st.markdown(f'<div class="nc-brand-header">💰 Fiscalidad — Sociedad Patrimonial</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="nc-brand-sub">IS al 25% · Modelo 200 · {_nom_soc}</div>', unsafe_allow_html=True)
        from fiscal_export import render_seccion_modelo_200
        render_seccion_modelo_200(df_inm, df_mov, safe_float, calcular_modelo_100,
                                   perfil=_perfil_fiscal)
    else:
        st.markdown('<div class="nc-brand-header">💰 Fiscalidad</div>', unsafe_allow_html=True)
        st.markdown('<div class="nc-brand-sub">Escudo fiscal · Modelo 100 IRPF · Deducciones optimizadas</div>', unsafe_allow_html=True)
        from fiscal_export import render_seccion_fiscal
        render_seccion_fiscal(df_inm, df_mov, safe_float, calcular_modelo_100)

# ================================================================
# PANTALLA: MACROFINANZAS
# Simulador amortización, stress test Euríbor, sensibilidad renta
# Deps: df_inm, df_mov, df_hip, calcular_amortizacion(), stress_test_euribor()
# ================================================================
elif menu == "Macrofinanzas":
    from supabase_db import guardar_hipoteca, eliminar_hipoteca
    st.markdown('<div class="nc-brand-header">Macrofinanzas</div>',unsafe_allow_html=True)
    st.markdown('<div class="nc-brand-sub">Simulador hipoteca · Stress test Euríbor · Análisis sensibilidad</div>',unsafe_allow_html=True)

    # ── Recargar hipotecas del usuario ──────────────────────────
    df_hip = _cargar_hipotecas_supabase()
    st.session_state.df_hip = df_hip

    # ── Gestión de hipotecas ─────────────────────────────────────
    with st.expander("➕ Gestionar hipotecas", expanded=df_hip.empty):
        _uid_hip = st.session_state.get("user_id","")
        _nombres_inm = list(df_inm["Nombre"].dropna()) if not df_inm.empty else []

        st.markdown("**Añadir / editar hipoteca**")
        _hcol1, _hcol2, _hcol3 = st.columns(3)
        with _hcol1:
            _h_inm   = st.selectbox("Inmueble", _nombres_inm, key="h_inm") if _nombres_inm else st.text_input("Inmueble", key="h_inm")
            _h_pri   = st.number_input("Principal (€)", min_value=0.0, step=1000.0, key="h_pri")
            _h_tasa  = st.number_input("Tasa inicial (%)", min_value=0.0, max_value=20.0, step=0.01, key="h_tasa")
        with _hcol2:
            _h_plazo = st.number_input("Plazo (años)", min_value=1, max_value=40, value=20, key="h_plazo")
            _h_fecha = st.date_input("Fecha inicio", key="h_fecha")
            _h_var   = st.radio("Tipo", ["Fija","Variable"], horizontal=True, key="h_var")
        with _hcol3:
            _h_idx   = st.selectbox("Índice", ["","Euríbor","IRPH"], key="h_idx") if _h_var=="Variable" else st.empty()
            _h_mrg   = st.number_input("Margen (%)", min_value=0.0, step=0.01, key="h_mrg") if _h_var=="Variable" else 0.0
            _h_saldo = st.number_input("Saldo actual (€)", min_value=0.0, step=1000.0, key="h_saldo")

        if st.button("💾 Guardar hipoteca", type="primary", key="btn_save_hip"):
            _ok = guardar_hipoteca(_uid_hip, {
                "inmueble": _h_inm, "principal": _h_pri, "tasa_inicial": _h_tasa,
                "plazo_años": _h_plazo, "fecha_inicio": str(_h_fecha),
                "es_variable": "S" if _h_var=="Variable" else "N",
                "indice_variable": _h_idx if _h_var=="Variable" else "",
                "margen": _h_mrg, "saldo_actual": _h_saldo
            })
            if _ok:
                st.success("✓ Hipoteca guardada")
                st.session_state.df_hip = _cargar_hipotecas_supabase()
                st.rerun()
            else:
                st.error("Error al guardar")

        if not df_hip.empty:
            st.markdown("**Hipotecas registradas**")
            st.dataframe(df_hip[["Inmueble","Principal","Tasa_Inicial","Plazo_Años","Saldo_Actual"]].style.format({
                "Principal": "{:,.0f} €", "Tasa_Inicial": "{:.2f}%",
                "Saldo_Actual": "{:,.0f} €"
            }), use_container_width=True, hide_index=True)
            _del_opts = list(df_hip["Inmueble"])
            _del_sel  = st.selectbox("Eliminar hipoteca:", _del_opts, key="del_hip_sel")
            if st.button("🗑️ Eliminar", type="secondary", key="btn_del_hip"):
                _fila_del = df_hip[df_hip["Inmueble"]==_del_sel]
                if not _fila_del.empty and "id" in _fila_del.columns:
                    eliminar_hipoteca(_uid_hip, int(_fila_del.iloc[0]["id"]))
                    st.session_state.df_hip = _cargar_hipotecas_supabase()
                    st.rerun()

    df_hip = st.session_state.df_hip
    tab1,tab2,tab3=st.tabs(["📊 Simulador Amortización","⚠️ Stress Test Euríbor","📈 Sensibilidad Rentabilidad"])

    with tab1:
        st.markdown('<div class="nc-section-title">Simulador de Amortización</div>',unsafe_allow_html=True)
        st.caption("Compara modalidades: cuota fija (francés) vs capital fijo (alemán)")
        inmuebles_con_hip=df_hip[df_hip["Principal"]>0]["Inmueble"].tolist()
        if not inmuebles_con_hip:
            st.warning("⚠️ No hay hipotecas cargadas.")
        else:
            sel_hip=st.selectbox("Selecciona inmueble:",inmuebles_con_hip,key="hip_sel")
            hip_row=df_hip[df_hip["Inmueble"]==sel_hip].iloc[0]
            col1,col2,col3,col4=st.columns(4)
            with col1: principal=st.number_input("Principal (€)",value=int(hip_row["Principal"]),min_value=0)
            with col2: tasa=st.number_input("Tasa (%)",value=float(hip_row["Tasa_Inicial"]),min_value=0.0,max_value=10.0,step=0.1)
            with col3: plazo=st.number_input("Plazo (años)",value=int(hip_row["Plazo_Años"]) if int(hip_row["Plazo_Años"])>0 else 20,min_value=1,max_value=50)
            with col4: modo=st.selectbox("Modalidad",["Cuota Fija","Capital Fijo"],key="modo_amort")
            modo_code="cuota_fija" if modo=="Cuota Fija" else "capital_fijo"
            resultado=calcular_amortizacion(principal,tasa,plazo,modo_code)
            k1,k2,k3=st.columns(3); cuota_val=resultado["cuota_mensual"]
            k1.metric("Cuota Mensual",f"{cuota_val:,.2f} €" if isinstance(cuota_val,float) else "Variable")
            k2.metric("Total Intereses",f"{resultado['total_intereses']:,.0f} €")
            k3.metric("Total Pagado",f"{resultado['total_pagado']:,.0f} €")
            tabla=resultado["tabla"].copy(); tabla["Año"]=tabla["Mes"]//12
            fig_amort=go.Figure()
            fig_amort.add_trace(go.Scatter(x=tabla["Año"],y=tabla["Pendiente"],mode="lines",name="Capital Pendiente",fill="tozeroy",line=dict(color=ACCENT)))
            fig_amort.add_trace(go.Scatter(x=tabla["Año"],y=tabla["Intereses"].cumsum(),mode="lines",name="Intereses Acumulados",line=dict(color=RED,dash="dash")))
            fig_amort.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=10,b=10),height=300,font=dict(family="DM Sans",size=12),hovermode="x unified")
            st.plotly_chart(fig_amort,use_container_width=True)
            col_t1,col_t2=st.columns(2)
            with col_t1:
                st.caption("Primeros 12 meses")
                st.dataframe(tabla.head(12)[["Mes","Cuota","Capital","Intereses","Pendiente"]].style.format({"Cuota":"{:,.2f} €","Capital":"{:,.2f} €","Intereses":"{:,.2f} €","Pendiente":"{:,.2f} €"}),use_container_width=True,hide_index=True)
            with col_t2:
                st.caption("Últimos 12 meses")
                st.dataframe(tabla.tail(12)[["Mes","Cuota","Capital","Intereses","Pendiente"]].style.format({"Cuota":"{:,.2f} €","Capital":"{:,.2f} €","Intereses":"{:,.2f} €","Pendiente":"{:,.2f} €"}),use_container_width=True,hide_index=True)

    with tab2:
        st.markdown('<div class="nc-section-title">Stress Test Euríbor</div>',unsafe_allow_html=True)
        st.caption("¿Cuánto sube tu cuota si el Euríbor sube 1%, 2% o 3%?")
        hips_variable=df_hip[(df_hip["Es_Variable"]=="S")&(df_hip["Principal"]>0)]
        if hips_variable.empty:
            st.warning("⚠️ No hay hipotecas variables.")
        else:
            sel_var=st.selectbox("Hipoteca variable:",hips_variable["Inmueble"].tolist(),key="hip_var")
            hip_var=hips_variable[hips_variable["Inmueble"]==sel_var].iloc[0]
            col_s1,col_s2,col_s3,col_s4=st.columns(4)
            with col_s1: saldo=st.number_input("Saldo Actual (€)",value=int(hip_var["Saldo_Actual"]),min_value=0)
            with col_s2: margen=st.number_input("Margen (%)",value=float(hip_var["Margen"]),min_value=0.0,max_value=3.0,step=0.05)
            with col_s3: euribor_ahora=st.number_input("Euríbor Actual (%)",value=3.5,min_value=0.0,max_value=10.0,step=0.1)
            with col_s4: plazo_rest=st.number_input("Años Restantes",value=20,min_value=1,max_value=40)
            stress_results=stress_test_euribor(saldo,margen,euribor_ahora,plazo_rest)
            tabla_stress=[{"Escenario":k,"Tasa Total":f"{v['tasa_total']:.2f}%","Cuota Mensual":f"{v['cuota_mensual']:,.2f} €","Cuota Anual":f"{v['cuota_anual']:,.2f} €"} for k,v in stress_results.items()]
            st.dataframe(pd.DataFrame(tabla_stress),use_container_width=True,hide_index=True)
            fig_stress=go.Figure(go.Bar(x=list(stress_results.keys()),y=[v["cuota_mensual"] for v in stress_results.values()],marker_color=[RED if k!="Euríbor actual" else ACCENT for k in stress_results.keys()],text=[f"{v['cuota_mensual']:,.0f} €" for v in stress_results.values()],textposition="outside"))
            fig_stress.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=10,b=10),height=300,font=dict(family="DM Sans",size=12),showlegend=False)
            st.plotly_chart(fig_stress,use_container_width=True)
            cuota_base=stress_results["Euríbor actual"]["cuota_mensual"]
            cuota_peligro=stress_results["Euríbor +2%"]["cuota_mensual"]; impacto=cuota_peligro-cuota_base
            if impacto>500: cls_r,msg_r="status-red",f"🔴 RIESGO ALTO: Subida +2% = +{impacto:,.0f} €/mes. Considera pasar a tipo fijo."
            elif impacto>200: cls_r,msg_r="status-yellow",f"🟡 RIESGO MEDIO: Subida +2% = +{impacto:,.0f} €/mes. Monitorear."
            else: cls_r,msg_r="status-green",f"🟢 RIESGO BAJO: Subida +2% = +{impacto:,.0f} €/mes. Asumible."
            st.markdown(f'<div class="{cls_r}">{msg_r}</div>',unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="nc-section-title">Análisis de Sensibilidad</div>',unsafe_allow_html=True)
        st.caption("Cómo cambia la rentabilidad si subes o bajas la renta")
        sel_sens=st.selectbox("Inmueble:",df_inm["Nombre"].tolist(),key="sens_inmueble")
        row_sens=df_inm[df_inm["Nombre"]==sel_sens].iloc[0]
        gastos_esp=df_mov[(df_mov["Apartamento"]==sel_sens)&(df_mov["Tipo"]=="Gasto")]["Importe"].sum()
        comunidad_esp=float(row_sens.get("Comunidad",0))*12
        gastos_anuales_sens=gastos_esp+comunidad_esp
        col_var1,col_var2=st.columns(2)
        with col_var1: renta_sens=st.number_input("Renta Mensual (€)",value=float(row_sens["Renta"]),min_value=0.0)
        with col_var2: variaciones=st.multiselect("Variaciones a analizar (%)",options=[-15,-10,-5,0,5,10,15],default=[-10,-5,0,5,10])
        if variaciones:
            tabla_sens=analisis_sensibilidad_renta(renta_sens,gastos_anuales_sens,float(row_sens["Valor_Construccion"]),variaciones)
            st.dataframe(tabla_sens,use_container_width=True,hide_index=True)
            datos_graf=[{"var":v,"rent":(renta_sens*(1+v/100)*12-gastos_anuales_sens)/float(row_sens["Valor_Construccion"])*100 if float(row_sens["Valor_Construccion"])>0 else 0} for v in sorted(variaciones)]
            df_graf=pd.DataFrame(datos_graf)
            fig_sens=go.Figure(go.Scatter(x=df_graf["var"],y=df_graf["rent"],mode="lines+markers",line=dict(color=ACCENT,width=3),marker=dict(size=10),fill="tozeroy"))
            fig_sens.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=10,b=10),height=300,xaxis_title="Variación Renta (%)",yaxis_title="Rentabilidad Neta (%)",font=dict(family="DM Sans",size=12))
            st.plotly_chart(fig_sens,use_container_width=True)

# ================================================================
# PANTALLA: ASESOR PATRIMONIAL IA (B2B2C)
# Deps: df_inm, asesoramiento_ia.py, nolasco_styles.py
# ================================================================
elif menu == "Asesor Patrimonial IA":
    st.markdown(f"""
    <div style='background:{SIDEBAR_BG};padding:20px 24px 16px;border-radius:12px;margin-bottom:24px;border-left:4px solid {ACCENT};'>
        <h2 style='color:white;margin:0;font-size:22px'>🧠 Asesor Patrimonial IA</h2>
        <p style='color:#8899AA;margin:6px 0 0;font-size:14px'>Analizamos tu cartera y te conectamos con inmobiliarias cuando lo necesitas. Tú controlas tus datos en todo momento.</p>
    </div>""",unsafe_allow_html=True)
    if df_inm.empty:
        st.info("📭 Añade inmuebles en 'Datos de la Cartera' para usar el Asesor.")
    else:
        def _safe_float(v):
            try: return float(str(v).replace(",","").replace("€","").strip())
            except: return 0.0
        renta_total   = df_inm["Renta"].apply(_safe_float).sum()
        mercado_total = df_inm["Renta_Mercado"].apply(_safe_float).sum()
        rent_pct      = round(renta_total/mercado_total*100,1) if mercado_total>0 else 0
        contexto_ia = {
            "num_inmuebles":       len(df_inm),
            "rentabilidad_media":  rent_pct,
            "rentabilidad_mercado":100,
            "perdida_mensual":     round(mercado_total-renta_total,0),
            "inmuebles": [{"nombre":row.get("Nombre",""),"renta":_safe_float(row.get("Renta",0)),"mercado":_safe_float(row.get("Renta_Mercado",0)),"vencimiento":str(row.get("Fecha_Vencimiento_Contrato",""))} for _,row in df_inm.iterrows()],
            "email": st.session_state.user_email or "",
        }
        st.markdown("<hr style='border:0;border-top:1px solid #D0DFF0;margin:1.5rem 0;'>",unsafe_allow_html=True)
        datos_propietario={"nombre":st.session_state.get("user_nombre",""),"email":st.session_state.get("user_email",st.session_state.user_email or ""),"telefono":st.session_state.get("user_telefono",""),}
        render_asesor_ia(user_id=st.session_state.user_id,df_inmuebles=df_inm,datos_propietario=datos_propietario)
        # ── SABIO PATRIMONIAL — Asesor ──────────────────────────
        render_sabio("asesor", contexto_ia)

# ================================================================
# PANTALLA: PRIVACIDAD Y CONSENTIMIENTOS (RGPD)
# Deps: asesoramiento_ia.render_privacidad()
# ================================================================
elif menu == "Privacidad y Consentimientos":
    st.markdown(f"""
    <div style='background:{SIDEBAR_BG};padding:20px 24px 16px;border-radius:12px;margin-bottom:24px;border-left:4px solid #0F6E56;'>
        <h2 style='color:white;margin:0;font-size:22px'>🔒 Privacidad y Consentimientos</h2>
        <p style='color:#8899AA;margin:6px 0 0;font-size:14px'>Gestiona quién tiene acceso a tus datos y revoca permisos en cualquier momento.</p>
    </div>""",unsafe_allow_html=True)
    render_privacidad(user_id=st.session_state.user_id)

# ================================================================
# PANTALLA: COMPARTIR CON ASESOR
# Deps: generar_codigo_acceso(), obtener_codigo_activo(), revocar_codigo_acceso()
# ================================================================
elif menu == "Compartir con Asesor":
    st.markdown('<div class="nc-brand-header">🔗 Compartir con Asesor</div>',unsafe_allow_html=True)
    st.markdown('<div class="nc-brand-sub">Permite a tu asesor fiscal o inmobiliaria ver tu patrimonio</div>',unsafe_allow_html=True)
    user_id=st.session_state.user_id; codigo_activo=obtener_codigo_activo(user_id)
    st.markdown("### ¿Cómo funciona?")
    st.info("1. Genera un código de 6 dígitos\n2. Compártelo con tu asesor por WhatsApp o email\n3. Ellos acceden a tu Torre de Control y Fichas (solo lectura)\n4. Puedes revocar el acceso en cualquier momento")
    st.markdown("---")
    if codigo_activo:
        st.markdown("### ✅ Tu código de acceso activo")
        st.markdown(f"""<div style='background:#0F2744;border:2px solid #185FA5;border-radius:12px;padding:2rem;text-align:center;margin:1rem 0;'>
            <div style='font-size:0.85rem;color:#8899AA;margin-bottom:0.5rem;'>Comparte este código con tu asesor</div>
            <div style='font-size:3rem;font-weight:700;color:#60B4FF;letter-spacing:0.5rem;font-family:monospace;'>{codigo_activo}</div>
        </div>""",unsafe_allow_html=True)
        col1,col2=st.columns(2)
        with col1:
            if st.button("🔄 Regenerar código",use_container_width=True):
                result=generar_codigo_acceso(user_id)
                if result["success"]: st.success(f"Nuevo código: {result['codigo']}"); st.rerun()
                else: st.error("Error al generar código")
        with col2:
            if st.button("❌ Revocar acceso",use_container_width=True,type="secondary"):
                if revocar_codigo_acceso(user_id): st.success("Acceso revocado."); st.rerun()
                else: st.error("Error al revocar acceso")
    else:
        st.warning("No tienes ningún código de acceso activo. Tu patrimonio no es visible para ningún asesor.")
        if st.button("🔗 Generar código de acceso",use_container_width=True,type="primary"):
            result=generar_codigo_acceso(user_id)
            if result["success"]: st.success(f"✅ Código generado: **{result['codigo']}**"); st.rerun()
            else: st.error(f"Error: {result.get('error','desconocido')}")
    st.markdown("---")
    st.markdown("""<div style='font-size:0.8rem;color:#8899AA;'>🔒 <strong>Privacidad:</strong> Solo lectura — Torre de Control y Fichas. Sin acceso al Diario Contable ni datos fiscales sensibles. Revocar en cualquier momento.</div>""",unsafe_allow_html=True)

# ================================================================
# PANTALLA: LEGAL — GENERADOR DE CONTRATOS + CALCULADORAS
# Deps: df_inm, generar_contrato_*(), safe_float(), REPORTLAB_OK
# ================================================================
elif menu == "Legal":
    st.markdown('<div class="nc-brand-header">⚖️ HERRAMIENTAS LEGALES</div>',unsafe_allow_html=True)
    st.markdown("""<style>
    .legal-card{background:linear-gradient(135deg,#1a3a5c 0%,#2d5a8c 100%);border:2px solid #c9a85c;border-radius:12px;padding:2rem;margin-bottom:2rem;}
    .legal-title{color:#c9a85c;font-size:1.3rem;font-weight:700;margin-bottom:0.5rem;}
    .legal-subtitle{color:#e8f2ff;font-size:0.95rem;margin-bottom:1.5rem;}
    .legal-section{background:#f8fafb;border-left:4px solid #1a3a5c;padding:1.2rem;border-radius:8px;margin:1.5rem 0;}
    .disclaimer{background:#fff3cd;border:1px solid #ffc107;border-left:4px solid #ff9800;border-radius:8px;padding:1rem;margin-top:2rem;color:#856404;font-size:0.85rem;line-height:1.5;}
    </style>""",unsafe_allow_html=True)

    st.markdown("""<div class="legal-card"><div class="legal-title">📋 GENERADOR DE CONTRATOS DE ARRENDAMIENTO</div>
    <div class="legal-subtitle">Genera contratos conformes a LAU 29/1994 con tus datos precargados</div></div>""",unsafe_allow_html=True)

    if "tipo_contrato_seleccionado" not in st.session_state:
        st.session_state.tipo_contrato_seleccionado=None

    col1,col2,col3=st.columns(3)
    with col1:
        if st.button("📜  LARGA DURACIÓN\nVivienda habitual · LAU Art. 9",key="btn_larga",use_container_width=True,type="primary" if st.session_state.tipo_contrato_seleccionado=="larga" else "secondary"):
            st.session_state.tipo_contrato_seleccionado="larga"; st.rerun()
    with col2:
        if st.button("⏰  TEMPORADA\nTurístico o estudios · ≤12 meses",key="btn_temp",use_container_width=True,type="primary" if st.session_state.tipo_contrato_seleccionado=="temporada" else "secondary"):
            st.session_state.tipo_contrato_seleccionado="temporada"; st.rerun()
    with col3:
        if st.button("🛏️  HABITACIÓN\nSubarrienda habitación · LAU parcial",key="btn_hab",use_container_width=True,type="primary" if st.session_state.tipo_contrato_seleccionado=="habitacion" else "secondary"):
            st.session_state.tipo_contrato_seleccionado="habitacion"; st.rerun()

    if st.session_state.tipo_contrato_seleccionado:
        tipo=st.session_state.tipo_contrato_seleccionado
        st.markdown("<br>",unsafe_allow_html=True)
        inmueble_seleccionado=st.selectbox("Selecciona el inmueble",options=df_inm["Nombre"].tolist(),key="inmueble_legal")
        inm_data=df_inm[df_inm["Nombre"]==inmueble_seleccionado].iloc[0]
        st.caption(f"📍 Ref. Catastral: {inm_data.get('Ref_Catastral','N/A')} | {inm_data.get('M2_Construidos',0)}m²")
        col_dur1,col_dur2=st.columns(2)
        with col_dur1:
            if tipo=="larga":
                duracion_anos=st.selectbox("Años",options=[1,2,3,4,5],index=2,key="dur_anos"); duracion_meses=0
            else:
                duracion_meses=st.selectbox("Meses",options=list(range(1,13)),index=5,key="dur_meses"); duracion_anos=0
        renta=inm_data.get("Renta",0); st.write(f"**Renta mensual:** {renta:,.0f}€")
        tipo_fianza=st.radio("Fianza",options=["1 mes","2 meses","Sin fianza"],index=1 if tipo=="larga" else 0,horizontal=True,key="fianza_tipo")
        importe_fianza=0 if "Sin" in tipo_fianza else (renta if "1 mes" in tipo_fianza else renta*2)
        st.caption(f"💵 Importe fianza: {importe_fianza:,.0f}€")
        col_sum1,col_sum2=st.columns(2)
        with col_sum1:
            incluye_luz=st.checkbox("⚡ Incluye electricidad",key="sum_luz"); incluye_gas=st.checkbox("🔥 Incluye gas",key="sum_gas")
        with col_sum2:
            incluye_internet=st.checkbox("📡 Incluye internet",key="sum_int"); incluye_agua=st.checkbox("💧 Incluye agua",key="sum_agua")
        ipc_anual=st.checkbox("✓ Actualización anual según IPC",value=True,key="ipc")
        mascotas=st.radio("🐕 Mascotas",options=["Permitidas","No permitidas","A consultar"],index=1,horizontal=True,key="mascotas")

        if st.button("⚖️ GENERAR CONTRATO",type="primary",use_container_width=True,key="generar_contrato"):
            contrato_data={"tipo":tipo,"inmueble":inmueble_seleccionado,"direccion":"Calle ejemplo, 1","ref_catastral":inm_data.get("Ref_Catastral","N/A"),"m2":inm_data.get("M2_Construidos",0),"renta":renta,"duracion_anos":duracion_anos,"duracion_meses":duracion_meses,"fianza_meses":0 if "Sin" in tipo_fianza else (1 if "1 mes" in tipo_fianza else 2),"importe_fianza":importe_fianza,"incluye_luz":incluye_luz,"incluye_gas":incluye_gas,"incluye_internet":incluye_internet,"incluye_agua":incluye_agua,"ipc":ipc_anual,"mascotas":mascotas}
            if tipo=="larga": contrato_texto=generar_contrato_larga_duracion(contrato_data)
            elif tipo=="temporada": contrato_texto=generar_contrato_temporada(contrato_data)
            else: contrato_texto=generar_contrato_habitacion(contrato_data)
            st.success("✅ Contrato generado correctamente")
            with st.expander("📄 PREVIEW DEL CONTRATO",expanded=True): st.text(contrato_texto)
            st.download_button("📥 Descargar TXT",data=contrato_texto,file_name=f"contrato_{tipo}_{inmueble_seleccionado.replace(' ','_')}.txt",mime="text/plain")

    st.markdown("""<div class="disclaimer"><strong>⚠️ AVISO LEGAL</strong><br>Contratos orientativos basados en LAU 29/1994. <strong>NO sustituye asesoramiento legal profesional.</strong> Consulte con un abogado antes de firmar.</div>""",unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="nc-brand-header">🧮 Calculadoras de Renta</div>',unsafe_allow_html=True)
    st.markdown('<div class="nc-brand-sub">Herramientas de negociación y actualización · Basadas en LAU y datos reales</div>',unsafe_allow_html=True)
    calc1,calc2=st.tabs(["📉 Renegociación (inquilino pide bajar)","📈 Actualización al alza"])

    with calc1:
        st.markdown('<div class="nc-section-title">¿Cuánto puedo bajar la renta sin perder dinero?</div>',unsafe_allow_html=True)
        inm_reneg=st.selectbox("Inmueble",df_inm["Nombre"].tolist(),key="reneg_inm")
        f_reneg=df_inm[df_inm["Nombre"]==inm_reneg].iloc[0]; renta_actual_reneg=safe_float(f_reneg.get("Renta",0))
        st.markdown(f"**Renta actual:** {renta_actual_reneg:,.2f} €/mes")
        c1a,c1b,c1c=st.columns(3)
        with c1a: renta_pedida=st.number_input("Renta que pide el inquilino (€/mes)",min_value=0.0,max_value=float(renta_actual_reneg),value=float(max(0,renta_actual_reneg-60)),step=10.0,format="%.2f",key="reneg_pedida")
        with c1b: meses_vacio=st.slider("Meses estimados que estaría vacío",min_value=0,max_value=12,value=2,key="reneg_meses")
        with c1c: meses_comision=st.slider("Meses de comisión inmobiliaria",min_value=0,max_value=3,value=1,key="reneg_comision")
        if st.button("🧮 Calcular",type="primary",key="btn_reneg"):
            bajada_mensual=renta_actual_reneg-renta_pedida
            coste_comision=renta_actual_reneg*meses_comision
            coste_total_si_se_va=renta_actual_reneg*meses_vacio+coste_comision
            cobro_nuevo_12m=renta_actual_reneg*(12-meses_vacio)-coste_comision
            renta_min_equilibrio=cobro_nuevo_12m/12
            es_aceptable=renta_pedida>=renta_min_equilibrio
            diferencia_12m=renta_pedida*12-cobro_nuevo_12m
            r1,r2,r3=st.columns(3)
            r1.markdown(f'<div class="nc-kpi"><div class="nc-kpi__label">Bajada solicitada</div><div class="nc-kpi__value" style="color:{RED};">−{bajada_mensual:,.0f} €/mes</div></div>',unsafe_allow_html=True)
            r2.markdown(f'<div class="nc-kpi"><div class="nc-kpi__label">Coste si se va</div><div class="nc-kpi__value" style="color:{RED};">−{coste_total_si_se_va:,.0f} €</div></div>',unsafe_allow_html=True)
            r3.markdown(f'<div class="nc-kpi is-highlight"><div class="nc-kpi__label">Renta mínima aceptable</div><div class="nc-kpi__value">{renta_min_equilibrio:,.0f} €/mes</div></div>',unsafe_allow_html=True)
            if bajada_mensual<=0: cls_rec,rec="nc-status nc-status--green","✅ El inquilino no pide bajada. No hay nada que negociar."
            elif es_aceptable: cls_rec,rec="nc-status nc-status--green",f"✅ ACEPTA — Renta pedida ({renta_pedida:,.0f} €) sobre el mínimo ({renta_min_equilibrio:,.0f} €). En 12 meses ganas {diferencia_12m:,.0f} € más."
            else: cls_rec,rec="nc-status nc-status--red",f"🔴 NO ACEPTES — Contraoferta recomendada: {renta_min_equilibrio:,.0f} €/mes."
            st.markdown(f'<div class="{cls_rec}">{rec}</div>',unsafe_allow_html=True)

    with calc2:
        st.markdown('<div class="nc-section-title">¿Cuánto puedo subir la renta?</div>',unsafe_allow_html=True)
        inm_sube=st.selectbox("Inmueble",df_inm["Nombre"].tolist(),key="sube_inm")
        f_sube=df_inm[df_inm["Nombre"]==inm_sube].iloc[0]
        renta_actual_sube=safe_float(f_sube.get("Renta",0))
        tipo_contrato_sube=str(f_sube.get("Tipo_Arrendamiento","Larga Duración"))
        zona_tens_sube=str(f_sube.get("Zona_Tensionada","N"))=="S"
        inquilino_sube=str(f_sube.get("Inquilino","El inquilino"))
        IRAV_ACTUAL=2.47; TOPE_RDL=2.0
        st.markdown(f"""<div class="nc-status nc-status--amber"><strong>📊 Índices oficiales 2026 (INE)</strong><br>
        IRAV enero: 2,14% · IRAV febrero: 2,16% · <strong>IRAV marzo (último): 2,47%</strong><br>
        ⚠️ Tope RDL 8/2026: <strong>máximo 2%</strong> hasta dic 2027</div>""",unsafe_allow_html=True)
        s1,s2=st.columns(2)
        with s1:
            ipc_aplicar=st.number_input("IPC a aplicar (%)",min_value=0.0,max_value=20.0,value=2.47,step=0.1,format="%.1f",key="sube_ipc")
            fecha_ultima_actualizacion=st.date_input("Fecha última actualización",key="sube_fecha")
        with s2:
            if tipo_contrato_sube=="Larga Duración":
                try:
                    fi2=pd.to_datetime(str(f_sube.get("Fecha_Inicio_Contrato","2022-01-01"))).date()
                    post_ley2=fi2>=date(2023,5,26)
                except: post_ley2=False
                if post_ley2: st.success(f"✅ Contrato post Ley Vivienda → IRAV {IRAV_ACTUAL}% (tope 2%)")
                else: st.info(f"📋 Contrato anterior → IPC topado al {TOPE_RDL}% (RDL 8/2026)")
            elif tipo_contrato_sube=="Temporada": st.info("📋 Temporada: renta libre al vencimiento. Sin tope IRAV.")
            else: st.info("📋 Habitaciones: renta libre. Sin tope IRAV.")
            if zona_tens_sube: st.warning("⚠️ Zona tensionada: no puedes superar la renta del contrato anterior.")

        if st.button("🧮 Calcular subida",type="primary",key="btn_sube"):
            try:
                fi=pd.to_datetime(str(f_sube.get("Fecha_Inicio_Contrato","2022-01-01"))).date()
                contrato_post_ley=fi>=date(2023,5,26)
            except: contrato_post_ley=False
            if tipo_contrato_sube=="Larga Duración":
                indice_aplicado=min(IRAV_ACTUAL if contrato_post_ley else ipc_aplicar,TOPE_RDL)
                nota_legal=f"{'IRAV' if contrato_post_ley else 'IPC'} topado al {TOPE_RDL}% por RDL 8/2026"
            else:
                indice_aplicado=ipc_aplicar; nota_legal="Contrato no sujeto a topes IRAV."
            subida_euros=renta_actual_sube*(indice_aplicado/100)
            nueva_renta=renta_actual_sube+subida_euros; subida_anual=subida_euros*12
            st.markdown(f'<div class="nc-status nc-status--amber">📋 {nota_legal}</div>',unsafe_allow_html=True)
            sk1,sk2,sk3=st.columns(3)
            sk1.markdown(f'<div class="nc-kpi"><div class="nc-kpi__label">Subida mensual</div><div class="nc-kpi__value" style="color:{GREEN};">+{subida_euros:,.2f} €</div></div>',unsafe_allow_html=True)
            sk2.markdown(f'<div class="nc-kpi"><div class="nc-kpi__label">Nueva renta</div><div class="nc-kpi__value">{nueva_renta:,.2f} €</div></div>',unsafe_allow_html=True)
            sk3.markdown(f'<div class="nc-kpi is-highlight"><div class="nc-kpi__label">Extra anual</div><div class="nc-kpi__value">+{subida_anual:,.0f} €</div></div>',unsafe_allow_html=True)
            fecha_hoy=datetime.now().strftime("%d de %B de %Y")
            carta=f"""Granada, {fecha_hoy}\n\nEstimado/a {inquilino_sube}:\n\nLe comunicamos la actualización anual de la renta conforme al artículo 18 de la LAU 29/1994.\n\nRenta actual: {renta_actual_sube:,.2f} €/mes\nÍndice aplicado: {indice_aplicado}%\nIncremento mensual: {subida_euros:,.2f} €\nNueva renta mensual: {nueva_renta:,.2f} €\n\nEfectiva a partir del próximo periodo de pago.\n\nAtentamente,\nPedro Nolasco — Propietario"""
            st.text_area("Carta lista para enviar:",value=carta,height=300,key="carta_notif")
            st.download_button("📥 Descargar carta (.txt)",data=carta,file_name=f"notificacion_{inm_sube.replace(' ','_')}.txt",mime="text/plain")

    st.markdown("""<div class="disclaimer"><strong>⚠️ AVISO LEGAL</strong><br>Calculadoras orientativas. <strong>Consulte siempre con un abogado especializado en arrendamientos antes de tomar decisiones.</strong></div>""",unsafe_allow_html=True)

# ================================================================
# PANTALLA: DATOS DE LA CARTERA
# Gestión de inmuebles, backups, importación Excel
# Deps: df_inm, guardar_inmuebles(), upsert_inmueble()
# ================================================================
elif menu == "Datos de la Cartera":
    st.markdown('<div class="nc-brand-header">Datos de la Cartera</div>',unsafe_allow_html=True)

    # ── Mostrar errores persistentes de guardado (sobreviven al rerun) ──
    if "_errores_guardar_inm" in st.session_state:
        ok = st.session_state.get("_ok_guardar_inm", 0)
        errores = st.session_state["_errores_guardar_inm"]
        st.error(f"⚠️ {len(errores)} inmueble(s) fallaron al guardar en Supabase ({ok} guardados correctamente). Copia estos errores:")
        for e in errores:
            st.code(e, language=None)
        if st.button("🗑️ Limpiar errores", key="limpiar_err_inm"):
            st.session_state.pop("_errores_guardar_inm", None)
            st.rerun()
    st.markdown('<div class="nc-brand-sub">Gestión de inmuebles · Backups · Configuración</div>',unsafe_allow_html=True)

    if "modo_cartera" not in st.session_state: st.session_state.modo_cartera="lista"
    if "inmueble_editando" not in st.session_state: st.session_state.inmueble_editando=None

    col_btn1,col_btn2,col_btn3,col_btn4=st.columns(4)
    with col_btn1:
        if st.button("📋 Ver Lista",key="btn_lista",use_container_width=True): st.session_state.modo_cartera="lista"; st.rerun()
    with col_btn2:
        if st.button("➕ Añadir Inmueble",key="btn_nuevo",use_container_width=True): st.session_state.modo_cartera="nuevo"; st.session_state.inmueble_editando=None; st.rerun()
    with col_btn3:
        if st.button("📊 Ver Tabla Completa",key="btn_tabla",use_container_width=True): st.session_state.modo_cartera="tabla"; st.rerun()
    with col_btn4:
        if st.button("💾 Backups",key="btn_backup",use_container_width=True): st.session_state.modo_cartera="backup"; st.rerun()
    st.markdown("---")

    # ── LISTA ──────────────────────────────────────────────────
    if st.session_state.modo_cartera=="lista":
        st.markdown(f'<div class="nc-section-title">🏠 Mis Inmuebles ({len(df_inm)})</div>',unsafe_allow_html=True)
        for idx,row in df_inm.iterrows():
            col_info,col_btn=st.columns([4,1])
            with col_info:
                st.markdown(f"""<div style="background:{CARD_BG};border:1px solid {BORDER};border-radius:10px;padding:1rem;margin-bottom:0.8rem;">
                    <div style="font-size:1.1rem;font-weight:600;color:{TEXT_PRI};margin-bottom:4px;">🏠 {row['Nombre']}</div>
                    <div style="font-size:0.85rem;color:{TEXT_SEC};">👤 {row.get('Inquilino','Sin inquilino')} · 📍 CP {row.get('CP','N/A')}</div>
                    <div style="margin-top:8px;font-size:0.82rem;">
                        <span style="background:#EDF7F1;color:#3B6D11;padding:3px 8px;border-radius:4px;margin-right:4px;">💰 {row['Renta']:,.0f} €/mes</span>
                        <span style="background:#F0F6FF;color:{ACCENT};padding:3px 8px;border-radius:4px;margin-right:4px;">📐 {row.get('M2_Construidos','N/A')} m²</span>
                        <span style="background:#FFF9E6;color:#854F0B;padding:3px 8px;border-radius:4px;">🛏️ {row.get('Habitaciones','N/A')} hab</span>
                    </div>
                </div>""",unsafe_allow_html=True)
            with col_btn:
                if st.button("✏️ Editar",key=f"edit_{idx}",use_container_width=True):
                    st.session_state.modo_cartera="editar"; st.session_state.inmueble_editando=idx; st.rerun()
                if st.button("🗑️",key=f"del_{idx}",use_container_width=True):
                    if len(st.session_state.df_inm_persistent)>1:
                        nombre_borrar = row['Nombre']
                        ok_delete = eliminar_inmueble(nombre_borrar, user_id=st.session_state.user_id)
                        if ok_delete:
                            df_nuevo=st.session_state.df_inm_persistent.drop(idx).reset_index(drop=True)
                            st.session_state.df_inm_persistent=df_nuevo
                            st.success(f"✅ '{nombre_borrar}' eliminado de Supabase"); st.rerun()
                        else:
                            st.error(f"❌ No se pudo eliminar '{nombre_borrar}' de Supabase")
                    else: st.error("No puedes eliminar el último inmueble")

    # ── FORMULARIO EDITAR / NUEVO ──────────────────────────────
    elif st.session_state.modo_cartera in ["editar","nuevo"]:
        es_nuevo=st.session_state.modo_cartera=="nuevo"
        titulo="➕ Añadir Inmueble Nuevo" if es_nuevo else f"✏️ Editar: {df_inm.iloc[st.session_state.inmueble_editando]['Nombre']}"
        st.markdown(f'<div class="nc-section-title">{titulo}</div>',unsafe_allow_html=True)
        datos={col: DEFAULTS_FISCAL.get(col,"") for col in COLS_INM} if es_nuevo else df_inm.iloc[st.session_state.inmueble_editando].to_dict()

        with st.form("form_inmueble"):
            st.markdown("### 📋 Datos Básicos")
            col1,col2=st.columns(2)
            with col1:
                nombre=st.text_input("Nombre del Inmueble *",value=datos.get("Nombre",""))
                inquilino=st.text_input("Inquilino",value=datos.get("Inquilino",""))
                renta=st.number_input("Renta Mensual (€) *",value=safe_float(datos.get("Renta"),0.0),min_value=0.0,step=50.0)
            with col2:
                renta_mercado=st.number_input("Renta de Mercado (€)",value=safe_float(datos.get("Renta_Mercado"),0.0),min_value=0.0,step=50.0)
                comunidad=st.number_input("Comunidad Mensual (€)",value=safe_float(datos.get("Comunidad"),0.0),min_value=0.0,step=10.0)
                valor_construccion=st.number_input("Valor Construcción (€) *",value=safe_float(datos.get("Valor_Construccion"),0.0),min_value=0.0,step=1000.0)
            st.markdown("### 🏠 Características")
            col3,col4,col5=st.columns(3)
            with col3:
                _m2_val=max(10.0,safe_float(datos.get("M2_Construidos"),80.0))
                m2=st.number_input("M² Construidos *",value=_m2_val,min_value=0.0,step=5.0)
                habitaciones=st.number_input("Habitaciones *",value=max(1,safe_int(datos.get("Habitaciones"),2)),min_value=1,max_value=10)
                planta=st.number_input("Planta",value=safe_int(datos.get("Planta"),1),min_value=0,max_value=20)
            with col4:
                cp=st.text_input("Código Postal *",value=str(datos.get("CP","18005")),max_chars=5)
                tipo=st.selectbox("Tipo",["Piso","Casa","Estudio","Local"],index=safe_index(["Piso","Casa","Estudio","Local"],datos.get("Tipo"),0))
                estado=st.selectbox("Estado",["Reformado","Bueno","Regular"],index=safe_index(["Reformado","Bueno","Regular"],datos.get("Estado"),1))
            with col5:
                mobiliario=st.selectbox("Mobiliario",["S","N"],index=0 if datos.get("Mobiliario")=="S" else 1)
                parking=st.selectbox("Parking",["S","N"],index=0 if datos.get("Parking")=="S" else 1)
                año_construccion=st.number_input("Año Construcción",value=max(1900,safe_int(datos.get("Año_Construccion"),2000)),min_value=1900,max_value=2030)
            st.markdown("### 📝 Información Adicional")
            col6,col7=st.columns(2)
            with col6:
                ref_catastral=st.text_input("Ref. Catastral",value=datos.get("Ref_Catastral",""))
                titular=st.text_input("Titular",value=datos.get("Titular",""))
                año_reforma=st.number_input("Año Última Reforma",value=max(1900,safe_int(datos.get("Año_Reforma"),2020)),min_value=1900,max_value=2030)
            with col7:
                tipo_arrendamiento=st.selectbox("Tipo Arrendamiento",["Larga Duración","Temporada","Vacacional"],index=safe_index(["Larga Duración","Temporada","Vacacional"],datos.get("Tipo_Arrendamiento"),0))
                cochera_vinculada=st.selectbox("Cochera Vinculada",["N","S"],index=0 if datos.get("Cochera_Vinculada")=="N" else 1)
                zona_tensionada=st.selectbox("Zona Tensionada",["N","S"],index=0 if datos.get("Zona_Tensionada")=="N" else 1)
            # ── Campos nuevos: inmueble no arrendado + cochera incluida ──
            col_flags1, col_flags2 = st.columns(2)
            with col_flags1:
                inmueble_no_arrendado = st.checkbox(
                    "🏚️ Inmueble NO arrendado (imputación 2% IRPF)",
                    value=bool(datos.get("Inmueble_No_Arrendado", False)),
                    help="Si el inmueble no está alquilado, Hacienda imputa una renta del 2% del valor catastral (o 1,1% si fue revisado después de 1994). No genera renta real — renta = 0."
                )
            with col_flags2:
                cochera_incluida_arrendamiento = st.checkbox(
                    "🚗 Cochera incluida en el arrendamiento",
                    value=bool(datos.get("Cochera_Incluida_Arrendamiento", False)),
                    help="La cochera se arrienda junto con el inmueble, sin contrato separado. Los gastos de la cochera (IBI, comunidad) son deducibles en el mismo contrato."
                )
            if inmueble_no_arrendado:
                st.info("ℹ️ Al marcar inmueble no arrendado, la renta se considera 0. La imputación fiscal del 2% se calculará automáticamente en el Escudo Fiscal.")
            st.markdown("### 📅 Contrato e Inquilino")
            col11,col12,col13=st.columns(3)
            with col11:
                nif_inquilino=st.text_input("NIF Inquilino",value=datos.get("NIF_Inquilino",""))
                fecha_inicio=st.date_input("Fecha Inicio Contrato",value=pd.to_datetime(datos.get("Fecha_Inicio_Contrato","2024-01-01")).date() if pd.notna(datos.get("Fecha_Inicio_Contrato")) else date(2024,1,1))
            with col12:
                iva_aplicable=st.checkbox("¿Arrendamiento a empresa (IVA)?",value=bool(datos.get("IVA_Aplicable",False)))
                fecha_vencimiento=st.date_input("Fecha Vencimiento Contrato",value=pd.to_datetime(datos.get("Fecha_Vencimiento_Contrato","2025-12-31")).date() if pd.notna(datos.get("Fecha_Vencimiento_Contrato")) else date(2025,12,31))
            with col13:
                retencion_irpf_pct=st.number_input("Retención IRPF (%)",value=safe_float(datos.get("Retencion_IRPF_Pct"),0.0),min_value=0.0,max_value=25.0,step=1.0)
                tipo_iva=st.number_input("Tipo IVA (%)",value=safe_float(datos.get("Tipo_IVA"),21.0),min_value=0.0,max_value=21.0,step=1.0,disabled=not iva_aplicable)
            col_dias1,col_dias2=st.columns(2)
            with col_dias1: dias_arrendados=st.number_input("Días arrendados año fiscal (cas. 0101)",value=safe_float(datos.get("Dias_Arrendados_Anio"),365.0),min_value=0.0,max_value=366.0,step=1.0)
            with col_dias2: gastos_formalizacion=st.number_input("Gastos Formalización (€)",value=safe_float(datos.get("Gastos_Formalizacion"),0.0),min_value=0.0,step=10.0)
            st.markdown("### 💰 Gastos Deducibles IRPF")
            col8,col9,col10=st.columns(3)
            with col8:
                ibi_anual=st.number_input("IBI Anual (€)",value=safe_float(datos.get("IBI_Anual"),0.0),min_value=0.0,step=10.0)
                seguro_anual=st.number_input("Seguro Hogar Anual (€)",value=safe_float(datos.get("Seguro_Anual"),0.0),min_value=0.0,step=10.0)
                seguro_vida=st.number_input("Seguro Vida Anual (€)",value=safe_float(datos.get("Seguro_Vida"),0.0),min_value=0.0,step=10.0)
            with col9:
                intereses_hipoteca=st.number_input("Intereses Hipoteca (€)",value=safe_float(datos.get("Intereses_Hipoteca"),0.0),min_value=0.0,step=100.0)
                gastos_juridicos=st.number_input("Gastos Jurídicos (€)",value=safe_float(datos.get("Gastos_Juridicos"),0.0),min_value=0.0,step=10.0)
                gasto_ascensor=st.number_input("Ascensor / Comunidad extra (€)",value=safe_float(datos.get("Gasto_Ascensor"),0.0),min_value=0.0,step=10.0)
            with col10:
                retenciones_irpf=st.number_input("Retenciones IRPF año (€)",value=safe_float(datos.get("Retenciones_IRPF"),0.0),min_value=0.0,step=10.0)
                gastos_pend_años_ant=st.number_input("Gastos Pend. Años Ant. (€)",value=safe_float(datos.get("Gastos_Pendientes_Años_Ant"),0.0),min_value=0.0,step=10.0)
                servicios_suministros=st.number_input("Servicios y Suministros (€)",value=safe_float(datos.get("Servicios_Suministros"),0.0),min_value=0.0,step=10.0)
            st.markdown("### 🏛️ Datos para Amortización Fiscal")
            st.info("Amortización = MAX(precio compra total, valor catastral) × % construcción × 3% × % titularidad")
            col_am1,col_am2,col_am3=st.columns(3)
            with col_am1:
                try:
                    fecha_adq_raw=datos.get("Fecha_Adquisicion")
                    fecha_adq_val=pd.to_datetime(fecha_adq_raw).date() if fecha_adq_raw and str(fecha_adq_raw) not in ["nan","None",""] else date(2010,1,1)
                except: fecha_adq_val=date(2010,1,1)
                fecha_adquisicion=st.date_input("Fecha Adquisición Inmueble",value=fecha_adq_val)
                precio_compra=st.number_input("Precio Compra (€)",value=safe_float(datos.get("Precio_Compra"),0.0),min_value=0.0,step=1000.0)
            with col_am2:
                impuestos_compra=st.number_input("Impuestos Compra ITP/IVA (€)",value=safe_float(datos.get("Impuestos_Compra"),0.0),min_value=0.0,step=100.0)
                gastos_compra=st.number_input("Gastos Notaría/Registro (€)",value=safe_float(datos.get("Gastos_Compra"),0.0),min_value=0.0,step=100.0)
            with col_am3:
                valor_catastral=st.number_input("Valor Catastral Total (€)",value=safe_float(datos.get("Valor_Catastral"),0.0),min_value=0.0,step=100.0)
                valor_catastral_piso=st.number_input("Valor Catastral Construcción (€)",value=safe_float(datos.get("Valor_Catastral_Piso"),0.0),min_value=0.0,step=100.0)
            col_pct1,col_pct2=st.columns(2)
            with col_pct1: pct_suelo=st.slider("% Suelo (catastral)",min_value=0.0,max_value=1.0,value=safe_float(datos.get("Pct_Suelo"),0.25),step=0.01,format="%.2f")
            with col_pct2: pct_construccion=round(1.0-pct_suelo,2); st.metric("% Construcción (calculado)",f"{pct_construccion*100:.0f}%")
            import re as _re
            base_compra=precio_compra+impuestos_compra+gastos_compra
            base_amortizacion=max(base_compra,valor_catastral)*pct_construccion
            titular_str=str(datos.get("Titular","100"))
            _match=_re.search(r'(\d+(?:\.\d+)?)',titular_str)
            pct_titular=float(_match.group(1))/100 if _match else 1.0
            if pct_titular>1: pct_titular=pct_titular/100
            amortizacion_fiscal=round(base_amortizacion*0.03*pct_titular,2)
            valor_real_construccion=round(max(base_compra,valor_catastral)*pct_construccion,2)
            st.success(f"📊 **Amortización Fiscal Calculada**\nBase compra: **{base_compra:,.0f} €** · Catastral: **{valor_catastral:,.0f} €**\n✅ Amortización anual (3% × {pct_titular*100:.0f}%): **{amortizacion_fiscal:,.0f} €/año**")
            st.markdown("### 🅿️ Cochera / Garaje")
            col_coch1,col_coch2,col_coch3=st.columns(3)
            with col_coch1: ref_catastral_cochera=st.text_input("Ref. Catastral Cochera",value=datos.get("Ref_Catastral_Cochera",""))
            with col_coch2: ibi_cocheras=st.number_input("IBI Cochera (€)",value=safe_float(datos.get("IBI_Cocheras"),0.0),min_value=0.0,step=10.0)
            with col_coch3: comunidad_cocheras=st.number_input("Comunidad Cochera (€)",value=safe_float(datos.get("Comunidad_Cocheras"),0.0),min_value=0.0,step=10.0)
            st.markdown("---")
            col_submit,col_cancel=st.columns(2)
            with col_submit: submitted=st.form_submit_button("💾 Guardar Inmueble",type="primary",use_container_width=True)
            with col_cancel: cancelled=st.form_submit_button("❌ Cancelar",use_container_width=True)

            if submitted:
                if not nombre.strip(): st.error("El nombre del inmueble es obligatorio")
                elif renta<=0: st.error("La renta debe ser mayor que 0")
                elif valor_construccion<=0: st.error("El valor de construcción debe ser mayor que 0")
                else:
                    nuevo_inmueble={"Nombre":nombre,"Inquilino":inquilino,"Renta":renta,"Renta_Mercado":renta_mercado,"Comunidad":comunidad,"Valor_Construccion":valor_construccion,"Año_Reforma":año_reforma,"Año_Construccion":año_construccion,"Mobiliario":mobiliario,"Tipo":tipo,"Ref_Catastral":ref_catastral,"Titular":titular,"M2_Construidos":m2,"Habitaciones":habitaciones,"CP":cp,"Planta":planta,"Parking":parking,"Estado":estado,"Tipo_Arrendamiento":tipo_arrendamiento,"Cochera_Vinculada":cochera_vinculada,"Zona_Tensionada":zona_tensionada,"Fecha_Inicio_Contrato":fecha_inicio.strftime("%Y-%m-%d"),"Fecha_Vencimiento_Contrato":fecha_vencimiento.strftime("%Y-%m-%d"),"Fecha_Adquisicion":fecha_adquisicion.strftime("%Y-%m-%d"),"Dias_Arrendados_Anio":int(dias_arrendados),"NIF_Inquilino":nif_inquilino,"IBI_Anual":ibi_anual,"Seguro_Anual":seguro_anual,"Seguro_Vida":seguro_vida,"Intereses_Hipoteca":intereses_hipoteca,"Gasto_Ascensor":gasto_ascensor,"Gastos_Juridicos":gastos_juridicos,"Retenciones_IRPF":retenciones_irpf,"Retencion_IRPF_Pct":retencion_irpf_pct,"IVA_Aplicable":iva_aplicable,"Tipo_IVA":tipo_iva,"Gastos_Formalizacion":gastos_formalizacion,"Gastos_Pendientes_Años_Ant":gastos_pend_años_ant,"Servicios_Suministros":servicios_suministros,"Precio_Compra":precio_compra,"Impuestos_Compra":impuestos_compra,"Gastos_Compra":gastos_compra,"Valor_Catastral":valor_catastral,"Valor_Catastral_Piso":valor_catastral_piso,"Pct_Suelo":pct_suelo,"Pct_Construccion":pct_construccion,"Valor_Real_Construccion":valor_real_construccion,"Amortizacion_Fiscal":amortizacion_fiscal,"Ref_Catastral_Cochera":ref_catastral_cochera,"IBI_Cocheras":ibi_cocheras,"Comunidad_Cocheras":comunidad_cocheras,"Inmueble_No_Arrendado":inmueble_no_arrendado,"Cochera_Incluida_Arrendamiento":cochera_incluida_arrendamiento}
                    if es_nuevo:
                        df_nuevo=pd.concat([st.session_state.df_inm_persistent,pd.DataFrame([nuevo_inmueble])],ignore_index=True)
                        st.session_state.df_inm_persistent=df_nuevo
                        try:
                            guardar_inmuebles(df_nuevo,user_id=st.session_state.user_id)
                            st.success(f"✅ '{nombre}' guardado en Supabase correctamente")
                        except Exception as e:
                            st.error(f"❌ Error al guardar en Supabase: {e}")
                    else:
                        for col,val in nuevo_inmueble.items():
                            st.session_state.df_inm_persistent.at[st.session_state.inmueble_editando,col]=val
                        try:
                            guardar_inmuebles(st.session_state.df_inm_persistent,user_id=st.session_state.user_id)
                            st.success(f"✅ '{nombre}' actualizado en Supabase correctamente")
                        except Exception as e:
                            st.error(f"❌ Error al actualizar en Supabase: {e}")
                    import time; time.sleep(1); st.session_state.modo_cartera="lista"; st.rerun()
            if cancelled:
                st.session_state.modo_cartera="lista"; st.rerun()

    # ── TABLA COMPLETA ─────────────────────────────────────────
    elif st.session_state.modo_cartera=="tabla":
        st.markdown('<div class="nc-section-title">📊 Tabla Completa de Datos</div>',unsafe_allow_html=True)
        st.warning("⚠️ Vista avanzada — solo para usuarios experimentados")
        col_cfg={"Tipo_Arrendamiento":st.column_config.SelectboxColumn("Tipo Arrend.",options=["Larga Duración","Temporada","Vacacional"],required=True),"Estado":st.column_config.SelectboxColumn("Estado",options=["Reformado","Bueno","Regular"],required=True),"Mobiliario":st.column_config.SelectboxColumn("Mobiliario",options=["S","N"],required=True),"Parking":st.column_config.SelectboxColumn("Parking",options=["S","N"],required=True)}
        df_ed=st.data_editor(df_inm,num_rows="dynamic",use_container_width=True,hide_index=True,column_config=col_cfg)
        if st.button("✅ Guardar Cambios de Tabla",type="primary"):
            nombres_antes = set(st.session_state.df_inm_persistent["Nombre"].dropna().astype(str))
            nombres_despues = set(df_ed["Nombre"].dropna().astype(str)) if "Nombre" in df_ed.columns else nombres_antes
            borrados = nombres_antes - nombres_despues
            errores_borrado = []
            for nombre_borrado in borrados:
                if not eliminar_inmueble(nombre_borrado, user_id=st.session_state.user_id):
                    errores_borrado.append(nombre_borrado)
            st.session_state.df_inm_persistent = df_ed
            guardado_ok = guardar_inmuebles(df_ed, user_id=st.session_state.user_id)
            if guardado_ok and not errores_borrado:
                st.session_state["_tabla_guardada_ok"] = True
            st.rerun()
        if st.session_state.pop("_tabla_guardada_ok", False):
            st.success("✅ Cambios guardados correctamente en Supabase")

    # ── BACKUPS ────────────────────────────────────────────────
    elif st.session_state.modo_cartera=="backup":
        st.markdown('<div class="nc-section-title">💾 Copias de Seguridad</div>',unsafe_allow_html=True)
        st.info("💡 Descarga tus datos regularmente para no perder información")
        col_b1,col_b2=st.columns(2)
        with col_b1: st.download_button("📥 Descargar Inmuebles (CSV)",generar_csv_backup(st.session_state.df_inm_persistent,"inmuebles"),"nolasco_inmuebles_backup.csv","text/csv",use_container_width=True)
        with col_b2: st.download_button("📥 Descargar Movimientos (CSV)",generar_csv_backup(st.session_state.df_mov_persistent,"movimientos"),"nolasco_movimientos_backup.csv","text/csv",use_container_width=True)
        st.markdown("---")
        st.markdown("### 📥 Importar Excel Asesor Fiscal")
        uploaded_excel=st.file_uploader("Sube el Excel de Nolasco Capital (.xlsx)",type=["xlsx"],key="upload_excel_asesor")
        if uploaded_excel:
            st.info(f"📄 Archivo: **{uploaded_excel.name}** — listo para importar")
            if st.button("📥 Importar inmuebles del Excel",type="primary",use_container_width=True,key="btn_import_excel"):
                from fiscal_export import importar_excel_asesor
                with st.spinner("Importando datos del Excel..."):
                    resultado=importar_excel_asesor(archivo_excel=uploaded_excel,user_id=st.session_state.user_id,upsert_inmueble_fn=upsert_inmueble,agregar_movimientos_fn=agregar_movimientos,leer_inmuebles_fn=leer_inmuebles)
                if "error" in resultado:
                    st.error(f"❌ {resultado['error']}")
                else:
                    n_ok = len(resultado["creados"]) + len(resultado["actualizados"])
                    n_err = len(resultado.get("errores", []))
                    if n_ok > 0:
                        st.success(f"✅ Import completado — {n_ok} inmuebles procesados")
                    if n_err > 0:
                        st.warning(f"⚠️ {n_err} inmueble(s) fallaron al guardar en Supabase:")
                        for err in resultado.get("errores", []):
                            st.code(err, language=None)
                    col_r1,col_r2,col_r3=st.columns(3)
                    col_r1.metric("Creados nuevos", len(resultado["creados"]))
                    col_r2.metric("Actualizados", len(resultado["actualizados"]))
                    col_r3.metric("Movimientos añadidos", resultado["movimientos"])
                    if n_ok > 0:
                        st.session_state.df_inm_persistent=leer_inmuebles(user_id=st.session_state.user_id)
                        st.rerun()

# ================================================================
# PANTALLA: MI PERFIL
# Datos fiscales del emisor + logo + cambio contraseña/email
# ================================================================
elif menu == "Mi Perfil":
    st.markdown('<div class="nc-brand-header">👤 Mi Perfil</div>', unsafe_allow_html=True)
    st.markdown('<div class="nc-brand-sub">Datos personales · Datos fiscales · Seguridad</div>', unsafe_allow_html=True)

    uid_perfil = st.session_state.user_id

    # Cargar perfil actual
    if "perfil_datos" not in st.session_state:
        st.session_state.perfil_datos = leer_perfil_usuario(uid_perfil)
    # Sanitizar — convertir None a defaults seguros
    _p_raw = st.session_state.perfil_datos
    p = {
        "nombre_fiscal":   str(_p_raw.get("nombre_fiscal")   or ""),
        "nif":             str(_p_raw.get("nif")             or ""),
        "telefono":        str(_p_raw.get("telefono")        or ""),
        "direccion":       str(_p_raw.get("direccion")       or ""),
        "ciudad":          str(_p_raw.get("ciudad")          or "Granada"),
        "cp":              str(_p_raw.get("cp")              or ""),
        "iban":            str(_p_raw.get("iban")            or ""),
        "prefijo_factura": str(_p_raw.get("prefijo_factura") or "F"),
        "siguiente_numero": int(_p_raw.get("siguiente_numero") or 1),
        "tipo_cuenta":     str(_p_raw.get("tipo_cuenta")     or "particular"),
        "nombre_sociedad": str(_p_raw.get("nombre_sociedad") or ""),
        "cif_sociedad":    str(_p_raw.get("cif_sociedad")    or ""),
    }

    tab_fiscal, tab_logo, tab_seguridad = st.tabs([
        "🏛️ Datos Fiscales", "🖼️ Logo", "🔐 Seguridad"
    ])

    # ── TAB 1: DATOS FISCALES ──────────────────────────────────
    with tab_fiscal:
        st.markdown('<div class="nc-section-title">Datos del emisor de facturas</div>', unsafe_allow_html=True)
        st.caption("Estos datos aparecerán en todas las facturas que generes.")

        # ── Tipo de cuenta FUERA del form (para recargar en tiempo real) ──
        tipo_actual = p.get("tipo_cuenta", "particular")
        tipo_cuenta = st.radio(
            "¿Cómo tributas?",
            options=["particular", "sociedad"],
            format_func=lambda x: "👤 Particular (IRPF — Modelo 100)" if x == "particular"
                                  else "🏢 Sociedad Patrimonial (IS — Modelo 200)",
            index=0 if tipo_actual == "particular" else 1,
            horizontal=True,
            key="radio_tipo_cuenta"
        )
        # Guardar selección en session_state para leerla dentro del form
        st.session_state["_tipo_cuenta_form"] = tipo_cuenta

        if tipo_cuenta == "sociedad":
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                nombre_sociedad = st.text_input("Nombre de la sociedad *",
                    value=p.get("nombre_sociedad",""),
                    placeholder="Inmuebles Nolasco SL",
                    key="input_nombre_sociedad")
            with col_s2:
                cif_sociedad = st.text_input("CIF de la sociedad *",
                    value=p.get("cif_sociedad",""),
                    placeholder="B12345678",
                    key="input_cif_sociedad")
            st.info("🏢 Modo Sociedad Patrimonial activado — IS al 25% sin reducción por arrendamiento.")
        else:
            nombre_sociedad = p.get("nombre_sociedad","")
            cif_sociedad    = p.get("cif_sociedad","")

        st.markdown("---")

        with st.form("form_perfil_fiscal"):
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                nombre_fiscal = st.text_input("Nombre fiscal completo *",
                    value=p.get("nombre_fiscal",""), placeholder="Pedro Campos Godoy")
                nif = st.text_input("NIF / DNI *",
                    value=p.get("nif",""), placeholder="24237110D")
                telefono = st.text_input("Teléfono",
                    value=p.get("telefono",""), placeholder="600 000 000")
            with col2:
                direccion = st.text_input("Dirección completa *",
                    value=p.get("direccion",""), placeholder="Calle Mayor, 1")
                ciudad = st.text_input("Ciudad",
                    value=p.get("ciudad","Granada"), placeholder="Granada")
                cp = st.text_input("Código Postal",
                    value=p.get("cp",""), placeholder="18001")

            iban = st.text_input("IBAN (cuenta bancaria para transferencias)",
                value=p.get("iban",""),
                placeholder="ES76 2100 2673 6202 1018 4323")

            col_pref1, col_pref2 = st.columns(2)
            with col_pref1:
                prefijo = st.text_input("Prefijo facturas",
                    value=p.get("prefijo_factura","F"),
                    help="Ej: F → F260001. Ej: NC → NC260001")
            with col_pref2:
                sig_num = st.number_input("Siguiente número de factura",
                    value=int(p.get("siguiente_numero",1)),
                    min_value=1, step=1,
                    help="Se incrementa automáticamente al generar cada factura")

            submitted = st.form_submit_button("💾 Guardar datos fiscales",
                                               type="primary", use_container_width=True)
            if submitted:
                # Leer tipo_cuenta y campos sociedad del session_state (están fuera del form)
                _tc  = st.session_state.get("_tipo_cuenta_form", "particular")
                _ns  = st.session_state.get("input_nombre_sociedad", nombre_sociedad)
                _cif = st.session_state.get("input_cif_sociedad", cif_sociedad)
                if not nombre_fiscal.strip() or not nif.strip():
                    st.warning("⚠️ Nombre fiscal y NIF son obligatorios.")
                elif _tc == "sociedad" and (not _ns.strip() or not _cif.strip()):
                    st.warning("⚠️ Nombre y CIF de la sociedad son obligatorios en modo Sociedad Patrimonial.")
                else:
                    ok = guardar_perfil_usuario(uid_perfil, {
                        "nombre_fiscal":   nombre_fiscal.strip(),
                        "nif":             nif.strip().upper(),
                        "direccion":       direccion.strip(),
                        "ciudad":          ciudad.strip(),
                        "cp":              cp.strip(),
                        "telefono":        telefono.strip(),
                        "iban":            iban.strip(),
                        "prefijo_factura": prefijo.strip() or "F",
                        "siguiente_numero": int(sig_num),
                        "tipo_cuenta":     _tc,
                        "nombre_sociedad": _ns.strip(),
                        "cif_sociedad":    _cif.strip().upper(),
                    })
                    if ok:
                        st.success("✅ Datos fiscales guardados correctamente")
                        st.session_state.perfil_datos = leer_perfil_usuario(uid_perfil)
                    else:
                        st.error("❌ Error al guardar. Inténtalo de nuevo.")

    # ── TAB 2: LOGO ────────────────────────────────────────────
    with tab_logo:
        st.markdown('<div class="nc-section-title">Logo de empresa</div>', unsafe_allow_html=True)
        st.caption("Aparece en el sidebar y en las facturas generadas.")

        logo_actual = st.session_state.get("sidebar_logo_bytes")
        if logo_actual:
            col_img, col_btn = st.columns([1, 3])
            with col_img:
                st.image(logo_actual, width=150)
            with col_btn:
                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Eliminar logo", key="btn_del_logo"):
                    guardar_logo_usuario(uid_perfil, b"", "png")
                    st.session_state.pop("sidebar_logo_bytes", None)
                    st.success("✅ Logo eliminado")
                    st.rerun()

        st.markdown("---")
        logo_file = st.file_uploader(
            "Subir nuevo logo (PNG o JPG, max 2MB)",
            type=["png","jpg","jpeg"],
            key="upload_logo_perfil"
        )
        if logo_file:
            if logo_file.size > 2_000_000:
                st.warning("⚠️ El archivo supera 2MB. Usa una imagen más pequeña.")
            else:
                ext = logo_file.name.split(".")[-1].lower()
                b = logo_file.read()
                if st.button("📤 Subir logo", type="primary", key="btn_up_logo"):
                    ok = guardar_logo_usuario(uid_perfil, b, ext)
                    if ok:
                        st.session_state["sidebar_logo_bytes"] = b
                        st.success("✅ Logo actualizado")
                        st.rerun()
                    else:
                        st.error("❌ Error al subir el logo.")

    # ── TAB 3: SEGURIDAD ───────────────────────────────────────
    with tab_seguridad:
        st.markdown('<div class="nc-section-title">Acceso y seguridad</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:10px;
                    padding:1rem 1.2rem;margin-bottom:1.5rem;'>
            <div style='font-size:0.72rem;color:{TEXT_SEC};text-transform:uppercase;
                        letter-spacing:.06em;margin-bottom:4px;'>Email actual</div>
            <div style='font-size:1rem;font-weight:600;color:{TEXT_PRI};'>
                {st.session_state.user_email}
            </div>
        </div>""", unsafe_allow_html=True)

        col_s1, col_s2 = st.columns(2)

        with col_s1:
            st.markdown("**Cambiar contraseña**")
            nueva_pass = st.text_input("Nueva contraseña",
                type="password", key="nueva_pass",
                placeholder="Mínimo 6 caracteres")
            nueva_pass2 = st.text_input("Repetir contraseña",
                type="password", key="nueva_pass2",
                placeholder="Repite la contraseña")
            if st.button("🔐 Cambiar contraseña", use_container_width=True,
                          key="btn_change_pass"):
                if not nueva_pass or len(nueva_pass) < 6:
                    st.warning("⚠️ Mínimo 6 caracteres.")
                elif nueva_pass != nueva_pass2:
                    st.warning("⚠️ Las contraseñas no coinciden.")
                else:
                    token = st.session_state.get("access_token","")
                    res = cambiar_contrasena(token, nueva_pass)
                    if res["ok"]:
                        st.success("✅ Contraseña actualizada")
                    else:
                        st.error(f"❌ {res.get('error','Error desconocido')}")

        with col_s2:
            st.markdown("**Cambiar email**")
            nuevo_email = st.text_input("Nuevo email",
                key="nuevo_email", placeholder="nuevo@email.com")
            if st.button("✉️ Cambiar email", use_container_width=True,
                          key="btn_change_email"):
                if not nuevo_email.strip() or "@" not in nuevo_email:
                    st.warning("⚠️ Introduce un email válido.")
                else:
                    token = st.session_state.get("access_token","")
                    res = cambiar_email(token, nuevo_email.strip())
                    if res["ok"]:
                        st.success("✅ Email actualizado. Revisa tu bandeja para confirmar.")
                    else:
                        st.error(f"❌ {res.get('error','Error desconocido')}")


# ================================================================
# PANTALLA: INGRESOS · RENTAS
# Plantillas por inmueble + generación de facturas + PDF
# ================================================================
elif menu == "Ingresos · Rentas":
    st.markdown('<div class="nc-brand-header">📥 Ingresos · Rentas</div>', unsafe_allow_html=True)
    st.markdown('<div class="nc-brand-sub">Facturas de arrendamiento · Numeración correlativa · PDF</div>', unsafe_allow_html=True)

    uid_ing = st.session_state.user_id

    # Verificar datos del emisor
    perfil_ing = leer_perfil_usuario(uid_ing)
    if not perfil_ing.get("nombre_fiscal") or not perfil_ing.get("nif"):
        st.warning("⚠️ Antes de generar facturas, completa tus datos fiscales en **👤 Mi Perfil**.")
        if st.button("→ Ir a Mi Perfil", type="primary"):
            st.session_state.menu = "Mi Perfil"; st.rerun()
        st.stop()

    tab_generar, tab_historial, tab_plantillas = st.tabs([
        "🧾 Generar Factura", "📋 Diario de Ingresos", "⚙️ Plantillas"
    ])

    # ── TAB 1: GENERAR FACTURA ─────────────────────────────────
    with tab_generar:
        st.markdown('<div class="nc-section-title">Nueva factura de renta</div>', unsafe_allow_html=True)

        # Cargar plantillas
        df_plantillas = leer_plantillas_factura(uid_ing)
        if df_plantillas.empty:
            st.info("📋 Aún no tienes plantillas configuradas. Ve a **⚙️ Plantillas** para crearlas.")
        else:
            # Selector de inmueble
            inmuebles_con_plantilla = df_plantillas["inmueble"].tolist()
            inm_sel = st.selectbox("Selecciona inmueble", inmuebles_con_plantilla,
                                    key="ing_inm_sel")
            plantilla = df_plantillas[df_plantillas["inmueble"] == inm_sel].iloc[0]

            # Key única por inmueble — fuerza re-render al cambiar inmueble
            _k = inm_sel.replace(" ","_").replace(".","")[:20]

            # Datos pre-rellenados de la plantilla
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                meses_es = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
                mes_fac = st.selectbox("Mes de la renta", meses_es,
                                        index=datetime.now().month - 1,
                                        key=f"ing_mes_{_k}")
                año_fac = st.number_input("Año", value=datetime.now().year,
                                           min_value=2020, max_value=2030,
                                           key=f"ing_año_{_k}")
            with col_f2:
                fecha_fac = st.date_input("Fecha factura",
                                           value=date.today(), key=f"ing_fecha_{_k}")
            with col_f3:
                fecha_venc = st.date_input("Fecha vencimiento",
                                            value=date.today(), key=f"ing_venc_{_k}")

            st.markdown("---")

            # Datos editables (pre-rellenados de plantilla)
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("**Inquilino**")
                inquilino = st.text_input("Nombre", value=str(plantilla.get("inquilino","") or ""),
                                           key=f"ing_inq_{_k}")
                nif_inq = st.text_input("NIF", value=str(plantilla.get("nif_inquilino","") or ""),
                                         key=f"ing_nif_{_k}")
                dir_inq = st.text_area("Dirección", value=str(plantilla.get("direccion_inquilino","") or ""),
                                        key=f"ing_dir_{_k}", height=80)
            with col_d2:
                st.markdown("**Importes**")
                base = st.number_input("Base imponible (€)",
                    value=float(plantilla.get("base_imponible",0) or 0),
                    min_value=0.0, step=10.0, format="%.2f", key=f"ing_base_{_k}")
                pct_iva = st.number_input("IVA (%)",
                    value=float(plantilla.get("pct_iva",0) or 0),
                    min_value=0.0, max_value=21.0, step=1.0, key=f"ing_iva_{_k}")
                pct_ret = st.number_input("Retención IRPF (%)",
                    value=float(plantilla.get("pct_retencion",0) or 0),
                    min_value=0.0, max_value=25.0, step=1.0, key=f"ing_ret_{_k}")

                imp_iva = round(base * pct_iva / 100, 2)
                imp_ret = round(base * pct_ret / 100, 2)
                total   = round(base + imp_iva - imp_ret, 2)

                st.markdown(f"""
                <div style='background:{CARD_BG};border:1px solid {BORDER};
                            border-radius:10px;padding:1rem;margin-top:8px;'>
                    <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
                        <span style='font-size:0.82rem;color:{TEXT_SEC};'>Base imponible</span>
                        <span style='font-size:0.9rem;'>{base:,.2f} €</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
                        <span style='font-size:0.82rem;color:{TEXT_SEC};'>IVA {pct_iva:.0f}%</span>
                        <span style='font-size:0.9rem;'>+{imp_iva:,.2f} €</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;margin-bottom:8px;'>
                        <span style='font-size:0.82rem;color:{TEXT_SEC};'>Retención {pct_ret:.0f}%</span>
                        <span style='font-size:0.9rem;color:{RED};'>−{imp_ret:,.2f} €</span>
                    </div>
                    <div style='border-top:1px solid {BORDER};padding-top:8px;
                                display:flex;justify-content:space-between;'>
                        <span style='font-weight:700;'>TOTAL</span>
                        <span style='font-size:1.2rem;font-weight:700;color:{ACCENT};'>
                            {total:,.2f} €</span>
                    </div>
                </div>""", unsafe_allow_html=True)

            # Número de factura
            prefijo_p = perfil_ing.get("prefijo_factura","F")
            sig_n     = int(perfil_ing.get("siguiente_numero",1))
            año_2d    = str(año_fac)[2:]
            num_fac   = f"{prefijo_p}{año_2d}{sig_n:04d}"
            concepto  = f"RENTA {inm_sel.upper()} · {mes_fac.upper()} {año_fac}"

            st.markdown(f"""
            <div style='background:#EAF3DE;border:1px solid #B5D4A0;border-radius:8px;
                        padding:10px 14px;margin:12px 0;'>
                <span style='font-size:0.8rem;color:#27500A;font-weight:600;'>
                    📄 Número de factura: <strong>{num_fac}</strong> · Concepto: {concepto}
                </span>
            </div>""", unsafe_allow_html=True)

            if st.button("🧾 Generar factura PDF", type="primary",
                          use_container_width=True, key="btn_generar_fac"):
                if not inquilino.strip():
                    st.warning("⚠️ El nombre del inquilino es obligatorio.")
                else:
                    # Crear registro en Supabase
                    datos_fac = {
                        "numero": num_fac,
                        "fecha": fecha_fac.strftime("%Y-%m-%d"),
                        "vencimiento": fecha_venc.strftime("%Y-%m-%d"),
                        "inmueble": inm_sel,
                        "inquilino": inquilino.strip(),
                        "nif_inquilino": nif_inq.strip(),
                        "direccion_inquilino": dir_inq.strip(),
                        "concepto": concepto,
                        "base_imponible": base,
                        "pct_iva": pct_iva,
                        "importe_iva": imp_iva,
                        "pct_retencion": pct_ret,
                        "importe_retencion": imp_ret,
                        "total": total,
                        "estado": "emitida"
                    }
                    res_fac = crear_factura_emitida(uid_ing, datos_fac)

                    if not res_fac["ok"]:
                        st.error(f"❌ Error creando factura: {res_fac['error']}")
                    else:
                        fac_id = res_fac["id"]
                        # Generar PDF con ReportLab
                        if REPORTLAB_OK:
                            pdf_buf = _generar_pdf_factura(
                                perfil_ing, datos_fac, num_fac
                            )
                            if pdf_buf:
                                pdf_bytes = pdf_buf.getvalue()
                                guardar_pdf_factura(uid_ing, fac_id, num_fac, pdf_bytes)
                                st.success(f"✅ Factura {num_fac} generada correctamente")
                                st.download_button(
                                    label=f"📥 Descargar {num_fac}.pdf",
                                    data=pdf_bytes,
                                    file_name=f"{num_fac}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                                # Actualizar perfil en session_state
                                st.session_state.pop("perfil_datos", None)
                            else:
                                st.warning("⚠️ Factura registrada pero el PDF falló. Descarga disponible en historial.")
                        else:
                            st.success(f"✅ Factura {num_fac} registrada (ReportLab no disponible para PDF)")

    # ── TAB 2: HISTORIAL ───────────────────────────────────────
    with tab_historial:
        st.markdown('<div class="nc-section-title">Facturas emitidas</div>', unsafe_allow_html=True)

        df_facs = leer_facturas_emitidas(uid_ing)
        if df_facs.empty:
            st.info("Aún no has generado ninguna factura.")
        else:
            # Asegurar columnas nuevas con defaults
            if "es_rectificativa"   not in df_facs.columns: df_facs["es_rectificativa"]   = False
            if "factura_rectificada" not in df_facs.columns: df_facs["factura_rectificada"] = None
            df_facs["es_rectificativa"] = df_facs["es_rectificativa"].fillna(False).astype(bool)

            # KPIs — excluir rectificativas y anuladas del total positivo
            df_activas = df_facs[~df_facs["es_rectificativa"] & (df_facs["estado"] != "anulada")]
            total_emitido   = df_activas["total"].sum()
            total_cobrado   = df_activas[df_activas["estado"]=="cobrada"]["total"].sum()
            total_pendiente = df_activas[df_activas["estado"]=="emitida"]["total"].sum()

            k1,k2,k3 = st.columns(3)
            for col_k, lbl, val, color in [
                (k1,"Total emitido",  f"{total_emitido:,.0f} €",   ACCENT),
                (k2,"Cobrado",        f"{total_cobrado:,.0f} €",   GREEN),
                (k3,"Pendiente",      f"{total_pendiente:,.0f} €", AMBER),
            ]:
                col_k.markdown(
                    f"<div style='background:{CARD_BG};border:1px solid {BORDER};"
                    f"border-top:3px solid {color};border-radius:10px;padding:.8rem;"
                    f"text-align:center;margin:8px 0;'>"
                    f"<div style='font-size:0.68rem;color:{TEXT_SEC};text-transform:uppercase;"
                    f"letter-spacing:.06em;margin-bottom:4px;'>{lbl}</div>"
                    f"<div style='font-size:1.1rem;font-weight:700;color:{color};'>{val}</div>"
                    f"</div>", unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            # ── LISTA DE FACTURAS ──────────────────────────────
            for _, fac in df_facs.iterrows():
                est        = str(fac.get("estado","emitida"))
                es_rec     = bool(fac.get("es_rectificativa", False))
                fac_rect   = str(fac.get("factura_rectificada","") or "")
                total_fac  = float(fac.get("total",0))
                _render_v  = st.session_state.get("fac_render_v", 0)

                # Badge de estado
                if es_rec:
                    badge = f"<span style='background:#E6F1FB;color:#0C447C;font-size:11px;padding:2px 8px;border-radius:20px;font-weight:600;'>🔄 Rectificativa</span>"
                elif est == "cobrada":
                    badge = f"<span style='background:#EAF3DE;color:#27500A;font-size:11px;padding:2px 8px;border-radius:20px;font-weight:600;'>✅ Cobrada</span>"
                elif est == "anulada":
                    badge = f"<span style='background:#FDECEA;color:#7F1D1D;font-size:11px;padding:2px 8px;border-radius:20px;font-weight:600;'>❌ Anulada</span>"
                else:
                    badge = f"<span style='background:#FFF9E6;color:#854F0B;font-size:11px;padding:2px 8px;border-radius:20px;font-weight:600;'>⏳ Emitida</span>"

                # Color total — negativo en rojo para rectificativas
                color_total = RED if total_fac < 0 else ACCENT

                # Referencia a factura original en rectificativas
                ref_html = f"<br><span style='font-size:0.75rem;color:#0C447C;'>Rectifica: <b>{fac_rect}</b></span>" if es_rec and fac_rect else ""

                fecha_s = str(fac.get("fecha",""))[:10]
                st.markdown(f"""
                <div style='background:{CARD_BG};border:1px solid {"#B5D4F4" if es_rec else BORDER};
                            border-left:3px solid {"#185FA5" if es_rec else "transparent"};
                            border-radius:10px;padding:12px 16px;margin-bottom:6px;
                            display:flex;justify-content:space-between;align-items:center;'>
                    <div>
                        <span style='font-weight:700;color:{TEXT_PRI};font-size:0.95rem;'>
                            {fac.get("numero","")}
                        </span>
                        <span style='color:{TEXT_SEC};font-size:0.82rem;margin-left:10px;'>
                            {fecha_s} · {fac.get("inmueble","")} · {fac.get("inquilino","")}
                        </span>
                        <br><span style='font-size:0.78rem;color:{TEXT_SEC};'>
                            {fac.get("concepto","")}
                        </span>{ref_html}
                    </div>
                    <div style='text-align:right;'>
                        <div style='font-size:1.1rem;font-weight:700;color:{color_total};'>
                            {total_fac:,.2f} €
                        </div>
                        {badge}
                    </div>
                </div>""", unsafe_allow_html=True)

                with st.expander("", expanded=False,
                                 key=f"fac_exp_{fac['id']}_{_render_v}"):
                    cf1, cf2, cf3 = st.columns(3)

                    with cf1:
                        # Edición — bloqueada para anuladas y rectificativas
                        _bloqueada = est == "anulada" or es_rec
                        if _bloqueada:
                            st.markdown(
                                f"<div style='background:#F8F8F8;border-radius:8px;"
                                f"padding:10px 12px;font-size:13px;color:{TEXT_SEC};'>"
                                f"{'🔄 Factura rectificativa — no editable' if es_rec else '❌ Factura anulada — no editable'}"
                                f"</div>", unsafe_allow_html=True)
                        else:
                            nueva_fecha = st.date_input("Fecha factura",
                                value=pd.to_datetime(fac.get("fecha", date.today())).date(),
                                key=f"fac_fecha_{fac['id']}")
                            nueva_base = st.number_input("Base imponible (€)",
                                value=float(fac.get("base_imponible",0)),
                                min_value=0.0, step=1.0, format="%.2f",
                                key=f"fac_base_{fac['id']}")
                            nuevo_concepto = st.text_input("Concepto",
                                value=str(fac.get("concepto","")),
                                key=f"fac_con_{fac['id']}")
                            nuevo_estado = st.selectbox(
                                "Estado",
                                ["emitida","cobrada"],
                                index=0 if est == "emitida" else 1,
                                key=f"fac_est_{fac['id']}"
                            )
                            if st.button("💾 Guardar cambios", key=f"fac_upd_{fac['id']}",
                                         use_container_width=True, type="primary"):
                                import requests as _rq
                                from supabase_db import SUPABASE_URL, SUPABASE_KEY
                                _pct_iva = float(fac.get("pct_iva",0))
                                _pct_ret = float(fac.get("pct_retencion",0))
                                _imp_iva = round(nueva_base * _pct_iva / 100, 2)
                                _imp_ret = round(nueva_base * _pct_ret / 100, 2)
                                _total   = round(nueva_base + _imp_iva - _imp_ret, 2)
                                _r = _rq.patch(
                                    f"{SUPABASE_URL}/rest/v1/facturas_emitidas"
                                    f"?id=eq.{fac['id']}&user_id=eq.{uid_ing}",
                                    headers={
                                        "apikey": SUPABASE_KEY,
                                        "Authorization": f"Bearer {st.session_state.get('access_token', SUPABASE_KEY)}",
                                        "Content-Type": "application/json",
                                        "Prefer": "return=minimal"
                                    },
                                    json={
                                        "fecha": nueva_fecha.strftime("%Y-%m-%d"),
                                        "base_imponible": nueva_base,
                                        "importe_iva": _imp_iva,
                                        "importe_retencion": _imp_ret,
                                        "total": _total,
                                        "concepto": nuevo_concepto,
                                        "estado": nuevo_estado,
                                    }, timeout=10
                                )
                                if _r.status_code in (200, 204):
                                    st.success("✅ Guardado correctamente")
                                    st.session_state["fac_render_v"] = st.session_state.get("fac_render_v",0)+1
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error {_r.status_code}: {_r.text[:100]}")

                    with cf2:
                        # Ver PDF
                        if fac.get("pdf_url"):
                            url_pdf = obtener_url_factura(uid_ing, str(fac["pdf_url"]))
                            if url_pdf:
                                st.markdown(
                                    f"<a href='{url_pdf}' target='_blank' "
                                    f"style='display:inline-block;background:#E6F1FB;"
                                    f"color:#0C447C;padding:8px 14px;border-radius:6px;"
                                    f"font-size:13px;font-weight:600;text-decoration:none;"
                                    f"border:1px solid #B5D4F4;'>👁️ Ver PDF</a>",
                                    unsafe_allow_html=True)

                        # Botón anular — solo para facturas activas no rectificativas
                        if not es_rec and est != "anulada":
                            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                            if st.button("🔄 Anular con rectificativa",
                                         key=f"btn_rect_{fac['id']}",
                                         use_container_width=True):
                                st.session_state[f"preview_rect_{fac['id']}"] = True

                        # Preview de la rectificativa
                        if st.session_state.get(f"preview_rect_{fac['id']}", False):
                            _b  = -abs(float(fac.get("base_imponible",0)))
                            _iv = -abs(float(fac.get("importe_iva",0)))
                            _rt = -abs(float(fac.get("importe_retencion",0)))
                            _tt = round(_b + _iv - _rt, 2)
                            perfil_p = leer_perfil_usuario(uid_ing)
                            _sig_r   = int(perfil_p.get("siguiente_numero_rec") or 1)
                            _anio_2d = str(date.today().year)[2:]
                            _num_rec = f"REC{_anio_2d}{_sig_r:04d}"

                            st.markdown(f"""
                            <div style='background:#EEF4FF;border:1.5px solid #185FA5;
                                        border-radius:10px;padding:14px;margin-top:10px;
                                        font-size:13px;'>
                                <div style='font-weight:700;color:#0C447C;margin-bottom:8px;'>
                                    📄 Preview Rectificativa
                                </div>
                                <div style='color:{TEXT_PRI};line-height:1.8;'>
                                    <b>Nº:</b> {_num_rec}<br>
                                    <b>Rectifica:</b> {fac.get("numero","")}<br>
                                    <b>Inquilino:</b> {fac.get("inquilino","")}<br>
                                    <b>Concepto:</b> ANULACIÓN {fac.get("numero","")} — {fac.get("concepto","")}<br>
                                    <hr style='border:0;border-top:1px dashed #B5D4F4;margin:6px 0;'>
                                    <b>Base:</b> {_b:,.2f} €<br>
                                    <b>IVA {float(fac.get("pct_iva",0)):.0f}%:</b> {_iv:,.2f} €<br>
                                    <b>Ret. {float(fac.get("pct_retencion",0)):.0f}%:</b> {_rt:,.2f} €<br>
                                    <b style='font-size:14px;'>TOTAL: {_tt:,.2f} €</b>
                                </div>
                            </div>""", unsafe_allow_html=True)

                            pr1, pr2 = st.columns(2)
                            with pr1:
                                if st.button("✅ Confirmar y generar",
                                             key=f"conf_rect_{fac['id']}",
                                             type="primary",
                                             use_container_width=True):
                                    _res = crear_factura_rectificativa(
                                        uid_ing, fac.to_dict()
                                    )
                                    if _res["ok"]:
                                        # Generar PDF rectificativa
                                        if REPORTLAB_OK:
                                            _datos_rec = {
                                                **fac.to_dict(),
                                                "numero": _res["numero"],
                                                "fecha": str(date.today()),
                                                "vencimiento": str(date.today()),
                                                "concepto": f"ANULACIÓN {fac.get('numero','')} — {fac.get('concepto','')}",
                                                "base_imponible": _b,
                                                "importe_iva": _iv,
                                                "importe_retencion": abs(_rt),
                                                "total": _tt,
                                                "es_rectificativa": True,
                                            }
                                            _pdf = _generar_pdf_factura(
                                                perfil_p, _datos_rec, _res["numero"],
                                                es_rectificativa=True
                                            )
                                            if _pdf:
                                                _pdf_bytes = _pdf.getvalue()
                                                guardar_pdf_factura(uid_ing, _res["id"],
                                                                    _res["numero"], _pdf_bytes)
                                                st.success(f"✅ Rectificativa {_res['numero']} generada")
                                                st.download_button(
                                                    f"📥 Descargar {_res['numero']}.pdf",
                                                    data=_pdf_bytes,
                                                    file_name=f"{_res['numero']}.pdf",
                                                    mime="application/pdf",
                                                    use_container_width=True
                                                )
                                        st.session_state.pop(f"preview_rect_{fac['id']}", None)
                                        st.session_state["fac_render_v"] = st.session_state.get("fac_render_v",0)+1
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {_res['error']}")
                            with pr2:
                                if st.button("❌ Cancelar",
                                             key=f"cancel_rect_{fac['id']}",
                                             use_container_width=True):
                                    st.session_state.pop(f"preview_rect_{fac['id']}", None)
                                    st.rerun()

                    with cf3:
                        st.markdown(f"**Base:** {float(fac.get('base_imponible',0)):,.2f} €")
                        st.markdown(f"**IVA {float(fac.get('pct_iva',0)):.0f}%:** {float(fac.get('importe_iva',0)):,.2f} €")
                        st.markdown(f"**Ret. {float(fac.get('pct_retencion',0)):.0f}%:** −{float(fac.get('importe_retencion',0)):,.2f} €")
                        st.markdown(f"**Total: {float(fac.get('total',0)):,.2f} €**")

    # ── TAB 3: PLANTILLAS ──────────────────────────────────────
    with tab_plantillas:
        st.markdown('<div class="nc-section-title">Plantillas por inmueble</div>', unsafe_allow_html=True)
        st.caption("Configura una vez los datos de cada inmueble. Se pre-rellenan al generar facturas.")

        df_plt = leer_plantillas_factura(uid_ing)

        # Mostrar plantillas existentes
        if not df_plt.empty:
            for _, plt_row in df_plt.iterrows():
                st.markdown(f"""
                <div style='background:{CARD_BG};border:1px solid {BORDER};
                            border-radius:10px;padding:12px 16px;margin-bottom:6px;'>
                    <b>{plt_row.get("inmueble","")}</b>
                    <span style='color:{TEXT_SEC};font-size:0.82rem;margin-left:10px;'>
                        {plt_row.get("inquilino","")} · Base: {float(plt_row.get("base_imponible",0)):,.2f}€
                        · IVA: {float(plt_row.get("pct_iva",0)):.0f}%
                        · Ret: {float(plt_row.get("pct_retencion",0)):.0f}%
                    </span>
                </div>""", unsafe_allow_html=True)
            st.markdown("---")

        # Formulario nueva plantilla / editar
        st.markdown("**Añadir o editar plantilla:**")

        # Selector inmueble — de la cartera o manual
        nombres_inm = df_inm["Nombre"].tolist() if not df_inm.empty else []
        inm_plt = st.selectbox("Inmueble", nombres_inm, key="plt_inm") if nombres_inm else \
                  st.text_input("Inmueble (escribe el nombre)", key="plt_inm_txt")

        if inm_plt:
            # Pre-rellenar si existe plantilla
            plt_exist = df_plt[df_plt["inmueble"]==inm_plt].iloc[0].to_dict() \
                        if not df_plt.empty and inm_plt in df_plt["inmueble"].values else {}
            # Pre-rellenar desde ficha del inmueble si existe
            inm_row = df_inm[df_inm["Nombre"]==inm_plt].iloc[0] if inm_plt in df_inm["Nombre"].values else {}

            with st.form(f"form_plt_{inm_plt}"):
                cp1, cp2 = st.columns(2)
                with cp1:
                    plt_inq = st.text_input("Inquilino *",
                        value=plt_exist.get("inquilino",
                              str(inm_row.get("Inquilino","")) if hasattr(inm_row,"get") else ""))
                    plt_nif = st.text_input("NIF inquilino",
                        value=plt_exist.get("nif_inquilino",
                              str(inm_row.get("NIF_Inquilino","")) if hasattr(inm_row,"get") else ""))
                    plt_dir = st.text_area("Dirección inquilino",
                        value=plt_exist.get("direccion_inquilino",""), height=80)
                with cp2:
                    plt_base = st.number_input("Base imponible (€) *",
                        value=float(plt_exist.get("base_imponible",
                                    float(inm_row.get("Renta",0)) if hasattr(inm_row,"get") else 0)),
                        min_value=0.0, step=10.0, format="%.2f")
                    plt_iva = st.number_input("IVA (%)",
                        value=float(plt_exist.get("pct_iva",
                                    float(inm_row.get("Tipo_IVA",0)) if hasattr(inm_row,"get") else 0)),
                        min_value=0.0, max_value=21.0, step=1.0)
                    plt_ret = st.number_input("Retención IRPF (%)",
                        value=float(plt_exist.get("pct_retencion",
                                    float(inm_row.get("Retencion_IRPF_Pct",0)) if hasattr(inm_row,"get") else 0)),
                        min_value=0.0, max_value=25.0, step=1.0)

                sub_plt = st.form_submit_button("💾 Guardar plantilla",
                                                 type="primary", use_container_width=True)
                if sub_plt:
                    if not plt_inq.strip():
                        st.warning("⚠️ El nombre del inquilino es obligatorio.")
                    else:
                        res_plt = guardar_plantilla_factura(uid_ing, {
                            "inmueble": inm_plt,
                            "inquilino": plt_inq.strip(),
                            "nif_inquilino": plt_nif.strip(),
                            "direccion_inquilino": plt_dir.strip(),
                            "base_imponible": plt_base,
                            "pct_iva": plt_iva,
                            "pct_retencion": plt_ret,
                        })
                        if res_plt["ok"]:
                            st.success(f"✅ Plantilla de {inm_plt} guardada")
                            st.rerun()
                        else:
                            st.error(f"❌ {res_plt['error']}")


# ================================================================
# FUNCIÓN: GENERAR PDF FACTURA EMITIDA (ReportLab)
# ================================================================
