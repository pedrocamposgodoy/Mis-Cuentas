import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="Curranteia - Gestión de Activos", layout="wide")

# --- 2. GESTIÓN DINÁMICA DE APARTAMENTOS ---
CONFIG_FILE = "lista_apartamentos.txt"

# Cargar o inicializar la lista de nombres
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
        f.write("Abarqueros,Puerta Real,Huerto 1,Huerto 2,Huerto 3")

def obtener_apartamentos():
    with open(CONFIG_FILE, "r") as f:
        return f.read().split(",")

def guardar_apartamentos(lista):
    with open(CONFIG_FILE, "w") as f:
        f.write(",".join(lista))

# --- 3. BASE DE DATOS DE MOVIMIENTOS ---
DB_FILE = "base_datos_curranteia.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["Fecha", "Apartamento", "Concepto", "Categoría", "Tipo", "Importe"]).to_csv(DB_FILE, index=False)

df = pd.read_csv(DB_FILE)
lista_aptos = obtener_apartamentos()

# --- 4. MENÚ PRINCIPAL (PESTAÑAS) ---
tab1, tab2 = st.tabs(["📊 Panel de Control", "⚙️ Configuración de Activos"])

with tab2:
    st.header("Gestión de la Cartera")
    st.write("Añade o elimina inmuebles de tu sistema de gestión.")
    
    nuevo_nombre = st.text_input("Nombre del nuevo apartamento")
    if st.button("➕ Añadir a Curranteia"):
        if nuevo_nombre and nuevo_nombre not in lista_aptos:
            lista_aptos.append(nuevo_nombre)
            guardar_apartamentos(lista_aptos)
            st.success(f"'{nuevo_nombre}' añadido con éxito.")
            st.rerun()

    st.divider()
    st.subheader("Inmuebles actuales")
    for i, apto in enumerate(lista_aptos):
        col_n, col_b = st.columns([4, 1])
        col_n.write(f"🏢 **{apto}**")
        if col_b.button("Eliminar", key=f"del_{i}"):
            lista_aptos.remove(apto)
            guardar_apartamentos(lista_aptos)
            st.rerun()

with tab1:
    st.title("🏙️ Curranteia: Estado de Rentas")
    
    # Métricas Globales
    ingresos = df[df["Tipo"] == "Ingreso"]["Importe"].sum()
    gastos = df[df["Tipo"] == "Gasto"]["Importe"].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("INGRESOS TOTALES", f"{ingresos:,.2f} €")
    c2.metric("GASTOS TOTALES", f"-{gastos:,.2f} €")
    c3.metric("RESULTADO NETO", f"{ingresos - gastos:,.2f} €")

    st.divider()
    
    # Listado visual de rentas por apartamento
    st.subheader("Rendimiento por Activo")
    cols = st.columns(len(lista_aptos))
    for i, apto in enumerate(lista_aptos):
        d_apto = df[df["Apartamento"] == apto]
        n_apto = d_apto[d_apto["Tipo"] == "Ingreso"]["Importe"].sum() - d_apto[d_apto["Tipo"] == "Gasto"]["Importe"].sum()
        with cols[i]:
            st.metric(apto, f"{n_apto:,.0f} €")

# --- BARRA LATERAL (Entrada de datos) ---
with st.sidebar:
    st.header("📝 Nuevo Movimiento")
    with st.form("registro", clear_on_submit=True):
        f_apto = st.selectbox("Inmueble", lista_aptos)
        f_tipo = st.radio("Tipo", ["Ingreso", "Gasto"], horizontal=True)
        f_imp = st.number_input("Importe (€)", min_value=0.0)
        if st.form_submit_button("Guardar"):
            # Lógica de guardado...
            pass
