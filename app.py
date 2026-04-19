import streamlit as st
import pandas as pd

# Configuración profesional de la página
st.set_page_config(page_title="Control Apartamentos", page_icon="🏨", layout="wide")

st.title("🏨 Gestión de Apartamentos - Granada")
st.markdown("---")

# URL de lectura (la que ya nos funciona)
SHEET_ID = "1aI2Dg5FjEJjaFU4v37sw9ZM3inuB2apgUJ4e3IA4xF8"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# Creamos dos pestañas para organizar tu mesa de trabajo
tab1, tab2 = st.tabs(["📊 Ver Apartamentos", "➕ Registrar Inquilino"])

# PESTAÑA 1: EL VISOR DE DATOS
with tab1:
    st.subheader("Estado actual de los alquileres")
    try:
        df = pd.read_csv(URL).dropna(how='all')
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            # Un pequeño panel de control métrico
            col1, col2 = st.columns(2)
            col1.metric("Total Inquilinos", len(df))
        else:
            st.info("La tabla está vacía en este momento.")
    except Exception as e:
        st.error("No se pudieron cargar los datos.")

# PESTAÑA 2: EL FORMULARIO DE ENTRADA
with tab2:
    st.subheader("Ficha de nuevo ingreso")
    
    # Creamos la caja del formulario
    with st.form("formulario_nuevo"):
        st.write("Rellena los datos para actualizar el Excel automáticamente:")
        
        # Organizamos en dos columnas para que quede elegante
        col_izq, col_der = st.columns(2)
        
        with col_izq:
            nombre = st.text_input("Nombre completo del inquilino")
            # Puedes cambiar los nombres de los pisos por los tuyos reales
            apartamento = st.selectbox("Asignar Apartamento", ["Centro", "Albaicín", "Realejo", "Otro"])
            
        with col_der:
            precio = st.number_input("Renta Mensual (€)", min_value=0, step=50)
            fecha = st.date_input("Fecha de firma del contrato")
            
        st.markdown("---")
        # El botón clave
        enviado = st.form_submit_button("💾 Guardar en Base de Datos")

        if enviado:
            # Aquí es donde meteremos el código de escritura en el futuro
            st.success(f"¡Datos capturados! -> {nombre} | {apartamento} | {precio}€")
            st.warning("⚠️ Nota técnica: El diseño está listo, pero para que este botón escriba realmente en Google Sheets, necesitaremos configurar de nuevo la 'Llave JSON' en los Secrets.")
