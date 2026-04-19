import streamlit as st
import pandas as pd

# Configuración de pantalla
st.set_page_config(page_title="Finanzas Estáticas", page_icon="📊", layout="wide")

st.title("📊 Simulador de Finanzas Estáticas - Granada")
st.markdown("*Entorno seguro de proyecciones y análisis de rentabilidad*")
st.markdown("---")

# Conexión directa (Lectura simple)
SHEET_ID = "1aI2Dg5FjEJjaFU4v37sw9ZM3inuB2apgUJ4e3IA4xF8"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

try:
    # Cargamos los datos limpios
    df = pd.read_csv(URL).dropna(how='all')
    
    # Protecciones por si las columnas cambian de nombre en el Excel
    if "Renta" not in df.columns:
        df["Renta"] = 0 
    if "Estado" not in df.columns:
        df["Estado"] = "Desconocido"

    # --- KPIs Y MÉTRICAS GLOBALES ---
    st.subheader("Resumen de la Cartera")
    
    total_inmuebles = len(df)
    ingreso_mensual = df["Renta"].sum()
    ingreso_anual = ingreso_mensual * 12
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Apartamentos Gestionados", total_inmuebles)
    kpi2.metric("Ingreso Mensual (Simulado)", f"{ingreso_mensual:,.0f} €")
    kpi3.metric("Proyección Anual", f"{ingreso_anual:,.0f} €")
    
    st.markdown("---")

    # --- TABLA INTERACTIVA DE PRUEBAS ---
    st.subheader("Tablero de Simulación")
    st.write("Modifica las rentas directamente en la tabla para ver el impacto en los gráficos. *(Los cambios realizados aquí no afectarán a tu Excel original)*")

    df_simulado = st.data_editor(
        df,
        column_config={
            "Renta": st.column_config.NumberColumn(
                "Renta Simulada (€)",
                min_value=0,
                step=50,
                format="%d €",
            ),
            "Estado": st.column_config.SelectboxColumn(
                "Estado Actual",
                options=["Ocupado", "Libre", "Reforma"],
            )
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown("---")
    
    # --- GRÁFICOS Y ESTRATEGIA ---
    st.subheader("Distribución de Ingresos")
    
    col_grafico1, col_grafico2 = st.columns(2)
    
    with col_grafico1:
        datos_estado = df_simulado.groupby("Estado")["Renta"].sum().reset_index()
        if not datos_estado.empty:
            st.bar_chart(data=datos_estado, x="Estado", y="Renta", use_container_width=True)
            
    with col_grafico2:
        st.info("💡 **Estrategia de Precios:**")
        st.write("¿Qué impacto tendría en la facturación anual subir 50€ la cuota a las próximas renovaciones en el Centro o el Albaicín? Ajusta las casillas de la tabla y compruébalo al instante.")

except Exception as e:
    st.error("No se ha podido conectar con la base de datos.")
    st.write("Verifica que el Excel sigue publicado como 'Cualquier persona con el enlace'.")
