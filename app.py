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
    /* Estilo de Tarjeta en Rejilla */
    .apto-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border-top: 4px solid #2E86C1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    .renta-val { color: #239B56; font-size: 1.4rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE DATOS REALES ---
DB_INMUEBLES = "nolasco_inmuebles.csv"
DB_MOVIMIENTOS = "nolasco_movimientos.csv"

DATOS_REALES_INM = [
    {"Nombre": "Casa Abarqueros", "Inquilino": "Victor Aguiluz", "Renta": 2200.0, "Comunidad": 193.76},
    {"Nombre": "Paseo del Salón", "Inquilino": "Pool Despachos", "Renta": 1591.8, "Comunidad": 175.18},
    {"Nombre": "Huerto Unidad 1", "Inquilino": "Alain", "Renta": 660.0, "Comunidad": 74.62},
    {"Nombre": "Huerto Unidad 2", "Inquilino": "Laura/Alex", "Renta": 800.0, "Comunidad": 74.62},
    {"Nombre": "Huerto Unidad 3", "Inquilino": "Jose Manuel", "Renta": 850.0, "Comunidad": 74.63}
]

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
    
    # 1. KPIs Globales
    ing_b = df_inm["Renta"].sum()
    gas_f = df_mov[df_mov["Tipo"] == "Gasto"]["Importe"].sum()
    comu = df_inm["Comunidad"].sum()
    neto = ing_b - gas_f - comu
    
    c1, c2, c3 = st.columns(3)
    c1.metric("INGRESOS BRUTOS", f"{ing_b:,.2f} €")
    c2.metric("GASTOS + TAX", f"-{gas_f + comu:,.2f} €")
    c3.metric("EL VICIO (NETO)", f"{neto:,.2f} €")
    
    st.divider()

    # 2. REJILLA DE APARTAMENTOS (Grid View)
    st.subheader("🏢 Estado Actual de la Cartera")
    cols_apto = st.columns(len(df_inm))
    for i, row in df_inm.iterrows():
        with cols_apto[i]:
            st.markdown(f"""
            <div class="apto-card">
                <small>{row['Nombre']}</small><br>
                <b>{row['Inquilino']}</b><br>
                <span class="renta-val">{row['Renta']:,.0f} €</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()

    # 3. TABLA DETALLADA Y GRÁFICOS
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader("📋 Listado Detallado de Rentas")
        st.table(df_inm[["Nombre", "Inquilino", "Renta"]])
        
        st.subheader("📈 Histograma de Ingresos")
        st.plotly_chart(px.bar(df_inm, x="Nombre", y="Renta", color="Nombre", text_auto=True), use_container_width=True)
    
    with col_r:
        st.subheader("🍰 Distribución de Costes")
        st.plotly_chart(px.pie(df_mov, values='Importe', names='Categoría', hole=0.5), use_container_width=True)

elif menu == "🏠 Fichas de Activos":
    sel = st.selectbox("Activo:", df_inm["Nombre"].tolist())
    f = df_inm[df_inm["Nombre"] == sel].iloc[0]
    st.write(f"### {sel}")
    st.info(f"**Inquilino:** {f['Inquilino']} | **Renta:** {f['Renta']} € | **Comunidad:** {f['Comunidad']} €")

elif menu == "📝 Diario de Operaciones":
    st.subheader("Libro de Movimientos")
    st.data_editor(df_mov, use_container_width=True)

elif menu == "⚙️ Configuración":
    st.title("Administración")
    if st.button("⚠️ REINICIAR Y CARGAR DATOS REALES"):
        inicializar_bd(force=True)
        st.success("Datos actualizados. Recarga la página.")
        st.rerun()
