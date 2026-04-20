import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────
# 1. DISEÑO DE INTERFAZ "NOLASCO COUTURE"
# ─────────────────────────────────────────────
st.set_page_config(page_title="Nolasco Capital", layout="wide", page_icon="🏛️")

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

/* Fondo y Fuente Global */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--parchment) !important;
    color: var(--ink);
}

/* BARRA LATERAL PERSONALIZADA */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
    border-right: 1px solid #222;
    min-width: 300px !important;
}

/* Estilo del Menú en la Barra Lateral */
[data-testid="stSidebar"] .stRadio > label { display: none; } /* Ocultar label radio */

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    padding-top: 2rem;
    gap: 1.5rem;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* Tipografía DM Serif para el menú */
[data-testid="stSidebar"] .stRadio p {
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.4rem !important;
    color: #E8E2D9 !important;
    letter-spacing: 0.03em !important;
    transition: all 0.4s ease;
    padding-left: 1rem;
    border-left: 0px solid var(--gold);
}

[data-testid="stSidebar"] .stRadio label[data-checked="true"] p {
    color: var(--gold) !important;
    border-left: 4px solid var(--gold);
    padding-left: 1.5rem;
}

/* Header y Componentes */
.brand-header { font-family: 'DM Serif Display', serif; font-size: 2.5rem; color: var(--ink); border-bottom: 2px solid var(--gold); padding-bottom: 0.5rem; margin-bottom: 0.2rem; }
.brand-sub { font-size: 0.8rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--slate); margin-bottom: 2rem; }

.kpi-card { background: var(--card-bg); border: 1px solid var(--border); border-top: 3px solid var(--gold); border-radius: 4px; padding: 1.5rem; text-align: center; }
.kpi-value { font-family: 'DM Serif Display', serif; font-size: 2.2rem; line-height: 1; }

.fiscal-panel { background: #F0F7F3; border: 1px solid #C3DDD0; border-radius: 6px; padding: 1.5rem; }
.ai-card { background: var(--ink); color: #F0EAD6; border-radius: 8px; padding: 1.5rem; border-left: 5px solid var(--gold); margin-bottom: 1rem; }

/* Ocultar elementos de Streamlit */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. MOTOR DE DATOS (NUEVAS COLUMNAS PREDICTIVAS)
# ─────────────────────────────────────────────
DB_INMUEBLES   = "nolasco_inmuebles_v5.csv"
DB_MOVIMIENTOS = "nolasco_movimientos_v5.csv"

def inicializar_bd(force=False):
    if force or not os.path.exists(DB_INMUEBLES):
        pd.DataFrame([
            {"Nombre": "Casa Abarqueros", "Inquilino": "Victor Aguiluz", "Renta": 2200.0, "Comunidad": 193.76, "Valor_Construccion": 150000.0, "Año_Reforma": 2018, "Mobiliario": "S", "Tipo": "Casa"},
            {"Nombre": "Paseo del Salón", "Inquilino": "Pool Despachos", "Renta": 1591.8, "Comunidad": 175.18, "Valor_Construccion": 120000.0, "Año_Reforma": 2020, "Mobiliario": "N", "Tipo": "Piso"},
            {"Nombre": "Huerto Unidad 1", "Inquilino": "Alain", "Renta": 660.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0, "Año_Reforma": 2022, "Mobiliario": "S", "Tipo": "Piso"},
            {"Nombre": "Huerto Unidad 2", "Inquilino": "Laura/Alex", "Renta": 800.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0, "Año_Reforma": 2022, "Mobiliario": "S", "Tipo": "Piso"},
            {"Nombre": "Huerto Unidad 3", "Inquilino": "Jose Manuel", "Renta": 850.0, "Comunidad": 74.63, "Valor_Construccion": 45000.0, "Año_Reforma": 2021, "Mobiliario": "S", "Tipo": "Piso"}
        ]).to_csv(DB_INMUEBLES, index=False)
    
    if force or not os.path.exists(DB_MOVIMIENTOS):
        pd.DataFrame([
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Hipoteca (Capital/Interés)", "Categoría": "Financiero", "Tipo": "Gasto", "Importe": 554.73, "Deducible": "N"},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Seguro MyBox", "Categoría": "Seguros", "Tipo": "Gasto", "Importe": 96.43, "Deducible": "S"},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Mantenimiento Ascensor", "Categoría": "Mantenimiento", "Tipo": "Gasto", "Importe": 65.44, "Deducible": "S"},
            {"Fecha": "2026-04-01", "Apartamento": "Global", "Concepto": "Sueldo Pedro", "Categoría": "Personal", "Tipo": "Gasto", "Importe": 600.00, "Deducible": "N"}
        ]).to_csv(DB_MOVIMIENTOS, index=False)

inicializar_bd()
df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)

