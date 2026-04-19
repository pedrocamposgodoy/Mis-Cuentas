import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Conexión en Directo", layout="wide")
st.title("🔗 Prueba de Sincronización Real")

try:
    # 1. Establecemos la conexión usando la llave oficial
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. Leemos los datos. El ttl=0 significa "no uses memoria, lee en directo"
    df = conn.read(ttl=0)
    
    st.success("¡Lectura directa autorizada! Los datos que ves aquí son exactamente los que están en la nube.")
    
    # 3. Mostramos la tabla editable
    df_editado = st.data_editor(df, use_container_width=True)
    
    st.markdown("---")
    
    # 4. El botón mágico para escribir en el Excel
    if st.button("💾 Enviar cambios al Excel"):
        # Esta línea coge la tabla editada y sobrescribe la hoja de Google
        conn.update(worksheet="Hoja 1", data=df_editado)
        st.success("¡Base de datos actualizada! Abre tu Excel y comprueba los cambios.")
        st.balloons()

except Exception as e:
    st.error("Error en la conexión maestra.")
    st.write(e)
