import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. ESTÉTICA Y CONFIGURACIÓN ---
st.set_page_config(page_title="Curranteia - Panel de Dirección", layout="wide", initial_sidebar_state="expanded")

# Inyección de CSS para diseño premium
st.markdown("""
    <style>
    /* Fondo general */
    .stApp { background-color: #F4F6F9; }
    
    /* Títulos corporativos */
    h1, h2, h3 { color: #2C3E50 !important; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Estilo de las métricas principales */
    div[data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 800; }
    
    /* Separador elegante */
    hr { border-top: 2px solid #E5E7EB; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BASE DE DATOS (Backend) ---
DB_FILE = "base_datos_curranteia.csv"
APARTAMENTOS = ["Abarqueros", "Puerta Real", "Huerto 1", "Huerto 2", "Huerto 3"]

if not os.path.exists(DB_FILE):
    columnas = ["Fecha", "Apartamento", "Concepto", "Categoría", "Tipo", "Importe"]
    df_inicial = pd.DataFrame(columns=columnas)
    df_inicial.to_csv(DB_FILE, index=False)

def cargar_datos():
    return pd.read_csv(DB_FILE)

def guardar_datos(df_datos):
    df_datos.to_csv(DB_FILE, index=False)

df = cargar_datos()

# --- 3. BARRA LATERAL (Entrada de datos) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/real-estate.png", width=60) # Icono decorativo
    st.header("⚙️ Operaciones")
    
    with st.form("nuevo_registro", clear_on_submit=True):
        st.subheader("➕ Añadir Movimiento")
        f_apto = st.selectbox("Inmueble", APARTAMENTOS)
        f_tipo = st.radio("Tipo", ["Ingreso", "Gasto"], horizontal=True)
        f_cat = st.selectbox("Categoría", ["Alquiler", "Suministros", "Reparaciones", "Impuestos", "Hipoteca/Bancos", "Varios"])
        f_con = st.text_input("Concepto (Ej: Fianza, Endesa...)")
        f_imp = st.number_input("Importe (€)", min_value=0.0, step=10.0)
        
        if st.form_submit_button("Registrar Operación"):
            nueva_fila = {"Fecha": datetime.now().strftime("%Y-%m-%d"), "Apartamento": f_apto, "Concepto": f_con, "Categoría": f_cat, "Tipo": f_tipo, "Importe": f_imp}
            df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
            guardar_datos(df)
            st.success("Registrado correctamente")
            st.rerun()
            
    st.divider()
    # Botón de seguridad
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Copia Excel", data=csv, file_name='backup_curranteia.csv', mime='text/csv')

# --- 4. PORTADA (DASHBOARD) ---
st.title("📊 Panel de Dirección: Curranteia")
st.markdown("Visión global del rendimiento patrimonial.")

# Cálculos Globales
ingresos_totales = df[df["Tipo"] == "Ingreso"]["Importe"].sum()
gastos_totales = df[df["Tipo"] == "Gasto"]["Importe"].sum()
beneficio_neto = ingresos_totales - gastos_totales

# Fila 1: KPIs Globales
c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.metric("INGRESOS TOTALES", f"{ingresos_totales:,.0f} €")
with c2:
    with st.container(border=True):
        st.metric("GASTOS TOTALES", f"-{gastos_totales:,.0f} €")
with c3:
    with st.container(border=True):
        eficiencia = (beneficio_neto / ingresos_totales * 100) if ingresos_totales > 0 else 0
        st.metric("BENEFICIO NETO", f"{beneficio_neto:,.0f} €", delta=f"Margen: {eficiencia:.1f}%", delta_color="normal")

st.markdown("---")

# Fila 2: Estado de la Cartera (Listado de Apartamentos)
st.subheader("🏢 Rendimiento por Inmueble")

# Creamos tantas columnas como apartamentos haya
cols_apto = st.columns(len(APARTAMENTOS))

for i, apto in enumerate(APARTAMENTOS):
    with cols_apto[i]:
        # Filtramos los datos solo de este apartamento
        df_apto = df[df["Apartamento"] == apto]
        ing_apto = df_apto[df_apto["Tipo"] == "Ingreso"]["Importe"].sum()
        gas_apto = df_apto[df_apto["Tipo"] == "Gasto"]["Importe"].sum()
        neto_apto = ing_apto - gas_apto
        
        # Tarjeta visual para cada apartamento
        with st.container(border=True):
            st.markdown(f"<h4 style='text-align: center; color: #1A5276;'>{apto}</h4>", unsafe_allow_html=True)
            st.metric("Rentabilidad", f"{neto_apto:,.0f} €", delta=f"{ing_apto:,.0f}€ Ing. | {gas_apto:,.0f}€ Gas.", delta_color="off")

st.markdown("---")

# Fila 3: Tabla Operativa
st.subheader("📝 Libro Mayor Operativo")
df_editado = st.data_editor(df, use_container_width=True, num_rows="dynamic")

if st.button("💾 Sincronizar Cambios de Tabla"):
    guardar_datos(df_editado)
    st.success("Datos actualizados.")
    st.rerun()
