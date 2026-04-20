import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# 1. CONFIGURACIÓN VISUAL PREMIUM (Tipografía Nolasco)
# ─────────────────────────────────────────────
st.set_page_config(page_title="Nolasco Capital", layout="wide", page_icon="🏛️")

st.markdown("""
<style>
/* Importación de las tipografías premium */
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --ink:       #0D0F12;
    --parchment: #F7F4EF;
    --gold:      #C9A84C;
    --emerald:   #1B5E3B;
    --crimson:   #8B1A1A;
    --slate:     #4A5568;
    --card-bg:   #FFFFFF;
    --border:    #E8E2D9;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--parchment) !important;
    color: var(--ink);
}

/* ─────────────────────────────────────────────
   DISEÑO EXCLUSIVO PARA LA BARRA LATERAL (SIDEBAR)
   ───────────────────────────────────────────── */
[data-testid="stSidebar"] { 
    background: var(--ink) !important; 
    border-right: 1px solid #222; 
}

/* Aplicar DM Serif Display a los botones del menú */
[data-testid="stSidebar"] .stRadio p { 
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.15rem !important; 
    letter-spacing: 0.02em; 
    color: #E8E2D9 !important;
    margin-bottom: 0.3rem;
    transition: all 0.3s ease;
}

/* Efecto hover (dorado) al pasar el ratón por el menú */
[data-testid="stSidebar"] .stRadio label:hover p {
    color: var(--gold) !important;
}

/* Header brand y subtítulos */
.brand-header { font-family: 'DM Serif Display', serif; font-size: 2.2rem; color: var(--ink); letter-spacing: -0.02em; border-bottom: 2px solid var(--gold); padding-bottom: 0.4rem; margin-bottom: 0.2rem; }
.brand-sub { font-size: 0.75rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--slate); margin-bottom: 1.5rem; font-family: 'DM Sans', sans-serif;}

/* KPI cards */
.kpi-card { background: var(--card-bg); border: 1px solid var(--border); border-top: 3px solid var(--gold); border-radius: 4px; padding: 1.2rem 1.5rem; text-align: center; }
.kpi-label { font-size: 0.65rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--slate); margin-bottom: 0.3rem; font-family: 'DM Sans', sans-serif;}
.kpi-value { font-family: 'DM Serif Display', serif; font-size: 1.9rem; color: var(--ink); line-height: 1; }
.kpi-value.positive { color: var(--emerald); }
.kpi-value.negative { color: var(--crimson); }

/* Asset cards */
.asset-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 4px; padding: 1.1rem; height: 100%; position: relative; overflow: hidden; }
.asset-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, var(--gold), transparent); }
.asset-name { font-size: 0.65rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--slate); margin-bottom: 0.2rem; }
.asset-tenant { font-size: 0.9rem; font-weight: 600; color: var(--ink); margin-bottom: 0.8rem; }
.asset-income { color: var(--emerald); font-weight: 600; font-size: 1.15rem; }
.asset-expense { color: var(--crimson); font-size: 0.9rem; margin-top: 0.2rem; }
.asset-net { font-family: 'DM Serif Display', serif; font-size: 1.3rem; color: var(--ink); border-top: 1px solid var(--border); margin-top: 0.7rem; padding-top: 0.5rem; }

/* Section titles & Panels */
.section-title { font-family: 'DM Serif Display', serif; font-size: 1.3rem; color: var(--ink); border-left: 3px solid var(--gold); padding-left: 0.7rem; margin: 1.5rem 0 1rem 0; }
.ai-panel { background: var(--ink); color: #F0EAD6; border-radius: 6px; padding: 1.5rem; margin-top: 1rem; border-left: 4px solid var(--gold); font-size: 0.95rem; line-height: 1.6; }
.fiscal-panel { background: #F0F7F3; border: 1px solid #C3DDD0; border-radius: 4px; padding: 1.2rem; font-size: 0.88rem; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. BASE DE DATOS Y PERSISTENCIA (SIN CLAVES)
# ─────────────────────────────────────────────
DB_INMUEBLES   = "nolasco_inmuebles.csv"
DB_MOVIMIENTOS = "nolasco_movimientos.csv"

def inicializar_bd(force=False):
    if force or not os.path.exists(DB_INMUEBLES):
        pd.DataFrame([
            {"Nombre": "Casa Abarqueros",  "Inquilino": "Victor Aguiluz", "Renta": 2200.0,  "Comunidad": 193.76, "Valor_Construccion": 150000.0},
            {"Nombre": "Paseo del Salón",  "Inquilino": "Pool Despachos",  "Renta": 1591.8,  "Comunidad": 175.18, "Valor_Construccion": 120000.0},
            {"Nombre": "Huerto Unidad 1",  "Inquilino": "Alain",           "Renta": 660.0,   "Comunidad": 74.62,  "Valor_Construccion": 45000.0},
            {"Nombre": "Huerto Unidad 2",  "Inquilino": "Laura/Alex",      "Renta": 800.0,   "Comunidad": 74.62,  "Valor_Construccion": 45000.0},
            {"Nombre": "Huerto Unidad 3",  "Inquilino": "Jose Manuel",     "Renta": 850.0,   "Comunidad": 74.63,  "Valor_Construccion": 45000.0},
        ]).to_csv(DB_INMUEBLES, index=False)

    if force or not os.path.exists(DB_MOVIMIENTOS):
        pd.DataFrame([
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Hipoteca Abarqueros",       "Categoría": "Financiero",   "Tipo": "Gasto", "Importe": 554.73},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Seguro MyBox",              "Categoría": "Seguros",      "Tipo": "Gasto", "Importe": 96.43},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Seguro Vida (Seviam)",      "Categoría": "Seguros",      "Tipo": "Gasto", "Importe": 55.93},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Mantenimiento Ascensor",    "Categoría": "Mantenimiento","Tipo": "Gasto", "Importe": 65.44},
            {"Fecha": "2026-04-01", "Apartamento": "Global",          "Concepto": "Software Holded",           "Categoría": "Sistemas",      "Tipo": "Gasto", "Importe": 18.15},
            {"Fecha": "2026-04-01", "Apartamento": "Global",          "Concepto": "Autónomos (TGSS)",          "Categoría": "Impuestos",    "Tipo": "Gasto", "Importe": 314.00},
            {"Fecha": "2026-04-01", "Apartamento": "Global",          "Concepto": "Sueldo Pedro",              "Categoría": "Personal",      "Tipo": "Gasto", "Importe": 600.00},
            {"Fecha": "2026-04-01", "Apartamento": "Global",          "Concepto": "IRPF (Aplazamiento)",       "Categoría": "Impuestos",    "Tipo": "Gasto", "Importe": 1100.00},
            {"Fecha": "2026-04-01", "Apartamento": "Global",          "Concepto": "IVA (Cuota Fija)",          "Categoría": "Impuestos",    "Tipo": "Gasto", "Importe": 325.00},
        ]).to_csv(DB_MOVIMIENTOS, index=False)

inicializar_bd()
df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)

# ─────────────────────────────────────────────
# 3. SIDEBAR Y MENÚ
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1.5rem 0 1rem 0;'>
        <div style='font-family:"DM Serif Display",serif; font-size:1.8rem; color:#C9A84C; letter-spacing:-0.01em;'>
            NOLASCO
        </div>
        <div style='font-size:0.6rem; letter-spacing:0.2em; color:#888; text-transform:uppercase; margin-top:2px; font-family:"DM Sans", sans-serif;'>
            Capital · Gestión de Activos
        </div>
    </div>
    <hr style='border-color:#333; margin-bottom:1rem;'>
    """, unsafe_allow_html=True)

    menu = st.radio("", [
        "📊  Torre de Control",
        "🏠  Fichas de Activos",
        "🤖  Auditoría Automática",
        "📝  Diario de Operaciones",
        "⚙️  Configuración & Backups",
    ], label_visibility="collapsed")

