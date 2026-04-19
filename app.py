import streamlit as st
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Gestión Patrimonial", page_icon="💼", layout="wide")

# 2. Estilos CSS personalizados (Fondo pastel, textos corporativos)
st.markdown("""
    <style>
    /* Fondo crema pastel */
    .stApp {
        background-color: #F0F2F6;
    }
    /* Títulos en azul corporativo */
    h1, h2, h3 {
        color: #2E86C1 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Tarjetas de métricas resaltadas */
    [data-testid="stMetricValue"] {
        color: #E67E22;
        font-weight: bold;
    }
    /* Estilo para las tablas */
    .stDataFrame, .stTable {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Simulador de Tesorería")
st.markdown("*Panel de control financiero y previsión de liquidez*")
st.markdown("---")

# --- BARRA LATERAL: ENTRADA DE DATOS ---
with st.sidebar:
    st.header("📥 Ingresos Mensuales")
    renta_abarqueros = st.number_input("Abarqueros (Victor)", value=2200.0, step=50.0)
    renta_salon = st.number_input("Paseo del Salón (Pool)", value=1591.80, step=50.0)
    h1 = st.number_input("Huerto 1 (Alain)", value=660.0, step=50.0)
    h2 = st.number_input("Huerto 2 (Laura)", value=800.0, step=50.0)
    h3 = st.number_input("Huerto 3 (Jose Manuel)", value=850.0, step=50.0)

    st.header("🏢 Comunidades")
    c_aba = st.number_input("C.P. Abarqueros 16", value=193.76, step=10.0)
    c_sal = st.number_input("C.P. Salón 1", value=175.18, step=10.0)
    c_hue = st.number_input("C.P. Huerto Cecilio (Total)", value=223.87, step=10.0)

    st.header("⚖️ Fiscalidad y Fijos")
    irpf = st.number_input("IRPF (Renta 23)", value=1100.0, step=100.0)
    iva = st.number_input("IVA AEAT (Fijo)", value=325.0, step=50.0)
    autonomos = st.number_input("Autónomos", value=314.0, step=10.0)
    hipoteca = st.number_input("Hipoteca Abarqueros", value=554.73, step=10.0)
    sueldo = st.number_input("Sueldo Gestión", value=600.0, step=100.0)

# --- CÁLCULOS FINANCIEROS ---
total_ingresos = renta_abarqueros + renta_salon + h1 + h2 + h3
total_comu = c_aba + c_sal + c_hue

# Gastos fijos adicionales según tu estructura
seguros = 152.36
ascensor = 65.44
holded = 18.15
otros_fijos = seguros + ascensor + holded + autonomos + hipoteca + sueldo

total_gastos = total_comu + otros_fijos + irpf + iva
beneficio_neto = total_ingresos - total_gastos

# --- PANEL CENTRAL: RESULTADOS ---
c1, c2, c3 = st.columns(3)
c1.metric("INGRESOS BRUTOS", f"{total_ingresos:,.2f} €")
c2.metric("GASTOS TOTALES", f"-{total_gastos:,.2f} €")

# Calculamos el margen de eficiencia
eficiencia = (beneficio_neto / total_ingresos) * 100 if total_ingresos > 0 else 0
c3.metric("BENEFICIO NETO (El Vicio)", f"{beneficio_neto:,.2f} €", delta=f"{eficiencia:.1f}% Margen")

st.markdown("---")
st.subheader("📋 Desglose de Partidas")

# Usamos un DataFrame de Pandas para que la tabla quede más estética y alineada
datos_desglose = {
    "Concepto": [
        "Rentas Totales Brutas", 
        "Gastos de Comunidad", 
        "Estructura, Seguros e Hipoteca", 
        "Impuestos (IVA / IRPF)", 
        "Sueldo Gestión"
    ],
    "Importe Mensual": [
        total_ingresos, 
        total_comu, 
        (otros_fijos - sueldo), 
        (irpf + iva), 
        sueldo
    ]
}

df_tabla = pd.DataFrame(datos_desglose)
# Formateamos la columna de importes para que muestre los euros correctamente
df_tabla["Importe Mensual"] = df_tabla["Importe Mensual"].apply(lambda x: f"{x:,.2f} €")

st.table(df_tabla)

# --- AVISOS ESTRATÉGICOS ---
if irpf > 0:
    st.info(f"💡 **Proyección Estratégica:** Al finalizar el aplazamiento de IRPF, el flujo de caja neto aumentará automáticamente a **{beneficio_neto + irpf:,.2f} €** mensuales.")
