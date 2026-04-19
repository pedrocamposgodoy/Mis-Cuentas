import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN VISUAL (ESTILO GRIS CLARO) ---
st.set_page_config(page_title="Curranteia - Gestión Patrimonial", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F6; }
    h1, h2, h3 { color: #1A5276 !important; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stMetricValue"] { color: #E67E22; font-weight: bold; }
    .stTable { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE LA BASE DE DATOS LOCAL (CSV) ---
DB_FILE = "base_datos_curranteia.csv"

# Si el archivo no existe, la app lo crea automáticamente con la estructura necesaria
if not os.path.exists(DB_FILE):
    columnas = ["Fecha", "Apartamento", "Concepto", "Categoría", "Tipo", "Importe"]
    # Creamos un par de datos de ejemplo para que no nazca vacía
    df_inicial = pd.DataFrame([
        {"Fecha": "2026-04-01", "Apartamento": "Abarqueros", "Concepto": "Renta Victor", "Categoría": "Alquiler", "Tipo": "Ingreso", "Importe": 2200.0},
        {"Fecha": "2026-04-02", "Apartamento": "P. Salón", "Concepto": "Hipoteca", "Categoría": "Bancos", "Tipo": "Gasto", "Importe": 554.73}
    ])
    df_inicial.to_csv(DB_FILE, index=False)

def cargar_datos():
    return pd.read_csv(DB_FILE)

def guardar_datos(df_datos):
    df_datos.to_csv(DB_FILE, index=False)

# --- 3. INTERFAZ Y LÓGICA ---
st.title("🏙️ Curranteia: Gestión de Apartamentos con IA")
st.markdown("---")

df = cargar_datos()

# --- BARRA LATERAL: ENTRADA DE DATOS (FRONTEND) ---
with st.sidebar:
    st.header("➕ Registro de Movimientos")
    with st.form("nuevo_registro", clear_on_submit=True):
        f_apto = st.selectbox("Inmueble", ["Abarqueros", "P. Salón", "Huerto 1", "Huerto 2", "Huerto 3"])
        f_tipo = st.radio("Tipo", ["Ingreso", "Gasto"], horizontal=True)
        f_cat = st.selectbox("Categoría", ["Alquiler", "Suministros", "Reparaciones", "Impuestos", "Hipoteca/Bancos", "Varios"])
        f_con = st.text_input("Concepto (ej: Factura Endesa)")
        f_imp = st.number_input("Importe (€)", min_value=0.0, step=10.0)
        
        if st.form_submit_button("Guardar en Backend"):
            nueva_fila = {
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Apartamento": f_apto,
                "Concepto": f_con,
                "Categoría": f_cat,
                "Tipo": f_tipo,
                "Importe": f_imp
            }
            # Añadimos el dato y guardamos
            df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
            guardar_datos(df)
            st.success("¡Registro guardado con éxito!")
            st.rerun()

# --- PANEL CENTRAL: DASHBOARD DE CONTROL ---
ingresos = df[df["Tipo"] == "Ingreso"]["Importe"].sum()
gastos = df[df["Tipo"] == "Gasto"]["Importe"].sum()
beneficio = ingresos - gastos

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("INGRESOS TOTALES", f"{ingresos:,.2f} €")
with c2:
    st.metric("GASTOS TOTALES", f"-{gastos:,.2f} €")
with c3:
    eficiencia = (beneficio / ingresos * 100) if ingresos > 0 else 0
    st.metric("EL VICIO (NETO)", f"{beneficio:,.2f} €", delta=f"{eficiencia:.1f}% Eficiencia")

st.markdown("---")

# --- EDICIÓN DE DATOS (PARA QUE NO SEA CUTRE) ---
st.subheader("📝 Gestión del Histórico")
st.write("Puedes editar cualquier celda directamente. Al terminar, pulsa el botón de abajo.")

# El editor interactivo permite borrar filas, cambiar precios, etc.
df_editado = st.data_editor(df, use_container_width=True, num_rows="dynamic")

if st.button("💾 Sincronizar y Guardar Cambios"):
    guardar_datos(df_editado)
    st.success("Base de datos actualizada correctamente.")
    st.balloons()
