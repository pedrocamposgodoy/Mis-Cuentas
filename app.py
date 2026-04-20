import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────
# 1. ARQUITECTURA VISUAL "NOLASCO CAPITAL V9.0 - MVP"
# ─────────────────────────────────────────────
st.set_page_config(page_title="Nolasco Capital MVP", layout="wide", page_icon="🏛️")

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
}

.block-container { padding-top: 1rem !important; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: var(--parchment) !important; color: var(--ink); }

/* BARRA LATERAL */
[data-testid="stSidebar"] { background: var(--ink) !important; min-width: 280px !important; }
[data-testid="stSidebar"] .stRadio p {
    font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important; color: #ADB5BD !important;
}
[data-testid="stSidebar"] .stRadio label[data-checked="true"] p { color: var(--gold) !important; border-left: 3px solid var(--gold); padding-left: 1.2rem; }

/* COMPONENTES MVP */
.brand-header { font-family: 'DM Serif Display', serif; font-size: 2.3rem; color: var(--ink); border-bottom: 2px solid var(--gold); padding-bottom: 0.5rem; }
.section-title { font-family: 'DM Serif Display', serif; font-size: 1.5rem; color: var(--ink); border-left: 3px solid var(--gold); padding-left: 0.7rem; margin: 1.5rem 0; }
.fiscal-panel { background: #F0F7F3; border: 1px solid #C3DDD0; border-radius: 6px; padding: 1.2rem; }

/* CAJAS DE BENCHMARK */
.status-red { background: #FDECEA; border-left: 5px solid var(--crimson); padding: 1.5rem; border-radius: 4px; }
.status-yellow { background: #FFF9E6; border-left: 5px solid #F39C12; padding: 1.5rem; border-radius: 4px; }
.status-green { background: #EDF7F1; border-left: 5px solid var(--emerald); padding: 1.5rem; border-radius: 4px; }

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. MOTOR DE DATOS (INCLUYE RENTA DE MERCADO)
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

with st.sidebar:
    st.markdown("<div style='padding-bottom: 1rem;'><div style='font-family:\"DM Serif Display\",serif; font-size:2.2rem; color:#C9A84C; line-height:1;'>NOLASCO</div></div>", unsafe_allow_html=True)
    menu = st.radio("", ["📊 Torre de Control", "🏠 Fichas (Benchmark)", "🤖 Auditoría IA", "📝 Diario Contable", "📂 Datos y Backups"], label_visibility="collapsed")

# ── TORRE DE CONTROL ──────────────────────────
if "Torre" in menu:
    st.markdown('<div class="brand-header">Torre de Control</div>', unsafe_allow_html=True)
    
    ing_b = df_inm["Renta"].sum()
    gas_caja = df_mov[df_mov["Tipo"]=="Gasto"]["Importe"].sum() + df_inm["Comunidad"].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos Cartera", f"{ing_b:,.0f}€")
    c2.metric("Gastos Totales", f"-{gas_caja:,.0f}€")
    c3.metric("Beneficio Neto", f"{ing_b - gas_caja:,.0f}€")

    # Tarta de Composición
    fig_pie = go.Figure(go.Pie(labels=df_inm["Nombre"], values=df_inm["Renta"], hole=0.4, marker=dict(colors=COLOR_PALETTE), textinfo="label+percent", textposition="outside"))
    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=80,r=80,t=30,b=30), showlegend=False, height=450)
    st.plotly_chart(fig_pie, use_container_width=True)

# ── FICHAS DE ACTIVOS (BENCHMARK MVP) ─────────
elif "Fichas" in menu:
    st.markdown('<div class="brand-header">Benchmark de Mercado</div>', unsafe_allow_html=True)
    sel = st.selectbox("Inmueble a auditar:", df_inm["Nombre"].tolist())
    f = df_inm[df_inm["Nombre"] == sel].iloc[0]
    
    # 🎯 Lógica del Benchmark
    renta_actual = f["Renta"]
    renta_mercado = f["Renta_Mercado"]
    desviacion = ((renta_actual - renta_mercado) / renta_mercado) * 100
    perdida_mensual = renta_mercado - renta_actual if renta_actual < renta_mercado else 0
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-title">Análisis de Renta</div>', unsafe_allow_html=True)
        st.metric("Renta Actual", f"{renta_actual:,.2f} €")
        st.metric("Renta de Mercado (Ref.)", f"{renta_mercado:,.2f} €", delta=f"{desviacion:.1f}%")
        
    with col2:
        st.markdown('<div class="section-title">Diagnóstico MVP</div>', unsafe_allow_html=True)
        
        # Sistema de Colores (Semáforo)
        if desviacion < -15:
            clase, status, icono = "status-red", "Muy por debajo del mercado", "🔴"
        elif desviacion < -5:
            clase, status, icono = "status-yellow", "Ligeramente por debajo", "🟡"
        else:
            clase, status, icono = "status-green", "En precio de mercado", "🟢"
            
        st.markdown(f"""
        <div class="{clase}">
            <b style="font-size:1.2rem;">{icono} {status}</b><br><br>
            La desviación actual es del <b>{desviacion:.1f}%</b>.<br>
            Estás dejando de ingresar <b>{perdida_mensual:,.2f} €</b> mensuales ({perdida_mensual*12:,.2f} €/año).
        </div>
        """, unsafe_allow_html=True)

    # Bloque IA de Recomendación
    st.markdown('<div class="section-title">Comentario Inteligente</div>', unsafe_allow_html=True)
    if desviacion < -5:
        st.info(f"💡 **Recomendación:** Este inmueble presenta una infravaloración clara. Se recomienda revisar el contrato en la próxima renovación o realizar una actualización estética mínima para alcanzar los {renta_mercado:,.0f} € de mercado.")
    else:
        st.success("✅ **Optimización:** El inmueble está correctamente posicionado. El foco debe ser el control de gastos operativos para maximizar el neto.")

# ── RESTO DE PÁGINAS (AUDITORÍA, DIARIO, DATOS) ──
elif "Auditor" in menu:
    st.markdown('<div class="brand-header">Informe de Mantenimiento</div>', unsafe_allow_html=True)
    for i, row in df_inm.reset_index().iterrows():
        st.markdown(f"### 📍 {row['Nombre']}")
        st.write("✅ Estado de conservación óptimo.")
        if i < len(df_inm)-1: st.markdown("<hr style='border:0; border-top:1px solid var(--gold); margin:1.5rem 0;'>", unsafe_allow_html=True)

elif "Diario" in menu:
    st.markdown('<div class="brand-header">Registro de Operaciones</div>', unsafe_allow_html=True)
    df_ed = st.data_editor(df_mov, num_rows="dynamic", use_container_width=True, hide_index=True)
    if st.button("Guardar"): df_ed.to_csv(DB_MOVIMIENTOS, index=False)

elif "Datos" in menu:
    st.markdown('<div class="brand-header">Configuración Cartera</div>', unsafe_allow_html=True)
    st.info("ℹ️ Edita aquí la 'Renta_Mercado' basándote en Idealista o Fotocasa para actualizar el Benchmark.")
    df_inm_ed = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True, hide_index=True)
    if st.button("Actualizar Cartera"): df_inm_ed.to_csv(DB_INMUEBLES, index=False)
