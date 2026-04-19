import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Conexión en Directo", layout="wide")
st.title("🔗 Prueba de Sincronización Real")

# Ponemos la URL directamente aquí por seguridad
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1aI2Dg5FjEJjaFU4v37sw9ZM3inuB2apgUJ4e3IA4xF8"

try:
    # 1. Conectamos
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. Leemos forzando la URL para evitar pérdidas
    df = conn.read(spreadsheet=URL_EXCEL, ttl=0)
    
    st.success("¡Lectura directa autorizada! Los datos que ves aquí son exactamente los que están en la nube.")
    
    # 3. Editor
    df_editado = st.data_editor(df, use_container_width=True)
    
    st.markdown("---")
    if st.button("💾 Enviar cambios al Excel"):
        # 4. Actualizamos forzando la misma URL
        conn.update(spreadsheet=URL_EXCEL, data=df_editado)
        st.success("¡Base de datos actualizada! Abre tu Excel y comprueba los cambios.")
        st.balloons()

except Exception as e:
    st.error("Error en la conexión maestra.")
    st.write("Si sale error 404, significa que el email de 'streamlit-acceso' no está puesto como EDITOR en la hoja de Google.")
    st.write("Detalle técnico:", e)
