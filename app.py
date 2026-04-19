import streamlit as st
import pandas as pd

# 1. Configuración de la página (estado de la barra lateral)
st.set_page_config(page_title="Dashboard Patrimonial", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

# 2. Estilo Visual Corporativo
st.markdown("""
    <style>
    .stApp { background-color: #F4F6F9; }
    h1, h2, h3 { color: #1A5276 !important; font-family: 'Helvetica Neue', sans-serif; }
    /* Darle color a las métricas */
    [data-testid="stMetricValue"] { color: #D35400; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

st.title("💼 Dashboard Patrimonial - Pedro Nolasco")
st.markdown("*Análisis de rentabilidad y simulación de escenarios*")
st.divider() # Una línea separadora más elegante

# 3. Conexión Estable (Lectura por Enlace Público)
SHEET_ID = "1aI2Dg5FjEJjaFU4v37sw9ZM3inuB2apgUJ4e3IA4xF8"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

try:
    df_excel = pd.read_csv(URL).dropna(how='all')

    # --- BARRA LATERAL (Con menús desplegables para limpiar la vista) ---
    with st.sidebar:
        st.header("⚙️ Simulador de Escenarios")
        
        with st.expander("📥 Ingresos Mensuales", expanded=True):
            renta_v = st.number_input("Abarqueros (Victor)", value=2200.0, step=50.0)
            renta_p = st.number_input("Paseo del Salón (Pool)", value=1591.80, step=50.0)
            h1 = st.number_input("Huerto 1 (Alain)", value=660.0, step=50.0)
            h2 = st.number_input("Huerto 2 (Laura)", value=800.0, step=50.0)
            h3 = st.number_input("Huerto 3 (Jose Manuel)", value=850.0, step=50.0)

        with st.expander("🏢 Gastos Operativos", expanded=False):
            hipoteca = st.number_input("Hipoteca Abarqueros", value=554.73)
            comunidades = st.number_input("Total Comunidades", value=592.81)
            sueldo = st.number_input("Sueldo Gestión", value=600.0)

        with st.expander("⚖️ Fiscalidad y Fijos", expanded=False):
            irpf = st.number_input("IRPF (Aprox)", value=1100.0)
            iva = st.number_input("IVA AEAT", value=325.0)
            autonomos = st.number_input("Cuota Autónomos", value=314.0)

    # --- CÁLCULOS FINANCIEROS ---
    total_ingresos = renta_v + renta_p + h1 + h2 + h3
    total_gastos = hipoteca + comunidades + sueldo + irpf + iva + autonomos
    beneficio_neto = total_ingresos - total_gastos
    margen_neto = (beneficio_neto / total_ingresos) * 100 if total_ingresos > 0 else 0

    # --- PANEL CENTRAL: TARJETAS DE RESULTADOS ---
    col1, col2, col3, col4 = st.columns(4)
    
    # Envolvemos las métricas en "contenedores con borde" para que parezcan tarjetas
    with col1:
        with st.container(border=True):
            st.metric("INGRESOS BRUTOS", f"{total_ingresos:,.2f} €")
    with col2:
        with st.container(border=True):
            st.metric("GASTOS TOTALES", f"-{total_gastos:,.2f} €")
    with col3:
        with st.container(border=True):
            st.metric("EL VICIO (NETO)", f"{beneficio_neto:,.2f} €")
    with col4:
        with st.container(border=True):
            st.metric("MARGEN EFICIENCIA", f"{margen_neto:.1f} %")

    st.write("") # Espacio en blanco

    # --- ZONA DE GRÁFICOS Y DESGLOSE ---
    col_grafico, col_tabla = st.columns([1.5, 1]) # El gráfico ocupará un poco más de espacio
    
    with col_grafico:
        st.subheader("📈 Balance Estructural")
        # Creamos un pequeño gráfico de barras comparativo
        df_chart = pd.DataFrame({
            "Categoría": ["Ingresos", "Gastos", "Beneficio Neto"],
            "Importe (€)": [total_ingresos, total_gastos, beneficio_neto]
        })
        st.bar_chart(df_chart.set_index("Categoría"), color="#2E86C1")

    with col_tabla:
        st.subheader("📋 Estructura de Gastos")
        # Creamos una tabla limpia solo para visualizar los gastos
        df_gastos = pd.DataFrame({
            "Concepto": ["Hipoteca", "Comunidades", "Impuestos (IRPF+IVA)", "Autónomos", "Sueldo Personal"],
            "Importe (€)": [hipoteca, comunidades, irpf+iva, autonomos, sueldo]
        })
        st.dataframe(df_gastos, hide_index=True, use_container_width=True)

    st.divider()

    # --- AUDITORÍA DE DATOS (Oculta por defecto) ---
    with st.expander("🔍 Ver Base de Datos Original (Conexión Excel)"):
        st.write("Estos son los datos crudos que la aplicación está leyendo ahora mismo desde tu Google Sheets:")
        st.dataframe(df_excel, use_container_width=True)

except Exception as e:
    st.error("No se pudo conectar con el Excel. Revisa el enlace público.")
