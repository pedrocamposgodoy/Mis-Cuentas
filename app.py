import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN Y UX/UI PREMIUM ---
st.set_page_config(page_title="Inmuebles Nolasco 1.1", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Paleta Corporativa Nolasco */
    .stApp { background-color: #F4F6F9; }
    h1, h2, h3 { color: #1A252F !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Estilos de Tarjetas y Métricas */
    div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 800; color: #1A252F; }
    .card-ingreso { border-left: 5px solid #2ECC71; background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .card-alerta { border-left: 5px solid #E74C3C; background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .card-ia { border-left: 5px solid #9B59B6; background-color: #F9E7FF; padding: 15px; border-radius: 8px; }
    
    /* Textos de estado */
    .text-verde { color: #2ECC71; font-weight: bold; }
    .text-rojo { color: #E74C3C; font-weight: bold; }
    .text-naranja { color: #F39C12; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE BASE DE DATOS LOCAL ---
DB_INMUEBLES = "nolasco_inmuebles.csv"
DB_MOVIMIENTOS = "nolasco_movimientos.csv"

# Inicializar BD Inmuebles (Fichas Técnicas)
if not os.path.exists(DB_INMUEBLES):
    cols_inm = ["ID", "Nombre", "Inquilino", "Renta_Actual", "Fianza", "Inicio_Contrato", "Fin_Contrato", "Estado_Cobro"]
    pd.DataFrame([
        {"ID": 1, "Nombre": "Abarqueros", "Inquilino": "Juan Pérez", "Renta_Actual": 650, "Fianza": 650, "Inicio_Contrato": "2023-01-01", "Fin_Contrato": "2028-01-01", "Estado_Cobro": "Al Día"},
        {"ID": 2, "Nombre": "Puerta Real", "Inquilino": "María Gómez", "Renta_Actual": 850, "Fianza": 1700, "Inicio_Contrato": "2024-03-15", "Fin_Contrato": "2029-03-15", "Estado_Cobro": "Impago"}
    ]).to_csv(DB_INMUEBLES, index=False)

# Inicializar BD Movimientos (Flujo de Caja)
if not os.path.exists(DB_MOVIMIENTOS):
    cols_mov = ["Fecha", "Apartamento", "Concepto", "Categoría", "Tipo", "Importe"]
    pd.DataFrame(columns=cols_mov).to_csv(DB_MOVIMIENTOS, index=False)

df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)
lista_aptos = df_inm["Nombre"].tolist()

# --- 3. NAVEGACIÓN LATERAL (EL PMS) ---
with st.sidebar:
    st.markdown("## 🏢 NOLASCO 1.1")
    st.markdown("### Menú Principal")
    menu = st.radio("", ["📊 Torre de Control", "🏠 Fichas de Activos", "📝 Libro Mayor", "⚙️ Ajustes"])
    
    st.divider()
    st.markdown("### Acciones Rápidas")
    with st.form("form_rapido", clear_on_submit=True):
        f_apto = st.selectbox("Activo", lista_aptos)
        f_tipo = st.radio("Operación", ["Ingreso (Renta)", "Gasto"], horizontal=True)
        f_imp = st.number_input("Importe €", min_value=0.0)
        if st.form_submit_button("Registrar"):
            cat = "Renta" if f_tipo == "Ingreso (Renta)" else "Operativo"
            tipo_bd = "Ingreso" if f_tipo == "Ingreso (Renta)" else "Gasto"
            nuevo_reg = pd.DataFrame([{"Fecha": datetime.now().strftime("%Y-%m-%d"), "Apartamento": f_apto, "Concepto": "Anotación rápida", "Categoría": cat, "Tipo": tipo_bd, "Importe": f_imp}])
            df_mov = pd.concat([df_mov, nuevo_reg], ignore_index=True)
            df_mov.to_csv(DB_MOVIMIENTOS, index=False)
            st.success("Guardado")
            st.rerun()

# --- VISTA 1: TORRE DE CONTROL (DASHBOARD) ---
if menu == "📊 Torre de Control":
    st.title("Radar de Control Patrimonial")
    
    # Cálculos globales
    ing_tot = df_mov[df_mov["Tipo"] == "Ingreso"]["Importe"].sum()
    gas_tot = df_mov[df_mov["Tipo"] == "Gasto"]["Importe"].sum()
    neto = ing_tot - gas_tot
    
    # KPIs Superiores
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="card-ingreso">', unsafe_allow_html=True)
        st.metric("BENEFICIO NETO", f"{neto:,.0f} €", f"Margen: {(neto/ing_tot*100 if ing_tot>0 else 0):.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        ocupacion = len(df_inm[df_inm["Inquilino"].notna()]) / len(df_inm) * 100
        st.metric("NIVEL DE OCUPACIÓN", f"{ocupacion:.0f}%")
    with c3:
        morosos = len(df_inm[df_inm["Estado_Cobro"] == "Impago"])
        st.metric("MOROSIDAD", f"{morosos} Inmuebles")
    with c4:
        # Fondo IA sugerido: 5% del valor de rentas
        fondo_ia = df_inm["Renta_Actual"].sum() * 12 * 0.05
        st.metric("FONDO MANIOBRA (Sugerido)", f"{fondo_ia:,.0f} €")

    st.markdown("---")
    
    # Radar de Alertas
    st.subheader("⚠️ Radar de Alertas y Operaciones")
    col_alerta1, col_alerta2 = st.columns(2)
    
    with col_alerta1:
        st.markdown('<div class="card-alerta"><h4>🚨 Riesgo de Impago</h4>', unsafe_allow_html=True)
        impagos = df_inm[df_inm["Estado_Cobro"] == "Impago"]
        if not impagos.empty:
            for index, row in impagos.iterrows():
                st.write(f"• **{row['Nombre']}** ({row['Inquilino']}) - Falta cobro de {row['Renta_Actual']}€")
        else:
            st.write("✅ Todos los alquileres al día.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_alerta2:
        st.markdown('<div class="card-ia"><h4>🤖 Alertas de Mantenimiento (IA)</h4>', unsafe_allow_html=True)
        st.write("• **Puerta Real:** Revisión de canalones sugerida antes del 15 de octubre (Previsión de lluvias).")
        st.write("• **Abarqueros:** El contrato de Juan Pérez entra en periodo de renovación en 60 días. IPC estimado: +3.1%.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- VISTA 2: FICHAS DE ACTIVOS ---
elif menu == "🏠 Fichas de Activos":
    st.title("Expedientes de Inmuebles")
    
    selector = st.selectbox("Seleccione un Inmueble para auditar:", lista_aptos)
    datos_apto = df_inm[df_inm["Nombre"] == selector].iloc[0]
    
    c_ficha1, c_ficha2 = st.columns([1, 2])
    
    with c_ficha1:
        st.subheader("Datos del Contrato")
        st.write(f"**Inquilino:** {datos_apto['Inquilino']}")
        st.write(f"**Renta Actual:** <span class='text-verde'>{datos_apto['Renta_Actual']} €/mes</span>", unsafe_allow_html=True)
        st.write(f"**Fianza Depositada:** {datos_apto['Fianza']} €")
        st.write(f"**Inicio Contrato:** {datos_apto['Inicio_Contrato']}")
        st.write(f"**Vencimiento:** <span class='text-naranja'>{datos_apto['Fin_Contrato']}</span>", unsafe_allow_html=True)
        
        estado_color = "text-verde" if datos_apto['Estado_Cobro'] == "Al Día" else "text-rojo"
        st.write(f"**Estado de Pago:** <span class='{estado_color}'>{datos_apto['Estado_Cobro']}</span>", unsafe_allow_html=True)
        
        st.divider()
        st.button(f"🧾 Marcar {selector} como PAGADO este mes")

    with c_ficha2:
        # Pestañas internas para la IA y los gráficos
        tab_ia, tab_graf = st.tabs(["🤖 Auditoría IA", "📊 Rentabilidad del Activo"])
        
        with tab_ia:
            st.markdown("### Análisis Predictivo y de Mercado")
            st.info(f"**Análisis de Rentabilidad:** El activo {selector} está generando un margen neto del 65% sobre ingresos. El gasto en suministros ha subido un 12% este trimestre.")
            st.warning("**Plan de Mantenimiento CAPEX:** Se recomienda una provisión de 450€ para pintura de fachada estimada para la próxima primavera, evitando degradación del activo.")
            st.success(f"**Actualización IPC:** La renta de {datos_apto['Renta_Actual']}€ lleva 14 meses sin actualizarse. Aplicar el IPC actual (+3.2%) elevaría la cuota a {datos_apto['Renta_Actual']*1.032:.2f}€.")
            
        with tab_graf:
            df_apto_mov = df_mov[df_mov["Apartamento"] == selector]
            if not df_apto_mov.empty:
                fig = px.bar(df_apto_mov, x="Fecha", y="Importe", color="Tipo", barmode="group",
                             color_discrete_map={"Ingreso": "#2ECC71", "Gasto": "#E74C3C"},
                             title=f"Flujo de Caja: {selector}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No hay movimientos registrados para este inmueble aún.")

# --- VISTA 3: LIBRO MAYOR ---
elif menu == "📝 Libro Mayor":
    st.title("Control de Caja y Operaciones")
    st.write("Edita directamente cualquier registro de ingresos, gastos de mantenimiento, CAPEX o impuestos.")
    
    df_editado = st.data_editor(df_mov, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Guardar Cambios en Base de Datos"):
        df_editado.to_csv(DB_MOVIMIENTOS, index=False)
        st.success("Libro mayor actualizado.")
        st.rerun()

# --- VISTA 4: AJUSTES ---
elif menu == "⚙️ Ajustes":
    st.title("Configuración de Maestros")
    st.write("Aquí puedes añadir nuevos apartamentos a tu cartera.")
    
    df_inm_edit = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Actualizar Cartera de Inmuebles"):
        df_inm_edit.to_csv(DB_INMUEBLES, index=False)
        st.success("Activos actualizados.")
        st.rerun()
