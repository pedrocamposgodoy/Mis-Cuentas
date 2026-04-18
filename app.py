import streamlit as st
from streamlit_gsheets import GSheetConnection

st.title("Control de Apartamentos - CurranteIA")

# Intentar la conexión con Google Sheets
try:
    # 1. Creamos la conexión
    conn = st.connection("gsheets", type=GSheetConnection)
    
    # 2. Leemos la hoja (aquí he añadido el signo igual que faltaba)
    df = conn.read()
    
    # 3. Si todo va bien, mostramos los mensajes de éxito
    st.success("¡Conexión total, Pedro! Ya leo tu Google Sheets.")
    st.write("Estos son los datos que tienes en la nube:")
    
    # 4. Mostramos la tabla con tus inquilinos
    st.dataframe(df)

except Exception as e:
    # Si algo falla, nos dará pistas aquí
    st.error("Todavía no puedo leer la hoja.")
    st.info("Revisa si pegaste bien el JSON en los Secrets de Streamlit o si compartiste la hoja con el email de la cuenta de servicio.")
    st.write("Error técnico para investigar:", e)
