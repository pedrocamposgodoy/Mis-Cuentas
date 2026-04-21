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

/* OCULTAR BOTONES SIDEBAR — invisibles pero clickables */
[data-testid="stSidebar"] .stButton button {{
    position: absolute !important;
    opacity: 0 !important;
    height: 44px !important;
    margin-top: -44px !important;
    width: 100% !important;
    cursor: pointer !important;
    z-index: 999 !important;
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
.kpi-card.highlight {{ background: {ACCENT}; border-color: {ACCENT}; }}
.kpi-label {{
    font-size: 0.62rem; letter-spacing: 0.1em;
    text-transform: uppercase; color: {TEXT_SEC}; margin-bottom: 0.4rem;
}}
.kpi-card.highlight .kpi-label {{ color: #B5D4F4; }}
.kpi-value {{ font-family: 'DM Serif Display', serif; font-size: 2rem; line-height: 1; color: {TEXT_PRI}; }}
.kpi-card.highlight .kpi-value {{ color: #fff; }}
.kpi-sub {{ font-size: 0.7rem; color: {TEXT_SEC}; margin-top: 0.3rem; }}
.kpi-card.highlight .kpi-sub {{ color: #B5D4F4; }}

/* ASSET CARDS */
.asset-card {{ background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 10px; overflow: hidden; }}
.asset-top {{ height: 4px; }}
.asset-body {{ padding: 1rem 1.1rem; }}
.asset-name {{ font-size: 0.82rem; font-weight: 600; color: {TEXT_PRI}; margin-bottom: 2px; }}
.asset-tenant {{ font-size: 0.72rem; color: {TEXT_SEC}; margin-bottom: 0.8rem; }}
.asset-row {{ display: flex; justify-content: space-between; margin-bottom: 4px; }}
.asset-ml {{ font-size: 0.65rem; color: {TEXT_SEC}; text-transform: uppercase; letter-spacing: 0.04em; }}
.asset-mv {{ font-size: 0.82rem; font-weight: 500; }}
.asset-div {{ height: 0.5px; background: {BORDER}; margin: 7px 0; }}
.asset-neto {{ font-size: 1rem; font-weight: 600; color: {TEXT_PRI}; }}
.pill {{ display: inline-block; font-size: 0.65rem; padding: 2px 7px; border-radius: 20px; margin-top: 5px; }}
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
# 2. MOTOR DE DATOS
# ─────────────────────────────────────────────
DB_INMUEBLES   = "nolasco_inmuebles_v10.csv"
DB_MOVIMIENTOS = "nolasco_movimientos_v10.csv"

def inicializar_bd():
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
# 3. NAVEGACIÓN CON BOTONES
# ─────────────────────────────────────────────
if "menu" not in st.session_state:
    st.session_state.menu = "Torre de Control"

PAGES = [
    ("📊", "Torre de Control"),
    ("🏠", "Fichas (Benchmark)"),
    ("🤖", "Auditoría IA"),
    ("📝", "Diario Contable"),
    ("⚡", "Suministros"),
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
        border = "3px solid #60B4FF" if active else "3px solid transparent"
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

PRECIOS_CP = {
    "18001": 12.5, "18002": 11.8, "18003": 10.2, "18004": 10.8,
    "18005": 11.2, "18006": 10.0, "18007": 9.5,  "18008": 10.4,
    "18009": 8.2,  "18010": 9.8,  "18011": 10.1, "18012": 9.6,
    "18013": 9.0,  "18014": 9.3,  "18015": 8.8,
}

def tasacion(row):
    precio_m2 = PRECIOS_CP.get(str(row.get("CP", "18005")), 10.0)
    m2        = float(row.get("M2_Construidos", 80))
    adj_mob   = 1.05 if row.get("Mobiliario") == "S" else 1.0
    adj_park  = 1.04 if row.get("Parking")    == "S" else 1.0
    adj_est   = {"Reformado": 1.08, "Bueno": 1.0, "Regular": 0.92}.get(row.get("Estado", "Bueno"), 1.0)
    planta    = int(row.get("Planta", 1))
    adj_pl    = 0.95 if planta == 0 else (1.03 if planta >= 3 else 1.0)
    hab       = int(row.get("Habitaciones", 2))
    adj_hab   = 1.05 if hab >= 4 else (0.97 if hab == 1 else 1.0)
    return round(precio_m2 * m2 * adj_mob * adj_park * adj_est * adj_pl * adj_hab, 2)

# ══════════════════════════════════════════════
# TORRE DE CONTROL
# ══════════════════════════════════════════════
if menu == "Torre de Control":
    st.markdown('<div class="brand-header">Torre de Control</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Rendimiento consolidado · Cartera Nolasco</div>', unsafe_allow_html=True)

    ing_b   = df_inm["Renta"].sum()
    gas_com = df_inm["Comunidad"].sum()
    gastos  = gas_com + df_mov[(df_mov["Tipo"] == "Gasto") & (df_mov["Categoría"] != "Comunidad")]["Importe"].sum()
    neto    = ing_b - gastos
    margen  = (neto / ing_b * 100) if ing_b > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Ingresos Brutos</div>
        <div class="kpi-value" style="color:{GREEN};">{ing_b:,.0f} €</div>
        <div class="kpi-sub">Renta mensual total</div></div>''', unsafe_allow_html=True)
    c2.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Gastos Operativos</div>
        <div class="kpi-value" style="color:{RED};">−{gastos:,.0f} €</div>
        <div class="kpi-sub">Comunidad + registrados</div></div>''', unsafe_allow_html=True)
    c3.markdown(f'''<div class="kpi-card highlight">
        <div class="kpi-label">Beneficio Neto</div>
        <div class="kpi-value">{neto:,.0f} €</div>
        <div class="kpi-sub">Margen {margen:.1f}%</div></div>''', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Rentabilidad por Activo</div>', unsafe_allow_html=True)
    cols = st.columns(len(df_inm))
    for i, row in df_inm.iterrows():
        g_esp    = df_mov[(df_mov["Apartamento"] == row["Nombre"]) & (df_mov["Tipo"] == "Gasto") & (df_mov["Categoría"] != "Comunidad")]["Importe"].sum()
        gastos_u = row["Comunidad"] + g_esp
        neto_u   = row["Renta"] - gastos_u
        renta_mer = tasacion(row)
        desv     = (row["Renta"] - renta_mer) / renta_mer * 100
        pill_cls, _ = bench_pill(desv)
        with cols[i]:
            st.markdown(f'''
            <div class="asset-card">
                <div class="asset-top" style="background:{COLOR_TOPS[i % len(COLOR_TOPS)]};"></div>
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

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-title">Composición de Rentas</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Bar(
            x=df_inm["Renta"], y=df_inm["Nombre"], orientation="h",
            marker_color=COLOR_TOPS[:len(df_inm)],
            text=[f"{r:,.0f} €" for r in df_inm["Renta"]], textposition="outside",
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
            renta_mer = tasacion(row)
            perdida_a = max(0, renta_mer - row["Renta"]) * 12
            total_lc += perdida_a
            if perdida_a > 0:
                desv = (row["Renta"] - renta_mer) / renta_mer * 100
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
    renta_mer = tasacion(f)
    desv      = (renta_act - renta_mer) / renta_mer * 100
    perdida_m = max(0, renta_mer - renta_act)
    perdida_a = perdida_m * 12

    df_g_ficha = df_mov[
        (df_mov["Apartamento"] == sel) &
        (df_mov["Tipo"] == "Gasto") &
        (df_mov["Categoría"] != "Comunidad")
    ]
    gastos_u   = f["Comunidad"] + df_g_ficha["Importe"].sum()
    rent_bruta = (renta_act * 12 / f["Valor_Construccion"] * 100) if f["Valor_Construccion"] > 0 else 0
    rent_neta  = ((renta_act - gastos_u) * 12 / f["Valor_Construccion"] * 100) if f["Valor_Construccion"] > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Renta Actual</div>
        <div class="kpi-value" style="color:{GREEN};">{renta_act:,.0f} €</div>
        <div class="kpi-sub">mensual</div></div>''', unsafe_allow_html=True)
    k2.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Renta Tasada</div>
        <div class="kpi-value" style="color:{TEXT_PRI};">{renta_mer:,.0f} €</div>
        <div class="kpi-sub">motor CP + características</div></div>''', unsafe_allow_html=True)
    k3.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Rentabilidad Bruta</div>
        <div class="kpi-value" style="color:{ACCENT};">{rent_bruta:.1f}%</div>
        <div class="kpi-sub">sobre valor construcción</div></div>''', unsafe_allow_html=True)
    k4.markdown(f'''<div class="kpi-card highlight">
        <div class="kpi-label">Rentabilidad Neta</div>
        <div class="kpi-value">{rent_neta:.1f}%</div>
        <div class="kpi-sub">anual tras gastos</div></div>''', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title">Renta Actual vs Tasada</div>', unsafe_allow_html=True)
        fig_bar = go.Figure(go.Bar(
            x=["Renta Actual", "Renta Tasada"],
            y=[renta_act, renta_mer],
            marker_color=[ACCENT, "#D0DFF0"],
            text=[f"{renta_act:,.0f} €", f"{renta_mer:,.0f} €"],
            textposition="outside", width=0.4,
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10), height=240,
            yaxis=dict(showgrid=False, visible=False),
            xaxis=dict(showgrid=False),
            font=dict(family="DM Sans", size=13), showlegend=False,
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

    st.markdown('<div class="section-title">Simulador de Subida de Renta</div>', unsafe_allow_html=True)
    nueva_renta = st.slider("Ajusta la renta mensual (€)",
        min_value=int(renta_act * 0.8), max_value=int(renta_mer * 1.2),
        value=int(renta_act), step=25)
    ganancia_m  = nueva_renta - renta_act
    ganancia_a  = ganancia_m * 12
    nueva_neta  = ((nueva_renta - gastos_u) * 12 / f["Valor_Construccion"] * 100) if f["Valor_Construccion"] > 0 else 0
    s1, s2, s3 = st.columns(3)
    s1.metric("Nueva Renta",      f"{nueva_renta:,.0f} €/mes", delta=f"{ganancia_m:+.0f} €")
    s2.metric("Impacto Anual",    f"{ganancia_a:+,.0f} €/año")
    s3.metric("Nueva Rent. Neta", f"{nueva_neta:.1f}%", delta=f"{nueva_neta - rent_neta:+.1f}%")

    st.markdown('<div class="section-title">Comparativa de Activos — Renta vs Tasación</div>', unsafe_allow_html=True)
    rentas_tasadas = [tasacion(r) for _, r in df_inm.iterrows()]
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name="Renta Actual", x=df_inm["Nombre"], y=df_inm["Renta"],
        marker_color=ACCENT, text=[f"{r:,.0f}€" for r in df_inm["Renta"]], textposition="outside"))
    fig_comp.add_trace(go.Bar(name="Renta Tasada", x=df_inm["Nombre"], y=rentas_tasadas,
        marker_color="#D0DFF0", text=[f"{r:,.0f}€" for r in rentas_tasadas], textposition="outside"))
    fig_comp.update_layout(
        barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10), height=300,
        yaxis=dict(showgrid=False, visible=False), xaxis=dict(showgrid=False),
        font=dict(family="DM Sans", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown('<div class="section-title">Análisis de Gastos Reales</div>', unsafe_allow_html=True)
    res = pd.concat([
        pd.DataFrame([{"Concepto": "Comunidad", "Importe": f["Comunidad"], "Deducible": "S"}]),
        df_g_ficha[["Concepto", "Importe", "Deducible"]]
    ])
    st.dataframe(res.style.format({"Importe": "{:,.2f} €"}), hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════
# AUDITORÍA IA
# ══════════════════════════════════════════════
elif menu == "Auditoría IA":
    st.markdown('<div class="brand-header">Informe de Mantenimiento</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Alertas preventivas basadas en antigüedad de reforma</div>', unsafe_allow_html=True)

    año_actual = datetime.now().year
    for i, row in df_inm.reset_index().iterrows():
        antiguedad = año_actual - int(row.get("Año_Reforma", año_actual))
        st.markdown(f"### 📍 {row['Nombre']}")
        if antiguedad >= 8:
            st.error(f"⚠️ Reforma hace {antiguedad} años. Revisión estructural recomendada.")
        elif antiguedad >= 5:
            st.warning(f"🔧 Reforma hace {antiguedad} años. Revisión preventiva en los próximos 6 meses.")
        elif antiguedad >= 3:
            st.info(f"📋 Reforma hace {antiguedad} años. Próxima revisión en 12 meses.")
        else:
            st.success(f"✅ Reforma reciente ({antiguedad} años). Sin acciones necesarias.")
        cols_a = st.columns(3)
        cols_a[0].metric("Año Reforma",  int(row.get("Año_Reforma", "-")))
        cols_a[1].metric("Antigüedad",   f"{antiguedad} años")
        cols_a[2].metric("Mobiliario",   "Sí" if row.get("Mobiliario") == "S" else "No")
        if i < len(df_inm) - 1:
            st.markdown(f"<hr style='border:0;border-top:1px solid {BORDER};margin:1rem 0;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# DIARIO CONTABLE
# ══════════════════════════════════════════════
elif menu == "Diario Contable":
    st.markdown('<div class="brand-header">Registro de Operaciones</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Diario contable dinámico</div>', unsafe_allow_html=True)

    l_inm = df_inm["Nombre"].tolist() + ["Global"]
    l_cat = ["Ingresos","Financiero","Tributario","Suministros","Seguros","Mantenimiento","Estructura","Comunidad","Otros"]
    l_con = ["Renta Mensual","Hipoteca (Intereses)","Hipoteca (Capital)","IBI","Comunidad Ordinaria","Seguro Hogar","Seguro Vida","Luz","Agua","Reparación","Sueldo Pedro"]

    config = {
        "Apartamento": st.column_config.SelectboxColumn("Inmueble",  options=l_inm, required=True),
        "Concepto":    st.column_config.SelectboxColumn("Concepto",  options=l_con, required=True),
        "Categoría":   st.column_config.SelectboxColumn("Categoría", options=l_cat, required=True),
        "Tipo":        st.column_config.SelectboxColumn("Tipo",      options=["Ingreso","Gasto"], required=True),
        "Deducible":   st.column_config.SelectboxColumn("Fiscal",    options=["S","N"], required=True),
        "Importe":     st.column_config.NumberColumn("Importe (€)",  format="%.2f", min_value=0),
    }
    df_ed = st.data_editor(df_mov, num_rows="dynamic", use_container_width=True, hide_index=True, column_config=config)
    t_ing = df_ed[df_ed["Tipo"] == "Ingreso"]["Importe"].sum()
    t_gas = df_ed[df_ed["Tipo"] == "Gasto"]["Importe"].sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("Ingresos Registrados", f"{t_ing:,.2f} €")
    m2.metric("Gastos Registrados",   f"−{t_gas:,.2f} €")
    m3.metric("Balance Total",        f"{t_ing - t_gas:,.2f} €")

    if st.button("💾 Guardar Cambios"):
        df_ed.to_csv(DB_MOVIMIENTOS, index=False)
        st.success("✓ Operaciones guardadas.")
        st.rerun()
# ══════════════════════════════════════════════
# SUMINISTROS — BLOQUE 3
# ══════════════════════════════════════════════
elif menu == "Suministros":
    st.markdown('<div class="brand-header">Optimización de Suministros</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Auditoría de potencia eléctrica · Comparador tarifario</div>', unsafe_allow_html=True)

    inmueble_sel = st.selectbox("Selecciona inmueble:", df_inm["Nombre"].tolist())
    f = df_inm[df_inm["Nombre"] == inmueble_sel].iloc[0]
    hab = int(f.get("Habitaciones", 2))
    tipo = f.get("Tipo", "Piso")

    # ── AUDITORÍA DE POTENCIA ──────────────────
    st.markdown('<div class="section-title">⚡ Auditoría de Potencia Contratada</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        potencia_actual = st.number_input("Potencia contratada actualmente (kW)", min_value=1.0, max_value=30.0, value=4.4, step=0.1)
        tiene_ac        = st.checkbox("¿Aire acondicionado?", value=True)
        tiene_vitro     = st.checkbox("¿Vitrocerámica/inducción?", value=True)
        tiene_termo     = st.checkbox("¿Termo eléctrico / calefacción eléctrica?", value=False)
        tiene_cargador  = st.checkbox("¿Cargador vehículo eléctrico?", value=False)

    # Cálculo potencia recomendada
    base_kw = {1: 2.3, 2: 3.3, 3: 3.3, 4: 4.4, 5: 5.5}.get(min(hab, 5), 4.4)
    extra = 0.0
    if tiene_ac:       extra += 2.0
    if tiene_vitro:    extra += 1.5
    if tiene_termo:    extra += 1.0
    if tiene_cargador: extra += 3.7

    # Potencias normalizadas REE
    POTENCIAS_REE = [1.15, 2.3, 3.45, 4.6, 5.75, 6.9, 8.05, 9.2, 10.35, 11.5, 14.49, 17.25]
    pot_ideal_raw = base_kw + extra
    pot_recomendada = next((p for p in POTENCIAS_REE if p >= pot_ideal_raw), 17.25)

    # Coste término de potencia (~42 €/kW/año en peaje 2.0TD)
    COSTE_KW_AÑO = 42.0
    coste_actual  = potencia_actual  * COSTE_KW_AÑO
    coste_optimo  = pot_recomendada  * COSTE_KW_AÑO
    ahorro_anual  = coste_actual - coste_optimo

    with col2:
        st.markdown(f"""
        <div style="background:{CARD_BG};border:1px solid {BORDER};border-radius:10px;padding:1.4rem;">
            <div class="kpi-label">Potencia recomendada</div>
            <div style="font-family:'DM Serif Display',serif;font-size:2.2rem;color:{ACCENT};">{pot_recomendada} kW</div>
            <div class="kpi-sub">Basado en {hab} hab. + equipos seleccionados</div>
            <hr style="border:0;border-top:1px solid {BORDER};margin:0.8rem 0;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span class="kpi-label">Coste actual/año</span>
                <span style="font-size:0.9rem;font-weight:600;color:{RED};">{coste_actual:,.0f} €</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span class="kpi-label">Coste óptimo/año</span>
                <span style="font-size:0.9rem;font-weight:600;color:{GREEN};">{coste_optimo:,.0f} €</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if ahorro_anual > 5:
            st.markdown(f"""
            <div style="background:#EDF7F1;border-left:5px solid {GREEN};padding:1rem;border-radius:6px;margin-top:0.8rem;">
                <b>✅ Ahorro potencial: {ahorro_anual:,.0f} €/año</b><br>
                <span style="font-size:0.82rem;">Bajando de {potencia_actual} kW → {pot_recomendada} kW</span>
            </div>""", unsafe_allow_html=True)
        elif ahorro_anual < -5:
            st.markdown(f"""
            <div style="background:#FDECEA;border-left:5px solid {RED};padding:1rem;border-radius:6px;margin-top:0.8rem;">
                <b>⚠️ Potencia insuficiente</b><br>
                <span style="font-size:0.82rem;">Recomendable subir a {pot_recomendada} kW para evitar cortes</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#EDF7F1;border-left:5px solid {GREEN};padding:1rem;border-radius:6px;margin-top:0.8rem;">
                <b>✅ Potencia correctamente ajustada</b><br>
                <span style="font-size:0.82rem;">Tu contrato actual de {potencia_actual} kW es óptimo</span>
            </div>""", unsafe_allow_html=True)

    # ── COMPARADOR TARIFARIO ──────────────────
    st.markdown('<div class="section-title">📊 Comparador Tarifa Fija vs Indexada</div>', unsafe_allow_html=True)
    st.caption("Introduce el consumo mensual estimado para comparar ambas modalidades")

    c1, c2, c3 = st.columns(3)
    with c1:
        consumo_kwh   = st.number_input("Consumo mensual estimado (kWh)", min_value=50, max_value=2000, value=200, step=10)
    with c2:
        precio_fijo   = st.number_input("Precio tarifa fija (€/kWh)", min_value=0.05, max_value=0.50, value=0.18, step=0.01, format="%.3f")
    with c3:
        precio_pool   = st.number_input("Precio medio pool PVPC (€/kWh)", min_value=0.02, max_value=0.40, value=0.12, step=0.01, format="%.3f",
                                         help="Precio medio del mercado mayorista. Histórico 2024 ≈ 0.08–0.14 €/kWh")

    margen_comercial = 0.04  # margen típico comercializadora indexada
    precio_indexado  = precio_pool + margen_comercial

    coste_fijo_mes   = consumo_kwh * precio_fijo
    coste_index_mes  = consumo_kwh * precio_indexado
    dif_mes          = coste_fijo_mes - coste_index_mes
    dif_año          = dif_mes * 12

    fig_tar = go.Figure(go.Bar(
        x=["Tarifa Fija", "Tarifa Indexada"],
        y=[coste_fijo_mes, coste_index_mes],
        marker_color=[ACCENT, "#639922"],
        text=[f"{coste_fijo_mes:.2f} €/mes", f"{coste_index_mes:.2f} €/mes"],
        textposition="outside", width=0.35,
    ))
    fig_tar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=10), height=260,
        yaxis=dict(showgrid=False, visible=False),
        xaxis=dict(showgrid=False),
        font=dict(family="DM Sans", size=13), showlegend=False,
    )
    st.plotly_chart(fig_tar, use_container_width=True)

    r1, r2, r3 = st.columns(3)
    r1.metric("Coste fijo/mes",     f"{coste_fijo_mes:.2f} €")
    r2.metric("Coste indexado/mes", f"{coste_index_mes:.2f} €", delta=f"{-dif_mes:+.2f} €")
    r3.metric("Ahorro anual potencial", f"{dif_año:+.0f} €")

    if dif_año > 30:
        recomendacion = f"✅ La tarifa <b>indexada</b> es más barata con el precio de pool actual. Ahorro estimado: <b>{dif_año:.0f} €/año</b>."
        clase_rec = "status-green"
    elif dif_año < -30:
        recomendacion = f"⚠️ Con el precio de pool actual, la tarifa <b>fija</b> resulta más económica. El mercado indexado está caro."
        clase_rec = "status-yellow"
    else:
        recomendacion = "➡️ Diferencia marginal. La elección depende de tu tolerancia al riesgo de variación de precio."
        clase_rec = "status-yellow"

    st.markdown(f'<div class="{clase_rec}" style="margin-top:0.5rem;">{recomendacion}</div>', unsafe_allow_html=True)
# ══════════════════════════════════════════════
# DATOS DE LA CARTERA
# ══════════════════════════════════════════════
elif menu == "Datos de la Cartera":
    st.markdown('<div class="brand-header">Datos de la Cartera</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Parámetros maestros y copias de seguridad</div>', unsafe_allow_html=True)
    st.info("ℹ️ Edita aquí los parámetros maestros. Los campos CP, M2, Habitaciones, Estado y Parking alimentan el motor de tasación.")

    df_inm_ed = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True, hide_index=True)
    if st.button("✅ Actualizar Cartera"):
        df_inm_ed.to_csv(DB_INMUEBLES, index=False)
        st.success("✓ Datos actualizados.")
        st.rerun()

    st.markdown('<div class="section-title">Copias de Seguridad</div>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        with open(DB_INMUEBLES, "rb") as fi:
            st.download_button("📥 Descargar Inmuebles",   fi, "nolasco_inmuebles.csv",   "text/csv")
    with b2:
        with open(DB_MOVIMIENTOS, "rb") as fm:
            st.download_button("📥 Descargar Movimientos", fm, "nolasco_movimientos.csv", "text/csv")
