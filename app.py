import streamlit as st

# 1. Configuración de página y Estilo Pastel
st.set_page_config(page_title="Gestión Patrimonial Pedro Nolasco", layout="wide")

st.markdown("""
    <style>
    /* Fondo crema pastel */
    .stApp {
        background-color: #FDF5E6;
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
    .stTable {
        background-color: white;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Simulador de Tesorería - Pedro Nolasco")
st.markdown("---")

# --- BARRA LATERAL: ENTRADA DE DATOS ---
with st.sidebar:
    st.header("📥 Ingresos Mensuales")
    renta_abarqueros = st.number_input("Abarqueros (Victor)", value=2200.0)
    renta_salon = st.number_input("Paseo del Salón (Pool)", value=1591.80)
    h1 = st.number_input("Huerto 1 (Alain)", value=660.0)
    h2 = st.number_input("Huerto 2 (Laura)", value=800.0)
    h3 = st.number_input("Huerto 3 (Jose Manuel)", value=850.0)

    st.header("🏢 Comunidades")
    c_aba = st.number_input("C.P. Abarqueros 16", value=193.76)
    c_sal = st.number_input("C.P. Salón 1", value=175.18)
    c_hue = st.number_input("C.P. Huerto Cecilio (Total)", value=223.87)

    st.header("⚖️ Fiscalidad y Fijos")
    irpf = st.number_input("IRPF (Renta 23)", value=1100.0)
    iva = st.number_input("IVA AEAT (Fijo)", value=325.0)
    autonomos = st.number_input("Autónomos", value=314.0)
    hipoteca = st.number_input("Hipoteca Abarqueros", value=554.73)
    sueldo = st.number_input("Sueldo Pedro", value=600.0)

# --- CÁLCULOS ---
total_ingresos = renta_abarqueros + renta_salon + h1 + h2 + h3
total_comu = c_aba + c_sal + c_hue
# Otros fijos: Seguros (152.36), Ascensor (65.44), Holded (18.15)
otros_fijos = 152.36 + 65.44 + 18.15 + autonomos + hipoteca + sueldo
total_gastos = total_comu + otros_fijos + irpf + iva
beneficio_neto = total_ingresos - total_gastos

# --- PANEL CENTRAL ---
c1, c2, c3 = st.columns(3)
c1.metric("INGRESOS BRUTOS", f"{total_ingresos:,.2f} €")
c2.metric("GASTOS TOTALES", f"-{total_gastos:,.2f} €")
c3.metric("EL VICIO (Neto)", f"{beneficio_neto:,.2f} €", delta=f"{((beneficio_neto/total_ingresos)*100):.1f}% Eficiencia")

st.markdown("---")
st.subheader("📋 Desglose de Partidas")
# Tabla informativa
tabla_datos = {
    "Concepto": ["Rentas Totales", "Gastos Comunidad", "Estructura e Hipoteca", "Impuestos (IVA/IRPF)", "Sueldo Personal"],
    "Importe Mensual": [f"{total_ingresos:,.2f} €", f"{total_comu:,.2f} €", f"{(otros_fijos-sueldo):,.2f} €", f"{(irpf+iva):,.2f} €", f"{sueldo:,.2f} €"]
}
st.table(tabla_datos)

if irpf > 0:
    st.info(f"💡 Nota: Al finalizar el aplazamiento de IRPF, tu beneficio neto subirá a {beneficio_neto + irpf:,.2f} €")
