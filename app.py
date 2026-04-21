import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# 1. ARQUITECTURA VISUAL "NOLASCO CAPITAL V9.7 - GOLDEN VERSION"
# ─────────────────────────────────────────────
st.set_page_config(page_title="Nolasco Capital", layout="wide", page_icon="🏛️")

COLOR_PALETTE = ["#C9A84C", "#1B5E3B", "#8B1A1A", "#4A5568", "#0D0F12", "#2E86C1"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
:root {
    --ink: #0D0F12; --parchment: #F7F4EF; --gold: #C9A84C;
    --emerald: #1B5E3B; --crimson: #8B1A1A; --slate: #4A5568;
    --card-bg: #FFFFFF; --border: #E8E2D9;
}
.block-container { padding-top: 1rem !important; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: var(--parchment) !important; color: var(--ink); }
[data-testid="stSidebar"] { background: var(--ink) !important; min-width: 280px !important; }
.brand-header { font-family: 'DM Serif Display', serif; font-size: 2.3rem; border-bottom: 2px solid var(--gold); margin-bottom: 1.5rem; }
.section-title { font-family: 'DM Serif Display', serif; font-size: 1.5rem; border-left: 3px solid var(--gold); padding-left: 0.7rem; margin: 2rem 0 1rem 0; }
.kpi-card { background: var(--card-bg); border: 1px solid var(--border); border-top: 3px solid var(--gold); border-radius: 4px; padding: 1.2rem; text-align: center; }
.status-red { background: #FDECEA; border-left: 5px solid var(--crimson); padding: 1.5rem; border-radius: 4px; }
.status-yellow { background: #FFF9E6; border-left: 5px solid #F39C12; padding: 1.5rem; border-radius: 4px; }
.status-green { background: #EDF7F1; border-left: 5px solid var(--emerald); padding: 1.5rem; border-radius: 4px; }
.tech-table { width: 100%; border-collapse: collapse; }
.tech-table td { padding: 8px; border-bottom: 1px solid #eee; font-size: 0.9rem; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. MOTOR DE DATOS (RESTAURADO Y SINCRONIZADO)
# ─────────────────────────────────────────────
DB_INMUEBLES = "nolasco_inmuebles_v9.csv"
DB_MOVIMIENTOS = "nolasco_movimientos_v9.csv"

def inicializar_bd(force=False):
    if force or not os.path.exists(DB_INMUEBLES):
        pd.DataFrame([
            {"Nombre": "Casa Abarqueros", "Titular": "Pedro Nolasco", "Ref_Catastral": "", "Tipo": "Casa", "m2": 180, "Dorm": 4, "Baños": 3, "Estado": "Buen estado", "Inquilino": "Victor A.", "Renta": 2200.0, "Renta_Mercado": 2600.0, "Comunidad": 193.76, "IBI_Anual": 650.0, "Seguro_Hogar": 240.0, "Seguro_Vida": 180.0, "Intereses_Pres": 450.0, "Amortiz_Pres": 800.0},
            {"Nombre": "Paseo del Salón", "Titular": "Pedro Nolasco", "Ref_Catastral": "", "Tipo": "Piso", "m2": 120, "Dorm": 3, "Baños": 2, "Estado": "Reformado", "Inquilino": "Pool Desp.", "Renta": 1591.8, "Renta_Mercado": 1650.0, "Comunidad": 175.18, "IBI_Anual": 450.0, "Seguro_Hogar": 200.0, "Seguro_Vida": 150.0, "Intereses_Pres": 0.0, "Amortiz_Pres": 0.0},
        ]).to_csv(DB_INMUEBLES, index=False)
    
    if force or not os.path.exists(DB_MOVIMIENTOS):
        pd.DataFrame([
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Renta Mensual", "Categoría": "Ingresos", "Tipo": "Ingreso", "Importe": 2200.00, "Deducible": "N"}
        ]).to_csv(DB_MOVIMIENTOS, index=False)

if os.path.exists(DB_INMUEBLES):
    if "IBI_Anual" not in pd.read_csv(DB_INMUEBLES).columns: inicializar_bd(force=True)
else: inicializar_bd()

df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)

# ─────────────────────────────────────────────
# 3. INTERFAZ Y NAVEGACIÓN
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='font-family:\"DM Serif Display\",serif; font-size:2.2rem; color:#C9A84C;'>NOLASCO</div>", unsafe_allow_html=True)
    menu = st.radio("", ["📊 Torre de Control", "🏠 Fichas Técnicas", "📝 Diario Contable", "📂 Datos y Backups"], label_visibility="collapsed")

# 📊 TORRE DE CONTROL (RESTAURADA)
if "Torre" in menu:
    st.markdown('<div class="brand-header">Torre de Control</div>', unsafe_allow_html=True)
    
    ing_b = df_inm["Renta"].sum()
    gas_fijos = (df_inm["Comunidad"].sum() + (df_inm["IBI_Anual"].sum()/12) + (df_inm["Seguro_Hogar"].sum()/12))
    gas_var = df_mov[df_mov["Tipo"]=="Gasto"]["Importe"].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="kpi-card">INGRESOS TOTALES<div style="font-family:DM Serif Display; font-size:2.2rem; color:var(--emerald)">{ing_b:,.0f}€</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card">COSTES ESTIMADOS<div style="font-family:DM Serif Display; font-size:2.2rem; color:var(--crimson)">-{(gas_fijos + gas_var):,.0f}€</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card">NETO OPERATIVO<div style="font-family:DM Serif Display; font-size:2.2rem;">{ing_b - gas_fijos - gas_var:,.0f}€</div></div>', unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-title">Composición de Rentas</div>', unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(labels=df_inm["Nombre"], values=df_inm["Renta"], hole=0.4, marker=dict(colors=COLOR_PALETTE)))
        fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=350, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_r:
        st.markdown('<div class="section-title">Análisis de Gastos Mensuales</div>', unsafe_allow_html=True)
        gastos_data = {
            "Concepto": ["Comunidades", "IBI (Prorrateado)", "Seguros (Prorrateado)", "Gastos Variables"],
            "Importe": [df_inm["Comunidad"].sum(), df_inm["IBI_Anual"].sum()/12, df_inm["Seguro_Hogar"].sum()/12, gas_var]
        }
        st.table(pd.DataFrame(gastos_data).style.format({"Importe": "{:,.2f} €"}))

# 🏠 FICHAS TÉCNICAS (CON LUCRO CESANTE EXTENDIDO)
elif "Fichas" in menu:
    st.markdown('<div class="brand-header">Auditoría de Activos</div>', unsafe_allow_html=True)
    sel = st.selectbox("Seleccione inmueble:", df_inm["Nombre"].tolist())
    f = df_inm[df_inm["Nombre"] == sel].iloc[0]
    
    c1, c2 = st.columns([1, 1.3])
    with c1:
        st.markdown('<div class="section-title">Ficha Técnica</div>', unsafe_allow_html=True)
        st.markdown(f"""<table class="tech-table">
            <tr><td><b>Superficie</b></td><td>{f['m2']} m²</td></tr>
            <tr><td><b>Dormitorios</b></td><td>{f['Dorm']} hab.</td></tr>
            <tr><td><b>Estado</b></td><td>{f['Estado']}</td></tr>
            <tr><td><b>Inquilino</b></td><td>{f['Inquilino']}</td></tr>
            <tr><td><b>IBI Anual</b></td><td>{f['IBI_Anual']} €</td></tr>
        </table>""", unsafe_allow_html=True)
    
    with c2:
        st.markdown('<div class="section-title">Análisis de Mercado</div>', unsafe_allow_html=True)
        renta_act, renta_mer = f["Renta"], f["Renta_Mercado"]
        desv = ((renta_act - renta_mer) / renta_mer) * 100
        perdida_mensual = renta_mer - renta_act if renta_act < renta_mer else 0
        
        if desv < -15: clase, msg, icon = "status-red", "Rentabilidad Crítica", "🔴"
        elif desv < -5: clase, msg, icon = "status-yellow", "Margen de Mejora", "🟡"
        else: clase, msg, icon = "status-green", "Activo en Mercado", "🟢"

        html_lucro = f"""
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px dashed rgba(0,0,0,0.2);">
            <b>💸 Análisis de Lucro Cesante:</b><br>
            Estás perdiendo <b>{perdida_mensual:,.2f}€ mensuales</b>.<br>
            Anualmente, esto supone <b style="color:var(--crimson); font-size:1.1rem;">{perdida_mensual*12:,.2f}€ al año</b> de ingresos no percibidos.
        </div>""" if perdida_mensual > 0 else "✓ Renta alineada con el mercado."

        st.markdown(f'<div class="{clase}"><b style="font-size:1.2rem;">{icon} {msg}</b><br>Desviación: {desv:.1f}%{html_lucro}</div>', unsafe_allow_html=True)

# 📂 DATOS Y BACKUPS (RESTAURADO)
elif "Datos" in menu:
    st.markdown('<div class="brand-header">Datos y Seguridad</div>', unsafe_allow_header=True)
    st.write("Edita aquí los datos maestros. Estos cambios se sincronizarán con tu plantilla Excel.")
    df_ed = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True)
    if st.button("Guardar Cambios"):
        df_ed.to_csv(DB_INMUEBLES, index=False)
        st.success("✓ Base de datos actualizada.")
        st.rerun()
    
    st.markdown('<div class="section-title">Copias de Seguridad (Backups)</div>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1: st.download_button("📥 Descargar Inmuebles (CSV)", df_inm.to_csv(index=False), "inmuebles_nolasco.csv", "text/csv")
    with b2: st.download_button("📥 Descargar Movimientos (CSV)", df_mov.to_csv(index=False), "movimientos_nolasco.csv", "text/csv")
