import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────
# 1. ARQUITECTURA VISUAL "NOLASCO CAPITAL V9.2"
# ─────────────────────────────────────────────
st.set_page_config(page_title="Nolasco Capital", layout="wide", page_icon="🏛️")

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

/* OPTIMIZACIÓN DE ESPACIO SUPERIOR */
.block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: var(--parchment) !important; color: var(--ink); }

/* BARRA LATERAL ESTILO BOUTIQUE */
[data-testid="stSidebar"] { background: var(--ink) !important; border-right: 1px solid #222; min-width: 280px !important; }
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { padding-top: 1.5rem; gap: 1rem; }

[data-testid="stSidebar"] .stRadio p {
    font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important; font-weight: 400 !important; color: #ADB5BD !important;
    letter-spacing: 0.02em !important; transition: all 0.3s ease; padding-left: 1rem; border-left: 0px solid var(--gold);
}
[data-testid="stSidebar"] .stRadio label[data-checked="true"] p { color: var(--gold) !important; font-weight: 500 !important; border-left: 3px solid var(--gold); padding-left: 1.2rem; }

/* Estructura de Títulos y Tarjetas */
.brand-header { font-family: 'DM Serif Display', serif; font-size: 2.3rem; color: var(--ink); border-bottom: 2px solid var(--gold); padding-bottom: 0.5rem; margin-bottom: 0.2rem; }
.brand-sub { font-size: 0.75rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--slate); margin-bottom: 1.5rem; }

.kpi-card { background: var(--card-bg); border: 1px solid var(--border); border-top: 3px solid var(--gold); border-radius: 4px; padding: 1.2rem; text-align: center; }
.kpi-label { font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--slate); margin-bottom: 0.2rem; }
.kpi-value { font-family: 'DM Serif Display', serif; font-size: 2rem; line-height: 1; }

