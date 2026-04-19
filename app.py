import streamlit as st
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Gestión Patrimonial", page_icon="💼", layout="wide")

# 2. Estilos: Fondo Gris Claro y Textos Corporativos
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F6; }
    h1, h2, h3 { color: #2E86C1 !important; }
    [data-testid="stMetricValue"] { color: #E67E22; font-weight: bold; }
    .stTable { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Simulador de Tesorería Inteligente")
st.markdown("---")

# --- CONEXIÓN CON EXCEL ---
SHEET_ID = "1aI2Dg5FjEJjaFU4v37sw9ZM3inuB2apgUJ4e3IA4xF8"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

try:
    # Leemos la tabla real
    df_excel = pd.read_csv(URL).dropna(how='all')
    
    # Función auxiliar para buscar un valor en tu Excel
    def buscar_renta(nombre_piso, valor_defecto):
        try:
            # Buscamos en la columna 'Apartamento' el valor que coincida
            fila = df_excel[df_excel['Apartamento'] == nombre_piso]
            return float(fila['Renta'].values[0])
        except:
            return valor_defecto

    # --- BARRA LATERAL CON DATOS DEL EXCEL ---
    with st.sidebar:
        st.header("📥 Ingresos desde Excel")
        # Ahora el 'value' no es un número fijo, es lo que encuentra en el Excel
        r_aba = st.number_input("Abarqueros", value=buscar_renta("Abarqueros", 2200.0))
        r_sal = st.number_input("Paseo del Salón", value=buscar_renta("Salón", 1591.80))
        r_h1 = st.number_input("Huerto 1", value=buscar_renta("Huerto 1", 660.0))
        r_h2 = st.number_input("Huerto 2", value=buscar_renta("Huerto 2", 800.0))
        r_h3 = st.number_input("Huerto 3", value=buscar_renta("Huerto 3", 850.0))

        st.header("🏢 Gastos y Fijos")
        hipoteca = st.number_input("Hipoteca", value=554.73)
        sueldo = st.number_input("Sueldo Gestión", value=600.0)

    # --- CÁLCULOS EN TIEMPO REAL ---
    total_ingresos = r_aba + r_sal + r_h1 + r_h2 + r_h3
    gastos_fijos = hipoteca + sueldo + 314.0 + 152.36 # (Autónomos + Seguros)
    beneficio_neto = total_ingresos - gastos_fijos

    # --- PANEL DE RESULTADOS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("INGRESOS BRUTOS", f"{total_ingresos:,.2f} €")
    c2.metric("GASTOS ESTIMADOS", f"-{gastos_fijos:,.2f} €")
    c3.metric("NETO DISPONIBLE", f"{beneficio_neto:,.2f} €")

    st.markdown("---")
    st.info("💡 Los valores iniciales se han cargado desde tu Google Sheets. Puedes modificarlos aquí para simular nuevos escenarios.")

except Exception as e:
    st.error("No se pudo conectar con el Excel. Usando valores por defecto.")
