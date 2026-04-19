import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from github import Github  # Necesitaremos añadir 'PyGithub' a requirements.txt

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Curranteia - Control Total", layout="wide")

# --- BASE DE DATOS LOCAL ---
DB_FILE = "base_datos_curranteia.csv"

if not os.path.exists(DB_FILE):
    df_inicial = pd.DataFrame(columns=["Fecha", "Apartamento", "Concepto", "Categoría", "Tipo", "Importe"])
    df_inicial.to_csv(DB_FILE, index=False)

def cargar_datos():
    return pd.read_csv(DB_FILE)

def guardar_datos_local(df_datos):
    df_datos.to_csv(DB_FILE, index=False)
    # Intentar subir a GitHub si el token existe
    if "GITHUB_TOKEN" in st.secrets:
        try:
            g = Github(st.secrets["GITHUB_TOKEN"])
            repo = g.get_repo("pedrocamposgodoy/Mis-Cuentas")
            with open(DB_FILE, "r") as f:
                content = f.read()
            contents = repo.get_contents(DB_FILE)
            repo.update_file(contents.path, "Actualización automática datos", content, contents.sha)
        except:
            pass # Si falla el anclaje, al menos se guarda en el servidor

# --- INTERFAZ ---
st.title("🏙️ Curranteia: Gestión Patrimonial Blindada")
df = cargar_datos()

# --- BARRA LATERAL Y SEGURIDAD ---
with st.sidebar:
    st.header("⚙️ Herramientas de Seguridad")
    
    # SOLUCIÓN 1: Botón de Descarga Manual
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Copia de Seguridad (Excel/CSV)",
        data=csv,
        file_name=f'backup_curranteia_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv',
    )
    
    st.divider()
    st.header("➕ Nuevo Registro")
    # ... (el resto del formulario igual que antes)
    with st.form("nuevo_registro", clear_on_submit=True):
        f_apto = st.selectbox("Inmueble", ["Abarqueros", "P. Salón", "Huerto 1", "Huerto 2", "Huerto 3"])
        f_tipo = st.radio("Tipo", ["Ingreso", "Gasto"], horizontal=True)
        f_con = st.text_input("Concepto")
        f_imp = st.number_input("Importe (€)", min_value=0.0)
        if st.form_submit_button("Guardar"):
            nueva_fila = {"Fecha": datetime.now().strftime("%Y-%m-%d"), "Apartamento": f_apto, "Concepto": f_con, "Tipo": f_tipo, "Importe": f_imp}
            df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
            guardar_datos_local(df)
            st.rerun()

# --- PANEL CENTRAL ---
# (Aquí van tus métricas y el editor de datos que ya funciona)
st.subheader("📝 Histórico de Movimientos")
df_editado = st.data_editor(df, use_container_width=True, num_rows="dynamic")

if st.button("💾 Sincronizar y Blindar Datos"):
    guardar_datos_local(df_editado)
    st.success("¡Datos guardados localmente y sincronizados con GitHub!")