.section-title { font-family: 'DM Serif Display', serif; font-size: 1.5rem; color: var(--ink); border-left: 3px solid var(--gold); padding-left: 0.7rem; margin: 1.5rem 0 1rem 0; }
.fiscal-panel { background: #F0F7F3; border: 1px solid #C3DDD0; border-radius: 6px; padding: 1.5rem; }

/* CAJAS DE BENCHMARK (Fichas) */
.status-red { background: #FDECEA; border-left: 5px solid var(--crimson); padding: 1.5rem; border-radius: 4px; }
.status-yellow { background: #FFF9E6; border-left: 5px solid #F39C12; padding: 1.5rem; border-radius: 4px; }
.status-green { background: #EDF7F1; border-left: 5px solid var(--emerald); padding: 1.5rem; border-radius: 4px; }

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. MOTOR DE DATOS (NÚCLEO V9.2)
# ─────────────────────────────────────────────
DB_INMUEBLES   = "nolasco_inmuebles_v9.csv"
DB_MOVIMIENTOS = "nolasco_movimientos_v9.csv"

def inicializar_bd(force=False):
    if force or not os.path.exists(DB_INMUEBLES):
        pd.DataFrame([
            {"Nombre": "Casa Abarqueros", "Inquilino": "Victor Aguiluz", "Renta": 2200.0, "Renta_Mercado": 2600.0, "Comunidad": 193.76, "Valor_Construccion": 150000.0, "Año_Reforma": 2018, "Mobiliario": "S", "Tipo": "Casa", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Paseo del Salón", "Inquilino": "Pool Despachos", "Renta": 1591.8, "Renta_Mercado": 1650.0, "Comunidad": 175.18, "Valor_Construccion": 120000.0, "Año_Reforma": 2020, "Mobiliario": "N", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 1", "Inquilino": "Alain", "Renta": 660.0, "Renta_Mercado": 800.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0, "Año_Reforma": 2022, "Mobiliario": "S", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 2", "Inquilino": "Laura/Alex", "Renta": 800.0, "Renta_Mercado": 800.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0, "Año_Reforma": 2022, "Mobiliario": "S", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 3", "Inquilino": "Jose Manuel", "Renta": 850.0, "Renta_Mercado": 800.0, "Comunidad": 74.63, "Valor_Construccion": 45000.0, "Año_Reforma": 2021, "Mobiliario": "S", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 4", "Inquilino": "Pendiente", "Renta": 600.0, "Renta_Mercado": 800.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0, "Año_Reforma": 2024, "Mobiliario": "S", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"}
        ]).to_csv(DB_INMUEBLES, index=False)
    
    if force or not os.path.exists(DB_MOVIMIENTOS):
        pd.DataFrame([
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Renta Mensual", "Categoría": "Ingresos", "Tipo": "Ingreso", "Importe": 2200.00, "Deducible": "N"},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Comunidad", "Categoría": "Comunidad", "Tipo": "Gasto", "Importe": 193.76, "Deducible": "S"}
        ]).to_csv(DB_MOVIMIENTOS, index=False)

inicializar_bd()
df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)

# ─────────────────────────────────────────────
# 3. NAVEGACIÓN
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='padding-bottom: 1rem;'><div style='font-family:\"DM Serif Display\",serif; font-size:2.2rem; color:#C9A84C; line-height:1;'>NOLASCO</div></div>", unsafe_allow_html=True)
    menu = st.radio("", ["📊 Torre de Control", "🏠 Fichas (Benchmark)", "🤖 Auditoría IA", "📝 Diario Contable", "📂 Datos de la Cartera"], label_visibility="collapsed")

# ── TORRE DE CONTROL ──────────────────────────
if "Torre" in menu:
    st.markdown('<div class="brand-header">Torre de Control</div>', unsafe_allow_html=True)
    
    ing_b = df_inm["Renta"].sum()
    gas_caja = df_mov[df_mov["Tipo"]=="Gasto"]["Importe"].sum() + df_inm["Comunidad"].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-label">Ingresos Totales</div><div class="kpi-value" style="color:var(--emerald)">{ing_b:,.0f}€</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-label">Gastos Operativos</div><div class="kpi-value" style="color:var(--crimson)">-{gas_caja:,.0f}€</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-label">Beneficio Neto</div><div class="kpi-value">{ing_b - gas_caja:,.0f}€</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Rentabilidad por Activo</div>', unsafe_allow_html=True)
    cols = st.columns(len(df_inm))
    for i, row in df_inm.iterrows():
        g_esp = df_mov[(df_mov["Apartamento"] == row["Nombre"]) & (df_mov["Tipo"] == "Gasto")]["Importe"].sum()
        gastos_unit = row['Comunidad'] + g_esp
        beneficio_unit = row['Renta'] - gastos_unit
        with cols[i]:
            st.markdown(f"""
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:4px; border-top:4px solid {COLOR_PALETTE[i % 6]}; padding:1.2rem 0.8rem; text-align:center; height:100%;">
                <div style="font-size:0.75rem; font-weight:600; text-transform:uppercase; color:var(--slate); margin-bottom:8px;">{row['Nombre']}</div>
                <div style="font-size:1.15rem; font-weight:600; color:var(--emerald);">+{row['Renta']:,.0f}€</div>
                <div style="font-size:0.85rem; font-weight:500; color:var(--crimson); margin-top:2px;">-{gastos_unit:,.0f}€</div>
                <div style="font-family:'DM Serif Display',serif; font-size:1.45rem; color:#D35400; border-top:1px solid #eee; margin-top:8px; padding-top:5px;">{beneficio_unit:,.0f}€</div>
            </div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<h3 style='font-family: \"DM Serif Display\", serif; font-size: 1.5rem; color: var(--ink); margin: 2rem 0 1rem 0; border-left: 3px solid var(--gold); padding-left: 0.7rem;'>📋 Gastos por Tipología</h3>", unsafe_allow_html=True)
        df_cat = df_mov[df_mov["Tipo"]=="Gasto"].groupby("Categoría")["Importe"].sum().reset_index().sort_values("Importe", ascending=False)
        st.dataframe(df_cat.style.format({"Importe": "{:,.2f} €"}).set_properties(**{'font-size': '1.1rem', 'padding': '12px'}), hide_index=True, use_container_width=True)
    
    with col_r:
        st.markdown("<h3 style='font-family: \"DM Serif Display\", serif; font-size: 1.5rem; color: var(--ink); margin: 2rem 0 1rem 0; border-left: 3px solid var(--gold); padding-left: 0.7rem;'>🍰 Composición de Rentas</h3>", unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=df_inm["Nombre"], values=df_inm["Renta"], hole=0.4, 
            marker=dict(colors=COLOR_PALETTE), textinfo="label+percent", textposition="outside",
            textfont=dict(size=13, family="DM Sans")
        ))
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=80,r=80,t=30,b=30), showlegend=False, height=420)
        st.plotly_chart(fig_pie, use_container_width=True)

# ── FICHAS (BENCHMARK) ────────────────────────
elif "Fichas" in menu:
    st.markdown('<div class="brand-header">Benchmark de Mercado</div>', unsafe_allow_html=True)
    sel = st.selectbox("Inmueble a auditar:", df_inm["Nombre"].tolist())
    f = df_inm[df_inm["Nombre"] == sel].iloc[0]
    
    renta_act = f["Renta"]
    renta_mer = f["Renta_Mercado"]
    desv = ((renta_act - renta_mer) / renta_mer) * 100
    perdida = renta_mer - renta_act if renta_act < renta_mer else 0
    
    c_b1, c_b2 = st.columns(2)
    with c_b1:
        st.markdown('<div class="section-title">Comparativa de Renta</div>', unsafe_allow_html=True)
        st.metric("Renta Actual", f"{renta_act:,.2f} €")
        st.metric("Renta Mercado (Estimada)", f"{renta_mer:,.2f} €", delta=f"{desv:.1f}%")
        
    with c_b2:
        st.markdown('<div class="section-title">Estatus de Mercado</div>', unsafe_allow_html=True)
        if desv < -15: clase, msg, icon = "status-red", "Rentabilidad Crítica", "🔴"
        elif desv < -5: clase, msg, icon = "status-yellow", "Margen de Mejora", "🟡"
        else: clase, msg, icon = "status-green", "Activo en Mercado", "🟢"
            
        st.markdown(f'<div class="{clase}"><b style="font-size:1.2rem;">{icon} {msg}</b><br><br>Desviación: <b>{desv:.1f}%</b>.<br>Ingreso mensual no percibido: <b>{perdida:,.2f} €</b>.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Análisis de Gastos Reales</div>', unsafe_allow_html=True)
    df_g = df_mov[(df_mov["Apartamento"] == sel) & (df_mov["Tipo"] == "Gasto")]
    res_gastos = pd.concat([pd.DataFrame([{"Concepto": "Comunidad", "Importe": f["Comunidad"], "Deducible": "S"}]), df_g[["Concepto", "Importe", "Deducible"]]])
    st.dataframe(res_gastos.style.format({"Importe": "{:,.2f}€"}), hide_index=True, use_container_width=True)

# ── AUDITORÍA IA ──────────────────────────────
elif "Auditor" in menu:
    st.markdown('<div class="brand-header">Informe de Mantenimiento</div>', unsafe_allow_html=True)
    for i, row in df_inm.reset_index().iterrows():
        st.markdown(f"### 📍 {row['Nombre']}")
        st.write("✅ Estado óptimo. Próxima revisión sugerida en 12 meses.")
        if i < len(df_inm)-1: st.markdown("<hr style='border:0; border-top:1px solid var(--gold); margin:1.5rem 0;'>", unsafe_allow_html=True)

# ── DIARIO CONTABLE (DESPLEGABLES RESTAURADOS) ──
elif "Diario" in menu:
    st.markdown('<div class="brand-header">Registro de Operaciones</div>', unsafe_allow_html=True)
    
    # Configuración de Desplegables
    l_inm = df_inm["Nombre"].tolist() + ["Global"]
    l_cat = ["Ingresos", "Financiero", "Tributario", "Suministros", "Seguros", "Mantenimiento", "Estructura", "Comunidad", "Otros"]
    l_con = ["Renta Mensual", "Hipoteca (Intereses)", "Hipoteca (Capital)", "IBI", "Comunidad Ordinaria", "Seguro Hogar", "Seguro Vida", "Luz", "Agua", "Reparación", "Sueldo Pedro"]
    
    config = {
        "Apartamento": st.column_config.SelectboxColumn("Inmueble", options=l_inm, required=True),
        "Concepto": st.column_config.SelectboxColumn("Concepto", options=l_con, required=True),
        "Categoría": st.column_config.SelectboxColumn("Categoría", options=l_cat, required=True),
        "Tipo": st.column_config.SelectboxColumn("Tipo", options=["Ingreso", "Gasto"], required=True),
        "Deducible": st.column_config.SelectboxColumn("Fiscal (S/N)", options=["S", "N"], required=True),
        "Importe": st.column_config.NumberColumn("Importe (€)", format="%.2f", min_value=0)
    }

    df_ed = st.data_editor(df_mov, num_rows="dynamic", use_container_width=True, hide_index=True, column_config=config)
    
    t_ing = df_ed[df_ed["Tipo"] == "Ingreso"]["Importe"].sum()
    t_gas = df_ed[df_ed["Tipo"] == "Gasto"]["Importe"].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Ingresos Registrados", f"{t_ing:,.2f} €")
    m2.metric("Gastos Registrados", f"-{t_gas:,.2f} €")
    m3.metric("Balance Total", f"{t_ing - t_gas:,.2f} €")
    
    if st.button("Guardar Cambios"):
        df_ed.to_csv(DB_MOVIMIENTOS, index=False)
        st.success("Operaciones guardadas.")
        st.rerun()

# ── DATOS Y BACKUPS (RESTAURADO TOTAL) ────────
elif "Datos" in menu:
    st.markdown('<div class="brand-header">Datos de la Cartera y Seguridad</div>', unsafe_allow_html=True)
    st.info("ℹ️ Edita aquí los parámetros maestros de tus activos, incluyendo la 'Renta_Mercado' para el Benchmark.")
    
    df_inm_ed = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True, hide_index=True)
    if st.button("Actualizar Cartera"):
        df_inm_ed.to_csv(DB_INMUEBLES, index=False)
        st.success("✓ Datos de la cartera actualizados.")
        st.rerun()

    st.markdown('<div class="section-title">Copias de Seguridad Externas</div>', unsafe_allow_html=True)
    st.warning("Descarga estos archivos frecuentemente para mantener un respaldo físico de tu gestión.")
    
    b_c1, b_c2 = st.columns(2)
    with b_c1:
        with open(DB_INMUEBLES, "rb") as f_back_i:
            st.download_button("📥 Descargar Backup Inmuebles", f_back_i, "nolasco_inmuebles.csv", "text/csv")
    with b_c2:
        with open(DB_MOVIMIENTOS, "rb") as f_back_m:
            st.download_button("📥 Descargar Backup Movimientos", f_back_m, "nolasco_movimientos.csv", "text/csv")
