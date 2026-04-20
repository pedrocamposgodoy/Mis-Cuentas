import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────
# 1. DISEÑO DE INTERFAZ "NOLASCO CAPITAL V7.0"
# ─────────────────────────────────────────────
st.set_page_config(page_title="Nolasco Capital", layout="wide", page_icon="🏛️")

# Mapeo de colores fijos por activo para consistencia visual
COLOR_PALETTE = ["#C9A84C", "#1B5E3B", "#8B1A1A", "#4A5568", "#0D0F12", "#2E86C1"]

st.markdown("""
<style>
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

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: var(--parchment) !important; color: var(--ink); }

/* BARRA LATERAL PERSONALIZADA */
[data-testid="stSidebar"] { background: var(--ink) !important; border-right: 1px solid #222; min-width: 280px !important; }
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { padding-top: 1.5rem; gap: 1rem; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { background: transparent !important; border: none !important; padding: 0 !important; }

/* Tipografía DM Sans para el menú lateral (fina y discreta) */
[data-testid="stSidebar"] .stRadio p {
    font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important; font-weight: 400 !important; color: #ADB5BD !important;
    letter-spacing: 0.02em !important; transition: all 0.3s ease; padding-left: 1rem; border-left: 0px solid var(--gold);
}
[data-testid="stSidebar"] .stRadio label[data-checked="true"] p { color: var(--gold) !important; font-weight: 500 !important; border-left: 3px solid var(--gold); padding-left: 1.2rem; }
[data-testid="stSidebar"] .stRadio label:hover p { color: var(--gold) !important; }

/* Headers y Componentes */
.brand-header { font-family: 'DM Serif Display', serif; font-size: 2.5rem; color: var(--ink); border-bottom: 2px solid var(--gold); padding-bottom: 0.5rem; margin-bottom: 0.2rem; }
.brand-sub { font-size: 0.8rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--slate); margin-bottom: 2rem; }

.kpi-card { background: var(--card-bg); border: 1px solid var(--border); border-top: 3px solid var(--gold); border-radius: 4px; padding: 1.5rem; text-align: center; }
.kpi-label { font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--slate); margin-bottom: 0.3rem; }
.kpi-value { font-family: 'DM Serif Display', serif; font-size: 2.2rem; line-height: 1; }

.asset-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 4px; padding: 1.1rem; height: 100%; position: relative; overflow: hidden; }
.asset-name { font-size: 0.65rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--slate); margin-bottom: 0.2rem; }
.asset-tenant { font-size: 0.9rem; font-weight: 600; color: var(--ink); margin-bottom: 0.8rem; }
.asset-income { color: var(--emerald); font-weight: 600; font-size: 1.15rem; }
.asset-expense { color: var(--crimson); font-size: 0.9rem; margin-top: 0.2rem; }
.asset-net { font-family: 'DM Serif Display', serif; font-size: 1.3rem; color: var(--ink); border-top: 1px solid var(--border); margin-top: 0.7rem; padding-top: 0.5rem; }

.section-title { font-family: 'DM Serif Display', serif; font-size: 1.4rem; color: var(--ink); border-left: 3px solid var(--gold); padding-left: 0.7rem; margin: 2rem 0 1rem 0; }
.fiscal-panel { background: #F0F7F3; border: 1px solid #C3DDD0; border-radius: 6px; padding: 1.5rem; }

/* Ajuste fino de la auditoría */
.ai-report-unit { padding: 1rem 0; border-bottom: 1px solid var(--gold); margin-bottom: 1rem; }
.ai-report-unit:last-child { border-bottom: none; }

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. MOTOR DE DATOS (VERSION 7)
# ─────────────────────────────────────────────
DB_INMUEBLES   = "nolasco_inmuebles_v7.csv"
DB_MOVIMIENTOS = "nolasco_movimientos_v7.csv"

def inicializar_bd(force=False):
    if force or not os.path.exists(DB_INMUEBLES):
        pd.DataFrame([
            {"Nombre": "Casa Abarqueros", "Inquilino": "Victor Aguiluz", "Renta": 2200.0, "Comunidad": 193.76, "Valor_Construccion": 150000.0, "Año_Reforma": 2018, "Mobiliario": "S", "Tipo": "Casa", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Paseo del Salón", "Inquilino": "Pool Despachos", "Renta": 1591.8, "Comunidad": 175.18, "Valor_Construccion": 120000.0, "Año_Reforma": 2020, "Mobiliario": "N", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 1", "Inquilino": "Alain", "Renta": 660.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0, "Año_Reforma": 2022, "Mobiliario": "S", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 2", "Inquilino": "Laura/Alex", "Renta": 800.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0, "Año_Reforma": 2022, "Mobiliario": "S", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 3", "Inquilino": "Jose Manuel", "Renta": 850.0, "Comunidad": 74.63, "Valor_Construccion": 45000.0, "Año_Reforma": 2021, "Mobiliario": "S", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 4", "Inquilino": "Pendiente", "Renta": 600.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0, "Año_Reforma": 2024, "Mobiliario": "S", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"}
        ]).to_csv(DB_INMUEBLES, index=False)
    
    if force or not os.path.exists(DB_MOVIMIENTOS):
        pd.DataFrame([
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Hipoteca (Intereses)", "Categoría": "Financiero", "Tipo": "Gasto", "Importe": 250.00, "Deducible": "S"},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Hipoteca (Capital)", "Categoría": "Financiero", "Tipo": "Gasto", "Importe": 304.73, "Deducible": "N"},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Seguro MyBox (Hogar)", "Categoría": "Seguros", "Tipo": "Gasto", "Importe": 96.43, "Deducible": "S"},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Seguro Vida (Seviam)", "Categoría": "Seguros", "Tipo": "Gasto", "Importe": 55.93, "Deducible": "S"},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Mantenimiento Ascensor", "Categoría": "Mantenimiento", "Tipo": "Gasto", "Importe": 65.44, "Deducible": "S"},
            {"Fecha": "2026-04-01", "Apartamento": "Global", "Concepto": "Sueldo Pedro", "Categoría": "Personal", "Tipo": "Gasto", "Importe": 600.00, "Deducible": "N"}
        ]).to_csv(DB_MOVIMIENTOS, index=False)

inicializar_bd()
df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)

# ─────────────────────────────────────────────
# 3. NAVEGACIÓN
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding-bottom: 2rem;'>
        <div style='font-family:"DM Serif Display",serif; font-size:2.2rem; color:#C9A84C; line-height:1;'>NOLASCO</div>
        <div style='font-family:"DM Sans", sans-serif; font-size:0.7rem; letter-spacing:0.3em; color:#888; text-transform:uppercase;'>Capital Management</div>
    </div>
    """, unsafe_allow_html=True)
    
    menu = st.radio("", ["📊 Torre de Control", "🏠 Fichas de Activos", "🤖 Auditoría IA", "📝 Diario Contable", "📂 Datos de la cartera"], label_visibility="collapsed")

