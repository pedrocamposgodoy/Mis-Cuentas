import streamlit as st
from streamlit_gsheets import GSheetConnection

st.title("Control de Apartamentos - CurranteIA")

# Intentar la conexión con Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetConnection)
    # Leemos la hoja (por defecto la primera pestaña)
    df = conn.read()
    
    st.success("¡Conexión total, Pedro! Ya leo tu Google Sheets.")
    st.write("Estos son los datos que tienes en la nube:")
    st.dataframe(df) # Muestra tu tabla de inquilinos
    
except Exception as e:
    st.error("Todavía no puedo leer la hoja.")
    st.info("Revisa si pegaste bien el JSON en los Secrets de Streamlit.")
    st.write("Error técnico para investigar:", e)
