import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Control Apartamentos", layout="wide")
st.title("🏨 Control de Apartamentos - Granada")

# 1. Tu ID de la hoja (Es el código que ya tenemos)
SHEET_ID = "1aI2Dg5FjEJjaFU4v37sw9ZM3inuB2apgUJ4e3IA4xF8"

# 2. Creamos el enlace mágico que descarga los datos directamente
# El "&gid=0" al final obliga a leer la PRIMERA pestaña del Excel
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

try:
    # 3. Leemos los datos del Excel
    # Usamos 'skip_blank_lines' para que no lea filas vacías
    df = pd.read_csv(URL).dropna(how='all')

    if not df.empty:
        st.success("¡Conexión lograda! Aquí tienes tus datos actualizados:")
        
        # 4. Mostramos la tabla bien bonita
        st.dataframe(df, use_container_width=True)
        
        # Pequeño resumen estadístico (como buen economista)
        st.info(f"Tienes un total de {len(df)} registros cargados.")
    else:
        st.warning("El puente funciona, pero la hoja parece estar vacía.")

except Exception as e:
    st.error("Algo impide leer los datos.")
    st.write("### 🛠️ Pasos para solucionar esto ahora mismo:")
    st.write("1. Abre tu Google Sheets.")
    st.write("2. Pulsa el botón azul **'Compartir'** (arriba a la derecha).")
    st.write("3. En 'Acceso general', cambia 'Restringido' por **'Cualquier persona con el enlace'**.")
    st.write("4. Asegúrate de que tus datos empiecen en la **Fila 1** del Excel.")