# ── TORRE DE CONTROL ──────────────────────────
if "Torre" in menu:
    st.markdown('<div class="brand-header">Torre de Control</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Cartera Consolidada (6 Activos)</div>', unsafe_allow_html=True)
    
    ing_b = df_inm["Renta"].sum()
    gas_caja = df_mov[df_mov["Tipo"]=="Gasto"]["Importe"].sum() + df_inm["Comunidad"].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-label">Ingreso Bruto</div><div class="kpi-value" style="color:var(--emerald)">{ing_b:,.0f}€</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-label">Salida de Caja</div><div class="kpi-value" style="color:var(--crimson)">-{gas_caja:,.0f}€</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-label">Resultado Neto</div><div class="kpi-value">{ing_b - gas_caja:,.0f}€</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Rentabilidad por Activo</div>', unsafe_allow_html=True)
    cols = st.columns(len(df_inm))
    for i, row in df_inm.iterrows():
        g_esp = df_mov[(df_mov["Apartamento"] == row["Nombre"])]["Importe"].sum()
        with cols[i]:
            st.markdown(f"""
            <div class="asset-card" style="border-top: 3px solid {COLOR_PALETTE[i % 6]};">
                <div class="asset-name">{row['Nombre']}</div>
                <div class="asset-income">+{row['Renta']:,.0f}€</div>
                <div class="asset-expense">-{row['Comunidad']+g_esp:,.0f}€</div>
                <div class="asset-net">{row['Renta'] - row['Comunidad'] - g_esp:,.0f}€</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Análisis de Costes y Distribución</div>', unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("📋 Gastos por Tipología")
        df_cat = df_mov.groupby("Categoría")["Importe"].sum().reset_index().sort_values("Importe", ascending=False)
        st.table(df_cat.style.format({"Importe": "{:,.2f} €"}))
    with col_r:
        st.subheader("🍰 Distribución de Rentas")
        fig_pie = go.Figure(go.Pie(labels=df_inm["Nombre"], values=df_inm["Renta"], hole=0.55, marker=dict(colors=COLOR_PALETTE), textinfo="label+percent"))
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10), showlegend=False, height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

# ── FICHAS DE ACTIVOS ─────────────────────────
elif "Fichas" in menu:
    st.markdown('<div class="brand-header">Fichas de Activos</div>', unsafe_allow_html=True)
    sel = st.selectbox("Seleccionar Inmueble:", df_inm["Nombre"].tolist())
    f = df_inm[df_inm["Nombre"] == sel].iloc[0]
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown(f"### Desglose de Gastos: {sel}")
        df_g = df_mov[df_mov["Apartamento"] == sel]
        resumen = pd.concat([pd.DataFrame([{"Concepto": "Comunidad", "Importe": f["Comunidad"], "Deducible": "S"}]), df_g[["Concepto", "Importe", "Deducible"]]])
        
        # Fila de Total
        total_suma = resumen["Importe"].sum()
        resumen_final = pd.concat([resumen, pd.DataFrame([{"Concepto": "TOTAL GASTOS CAJA", "Importe": total_suma, "Deducible": "-"}])])
        
        st.table(resumen_final.style.format({"Importe": "{:,.2f}€"}))
        
    with col_b:
        st.markdown('<div class="fiscal-panel">', unsafe_allow_html=True)
        st.markdown("### ⚖️ Balance Fiscal vs Caja")
        total_deducible = resumen[resumen["Deducible"]=="S"]["Importe"].sum()
        amort = (f["Valor_Construccion"] * 0.03) / 12
        
        st.write(f"**Salida de Caja (Total):** {total_suma:,.2f}€")
        st.write(f"**Gasto Fiscal Deducible:** {total_deducible:,.2f}€")
        st.write(f"**Amortización (3%):** {amort:,.2f}€")
        st.divider()
        st.write(f"**Rendimiento Neto Fiscal:** {f['Renta'] - total_deducible - amort:,.2f}€")
        st.markdown('</div>', unsafe_allow_html=True)

# ── AUDITORÍA IA ──────────────────────────────
elif "Auditor" in menu:
    st.markdown('<div class="brand-header">Auditoría Automática</div>', unsafe_allow_html=True)
    año_actual = datetime.now().year
    
    for _, row in df_inm.iterrows():
        st.markdown(f'<div class="ai-report-unit">', unsafe_allow_html=True)
        st.markdown(f"### 📍 {row['Nombre']}")
        
        consejos = []
        if año_actual - int(row["Año_Reforma"]) > 6:
            consejos.append(f"🎨 **Estética:** Han pasado {año_actual - int(row['Año_Reforma'])} años. Una renovación de pintura y textiles revalorizará el activo.")
        
        if row["Mobiliario"] == "S":
            consejos.append("🔌 **Mobiliario:** Activo amueblado. Se recomienda provisión para reposición de electrodomésticos.")
        
        if row["Tipo"] == "Casa":
            consejos.append("🏠 **Estructura:** Recomendada limpieza de canalones y revisión de cubiertas pre-invierno.")
        
        if not consejos: consejos.append("✅ Activo en ciclo óptimo de mantenimiento.")
        
        st.write("  \n".join(consejos))
        st.markdown('</div>', unsafe_allow_html=True)

# ── DIARIO Y DATOS CARTERA ────────────────────
elif "Diario" in menu:
    st.markdown('<div class="brand-header">Diario Contable</div>', unsafe_allow_html=True)
    df_ed = st.data_editor(df_mov, num_rows="dynamic", use_container_width=True)
    if st.button("Guardar Cambios"):
        df_ed.to_csv(DB_MOVIMIENTOS, index=False)
        st.rerun()

elif "Datos" in menu:
    st.markdown('<div class="brand-header">Datos de la cartera</div>', unsafe_allow_html=True)
    df_inm_ed = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True)
    if st.button("Guardar Datos de Cartera"):
        df_inm_ed.to_csv(DB_INMUEBLES, index=False)
        st.success("✓ Base de datos actualizada.")
        st.rerun()
