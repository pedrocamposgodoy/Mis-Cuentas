import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Finanzas Estáticas - Pedro", layout="wide")

# 2. Estilo Visual: Fondo Gris Claro y Colores Corporativos
st.markdown("""
    <style>
    .stApp {
        background-color: #F0F2F6;
    }
    h1, h2, h3 {
        color: #2E86C1 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    [data-testid="stMetricValue"] {
        color: #E67E22;
        font-weight: bold;
    }
    .stTable {
        background-color: white;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Simulador de Tesorería - Finanzas Estáticas")
st.markdown("---")

# 3. Conexión Estable (Lectura por Enlace Público)
SHEET_ID = "1aI2Dg5FjEJjaFU4v37sw9ZM3inuB2apgUJ4e3IA4xF8"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

try:
    # Leemos los datos directamente del Excel
    # El ttl=0 aquí no se usa porque leemos por URL directa
    df_excel = pd.read_csv(URL).dropna(how='all')

    # --- BARRA LATERAL: ENTRADA DE DATOS ---
    with st.sidebar:
        st.header("📥 Ingresos Mensuales")
        # Estos valores los puedes cambiar manualmente en la app para simular
        renta_v = st.number_input("Abarqueros (Victor)", value=2200.0)
        renta_p = st.number_input("Paseo del Salón (Pool)", value=1591.80)
        h1 = st.number_input("Huerto 1 (Alain)", value=660.0)
        h2 = st.number_input("Huerto 2 (Laura)", value=800.0)
        h3 = st.number_input("Huerto 3 (Jose Manuel)", value=850.0)

        st.header("🏢 Gastos Fijos")
        hipoteca = st.number_input("Hipoteca Abarqueros", value=554.73)
        comunidades = st.number_input("Total Comunidades", value=592.81)
        sueldo = st.number_input("Sueldo Gestión", value=600.0)

    # --- CÁLCULOS ---
    total_ingresos = renta_v + renta_p + h1 + h2 + h3
    total_gastos = hipoteca + comunidades + sueldo + 314.0 + 325.0 + 1100.0 # (Autónomos + IVA + IRPF)
    beneficio_neto = total_ingresos - total_gastos

    # --- PANEL CENTRAL ---
    c1, c2, c3 = st.columns(3)
    c1.metric("INGRESOS BRUTOS", f"{total_ingresos:,.2f} €")
    c2.metric("GASTOS TOTALES", f"-{total_gastos:,.2f} €")
    c3.metric("BENEFICIO NETO", f"{beneficio_neto:,.2f} €")

    st.markdown("---")
    st.subheader("📋 Datos Actuales del Excel")
    # Mostramos la tabla que viene directamente del Excel para confirmar conexión
    st.dataframe(df_excel, use_container_width=True)

except Exception as e:
    st.error("No se pudo conectar con el Excel por el enlace público.")
    st.info("Asegúrate de que en Google Sheets has dado a 'Compartir' -> 'Cualquier persona con el enlace'.")
