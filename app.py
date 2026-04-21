import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────
# 1. ARQUITECTURA VISUAL "NOLASCO CAPITAL V9.5"
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

.block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: var(--parchment) !important; color: var(--ink); }

/* BARRA LATERAL */
[data-testid="stSidebar"] { background: var(--ink) !important; border-right: 1px solid #222; min-width: 280px !important; }
[data-testid="stSidebar"] .stRadio p { color: #ADB5BD !important; padding-left: 1rem; transition: all 0.3s; }
[data-testid="stSidebar"] .stRadio label[data-checked="true"] p { color: var(--gold) !important; border-left: 3px solid var(--gold); padding-left: 1.2rem; }

/* CABECERAS Y TARJETAS */
.brand-header { font-family: 'DM Serif Display', serif; font-size: 2.3rem; color: var(--ink); border-bottom: 2px solid var(--gold); padding-bottom: 0.5rem; margin-bottom: 1.5rem; }
.section-title { font-family: 'DM Serif Display', serif; font-size: 1.5rem; color: var(--ink); border-left: 3px solid var(--gold); padding-left: 0.7rem; margin: 2rem 0 1rem 0; }

.kpi-card { background: var(--card-bg); border: 1px solid var(--border); border-top: 3px solid var(--gold); border-radius: 4px; padding: 1.2rem; text-align: center; }
.kpi-label { font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--slate); margin-bottom: 0.2rem; }
.kpi-value { font-family: 'DM Serif Display', serif; font-size: 2rem; line-height: 1; }

/* STATUS BOXES */
.status-red { background: #FDECEA; border-left: 5px solid var(--crimson); padding: 1.5rem; border-radius: 4px; }
.status-yellow { background: #FFF9E6; border-left: 5px solid #F39C12; padding: 1.5rem; border-radius: 4px; }
.status-green { background: #EDF7F1; border-left: 5px solid var(--emerald); padding: 1.5rem; border-radius: 4px; }

.tech-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
.tech-table td { padding: 8px; border-bottom: 1px solid #eee; font-size: 0.9rem; }
.tech-label { font-weight: 600; color: var(--slate); width: 40%; }

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. MOTOR DE DATOS (CONSOLIDADO)
# ─────────────────────────────────────────────
DB_INMUEBLES   = "nolasco_inmuebles_v9.csv"
DB_MOVIMIENTOS = "nolasco_movimientos_v9.csv"

def inicializar_bd(force=False):
    # Aseguramos que la fecha es fija: 2026-04-01
    if force or not os.path.exists(DB_INMUEBLES):
        pd.DataFrame([
            {"Nombre": "Casa Abarqueros", "Inquilino": "Victor Aguiluz", "Renta": 2200.0, "Renta_Mercado": 2600.0, "Comunidad": 193.76, "m2": 180, "Dorm": 4, "Baños": 3, "Estado": "Buen estado", "Tipo": "Casa", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Paseo del Salón", "Inquilino": "Pool Despachos", "Renta": 1591.8, "Renta_Mercado": 1650.0, "Comunidad": 175.18, "m2": 120, "Dorm": 3, "Baños": 2, "Estado": "Reformado", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 1", "Inquilino": "Alain", "Renta": 660.0, "Renta_Mercado": 800.0, "Comunidad": 74.62, "m2": 45, "Dorm": 1, "Baños": 1, "Estado": "Lujo", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 2", "Inquilino": "Laura/Alex", "Renta": 800.0, "Renta_Mercado": 800.0, "Comunidad": 74.62, "m2": 45, "Dorm": 1, "Baños": 1, "Estado": "Lujo", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 3", "Inquilino": "Jose Manuel", "Renta": 850.0, "Renta_Mercado": 800.0, "Comunidad": 74.63, "m2": 45, "Dorm": 1, "Baños": 1, "Estado": "Lujo", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 4", "Inquilino": "Pendiente", "Renta": 600.0, "Renta_Mercado": 800.0, "Comunidad": 74.62, "m2": 45, "Dorm": 1, "Baños": 1, "Estado": "En reforma", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"}
        ]).to_csv(DB_INMUEBLES, index=False)
    
    if force or not os.path.exists(DB_MOVIMIENTOS):
        pd.DataFrame([
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Renta Mensual", "Categoría": "Ingresos", "Tipo": "Ingreso", "Importe": 2200.00, "Deducible": "N"},
            {"Fecha": "2026-04-01", "Apartamento": "Paseo del Salón", "Concepto": "I.B.I.", "Categoría": "Tributario", "Tipo": "Gasto", "Importe": 450.00, "Deducible": "S"}
        ]).to_csv(DB_MOVIMIENTOS, index=False)

inicializar_bd()
df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)

# ─────────────────────────────────────────────
# 3. NAVEGACIÓN
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='padding-bottom: 1rem;'><div style='font-family:\"DM Serif Display\",serif; font-size:2.2rem; color:#C9A84C; line-height:1;'>NOLASCO</div></div>", unsafe_allow_html=True)
    menu = st.radio("", ["📊 Torre de Control", "🏠 Fichas Técnicas", "📝 Diario Contable", "📂 Datos y Plantillas"], label_visibility="collapsed")

# ── TORRE DE CONTROL (RESTAURADA COMPLETA) ────
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
                <div style="font-family:'DM Serif Display',serif; font-size:1.45rem; color:#D35400; border-top:1px solid #eee; margin-top:8px; padding-top:5px;">{beneficio_unit:,.0f}€</div>
            </div>""", unsafe_allow_html=True)

    # RE-INTRODUCCIÓN DE LA TARTA Y TABLA DE GASTOS
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-title">Análisis de Gastos</div>', unsafe_allow_html=True)
        df_cat = df_mov[df_mov["Tipo"]=="Gasto"].groupby("Categoría")["Importe"].sum().reset_index()
        if not df_cat.empty:
            st.dataframe(df_cat.style.format({"Importe": "{:,.2f} €"}), hide_index=True, use_container_width=True)
        else:
            st.info("No hay gastos adicionales registrados este mes.")
    
    with col_r:
        st.markdown('<div class="section-title">Composición de Rentas</div>', unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=df_inm["Nombre"], values=df_inm["Renta"], hole=0.4, 
            marker=dict(colors=COLOR_PALETTE), textinfo="label+percent"
        ))
        fig_pie.update_layout(margin=dict(l=20,r=20,t=20,b=20), showlegend=False, height=350, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)

# ── FICHAS TÉCNICAS (CONBenchmark) ───────────
elif "Fichas" in menu:
    st.markdown('<div class="brand-header">Auditoría Técnica y Benchmark</div>', unsafe_allow_html=True)
    sel = st.selectbox("Inmueble a analizar:", df_inm["Nombre"].tolist())
    f = df_inm[df_inm["Nombre"] == sel].iloc[0]
    
    c_f1, c_f2 = st.columns([1, 1.2])
    with c_f1:
        st.markdown('<div class="section-title">Ficha del Activo</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <table class="tech-table">
            <tr><td class="tech-label">Tipología</td><td>{f['Tipo']}</td></tr>
            <tr><td class="tech-label">Superficie</td><td>{f['m2']} m²</td></tr>
            <tr><td class="tech-label">Dormitorios</td><td>{f['Dorm']} hab.</td></tr>
            <tr><td class="tech-label">Estado</td><td>{f['Estado']}</td></tr>
            <tr><td class="tech-label">Comunidad</td><td>{f['Comunidad']} €/mes</td></tr>
        </table>
        """, unsafe_allow_html=True)

    with c_f2:
        st.markdown('<div class="section-title">Estatus de Mercado</div>', unsafe_allow_html=True)
        renta_act, renta_mer = f["Renta"], f["Renta_Mercado"]
        desv = ((renta_act - renta_mer) / renta_mer) * 100
        perdida_anual = (renta_mer - renta_act) * 12 if renta_act < renta_mer else 0
        
        if desv < -15: clase, msg, icon = "status-red", "Rentabilidad Crítica", "🔴"
        elif desv < -5: clase, msg, icon = "status-yellow", "Margen de Mejora", "🟡"
        else: clase, msg, icon = "status-green", "Activo en Mercado", "🟢"

        st.markdown(f"""
        <div class="{clase}">
            <b style="font-size:1.2rem;">{icon} {msg}</b><br>
            Desviación: <b>{desv:.1f}%</b>.<br><br>
            {f'📉 <b>Lucro Cesante:</b> estás perdiendo <b style="color:var(--crimson);">{perdida_anual:,.2f}€/año</b>' if perdida_anual > 0 else '✓ Óptima gestión de renta.'}
        </div>
        """, unsafe_allow_html=True)

# ── DIARIO Y DATOS ────────────────────────────
elif "Diario" in menu:
    st.markdown('<div class="brand-header">Registro de Operaciones</div>', unsafe_allow_html=True)
    df_ed = st.data_editor(df_mov, num_rows="dynamic", use_container_width=True, hide_index=True)
    if st.button("Guardar Cambios"):
        df_ed.to_csv(DB_MOVIMIENTOS, index=False)
        st.success("✓ Operaciones guardadas.")
        st.rerun()

elif "Datos" in menu:
    st.markdown('<div class="brand-header">Gestión Masiva</div>', unsafe_allow_html=True)
    df_inm_ed = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True, hide_index=True)
    if st.button("Actualizar Cartera"):
        df_inm_ed.to_csv(DB_INMUEBLES, index=False)
        st.success("✓ Cartera actualizada.")
        st.rerun()
