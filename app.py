import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Inmuebles Nolasco 1.1", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    h1, h2, h3 { color: #1B2631 !important; font-family: 'Segoe UI', sans-serif; }
    .apto-card {
        background-color: white; padding: 15px; border-radius: 10px;
        border-top: 4px solid #2E86C1; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center; height: 100%;
    }
    .renta-val { color: #239B56; font-size: 1.2rem; font-weight: bold; }
    .gasto-val { color: #CB4335; font-size: 1.1rem; }
    .neto-val { color: #1B2631; font-size: 1.3rem; font-weight: bold; border-top: 1px solid #eee; margin-top: 10px; padding-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE DATOS ---
DB_INMUEBLES = "nolasco_inmuebles.csv"
DB_MOVIMIENTOS = "nolasco_movimientos.csv"

# Cartera real
DATOS_REALES_INM = [
    {"Nombre": "Casa Abarqueros", "Inquilino": "Victor Aguiluz", "Renta": 2200.0, "Comunidad": 193.76},
    {"Nombre": "Paseo del Salón", "Inquilino": "Pool Despachos", "Renta": 1591.8, "Comunidad": 175.18},
    {"Nombre": "Huerto Unidad 1", "Inquilino": "Alain", "Renta": 660.0, "Comunidad": 74.62},
    {"Nombre": "Huerto Unidad 2", "Inquilino": "Laura/Alex", "Renta": 800.0, "Comunidad": 74.62},
    {"Nombre": "Huerto Unidad 3", "Inquilino": "Jose Manuel", "Renta": 850.0, "Comunidad": 74.63}
]

# Gastos de Abril agrupados por tipología
MOVIMIENTOS_ABRIL = [
    {"Fecha": "2026-04-01", "Concepto": "Hipoteca Abarqueros", "Categoría": "Financiero", "Tipo": "Gasto", "Importe": 554.73},
    {"Fecha": "2026-04-01", "Concepto": "Seguro MyBox (Hogar/Alarma)", "Categoría": "Seguros", "Tipo": "Gasto", "Importe": 96.43},
    {"Fecha": "2026-04-01", "Concepto": "Seguro Vida (Seviam)", "Categoría": "Seguros", "Tipo": "Gasto", "Importe": 55.93},
    {"Fecha": "2026-04-01", "Concepto": "Autónomos (TGSS)", "Categoría": "Impuestos", "Tipo": "Gasto", "Importe": 314.00},
    {"Fecha": "2026-04-01", "Concepto": "Sueldo Pedro (Asignación)", "Categoría": "Personal", "Tipo": "Gasto", "Importe": 600.00},
    {"Fecha": "2026-04-01", "Concepto": "IRPF (Aplazamiento)", "Categoría": "Impuestos", "Tipo": "Gasto", "Importe": 1100.00},
    {"Fecha": "2026-04-01", "Concepto": "IVA (Cuota Fija)", "Categoría": "Impuestos", "Tipo": "Gasto", "Importe": 325.00}
]

def inicializar_bd(force=False):
    if force or not os.path.exists(DB_INMUEBLES):
        pd.DataFrame(DATOS_REALES_INM).to_csv(DB_INMUEBLES, index=False)
    if force or not os.path.exists(DB_MOVIMIENTOS):
        pd.DataFrame(MOVIMIENTOS_ABRIL).to_csv(DB_MOVIMIENTOS, index=False)

inicializar_bd()
df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)

# --- NAVEGACIÓN ---
menu = st.sidebar.radio("GESTIÓN", ["📊 Torre de Control", "🏠 Fichas de Activos", "📝 Diario de Operaciones", "⚙️ Configuración"])

if menu == "📊 Torre de Control":
    st.title("Torre de Control: Cartera Nolasco")
    
    # KPIs Globales
    ing_b = df_inm["Renta"].sum()
    comu_total = df_inm["Comunidad"].sum()
    gastos_otros = df_mov[df_mov["Tipo"] == "Gasto"]["Importe"].sum()
    gas_total = comu_total + gastos_otros
    
    c1, c2, c3 = st.columns(3)
    c1.metric("INGRESOS BRUTOS", f"{ing_b:,.2f} €")
    c2.metric("GASTOS TOTALES", f"-{gas_total:,.2f} €")
    c3.metric("RESULTADO NETO", f"{ing_b - gas_total:,.2f} €")
    
    st.divider()

    # REJILLA DE ACTIVOS (RESUMEN RÁPIDO)
    st.subheader("🏢 Balance por Activo (Ingreso - Comunidad)")
    cols_apto = st.columns(len(df_inm))
    for i, row in df_inm.iterrows():
        with cols_apto[i]:
            neto_apto = row['Renta'] - row['Comunidad']
            st.markdown(f"""
            <div class="apto-card">
                <small>{row['Nombre']}</small><br>
                <b>{row['Inquilino']}</b><br>
                <div class="renta-val">+{row['Renta']:,.0f}€</div>
                <div class="gasto-val">-{row['Comunidad']:,.0f}€</div>
                <div class="neto-val">{neto_apto:,.0f}€</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()

    # ANÁLISIS DE GASTOS POR TIPOLOGÍA
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.subheader("📋 Gastos por Tipología")
        # Agrupamos por Categoría para la tabla
        df_tipologia = df_mov.groupby("Categoría")["Importe"].sum().reset_index()
        df_tipologia = df_tipologia.sort_values("Importe", ascending=False)
        st.table(df_tipologia.style.format({"Importe": "{:,.2f} €"}))
    
    with col_r:
        st.subheader("🍰 Distribución del Gasto")
        fig_p = px.pie(df_mov, values='Importe', names='Categoría', hole=0.4, 
                       color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_p, use_container_width=True)

elif menu == "🏠 Fichas de Activos":
    sel = st.selectbox("Activo:", df_inm["Nombre"].tolist())
    f = df_inm[df_inm["Nombre"] == sel].iloc[0]
    
    st.write(f"### Expediente: {sel}")
    
    # Ficha Técnica Detallada
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        st.markdown(f"**Inquilino:** {f['Inquilino']}")
        st.markdown(f"**Renta Mensual:** {f['Renta']:,} €")
    with c_f2:
        st.markdown(f"**Gasto Directo (Comunidad):** -{f['Comunidad']:,} €")
        st.markdown(f"**Margen Operativo Activo:** {((f['Renta']-f['Comunidad'])/f['Renta']*100):.1f}%")
    with c_f3:
        neto_f = f['Renta'] - f['Comunidad']
        st.metric("RESULTADO ACTIVO", f"{neto_f:,.2f} €")

    st.info("💡 Próximamente: Podrás asignar gastos variables específicos (reparaciones, averías) directamente a esta ficha.")

elif menu == "📝 Diario de Operaciones":
    st.subheader("Libro de Movimientos")
    st.data_editor(df_mov, use_container_width=True)

elif menu == "⚙️ Configuración":
    st.title("Administración")
    if st.button("⚠️ REINICIAR Y CARGAR DATOS REALES"):
        inicializar_bd(force=True)
        st.success("Datos actualizados. Recarga la página.")
        st.rerun()
