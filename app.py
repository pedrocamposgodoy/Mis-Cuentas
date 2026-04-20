import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN ESTÉTICA NOLASCO 1.1 ---
st.set_page_config(page_title="Inmuebles Nolasco 1.1", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #F4F6F9; }
    h1, h2, h3 { color: #1B2631 !important; font-family: 'Segoe UI', sans-serif; }
    div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 800; color: #1B2631; }
    .stTabs [aria-selected="true"] { background-color: #2E86C1 !important; color: white !important; }
    .card-ia { border-left: 5px solid #9B59B6; background-color: #F9E7FF; padding: 15px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE LA CARTERA "NOLASCO 1.1" ---
DB_INMUEBLES = "nolasco_inmuebles.csv"
DB_MOVIMIENTOS = "nolasco_movimientos.csv"

# Datos Maestros de tu cartera
datos_iniciales = [
    {"ID": 1, "Nombre": "Abarqueros", "Inquilino": "Juan Pérez", "Renta_Actual": 650.0, "Fianza": 650.0, "Inicio_Contrato": "2023-01-01", "Fin_Contrato": "2028-01-01", "Estado_Cobro": "Al Día"},
    {"ID": 2, "Nombre": "Puerta Real", "Inquilino": "María Gómez", "Renta_Actual": 850.0, "Fianza": 1700.0, "Inicio_Contrato": "2024-03-15", "Fin_Contrato": "2029-03-15", "Estado_Cobro": "Impago"},
    {"ID": 3, "Nombre": "Huerto 1", "Inquilino": "Sin Inquilino", "Renta_Actual": 0.0, "Fianza": 0.0, "Inicio_Contrato": "N/A", "Fin_Contrato": "N/A", "Estado_Cobro": "Disponible"},
    {"ID": 4, "Nombre": "Huerto 2", "Inquilino": "Sin Inquilino", "Renta_Actual": 0.0, "Fianza": 0.0, "Inicio_Contrato": "N/A", "Fin_Contrato": "N/A", "Estado_Cobro": "Disponible"},
    {"ID": 5, "Nombre": "Huerto 3", "Inquilino": "Sin Inquilino", "Renta_Actual": 0.0, "Fianza": 0.0, "Inicio_Contrato": "N/A", "Fin_Contrato": "N/A", "Estado_Cobro": "Disponible"}
]

if not os.path.exists(DB_INMUEBLES):
    pd.DataFrame(datos_iniciales).to_csv(DB_INMUEBLES, index=False)

if not os.path.exists(DB_MOVIMIENTOS):
    pd.DataFrame(columns=["Fecha", "Apartamento", "Concepto", "Categoría", "Tipo", "Importe"]).to_csv(DB_MOVIMIENTOS, index=False)

df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)
lista_aptos = df_inm["Nombre"].tolist()

# --- 3. NAVEGACIÓN Y MENÚ ---
with st.sidebar:
    st.title("🏢 NOLASCO 1.1")
    menu = st.radio("Gestión", ["📊 Torre de Control", "🏠 Fichas de Activos", "📝 Libro Mayor", "⚙️ Configuración"])
    
    st.divider()
    st.subheader("Entrada Rápida")
    with st.form("quick_form", clear_on_submit=True):
        q_apto = st.selectbox("Activo", lista_aptos)
        q_tipo = st.radio("Tipo", ["Ingreso", "Gasto"], horizontal=True)
        q_imp = st.number_input("Importe (€)", min_value=0.0)
        if st.form_submit_button("Registrar"):
            nuevo = pd.DataFrame([{"Fecha": datetime.now().strftime("%Y-%m-%d"), "Apartamento": q_apto, "Concepto": "Registro rápido", "Categoría": "Varios", "Tipo": q_tipo, "Importe": q_imp}])
            df_mov = pd.concat([df_mov, nuevo], ignore_index=True)
            df_mov.to_csv(DB_MOVIMIENTOS, index=False)
            st.rerun()

# --- VISTA: TORRE DE CONTROL ---
if menu == "📊 Torre de Control":
    st.title("Radar Patrimonial Global")
    
    ing = df_mov[df_mov["Tipo"] == "Ingreso"]["Importe"].sum()
    gas = df_mov[df_mov["Tipo"] == "Gasto"]["Importe"].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("INGRESOS ACUMULADOS", f"{ing:,.2f} €")
    c2.metric("GASTOS ACUMULADOS", f"-{gas:,.2f} €")
    c3.metric("MARGEN NETO", f"{ing-gas:,.2f} €")

    st.divider()
    
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        st.subheader("⚠️ Alertas de Cobro")
        morosos = df_inm[df_inm["Estado_Cobro"] == "Impago"]
        if not morosos.empty:
            for _, row in morosos.iterrows():
                st.error(f"PAGO PENDIENTE: {row['Nombre']} - {row['Inquilino']} ({row['Renta_Actual']} €)")
        else:
            st.success("Cartera al día. No se detectan impagos.")

    with col_inf2:
        st.subheader("📅 Próximos Mantenimientos (IA)")
        st.markdown("""
        <div class="card-ia">
        • <b>Huerto 1, 2 y 3:</b> Revisión de sistemas de climatización sugerida para Mayo.<br>
        • <b>Abarqueros:</b> Actualización de renta por IPC prevista para Enero 2027.
        </div>
        """, unsafe_allow_html=True)

# --- VISTA: FICHAS DE ACTIVOS ---
elif menu == "🏠 Fichas de Activos":
    st.title("Expedientes Individuales")
    sel = st.selectbox("Seleccione inmueble:", lista_aptos)
    ficha = df_inm[df_inm["Nombre"] == sel].iloc[0]
    
    f1, f2 = st.columns([1, 2])
    with f1:
        st.write(f"### Detalle: {sel}")
        st.write(f"**Inquilino:** {ficha['Inquilino']}")
        st.write(f"**Renta:** {ficha['Renta_Actual']} €")
        st.write(f"**Contrato hasta:** {ficha['Fin_Contrato']}")
        st.write(f"**Estado:** {ficha['Estado_Cobro']}")
        
        if st.button("Marcar como PAGADO"):
            df_inm.loc[df_inm["Nombre"] == sel, "Estado_Cobro"] = "Al Día"
            df_inm.to_csv(DB_INMUEBLES, index=False)
            st.rerun()

    with f2:
        tab_ia, tab_hist = st.tabs(["🤖 Auditoría IA", "📊 Historial"])
        with tab_ia:
            st.markdown(f"**Análisis de Rentabilidad para {sel}:**")
            st.info("La IA sugiere revisar el mobiliario en este activo para mantener el valor competitivo en la zona de Granada.")
        with tab_hist:
            st.dataframe(df_mov[df_mov["Apartamento"] == sel], use_container_width=True)

# --- VISTAS RESTANTES ---
elif menu == "📝 Libro Mayor":
    st.title("Libro de Movimientos")
    ed = st.data_editor(df_mov, num_rows="dynamic", use_container_width=True)
    if st.button("Guardar Cambios"):
        ed.to_csv(DB_MOVIMIENTOS, index=False)
        st.success("Guardado")

elif menu == "⚙️ Configuración":
    st.title("Maestro de Inmuebles")
    ed_inm = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True)
    if st.button("Actualizar Cartera"):
        ed_inm.to_csv(DB_INMUEBLES, index=False)
        st.success("Cartera Actualizada")