# ─────────────────────────────────────────────
# 3. NAVEGACIÓN Y ESTRUCTURA
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding-bottom: 2rem;'>
        <div style='font-family:"DM Serif Display",serif; font-size:2.2rem; color:#C9A84C; line-height:1;'>NOLASCO</div>
        <div style='font-size:0.7rem; letter-spacing:0.3em; color:#888; text-transform:uppercase;'>Capital Management</div>
    </div>
    """, unsafe_allow_html=True)
    
    menu = st.radio("", ["📊 Torre de Control", "🏠 Fichas de Activos", "🤖 Auditoría IA", "📝 Diario Contable", "⚙️ Configuración"], label_visibility="collapsed")

# ── TORRE DE CONTROL ──────────────────────────
if "Torre" in menu:
    st.markdown('<div class="brand-header">Torre de Control</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Cartera Consolidada</div>', unsafe_allow_html=True)
    
    ing_b = df_inm["Renta"].sum()
    gas_caja = df_mov[df_mov["Tipo"]=="Gasto"]["Importe"].sum() + df_inm["Comunidad"].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-label">Ingreso Bruto</div><div class="kpi-value">{ing_b:,.0f}€</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-label">Salida de Caja</div><div class="kpi-value" style="color:var(--crimson)">-{gas_caja:,.0f}€</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-label">Resultado Neto</div><div class="kpi-value" style="color:var(--emerald)">{ing_b - gas_caja:,.0f}€</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Rentabilidad por Activo</div>', unsafe_allow_html=True)
    cols = st.columns(len(df_inm))
    for i, row in df_inm.iterrows():
        g_esp = df_mov[(df_mov["Apartamento"] == row["Nombre"])]["Importe"].sum()
        with cols[i]:
            st.markdown(f"""
            <div class="asset-card">
                <div class="asset-name">{row['Nombre']}</div>
                <div class="asset-income">+{row['Renta']:,.0f}€</div>
                <div class="asset-expense">-{row['Comunidad']+g_esp:,.0f}€</div>
                <div class="asset-net">{row['Renta'] - row['Comunidad'] - g_esp:,.0f}€</div>
            </div>""", unsafe_allow_html=True)

# ── FICHAS DE ACTIVOS (NUEVA ANALÍTICA) ───────
elif "Fichas" in menu:
    st.markdown('<div class="brand-header">Fichas de Activos</div>', unsafe_allow_html=True)
    sel = st.selectbox("Seleccionar Inmueble:", df_inm["Nombre"].tolist())
    f = df_inm[df_inm["Nombre"] == sel].iloc[0]
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown(f"### Detalle: {sel}")
        # Gastos de Caja
        df_g = df_mov[df_mov["Apartamento"] == sel]
        resumen = pd.concat([pd.DataFrame([{"Concepto": "Comunidad", "Importe": f["Comunidad"], "Deducible": "S"}]), df_g[["Concepto", "Importe", "Deducible"]]])
        st.table(resumen.style.format({"Importe": "{:,.2f}€"}))
        
    with col_b:
        st.markdown('<div class="fiscal-panel">', unsafe_allow_html=True)
        st.markdown("### ⚖️ Balance Fiscal vs Caja")
        total_caja = resumen["Importe"].sum()
        total_deducible = resumen[resumen["Deducible"]=="S"]["Importe"].sum()
        amort = (f["Valor_Construccion"] * 0.03) / 12
        
        st.write(f"**Gasto Total (Caja):** {total_caja:,.2f}€")
        st.write(f"**Gasto Deducible:** {total_deducible:,.2f}€")
        st.write(f"**Amortización Fiscal:** {amort:,.2f}€")
        st.divider()
        st.write(f"**Base Imponible Mensual:** {f['Renta'] - total_deducible - amort:,.2f}€")
        st.markdown('</div>', unsafe_allow_html=True)

# ── AUDITORÍA IA (PREDICTIVA PISO A PISO) ─────
elif "Auditor" in menu:
    st.markdown('<div class="brand-header">Auditoría Automática</div>', unsafe_allow_html=True)
    año_actual = datetime.now().year
    
    for _, row in df_inm.iterrows():
        with st.container():
            st.markdown(f'<div class="ai-card">', unsafe_allow_html=True)
            st.markdown(f"### 📍 {row['Nombre']}")
            
            # Lógica Algorítmica de IA
            consejos = []
            if año_actual - row["Año_Reforma"] > 6:
                consejos.append(f"🎨 **Pintura:** Han pasado {año_actual - row['Año_Reforma']} años. Toca renovar estética para mantener valor de renta.")
            
            if row["Mobiliario"] == "S":
                consejos.append("🔌 **Electrodomésticos:** Activo amueblado. Reservar 15€/mes para fondo de reposición (Lavadora/Frigorífico).")
            
            if row["Tipo"] == "Casa":
                consejos.append("🏠 **Estructura:** Revisión de tejados y bajantes recomendada antes de invierno.")
            
            if not consejos: consejos.append("✅ Activo en ciclo óptimo de mantenimiento.")
            
            st.write("  \n".join(consejos))
            st.markdown('</div>', unsafe_allow_html=True)

# ── DIARIO Y CONFIGURACIÓN (CRUD) ─────────────
elif "Diario" in menu:
    st.markdown('<div class="brand-header">Diario Contable</div>', unsafe_allow_html=True)
    df_ed = st.data_editor(df_mov, num_rows="dynamic", use_container_width=True)
    if st.button("Guardar Cambios"):
        df_ed.to_csv(DB_MOVIMIENTOS, index=False)
        st.rerun()

elif "Config" in menu:
    st.markdown('<div class="brand-header">Configuración Máster</div>', unsafe_allow_html=True)
    st.write("Edita aquí los parámetros de los inmuebles (Años de reforma, Valor de construcción, etc.)")
    df_inm_ed = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True)
    if st.button("Actualizar Cartera"):
        df_inm_ed.to_csv(DB_INMUEBLES, index=False)
        st.rerun()
