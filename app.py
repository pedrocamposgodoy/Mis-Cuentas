import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Diagnóstico de Conexión - Pedro")

try:
    # 1. Intentamos conectar
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. Intentamos leer solo para ver si hay error de permisos
    df = conn.read()
    
    st.success("¡POR FIN! Conexión exitosa.")
    st.dataframe(df)

except Exception as e:
    st.error("Error detectado")
    # Este bloque nos dirá el email exacto que está intentando entrar
    if "service_account" in st.secrets["connections"]["gsheets"]:
        import json
        info = json.loads(st.secrets["connections"]["gsheets"]["service_account"])
        email_en_secrets = info.get("client_email")
        st.warning(f"La app está intentando entrar con este email: {email_en_secrets}")
        st.info("Copia ese email de arriba y asegúrate de que sea EXACTAMENTE el que tiene permiso de EDITOR en tu hoja de Google.")
    
    st.write("Detalle técnico del error:", e)
