import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestión de Rentas", page_icon="💰", layout="wide")

st.title("💰 Gestión de Rentas en Tiempo Real")
st.markdown("---")

# 1. Conexión con tu hoja (ID que ya conocemos)
SHEET_ID = "1aI2Dg5FjEJjaFU4v37sw9ZM3inuB2apgUJ4e3IA4xF8"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

try:
    # Leemos los datos actuales
    df = pd.read_csv(URL).dropna(how='all')

    st.subheader("Control de Importes por Apartamento")
    st.info("💡 Haz clic en la cifra de 'Renta' para cambiarla manualmente o usa las flechas que aparecen al pasar el ratón.")

    # 2. LA MAGIA: Editor de datos con configuración de columnas
    # Aquí definimos que la columna 'Renta' tenga botones y formato moneda
    df_editado = st.data_editor(
        df,
        column_config={
            "Renta": st.column_config.NumberColumn(
                "Importe Mensual (€)",
                help="Sueldo mensual del apartamento",
                min_value=0,
                max_value=5000,
                step=10, # Sube y baja de 10 en 10 con los botones
                format="%d €", # Añade el símbolo de euro automáticamente
            ),
            "Inquilino": st.column_config.TextColumn("Nombre del Inquilino"),
            "Estado": st.column_config.SelectboxColumn(
                "Disponibilidad",
                options=["Ocupado", "Libre", "En reforma"],
            )
        },
        hide_index=True,
        use_container_width=True,
    )

    # 3. Cálculo automático para tu análisis financiero
    if "Renta" in df_editado.columns:
        total_actual = df_editado["Renta"].sum()
        st.metric("Total Ingresos Mensuales", f"{total_actual} €", delta=f"{total_actual - df['Renta'].sum()} € de diferencia")

    st.markdown("---")
    if st.button("💾 Guardar cambios de forma permanente"):
        st.warning("⚠️ El diseño está listo. Para que este botón guarde los cambios en tu Google Sheets real, necesitamos activar de nuevo la 'Llave de Seguridad' (JSON) que configuramos al principio. ¿Quieres que lo intentemos ahora que la estructura está clara?")

except Exception as e:
    st.error("Error al cargar la tabla interactiva.")