# ─────────────────────────────────────────────
# 4. PÁGINAS DEL SISTEMA
# ─────────────────────────────────────────────

# ── TORRE DE CONTROL ──────────────────────────
if "Torre" in menu:
    st.markdown('<div class="brand-header">Torre de Control</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Cartera Nolasco · Resumen Mensual</div>', unsafe_allow_html=True)

    ing_b       = df_inm["Renta"].sum()
    comu_total  = df_inm["Comunidad"].sum()
    gastos_adic = df_mov[df_mov["Tipo"] == "Gasto"]["Importe"].sum()
    gas_total   = comu_total + gastos_adic
    neto        = ing_b - gas_total
    margen_pct  = neto / ing_b * 100 if ing_b else 0

    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        ("Ingresos Brutos",   f"{ing_b:,.0f} €",        "positive"),
        ("Gastos Totales",    f"{gas_total:,.0f} €",      "negative"),
        ("Resultado Neto",    f"{neto:,.0f} €",           "positive" if neto > 0 else "negative"),
        ("Margen Neto",       f"{margen_pct:.1f} %",      "positive" if margen_pct > 30 else ""),
    ]
    for col, (label, val, cls) in zip([c1, c2, c3, c4], kpis):
        col.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value {cls}">{val}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Balance por Activo</div>', unsafe_allow_html=True)
    cols_apto = st.columns(len(df_inm))
    for i, row in df_inm.iterrows():
        g_esp      = df_mov[(df_mov["Apartamento"] == row["Nombre"]) & (df_mov["Tipo"] == "Gasto")]["Importe"].sum()
        cargas     = row["Comunidad"] + g_esp
        neto_apto  = row["Renta"] - cargas
        margen_a   = neto_apto / row["Renta"] * 100 if row["Renta"] else 0
        color_neto = "var(--emerald)" if neto_apto >= 0 else "var(--crimson)"
        with cols_apto[i]:
            st.markdown(f"""
            <div class="asset-card">
                <div class="asset-name">{row['Nombre']}</div>
                <div class="asset-tenant">{row['Inquilino']}</div>
                <div class="asset-income">+{row['Renta']:,.0f} €</div>
                <div class="asset-expense">−{cargas:,.0f} €</div>
                <div class="asset-net" style="color:{color_neto};">{neto_apto:,.0f} €</div>
                <div style="font-size:0.7rem;color:var(--slate);margin-top:0.3rem;">{margen_a:.0f}% margen</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Distribución de Costes</div>', unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        df_cat = df_mov.groupby("Categoría")["Importe"].sum().reset_index().sort_values("Importe", ascending=True)
        fig_bar = go.Figure(go.Bar(x=df_cat["Importe"], y=df_cat["Categoría"], orientation="h", marker=dict(color="#C9A84C"), text=df_cat["Importe"].apply(lambda x: f"{x:,.0f}€"), textposition="outside"))
        fig_bar.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=10, r=60, t=10, b=10), xaxis=dict(showgrid=False, showticklabels=False), height=260)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_r:
        fig_pie = go.Figure(go.Pie(labels=df_inm["Nombre"], values=df_inm["Renta"], hole=0.55, marker=dict(colors=["#C9A84C","#1B5E3B","#8B1A1A","#4A5568","#0D0F12"]), textinfo="label+percent"))
        fig_pie.update_layout(paper_bgcolor="white", margin=dict(l=10, r=10, t=10, b=10), showlegend=False, height=260)
        st.plotly_chart(fig_pie, use_container_width=True)

# ── FICHAS DE ACTIVOS ────────────────────────
elif "Fichas" in menu:
    st.markdown('<div class="brand-header">Fichas de Activos</div>', unsafe_allow_html=True)
    sel = st.selectbox("Seleccionar inmueble:", df_inm["Nombre"].tolist())
    f   = df_inm[df_inm["Nombre"] == sel].iloc[0]

    df_g_apto = df_mov[(df_mov["Apartamento"] == sel) & (df_mov["Tipo"] == "Gasto")]
    resumen   = pd.concat([pd.DataFrame([{"Concepto": "Comunidad", "Importe": f["Comunidad"]}]), df_g_apto[["Concepto", "Importe"]]]).reset_index(drop=True)
    total_gastos = resumen["Importe"].sum()
    neto_mensual = f["Renta"] - total_gastos
    amort_mensual= (f["Valor_Construccion"] * 0.03) / 12

    c_left, c_right = st.columns([3, 2])
    with c_left:
        st.markdown(f"**Inquilino:** {f['Inquilino']}")
        st.dataframe(resumen.style.format({"Importe": "{:,.2f} €"}), use_container_width=True, hide_index=True)

    with c_right:
        st.markdown(f"""
        <div class="fiscal-panel">
            <div style="font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;color:#4A5568;">Neto Mensual Operativo</div>
            <div style="font-size:1.6rem;font-family:'DM Serif Display',serif;color:#1B5E3B;margin-bottom:1rem;">{neto_mensual:,.2f} €</div>
            <div style="font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;color:#4A5568;">Amortización deducible (3%/año)</div>
            <div style="font-size:1.2rem;font-family:'DM Serif Display',serif;">{amort_mensual:,.2f} €/mes</div>
        </div>
        """, unsafe_allow_html=True)

# ── AUDITORÍA AUTOMÁTICA (SIN API) ───────────
elif "Auditor" in menu:
    st.markdown('<div class="brand-header">Auditoría Automática</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Análisis algorítmico de la cartera (Local y Seguro)</div>', unsafe_allow_html=True)
    
    mejor_margen, peor_margen = 0, 100
    mejor_apto, peor_apto = "", ""
    
    for _, row in df_inm.iterrows():
        g_esp = df_mov[(df_mov["Apartamento"] == row["Nombre"]) & (df_mov["Tipo"] == "Gasto")]["Importe"].sum()
        margen = ((row["Renta"] - row["Comunidad"] - g_esp) / row["Renta"] * 100) if row["Renta"] > 0 else 0
        if margen > mejor_margen:
            mejor_margen, mejor_apto = margen, row["Nombre"]
        if margen < peor_margen:
            peor_margen, peor_apto = margen, row["Nombre"]
            
    gasto_mayor_cat = df_mov.groupby("Categoría")["Importe"].sum().idxmax()
    gasto_mayor_val = df_mov.groupby("Categoría")["Importe"].sum().max()

    st.markdown(f"""
    <div class="ai-panel">
        <span style="color:var(--gold); font-size:1.2rem; font-family:'DM Serif Display', serif;">🔍 Conclusiones del Sistema Nolasco:</span><br><br>
        1. <b>Activo Estrella:</b> "{mejor_apto}" es tu inmueble más eficiente con un margen operativo del {mejor_margen:.1f}%.<br>
        2. <b>Punto de Fuga:</b> "{peor_apto}" presenta el margen más ajustado ({peor_margen:.1f}%). Recomiendo revisar su cuota de comunidad o posibles gastos asociados.<br>
        3. <b>Control de Costes:</b> Tu mayor pozo de gastos estructurales recae en la categoría "<b>{gasto_mayor_cat}</b>" ({gasto_mayor_val:,.2f} €). Como economista, este es el primer punto donde buscar optimización fiscal.
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 Este análisis se genera automáticamente leyendo los datos de tu libro de movimientos sin necesidad de conectarse a internet.")

# ── DIARIO DE OPERACIONES ────────────────────
elif "Diario" in menu:
    st.markdown('<div class="brand-header">Diario de Operaciones</div>', unsafe_allow_html=True)
    df_ed = st.data_editor(df_mov, num_rows="dynamic", use_container_width=True)
    if st.button("💾  Guardar Movimientos"):
        df_ed.to_csv(DB_MOVIMIENTOS, index=False)
        st.success("✓ Cambios guardados.")

# ── CONFIGURACIÓN & BACKUPS ──────────────────
elif "Config" in menu:
    st.markdown('<div class="brand-header">Configuración y Backups</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">1. Gestión de Activos (Inmuebles)</div>', unsafe_allow_html=True)
    df_inm_ed = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True)
    if st.button("💾  Actualizar Inmuebles"):
        df_inm_ed.to_csv(DB_INMUEBLES, index=False)
        st.success("✓ Activos actualizados.")

    st.markdown('<div class="section-title">2. Copias de Seguridad (Backups)</div>', unsafe_allow_html=True)
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        with open(DB_INMUEBLES, "rb") as file:
            st.download_button(label="📥 Descargar Inmuebles", data=file, file_name="backup_inmuebles.csv", mime="text/csv")
    with col_b2:
        with open(DB_MOVIMIENTOS, "rb") as file:
            st.download_button(label="📥 Descargar Movimientos", data=file, file_name="backup_movimientos.csv", mime="text/csv")

    st.markdown('<div class="section-title">3. Peligro</div>', unsafe_allow_html=True)
    if st.button("⚠️  Reiniciar Todo (Borrar y volver a datos de fábrica)"):
        inicializar_bd(force=True)
        st.rerun()
