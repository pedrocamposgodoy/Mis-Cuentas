import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────
# 1. CONFIG Y PALETA
# ─────────────────────────────────────────────
st.set_page_config(page_title="Nolasco Capital", layout="wide", page_icon="🏛️")

ACCENT      = "#185FA5"
SIDEBAR_BG  = "#0F2744"
MAIN_BG     = "#F4F7FB"
CARD_BG     = "#FFFFFF"
BORDER      = "#D0DFF0"
TEXT_PRI    = "#0D1B2A"
TEXT_SEC    = "#5A7A9A"
GREEN       = "#1a7a40"
RED         = "#C0392B"
AMBER       = "#854F0B"
COLOR_TOPS  = ["#185FA5", "#0F6E56", "#378ADD", "#639922", "#D85A30", "#7F77DD"]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

.block-container {{ padding-top: 1.2rem !important; padding-bottom: 0 !important; }}
html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background-color: {MAIN_BG} !important;
    color: {TEXT_PRI};
}}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
    border-right: 1px solid #1a3a5c;
    min-width: 260px !important;
}}
[data-testid="stSidebar"] .stRadio > label {{ display: none; }}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{ padding-top: 1rem; gap: 0.5rem; }}
[data-testid="stSidebar"] .stRadio p {{
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 400 !important;
    color: #4a6f96 !important;
    letter-spacing: 0.02em !important;
    padding-left: 1rem;
    border-left: 3px solid transparent;
    transition: all 0.2s ease;
}}
[data-testid="stSidebar"] .stRadio label[data-checked="true"] p {{
    color: #60B4FF !important;
    font-weight: 500 !important;
    border-left: 3px solid {ACCENT};
    padding-left: 1.2rem;
    background: rgba(96,180,255,0.06);
}}

/* TIPOGRAFÍA */
.brand-header {{
    font-family: 'DM Serif Display', serif;
    font-size: 2rem; color: {TEXT_PRI};
    border-bottom: 2px solid {ACCENT};
    padding-bottom: 0.4rem; margin-bottom: 0.2rem;
}}
.brand-sub {{
    font-size: 0.7rem; letter-spacing: 0.18em;
    text-transform: uppercase; color: {TEXT_SEC};
    margin-bottom: 1.5rem;
}}
.section-title {{
    font-family: 'DM Serif Display', serif;
    font-size: 1.35rem; color: {TEXT_PRI};
    border-left: 3px solid {ACCENT};
    padding-left: 0.7rem; margin: 1.5rem 0 1rem 0;
}}

