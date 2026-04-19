import streamlit as st
import pandas as pd

# 1. Configuración de pantalla completa
st.set_page_config(page_title="Dashboard Patrimonio", page_icon="🏢", layout="wide")

# 2. Título y cabecera elegante
st.title("🏢 Dashboard de Patrimonio - Granada")
st.markdown("*Herramienta de simulación y análisis financiero (Modo Solo Lectura)*")
st.markdown("---")

# 3. Datos de conexión (Tu hoja pública)
SHEET_ID = "1aI2Dg5FjEJjaFU4v37sw9ZM3inuB2apgUJ4e3IA4xF8"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

try:
    # 4. Cargamos los datos
    df = pd.read_csv(URL).dropna(how='all')
    
    # Nos aseguramos de que las columnas críticas existan para que no dé error
    if "Renta" not in df.columns:
        df["Renta"] = 0 # Si no existe, la creamos a cero
    if "Estado" not in df.columns:
        df["Estado"] = "Desconocido"

    # --- PANELES SUPERIORES (KPIs) ---
    st.subheader("📊 Análisis Global")
    
    # Calculamos datos clave
    total_inmuebles = len(df)
    ingreso_mensual_potencial = df["Renta"].sum()
    ingreso_anual_potencial = ingreso_mensual_potencial * 12
    
    # Mostramos las tarjetas
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Apartamentos Gestionados", total_inmuebles)
    kpi2.metric("Ingreso Mensual (Simulado)", f"{ingreso_mensual_potencial:,.0f} €")
    kpi3.metric("Proyección Anual", f"{ingreso_anual_potencial:,.0f} €")
    
    st.markdown("---")

    # --- ZONA INTERACTIVA ---
    st.subheader("📝 Simulador de Rentas")
    st.write("Modifica los importes en la tabla inferior para ver cómo cambian los KPIs superiores. *(Nota: Al recargar la página, los datos volverán a su estado original del Excel)*")

    # Creamos un editor de datos muy visual
    df_simulado = st.data_editor(
        df,
        column_config={
            "Renta": st.column_config.NumberColumn(
                "Renta Simulada (€)",
                help="Haz doble clic para cambiar el precio",
                min_value=0,
                step=50,
                format="%d €",
            ),
            "Estado": st.column_config.SelectboxColumn(
                "Estado Actual",
                help="Elige de la lista",
                options=["Ocupado", "Libre", "Reforma"],
            )
        },
        hide_index=True,
        use_container_width=True
    )
    
    # --- ANÁLISIS VISUAL ---
    st.markdown("---")
    st.subheader("📈 Distribución de la Cartera")
    
    # Usamos las columnas para poner gráficos
    col_grafico1, col_grafico2 = st.columns(2)
    
    with col_grafico1:
        st.write("**Ingresos por Estado**")
        # Agrupamos por estado y sumamos las rentas
        datos_estado = df_simulado.groupby("Estado")["Renta"].sum().reset_index()
        if not datos_estado.empty:
            st.bar_chart(data=datos_estado, x="Estado", y="Renta", use_container_width=True)
            
    with col_grafico2:
        st.info("💡 **Consejo de Gestión:**")
        st.write("Utiliza la tabla superior para hacer escenarios: ¿Qué pasaría con tus ingresos anuales si subes la renta de los pisos del Albaicín en 50€?")
        st.write("Este dashboard es ideal para preparar estrategias antes de negociar renovaciones de contratos.")

except Exception as e:
    st.error("No se ha podido leer el archivo de Google Sheets.")
    st.write("Asegúrate de que la hoja sigue siendo pública ('Cualquier persona con el enlace').")
