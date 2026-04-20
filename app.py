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
    .apto-card {
        background-color: white; padding: 15px; border-radius: 10px;
        border-top: 4px solid #2E86C1; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center; height: 100%;
    }
    .renta-val { color: #239B56; font-size: 1.2rem; font-weight: bold; }
    .gasto-val { color: #CB4335; font-size: 1.1rem; }
    .neto-val { color: #1B2631; font-size: 1.3rem; font-weight: bold; border-top: 1px solid #eee; margin-top: 10px; padding-top: 5px; }
    .fiscal-box { background-color: #F9F9F9; padding: 15px; border-radius: 10px; border-left: 5px solid #239B56; }
    .ai-box { background-color: #F0F4FF; padding: 15px; border-radius: 10px; border-left: 5px solid #2E86C1; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE DATOS E INICIALIZACIÓN ---
DB_INMUEBLES = "nolasco_inmuebles.csv"
DB_MOVIMIENTOS = "nolasco_movimientos.csv"

def inicializar_bd(force=False):
    if force or not os.path.exists(DB_INMUEBLES):
        pd.DataFrame([
            {"Nombre": "Casa Abarqueros", "Inquilino": "Victor Aguiluz", "Renta": 2200.0, "Comunidad": 193.76, "Valor_Construccion": 150000.0},
            {"Nombre": "Paseo del Salón", "Inquilino": "Pool Despachos", "Renta": 1591.8, "Comunidad": 175.18, "Valor_Construccion": 120000.0},
            {"Nombre": "Huerto Unidad 1", "Inquilino": "Alain", "Renta": 660.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0},
            {"Nombre": "Huerto Unidad 2", "Inquilino": "Laura/Alex", "Renta": 800.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0},
            {"Nombre": "Huerto Unidad 3", "Inquilino": "Jose Manuel", "Renta": 850.0, "Comunidad": 74.63, "Valor_Construccion": 45000.0}
        ]).to_csv(DB_INMUEBLES, index=False)
        
    if force or not os.path.exists(DB_MOVIMIENTOS):
        pd.DataFrame([
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Hipoteca Abarqueros", "Categoría": "Financiero", "Tipo": "Gasto", "Importe": 554.73},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Seguro MyBox (Hogar/Alarma)", "Categoría": "Seguros", "Tipo": "Gasto", "Importe": 96.43},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Seguro Vida (Seviam)", "Categoría": "Seguros", "Tipo": "Gasto", "Importe": 55.93},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Mantenimiento Ascensor", "Categoría": "Mantenimiento", "Tipo": "Gasto", "Importe": 65.44},
            {"Fecha": "2026-04-01", "Apartamento": "Global", "Concepto": "Software Holded", "Categoría": "Sistemas", "Tipo": "Gasto", "Importe": 18.15},
            {"Fecha": "2026-04-01", "Apartamento": "Global", "Concepto": "Autónomos (TGSS)", "Categoría": "Impuestos", "Tipo": "Gasto", "Importe": 314.00},
            {"Fecha": "2026-04-01", "Apartamento": "Global", "Concepto": "Sueldo Pedro (Asignación)", "Categoría": "Personal", "Tipo": "Gasto", "Importe": 600.00},
            {"Fecha": "2026-04-01", "Apartamento": "Global", "Concepto": "IRPF (Aplazamiento)", "Categoría": "Impuestos", "Tipo": "Gasto", "Importe": 1100.00},
            {"Fecha": "2026-04-01", "Apartamento": "Global", "Concepto": "IVA (Cuota Fija)", "Categoría": "Impuestos", "Tipo": "Gasto", "Importe": 325.00}
        ]).to_csv(DB_MOVIMIENTOS, index=False)

inicializar_bd()
df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)

# --- 3. NAVEGACIÓN ---
menu = st.sidebar.radio("SISTEMA NOLASCO", ["📊 Torre de Control", "🏠 Fichas de Activos", "📝 Diario de Operaciones", "⚙️ Configuración"])

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

    # REJILLA DE ACTIVOS
    st.subheader("🏢 Balance Mensual por Activo")
    cols_apto = st.columns(len(df_inm))
    for i, row in df_inm.iterrows():
        with cols_apto[i]:
            gastos_esp = df_mov[(df_mov["Apartamento"] == row['Nombre']) & (df_mov["Tipo"] == "Gasto")]["Importe"].sum()
            total_cargas = row['Comunidad'] + gastos_esp
            neto_apto = row['Renta'] - total_cargas
            st.markdown(f"""
            <div class="apto-card">
                <small>{row['Nombre']}</small><br>
                <b>{row['Inquilino']}</b><br>
                <div class="renta-val">+{row['Renta']:,.0f}€</div>
                <div class="gasto-val">-{total_cargas:,.0f}€</div>
                <div class="neto-val">{neto_apto:,.0f}€</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()

    # TABLA DE GASTOS Y GRÁFICO
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.subheader("📋 Gastos por Tipología")
        df_tip = df_mov.groupby("Categoría")["Importe"].sum().reset_index().sort_values("Importe", ascending=False)
        st.table(df_tip.style.format({"Importe": "{:,.2f} €"}))
    with col_r:
        st.subheader("🍰 Distribución de Costes")
        st.plotly_chart(px.pie(df_mov, values='Importe', names='Categoría', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)

elif menu == "🏠 Fichas de Activos":
    sel = st.selectbox("Expediente:", df_inm["Nombre"].tolist())
    f = df_inm[df_inm["Nombre"] == sel].iloc[0]
    
    st.header(f"Ficha: {sel}")
    
    c_f1, c_f2 = st.columns([2, 1])
    with c_f1:
        st.markdown(f"**Inquilino:** {f['Inquilino']}")
        df_g_apto = df_mov[(df_mov["Apartamento"] == sel) & (df_mov["Tipo"] == "Gasto")]
        resumen = pd.concat([pd.DataFrame([{"Concepto": "Comunidad", "Importe": f['Comunidad']}]), df_g_apto[["Concepto", "Importe"]]])
        st.table(resumen.style.format({"Importe": "{:,.2f} €"}))
        
    with c_f2:
        st.markdown('<div class="fiscal-box">', unsafe_allow_html=True)
        st.markdown("### ⚖️ Gestión Fiscal")
        amort = (f['Valor_Construccion'] * 0.03) / 12
        st.write(f"**Amortización (3%):** {amort:,.2f} €/mes")
        st.caption("Deducible no monetario")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="ai-box">', unsafe_allow_html=True)
    st.markdown("### 🤖 Previsiones IA")
    c_ia1, c_ia2 = st.columns(2)
    with c_ia1:
        st.write("**Mantenimiento Fachada**")
        st.caption("Previsión: Ciclo de 5 años. Pintura recomendada en 18 meses.")
    with c_ia2:
        st.write("**Eficiencia Activo**")
        benef_neto = f['Renta'] - resumen['Importe'].sum()
        st.metric("Resultado Neto", f"{benef_neto:,.2f} €", delta=f"{(benef_neto/f['Renta']*100):.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📝 Diario de Operaciones":
    st.subheader("Registro de Contabilidad")
    df_ed = st.data_editor(df_mov, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Sincronizar"):
        df_ed.to_csv(DB_MOVIMIENTOS, index=False)
        st.success("Guardado.")

elif menu == "⚙️ Configuración":
    st.title("Administración")
    if st.button("⚠️ REINICIAR SISTEMA (Carga Real)"):
        inicializar_bd(force=True)
        st.rerun()
