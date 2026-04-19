import streamlit as st
import pandas as pd

# Configuración de la página (más ancha y con icono)
st.set_page_config(page_title="Dashboard Apartamentos", page_icon="🏢", layout="wide")

st.title("🏢 Panel de Control de Apartamentos - Granada")
st.markdown("---")

# 1. Obtenemos los datos (tu URL pública)
SHEET_ID = "1aI2Dg5FjEJjaFU4v37sw9ZM3inuB2apgUJ4e3IA4xF8"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

try:
    df = pd.read_csv(URL).dropna(how='all')
    
    # 2. SECCIÓN VISUAL: Tarjetas de Resumen (KPIs)
    st.subheader("📊 Resumen Financiero y de Ocupación")
    
    # Creamos 3 columnas para poner tarjetas de colores
    col1, col2, col3 = st.columns(3)
    
    # Suponiendo que tienes una columna de precios, calculamos el total. 
    # (Si no se llama 'Precio', cambia la palabra abajo por el nombre exacto de tu columna)
    total_ingresos = 0
    if 'Precio' in df.columns:
        total_ingresos = df['Precio'].sum()
        
    with col1:
        st.metric(label="Total Inquilinos", value=f"{len(df)} activos", delta="1 este mes")
    with col2:
        st.metric(label="Ingresos Estimados", value=f"{total_ingresos} €", delta="Estable", delta_color="normal")
    with col3:
        st.metric(label="Apartamentos Libres", value="0", delta="-1 ocupado hoy", delta_color="inverse")

    st.markdown("---")

    # 3. SECCIÓN INTERACTIVA: La tabla editable
    st.subheader("📝 Base de Datos Editable")
    st.info("💡 Haz doble clic en cualquier celda para modificar el dato directamente.")
    
    # MAGIA: Usamos data_editor en lugar de dataframe
    datos_modificados = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic" # Esto te permite añadir filas nuevas desde la propia tabla
    )

    # 4. SECCIÓN FORMULARIO: Con botones de subir/bajar importes
    st.markdown("---")
    st.subheader("⚙️ Ajuste Rápido de Renta")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("Usa los botones o escribe el importe exacto:")
        # number_input tiene botones + y - integrados. 'step=50' hace que suba de 50 en 50.
        nueva_renta = st.number_input("Modificar importe de renta (€)", min_value=0, value=650, step=50)
    with col_b:
        st.write(" ") # Espacio en blanco para alinear
        st.write(" ") 
        st.button(f"Aplicar {nueva_renta}€ al seleccionado", type="primary")

except Exception as e:
    st.error("No se pudieron cargar los datos de la hoja pública.")
    st.write(e)
