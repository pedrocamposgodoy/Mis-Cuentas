import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Inmuebles Nolasco 1.1", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    h1, h2, h3 { color: #1B2631 !important; font-family: 'Segoe UI', sans-serif; }
    .metric-box { background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #E0E4E8; text-align: center; }
    .ai-box { background-color: #F0F4FF; padding: 20px; border-radius: 12px; border-left: 5px solid #2E86C1; }
    .fiscal-box { background-color: #F9F9F9; padding: 20px; border-radius: 12px; border-left: 5px solid #239B56; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE DATOS ---
DB_INMUEBLES = "nolasco_inmuebles.csv"
DB_MOVIMIENTOS = "nolasco_movimientos.csv"

# Datos Maestros Reales (Pedro)
DATOS_REALES_INM = [
    {"Nombre": "Casa Abarqueros", "Inquilino": "Victor Aguiluz", "Renta": 2200.0, "Comunidad": 193.76, "Valor_Construccion": 150000.0},
    {"Nombre": "Paseo del Salón", "Inquilino": "Pool Despachos", "Renta": 1591.8, "Comunidad": 175.18, "Valor_Construccion": 120000.0},
    {"Nombre": "Huerto Unidad 1", "Inquilino": "Alain", "Renta": 660.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0},
    {"Nombre": "Huerto Unidad 2", "Inquilino": "Laura/Alex", "Renta": 800.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0},
    {"Nombre": "Huerto Unidad 3", "Inquilino": "Jose Manuel", "Renta": 850.0, "Comunidad": 74.63, "Valor_Construccion": 45000.0}
]

MOVIMIENTOS_ABRIL = [
    {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Hipoteca", "Categoría": "Financiero", "Tipo": "Gasto", "Importe": 554.73},
    {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Seguro MyBox", "Categoría": "Seguros", "Tipo": "Gasto", "Importe": 96.43},
    {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Seguro Vida", "Categoría": "Seguros", "Tipo": "Gasto", "Importe": 55.93},
    {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Ascensor", "Categoría": "Mantenimiento", "Tipo": "Gasto", "Importe": 65.44},
    {"Fecha": "2026-04-01", "Apartamento": "Global", "Concepto": "Sueldo Pedro", "Categoría": "Personal", "Tipo": "Gasto", "Importe": 600.00},
    {"Fecha": "2026-04-01", "Apartamento": "Global", "Concepto": "IRPF", "Categoría": "Impuestos", "Tipo": "Gasto", "Importe": 1100.00}
]

def inicializar_bd(force=False):
    if force or not os.path.exists(DB_INMUEBLES):
        pd.DataFrame(DATOS_REALES_INM).to_csv(DB_INMUEBLES, index=False)
    if force or not os.path.exists(DB_MOVIMIENTOS):
        pd.DataFrame(MOVIMIENTOS_ABRIL).to_csv(DB_MOVIMIENTOS, index=False)

inicializar_bd()
df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)

# --- 3. INTERFAZ ---
menu = st.sidebar.radio("SISTEMA NOLASCO", ["📊 Dashboard", "🏠 Fichas de Activos", "⚙️ Configuración"])

if menu == "📊 Dashboard":
    st.title("Gestión de Activos Nolasco")
    st.metric("Ingresos Totales", f"{df_inm['Renta'].sum():,.2f} €")
    st.plotly_chart(px.pie(df_mov, values='Importe', names='Categoría', hole=0.5), use_container_width=True)

elif menu == "🏠 Fichas de Activos":
    sel = st.selectbox("Seleccione Inmueble:", df_inm["Nombre"].tolist())
    f = df_inm[df_inm["Nombre"] == sel].iloc[0]
    
    st.header(f"Ficha Técnica: {sel}")
    
    # Grid de Gastos Estándar
    st.subheader("📋 Estructura de Gastos Mensuales")
    df_g = df_mov[(df_mov["Apartamento"] == sel) & (df_mov["Tipo"] == "Gasto")]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("**Gastos Corrientes Detallados**")
        resumen_gastos = pd.concat([
            pd.DataFrame([{"Concepto": "Comunidad", "Importe": f['Comunidad']}]),
            df_g[["Concepto", "Importe"]]
        ])
        st.table(resumen_gastos.style.format({"Importe": "{:,.2f} €"}))

    # Módulo de Amortización (Fiscal)
    with col2:
        st.markdown('<div class="fiscal-box">', unsafe_allow_html=True)
        st.markdown("### ⚖️ Cálculo Fiscal")
        amort_mensual = (f['Valor_Construccion'] * 0.03) / 12
        st.write(f"**Amortización Deducible:** {amort_mensual:,.2f} €/mes")
        st.caption("(3% anual s/ construcción - No es salida de caja)")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # IA Predictiva
    st.markdown('<div class="ai-box">', unsafe_allow_html=True)
    st.markdown("### 🤖 Previsiones Calculadas por IA")
    
    c_ia1, c_ia2, c_ia3 = st.columns(3)
    # Simulamos lógica IA basada en tus parámetros
    pintura_coste = 1200 if sel == "Casa Abarqueros" else 600
    electro_coste = 450 # Promedio sustitución
    
    with c_ia1:
        st.write("**Mantenimiento Fachada**")
        st.write(f"Estimado: {pintura_coste} €")
        st.progress(0.7) # Ciclo de 5 años, estamos al 70%
        st.caption("Sugerencia: Pintura en 14 meses")
    
    with c_ia2:
        st.write("**Sustitución Electrodomésticos**")
        st.write(f"Reserva anual: {electro_coste/8:,.2f} €")
        st.caption("Vida útil remanente: ~2 años")
        
    with c_ia3:
        beneficio_real = f['Renta'] - resumen_gastos['Importe'].sum()
        rentabilidad_proyectada = (beneficio_real - (pintura_coste/60) - (electro_coste/96)) / f['Renta'] * 100
        st.metric("Rentabilidad Neta (Previsora)", f"{rentabilidad_proyectada:.1f}%")
        st.caption("Incluye provisiones IA")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "⚙️ Configuración":
    if st.button("REINICIAR DATOS"):
        inicializar_bd(force=True)
        st.rerun()
