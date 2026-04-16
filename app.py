import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Gestión Patrimonial Pedro Nolasco", layout="wide")

st.title("📊 Simulador de Tesorería - Pedro Nolasco")
st.markdown("---")

# --- BARRA LATERAL: ENTRADA DE DATOS ---
st.sidebar.header("📥 Configuración de Ingresos")
renta_abarqueros = st.sidebar.number_input("Abarqueros (Victor)", value=2200.0, step=50.0)
renta_salon = st.sidebar.number_input("Paseo del Salón (Pool)", value=1591.80, step=50.0)
huerto_1 = st.sidebar.number_input("Huerto 1 (Alain)", value=660.0, step=10.0)
huerto_2 = st.sidebar.number_input("Huerto 2 (Laura)", value=800.0, step=10.0)
huerto_3 = st.sidebar.number_input("Huerto 3 (Jose Manuel)", value=850.0, step=10.0)

st.sidebar.header("💸 Gastos de Comunidad")
comu_abarqueros = st.sidebar.number_input("C.P. Abarqueros 16", value=193.76, step=5.0)
comu_salon = st.sidebar.number_input("C.P. Salón 1", value=175.18, step=5.0)
comu_huertos = st.sidebar.number_input("C.P. Huerto Cecilio (Bloque)", value=223.87, step=5.0)

st.sidebar.header("⚖️ Impuestos y Otros")
irpf_mensual = st.sidebar.number_input("IRPF (Renta 23)", value=1100.0, step=100.0)
iva_mensual = st.sidebar.number_input("IVA AEAT (Fijo)", value=325.0, step=5.0)
ibi_granada = st.sidebar.number_input("IBI Granada (Si aplica)", value=0.0, step=10.0)
autonomos = st.sidebar.number_input("Autónomos (TGSS)", value=314.0, step=5.0)

st.sidebar.header("🏠 Gastos Estructura")
hipoteca = st.sidebar.number_input("Hipoteca Abarqueros", value=554.73, step=5.0)
seguro_hogar = st.sidebar.number_input("Seguro MyBox", value=96.43, step=5.0)
seguro_vida = st.sidebar.number_input("Seguro Seviam", value=55.93, step=5.0)
mantenimiento = st.sidebar.number_input("Mantenimiento Ascensor", value=65.44, step=5.0)
sueldo_casa = st.sidebar.number_input("Asignación Personal", value=600.0, step=50.0)

# --- CÁLCULOS ---
total_ingresos = renta_abarqueros + renta_salon + huerto_1 + huerto_2 + huerto_3
total_comunidades = comu_abarqueros + comu_salon + comu_huertos
total_otros_gastos = hipoteca + seguro_hogar + seguro_vida + mantenimiento + autonomos + sueldo_casa + 18.15 # 18.15 de Holded
total_impuestos = irpf_mensual + iva_mensual + ibi_granada

total_gastos = total_comunidades + total_otros_gastos + total_impuestos
beneficio_neto = total_ingresos - total_gastos

# --- PANEL CENTRAL: RESULTADOS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Ingresos Brutos", f"{total_ingresos:,.2f} €")
with col2:
    st.metric("Gastos Totales", f"-{total_gastos:,.2f} €", delta_color="inverse")
with col3:
    st.metric("EL VICIO (Neto)", f"{beneficio_neto:,.2f} €", delta=f"{((beneficio_neto/total_ingresos)*100):.1f}% Eficiencia")

st.markdown("---")

# Tabla de resumen
st.subheader("📋 Resumen de Partidas")
data = {
    "Categoría": ["Ingresos", "Comunidades", "Fijos/Hipotecas", "Impuestos", "Asignación Casa"],
    "Importe (€)": [total_ingresos, total_comunidades, total_otros_gastos-sueldo_casa, total_impuestos, sueldo_casa]
}
st.table(data)

if irpf_mensual > 0:
    st.info(f"💡 Recuerda: En julio tu beneficio subirá un promedio de {irpf_mensual} € al finalizar el IRPF.")