/* KPI CARDS */
.kpi-card {{
    background: {CARD_BG}; border: 1px solid {BORDER};
    border-radius: 10px; padding: 1.2rem 1.3rem; text-align: left;
}}
.kpi-card.highlight {{
    background: {ACCENT}; border-color: {ACCENT};
}}
.kpi-label {{
    font-size: 0.62rem; letter-spacing: 0.1em;
    text-transform: uppercase; color: {TEXT_SEC}; margin-bottom: 0.4rem;
}}
.kpi-card.highlight .kpi-label {{ color: #B5D4F4; }}
.kpi-value {{
    font-family: 'DM Serif Display', serif;
    font-size: 2rem; line-height: 1; color: {TEXT_PRI};
}}
.kpi-card.highlight .kpi-value {{ color: #fff; }}
.kpi-sub {{ font-size: 0.7rem; color: {TEXT_SEC}; margin-top: 0.3rem; }}
.kpi-card.highlight .kpi-sub {{ color: #B5D4F4; }}

/* ASSET CARDS */
.asset-card {{
    background: {CARD_BG}; border: 1px solid {BORDER};
    border-radius: 10px; overflow: hidden;
}}
.asset-top {{ height: 4px; }}
.asset-body {{ padding: 1rem 1.1rem; }}
.asset-name {{ font-size: 0.82rem; font-weight: 600; color: {TEXT_PRI}; margin-bottom: 2px; }}
.asset-tenant {{ font-size: 0.72rem; color: {TEXT_SEC}; margin-bottom: 0.8rem; }}
.asset-row {{ display: flex; justify-content: space-between; margin-bottom: 4px; }}
.asset-ml {{ font-size: 0.65rem; color: {TEXT_SEC}; text-transform: uppercase; letter-spacing: 0.04em; }}
.asset-mv {{ font-size: 0.82rem; font-weight: 500; }}
.asset-div {{ height: 0.5px; background: {BORDER}; margin: 7px 0; }}
.asset-neto {{ font-size: 1rem; font-weight: 600; color: {TEXT_PRI}; }}
.pill {{
    display: inline-block; font-size: 0.65rem;
    padding: 2px 7px; border-radius: 20px; margin-top: 5px;
}}
.pill-red   {{ background: #FCEBEB; color: #A32D2D; }}
.pill-amber {{ background: #FAEEDA; color: #854F0B; }}
.pill-green {{ background: #EAF3DE; color: #3B6D11; }}

/* STATUS BOXES */
.status-red    {{ background: #FDECEA; border-left: 5px solid {RED};   padding: 1.2rem; border-radius: 6px; }}
.status-yellow {{ background: #FFF9E6; border-left: 5px solid #F39C12; padding: 1.2rem; border-radius: 6px; }}
.status-green  {{ background: #EDF7F1; border-left: 5px solid {GREEN}; padding: 1.2rem; border-radius: 6px; }}

#MainMenu, footer, header {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. MOTOR DE DATOS  (bug fix: force=False)
# ─────────────────────────────────────────────
DB_INMUEBLES   = "nolasco_inmuebles_v10.csv"
DB_MOVIMIENTOS = "nolasco_movimientos_v10.csv"

def inicializar_bd():
    """Solo crea los CSV si NO existen. Nunca sobreescribe datos del usuario."""
    if not os.path.exists(DB_INMUEBLES):
        pd.DataFrame([
            {"Nombre": "Casa Abarqueros",  "Inquilino": "Victor Aguiluz", "Renta": 2200.0, "Renta_Mercado": 2600.0, "Comunidad": 193.76, "Valor_Construccion": 150000.0, "Año_Reforma": 2018, "Año_Construccion": 1975, "Mobiliario": "S", "Tipo": "Casa",  "Ref_Catastral": "", "Titular": "Pedro Nolasco", "M2_Construidos": 180, "Habitaciones": 5, "CP": "18001", "Planta": 0,  "Parking": "N", "Estado": "Reformado"},
            {"Nombre": "Paseo del Salón",  "Inquilino": "Pool Despachos", "Renta": 1591.8, "Renta_Mercado": 1650.0, "Comunidad": 175.18, "Valor_Construccion": 120000.0, "Año_Reforma": 2020, "Año_Construccion": 1990, "Mobiliario": "N", "Tipo": "Piso",  "Ref_Catastral": "", "Titular": "Pedro Nolasco", "M2_Construidos": 130, "Habitaciones": 4, "CP": "18005", "Planta": 3,  "Parking": "S", "Estado": "Bueno"},
            {"Nombre": "Huerto Unidad 1",  "Inquilino": "Alain",          "Renta":  660.0, "Renta_Mercado":  800.0, "Comunidad":  74.62, "Valor_Construccion":  45000.0, "Año_Reforma": 2022, "Año_Construccion": 2005, "Mobiliario": "S", "Tipo": "Piso",  "Ref_Catastral": "", "Titular": "Pedro Nolasco", "M2_Construidos":  60, "Habitaciones": 2, "CP": "18008", "Planta": 1,  "Parking": "N", "Estado": "Reformado"},
            {"Nombre": "Huerto Unidad 2",  "Inquilino": "Laura/Alex",     "Renta":  800.0, "Renta_Mercado":  800.0, "Comunidad":  74.62, "Valor_Construccion":  45000.0, "Año_Reforma": 2022, "Año_Construccion": 2005, "Mobiliario": "S", "Tipo": "Piso",  "Ref_Catastral": "", "Titular": "Pedro Nolasco", "M2_Construidos":  65, "Habitaciones": 2, "CP": "18008", "Planta": 2,  "Parking": "N", "Estado": "Reformado"},
            {"Nombre": "Huerto Unidad 3",  "Inquilino": "Jose Manuel",    "Renta":  850.0, "Renta_Mercado":  800.0, "Comunidad":  74.63, "Valor_Construccion":  45000.0, "Año_Reforma": 2021, "Año_Construccion": 2005, "Mobiliario": "S", "Tipo": "Piso",  "Ref_Catastral": "", "Titular": "Pedro Nolasco", "M2_Construidos":  68, "Habitaciones": 3, "CP": "18008", "Planta": 3,  "Parking": "N", "Estado": "Bueno"},
            {"Nombre": "Huerto Unidad 4",  "Inquilino": "Pendiente",      "Renta":  600.0, "Renta_Mercado":  800.0, "Comunidad":  74.62, "Valor_Construccion":  45000.0, "Año_Reforma": 2024, "Año_Construccion": 2005, "Mobiliario": "S", "Tipo": "Piso",  "Ref_Catastral": "", "Titular": "Pedro Nolasco", "M2_Construidos":  62, "Habitaciones": 2, "CP": "18008", "Planta": 4,  "Parking": "N", "Estado": "Reformado"},
        ]).to_csv(DB_INMUEBLES, index=False)

    if not os.path.exists(DB_MOVIMIENTOS):
        pd.DataFrame([
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Renta Mensual", "Categoría": "Ingresos",  "Tipo": "Ingreso", "Importe": 2200.00, "Deducible": "N"},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Comunidad",     "Categoría": "Comunidad", "Tipo": "Gasto",   "Importe":  193.76, "Deducible": "S"},
        ]).to_csv(DB_MOVIMIENTOS, index=False)

inicializar_bd()

df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)

# ─────────────────────────────────────────────
# 3. NAVEGACIÓN
# ─────────────────────────────────────────────
if "menu" not in st.session_state:
    st.session_state.menu = "Torre de Control"

PAGES = [
    ("📊", "Torre de Control"),
    ("🏠", "Fichas (Benchmark)"),
    ("🤖", "Auditoría IA"),
    ("📝", "Diario Contable"),
    ("📂", "Datos de la Cartera"),
]

with st.sidebar:
    st.markdown(f"""
    <div style='padding:1.6rem 1.4rem 1rem;'>
        <div style='font-family:"DM Serif Display",serif;font-size:2rem;color:#60B4FF;line-height:1;'>NOLASCO</div>
        <div style='font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:#5a8aaa;margin-top:4px;'>Capital · Granada</div>
    </div>
    <hr style='border:0;border-top:1px solid #1a3a5c;margin:0 0 0.8rem 0;'>
    """, unsafe_allow_html=True)

    for icon, page in PAGES:
        active = st.session_state.menu == page
        bg     = "rgba(96,180,255,0.12)" if active else "transparent"
        color  = "#FFFFFF" if active else "#A8C4E0"
        weight = "600" if active else "400"
        border = f"3px solid #60B4FF" if active else "3px solid transparent"
        st.markdown(f"""
        <div style='border-left:{border};background:{bg};padding:0.7rem 1.4rem;
                    margin-bottom:2px;cursor:pointer;border-radius:0 6px 6px 0;'>
            <span style='font-size:0.88rem;font-weight:{weight};color:{color};
                         font-family:"DM Sans",sans-serif;letter-spacing:0.01em;'>
                {icon} {page}
            </span>
        </div>""", unsafe_allow_html=True)
        if st.button(page, key=f"nav_{page}", use_container_width=True):
            st.session_state.menu = page
            st.rerun()

    n_activos = len(df_inm)
    st.markdown(f"""
    <div style='padding:1rem 1.4rem;font-size:0.7rem;color:#3a6080;margin-top:1rem;'>
        {n_activos} activos · {datetime.now().strftime("%b %Y")}
    </div>""", unsafe_allow_html=True)

menu = st.session_state.menu

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def bench_pill(desv):
    if desv < -15:  return "pill-red",   "🔴"
    if desv < -5:   return "pill-amber", "🟡"
    return "pill-green", "🟢"

# ══════════════════════════════════════════════
# TORRE DE CONTROL
# ══════════════════════════════════════════════
if menu == "Torre de Control":
    st.markdown('<div class="brand-header">Torre de Control</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Rendimiento consolidado · Cartera Nolasco</div>', unsafe_allow_html=True)

    ing_b   = df_inm["Renta"].sum()
    # Bug fix: gastos = comunidad + movimientos de gasto (sin duplicar comunidad del diario)
    gas_mov = df_mov[df_mov["Tipo"] == "Gasto"]["Importe"].sum()
    gas_com = df_inm["Comunidad"].sum()
    # Solo sumamos comunidad del CSV maestro; el diario contable puede tener entradas adicionales
    gastos  = gas_com + df_mov[(df_mov["Tipo"] == "Gasto") & (df_mov["Categoría"] != "Comunidad")]["Importe"].sum()
    neto    = ing_b - gastos
    margen  = (neto / ing_b * 100) if ing_b > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Ingresos Brutos</div>
        <div class="kpi-value" style="color:{GREEN};">{ing_b:,.0f} €</div>
        <div class="kpi-sub">Renta mensual total</div>
    </div>''', unsafe_allow_html=True)
    c2.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Gastos Operativos</div>
        <div class="kpi-value" style="color:{RED};">−{gastos:,.0f} €</div>
        <div class="kpi-sub">Comunidad + registrados</div>
    </div>''', unsafe_allow_html=True)
    c3.markdown(f'''<div class="kpi-card highlight">
        <div class="kpi-label">Beneficio Neto</div>
        <div class="kpi-value">{neto:,.0f} €</div>
        <div class="kpi-sub">Margen {margen:.1f}%</div>
    </div>''', unsafe_allow_html=True)

    # ── Tarjetas por activo ──
    st.markdown('<div class="section-title">Rentabilidad por Activo</div>', unsafe_allow_html=True)
    cols = st.columns(len(df_inm))
    for i, row in df_inm.iterrows():
        g_esp  = df_mov[(df_mov["Apartamento"] == row["Nombre"]) & (df_mov["Tipo"] == "Gasto") & (df_mov["Categoría"] != "Comunidad")]["Importe"].sum()
        gastos_u = row["Comunidad"] + g_esp
        neto_u   = row["Renta"] - gastos_u
        desv     = (row["Renta"] - row["Renta_Mercado"]) / row["Renta_Mercado"] * 100
        pill_cls, _ = bench_pill(desv)
        color_top = COLOR_TOPS[i % len(COLOR_TOPS)]
        with cols[i]:
            st.markdown(f'''
            <div class="asset-card">
                <div class="asset-top" style="background:{color_top};"></div>
                <div class="asset-body">
                    <div class="asset-name">{row["Nombre"]}</div>
                    <div class="asset-tenant">{row["Inquilino"]}</div>
                    <div class="asset-row">
                        <span class="asset-ml">Renta</span>
                        <span class="asset-mv" style="color:{GREEN};">+{row["Renta"]:,.0f}€</span>
                    </div>
                    <div class="asset-row">
                        <span class="asset-ml">Gastos</span>
                        <span class="asset-mv" style="color:{RED};">−{gastos_u:,.0f}€</span>
                    </div>
                    <div class="asset-div"></div>
                    <div class="asset-row">
                        <span class="asset-ml">Neto</span>
                        <span class="asset-neto">{neto_u:,.0f}€</span>
                    </div>
                    <span class="pill {pill_cls}">{desv:+.1f}% mercado</span>
                </div>
            </div>''', unsafe_allow_html=True)

    # ── Paneles inferiores ──
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">Composición de Rentas</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Bar(
            x=df_inm["Renta"], y=df_inm["Nombre"],
            orientation="h",
            marker_color=COLOR_TOPS[:len(df_inm)],
            text=[f"{r:,.0f} €" for r in df_inm["Renta"]],
            textposition="outside",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=60, t=10, b=10), height=280,
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False),
            font=dict(family="DM Sans", size=12),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Lucro Cesante Anual</div>', unsafe_allow_html=True)
        total_lc = 0
        for _, row in df_inm.iterrows():
            perdida_m = max(0, row["Renta_Mercado"] - row["Renta"])
            perdida_a = perdida_m * 12
            total_lc += perdida_a
            if perdida_a > 0:
                desv = (row["Renta"] - row["Renta_Mercado"]) / row["Renta_Mercado"] * 100
                pill_cls, _ = bench_pill(desv)
                color_val = RED if desv < -15 else AMBER
                st.markdown(f'''
                <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:9px 12px;background:{CARD_BG};border:1px solid {BORDER};
                            border-radius:8px;margin-bottom:6px;">
                    <span style="font-size:0.8rem;color:{TEXT_SEC};">{row["Nombre"]}</span>
                    <span style="font-size:0.9rem;font-weight:600;color:{color_val};">−{perdida_a:,.0f} €/año</span>
                </div>''', unsafe_allow_html=True)
        st.markdown(f'''
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:11px 14px;background:{ACCENT};border-radius:8px;margin-top:4px;">
            <span style="font-size:0.72rem;font-weight:500;color:#B5D4F4;text-transform:uppercase;letter-spacing:0.06em;">Total pérdida anual</span>
            <span style="font-size:1.3rem;font-weight:600;color:#fff;">−{total_lc:,.0f} €</span>
        </div>''', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# FICHAS BENCHMARK
# ══════════════════════════════════════════════
elif menu == "Fichas (Benchmark)":
    st.markdown('<div class="brand-header">Benchmark y Lucro Cesante</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Análisis de mercado por activo</div>', unsafe_allow_html=True)

    sel = st.selectbox("Inmueble a auditar:", df_inm["Nombre"].tolist())
    f   = df_inm[df_inm["Nombre"] == sel].iloc[0]

    renta_act = f["Renta"]
    renta_mer = f["Renta_Mercado"]
    desv      = (renta_act - renta_mer) / renta_mer * 100
    perdida_m = max(0, renta_mer - renta_act)
    perdida_a = perdida_m * 12

    # ── Motor de tasación por CP ──
    PRECIOS_CP = {
        "18001": 12.5,  # Centro / Realejo
        "18002": 11.8,  # Sagrario / San Ildefonso
        "18003": 10.2,  # Ronda / Arabial
        "18004": 10.8,  # Campus / Fígares
        "18005": 11.2,  # Genil / Paseo del Salón
        "18006": 10.0,  # Zaidín norte
        "18007": 9.5,   # Zaidín sur
        "18008": 10.4,  # Chana / Pajaritos
        "18009": 8.2,   # Almanjáyar
        "18010": 9.8,   # Norte / Cartuja
        "18011": 10.1,  # Beiro
        "18012": 9.6,   # Ogíjares / sur
        "18013": 9.0,   # Albolote / norte provincia
        "18014": 9.3,   # Este
        "18015": 8.8,   # Peripheral
    }
    cp = str(f.get("CP", "18005"))
    precio_m2_base = PRECIOS_CP.get(cp, 10.0)
    m2 = float(f.get("M2_Construidos", 80))

    # Ajustes
    adj_mob    = 1.05 if f.get("Mobiliario") == "S" else 1.0
    adj_park   = 1.04 if f.get("Parking")    == "S" else 1.0
    adj_estado = {"Reformado": 1.08, "Bueno": 1.0, "Regular": 0.92}.get(f.get("Estado", "Bueno"), 1.0)
    planta     = int(f.get("Planta", 1))
    adj_planta = 0.95 if planta == 0 else (1.03 if planta >= 3 else 1.0)
    hab        = int(f.get("Habitaciones", 2))
    adj_hab    = 1.05 if hab >= 4 else (0.97 if hab == 1 else 1.0)

    renta_tasada = precio_m2_base * m2 * adj_mob * adj_park * adj_estado * adj_planta * adj_hab
    renta_mer    = round(renta_tasada, 2)

    # Actualizar Renta_Mercado con la tasación calculada
    # (se usa para el resto de cálculos de esta ficha)

    # ── Gastos reales (bug fix: comunidad solo del CSV maestro, sin duplicar del diario) ──
    df_g_ficha = df_mov[
        (df_mov["Apartamento"] == sel) &
        (df_mov["Tipo"] == "Gasto") &
        (df_mov["Categoría"] != "Comunidad")   # evita duplicado
    ]
    gastos_u   = f["Comunidad"] + df_g_ficha["Importe"].sum()
    rent_bruta = (renta_act / f["Valor_Construccion"] * 100) if f["Valor_Construccion"] > 0 else 0
    rent_neta  = ((renta_act - gastos_u) * 12 / f["Valor_Construccion"] * 100) if f["Valor_Construccion"] > 0 else 0

    # ── Fila KPIs superior ──
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Renta Actual</div>
        <div class="kpi-value" style="color:{GREEN};">{renta_act:,.0f} €</div>
        <div class="kpi-sub">mensual</div></div>''', unsafe_allow_html=True)
    k2.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Renta Mercado</div>
        <div class="kpi-value" style="color:{TEXT_PRI};">{renta_mer:,.0f} €</div>
        <div class="kpi-sub">estimada</div></div>''', unsafe_allow_html=True)
    k3.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Rentabilidad Bruta</div>
        <div class="kpi-value" style="color:{ACCENT};">{rent_bruta:.1f}%</div>
        <div class="kpi-sub">sobre valor construcción</div></div>''', unsafe_allow_html=True)
    k4.markdown(f'''<div class="kpi-card highlight">
        <div class="kpi-label">Rentabilidad Neta</div>
        <div class="kpi-value">{rent_neta:.1f}%</div>
        <div class="kpi-sub">anual tras gastos</div></div>''', unsafe_allow_html=True)

    # ── Comparativa visual + estatus ──
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title">Comparativa Renta Actual vs Mercado</div>', unsafe_allow_html=True)
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=["Renta Actual", "Renta Mercado"],
            y=[renta_act, renta_mer],
            marker_color=[ACCENT, "#D0DFF0"],
            text=[f"{renta_act:,.0f} €", f"{renta_mer:,.0f} €"],
            textposition="outside",
            width=0.4,
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10), height=240,
            yaxis=dict(showgrid=False, visible=False),
            xaxis=dict(showgrid=False),
            font=dict(family="DM Sans", size=13),
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.markdown('<div class="section-title">Estatus de Mercado</div>', unsafe_allow_html=True)
        if desv < -15:   clase, msg, icon = "status-red",    "Rentabilidad Crítica", "🔴"
        elif desv < -5:  clase, msg, icon = "status-yellow", "Margen de Mejora",     "🟡"
        else:            clase, msg, icon = "status-green",  "Activo en Mercado",    "🟢"
        lucro_html = ""
        if perdida_a > 0:
            lucro_html = f"""
            <div style="margin-top:12px;padding-top:12px;border-top:1px dashed rgba(0,0,0,0.15);">
                <span style="font-size:0.88rem;">
                    <b>💸 Lucro Cesante:</b><br>
                    Pérdida mensual: <b>{perdida_m:,.2f} €</b><br>
                    Pérdida anualizada: <b style="color:{RED};font-size:1.15rem;">{perdida_a:,.2f} €/año</b>
                </span>
            </div>"""
        st.markdown(f'<div class="{clase}"><b style="font-size:1.1rem;">{icon} {msg}</b><br>Desviación: <b>{desv:.1f}%</b>{lucro_html}</div>', unsafe_allow_html=True)

    # ── Simulador de subida de renta ──
    st.markdown('<div class="section-title">Simulador de Subida de Renta</div>', unsafe_allow_html=True)
    nueva_renta = st.slider(
        "Ajusta la renta mensual (€)",
        min_value=int(renta_act * 0.8),
        max_value=int(renta_mer * 1.2),
        value=int(renta_act),
        step=25,
    )
    ganancia_m = nueva_renta - renta_act
    ganancia_a = ganancia_m * 12
    nueva_neta = ((nueva_renta - gastos_u) * 12 / f["Valor_Construccion"] * 100) if f["Valor_Construccion"] > 0 else 0
    s1, s2, s3 = st.columns(3)
    s1.metric("Nueva Renta",         f"{nueva_renta:,.0f} €/mes", delta=f"{ganancia_m:+.0f} €")
    s2.metric("Impacto Anual",       f"{ganancia_a:+,.0f} €/año")
    s3.metric("Nueva Rent. Neta",    f"{nueva_neta:.1f}%", delta=f"{nueva_neta - rent_neta:+.1f}%")

    # ── Comparativa todos los activos ──
    st.markdown('<div class="section-title">Comparativa de Activos — Renta vs Mercado</div>', unsafe_allow_html=True)
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        name="Renta Actual", x=df_inm["Nombre"], y=df_inm["Renta"],
        marker_color=ACCENT, text=[f"{r:,.0f}€" for r in df_inm["Renta"]],
        textposition="outside",
    ))
    fig_comp.add_trace(go.Bar(
        name="Renta Mercado", x=df_inm["Nombre"], y=df_inm["Renta_Mercado"],
        marker_color="#D0DFF0", text=[f"{r:,.0f}€" for r in df_inm["Renta_Mercado"]],
        textposition="outside",
    ))
    fig_comp.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10), height=300,
        yaxis=dict(showgrid=False, visible=False),
        xaxis=dict(showgrid=False),
        font=dict(family="DM Sans", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # ── Tabla gastos (bug fix) ──
    st.markdown('<div class="section-title">Análisis de Gastos Reales</div>', unsafe_allow_html=True)
    res = pd.concat([
        pd.DataFrame([{"Concepto": "Comunidad", "Importe": f["Comunidad"], "Deducible": "S"}]),
        df_g_ficha[["Concepto", "Importe", "Deducible"]]
    ])
    st.dataframe(res.style.format({"Importe": "{:,.2f} €"}), hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════
# AUDITORÍA IA  (lógica dinámica por Año_Reforma)
# ══════════════════════════════════════════════
elif menu == "Auditoría IA":
    st.markdown('<div class="brand-header">Informe de Mantenimiento</div>', unsafe_allow_html=True)
elif menu == "Diario Contable":

    año_actual = datetime.now().year
    for i, row in df_inm.reset_index().iterrows():
        antiguedad = año_actual - int(row.get("Año_Reforma", año_actual))
        st.markdown(f"### 📍 {row['Nombre']}")

        if antiguedad >= 8:
            st.error(f"⚠️ Reforma hace {antiguedad} años. Revisión estructural recomendada: instalación eléctrica, fontanería y caldera.")
        elif antiguedad >= 5:
            st.warning(f"🔧 Reforma hace {antiguedad} años. Revisión preventiva recomendada en los próximos 6 meses.")
        elif antiguedad >= 3:
            st.info(f"📋 Reforma hace {antiguedad} años. Estado óptimo. Próxima revisión sugerida en 12 meses.")
        else:
            st.success(f"✅ Reforma reciente ({antiguedad} años). Sin acciones necesarias.")

        cols_a = st.columns(3)
        cols_a[0].metric("Año de Reforma", int(row.get("Año_Reforma", "-")))
        cols_a[1].metric("Antigüedad",     f"{antiguedad} años")
        cols_a[2].metric("Mobiliario",     "Sí" if row.get("Mobiliario") == "S" else "No")

        if i < len(df_inm) - 1:
            st.markdown(f"<hr style='border:0;border-top:1px solid {BORDER};margin:1rem 0;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# DIARIO CONTABLE
# ══════════════════════════════════════════════
elif "Diario" in menu:
    st.markdown('<div class="brand-header">Registro de Operaciones</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Diario contable dinámico</div>', unsafe_allow_html=True)

    l_inm = df_inm["Nombre"].tolist() + ["Global"]
    l_cat = ["Ingresos","Financiero","Tributario","Suministros","Seguros","Mantenimiento","Estructura","Comunidad","Otros"]
    l_con = ["Renta Mensual","Hipoteca (Intereses)","Hipoteca (Capital)","IBI","Comunidad Ordinaria","Seguro Hogar","Seguro Vida","Luz","Agua","Reparación","Sueldo Pedro"]

    config = {
        "Apartamento": st.column_config.SelectboxColumn("Inmueble",   options=l_inm, required=True),
        "Concepto":    st.column_config.SelectboxColumn("Concepto",   options=l_con, required=True),
        "Categoría":   st.column_config.SelectboxColumn("Categoría",  options=l_cat, required=True),
        "Tipo":        st.column_config.SelectboxColumn("Tipo",       options=["Ingreso","Gasto"], required=True),
        "Deducible":   st.column_config.SelectboxColumn("Fiscal",     options=["S","N"], required=True),
        "Importe":     st.column_config.NumberColumn("Importe (€)",   format="%.2f", min_value=0),
    }
    df_ed  = st.data_editor(df_mov, num_rows="dynamic", use_container_width=True, hide_index=True, column_config=config)
    t_ing  = df_ed[df_ed["Tipo"] == "Ingreso"]["Importe"].sum()
    t_gas  = df_ed[df_ed["Tipo"] == "Gasto"]["Importe"].sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("Ingresos Registrados", f"{t_ing:,.2f} €")
    m2.metric("Gastos Registrados",   f"−{t_gas:,.2f} €")
    m3.metric("Balance Total",        f"{t_ing - t_gas:,.2f} €")

    if st.button("💾 Guardar Cambios"):
        df_ed.to_csv(DB_MOVIMIENTOS, index=False)
        st.success("✓ Operaciones guardadas correctamente.")
        st.rerun()

# ══════════════════════════════════════════════
# DATOS DE LA CARTERA
# ══════════════════════════════════════════════
elif menu == "Datos de la Cartera":
    st.markdown('<div class="brand-header">Datos de la Cartera</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Parámetros maestros y copias de seguridad</div>', unsafe_allow_html=True)
    st.info("ℹ️ Edita aquí los parámetros maestros. Actualiza 'Renta_Mercado' para recalcular el Benchmark.")

    df_inm_ed = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True, hide_index=True)
    if st.button("✅ Actualizar Cartera"):
        df_inm_ed.to_csv(DB_INMUEBLES, index=False)
        st.success("✓ Datos actualizados.")
        st.rerun()

    st.markdown('<div class="section-title">Copias de Seguridad</div>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        with open(DB_INMUEBLES, "rb") as f_i:
            st.download_button("📥 Descargar Inmuebles",   f_i, "nolasco_inmuebles.csv",   "text/csv")
    with b2:
        with open(DB_MOVIMIENTOS, "rb") as f_m:
            st.download_button("📥 Descargar Movimientos", f_m, "nolasco_movimientos.csv", "text/csv")
