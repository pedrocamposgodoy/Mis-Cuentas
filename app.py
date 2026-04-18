import streamlit as st
# Cambio clave: ahora la conexión se llama de forma más directa
from streamlit_gsheets import GSheetsConnection

st.title("Control de Apartamentos - CurranteIA")

# Intentar la conexión con Google Sheets
try:
    # Fíjate que ahora lleva una 's' al final: GSheetsConnection
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    df = conn.read()
    
    st.success("¡Conexión total, Pedro! Ya leo tu Google Sheets.")
    st.write("Estos son los datos que tienes en la nube:")
    st.dataframe(df)

except Exception as e:
    st.error("Todavía no puedo leer la hoja.")
    st.info("Revisa si los Secrets de Streamlit están bien configurados.")
    st.write("Error técnico para investigar:", e)
