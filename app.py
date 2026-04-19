import streamlit as st
import pandas as pd

st.title("Control de Apartamentos - Versión Simple")

# La URL de tu hoja (asegúrate de que termina en /export?format=csv)
sheet_id = "1aI2Dg5FjEJjaFU4v37sw9ZM3inuB2apgUJ4e3IA4xF8"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    # Leemos directamente la hoja como si fuera un archivo de internet
    df = pd.read_csv(url)
    
    st.success("¡Conectado con éxito!")
    st.write("Esta es la información de tu Excel:")
    st.dataframe(df)

except Exception as e:
    st.error("No se pudo leer la hoja.")
    st.write("Asegúrate de que has puesto la hoja como 'Cualquier persona con el enlace'.")
