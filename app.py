import streamlit as st
import pandas as pd
import os
from datetime import datetime
from github import Github
import plotly.express as px

# --- 1. CONFIGURACIÓN ESTÉTICA PREMIUM (UX/UI) ---
st.set_page_config(page_title="Curranteia v2.0", layout="wide", initial_sidebar_state="expanded")

# Inyección de CSS para colores vivos y tarjetas profesionales
st.markdown("""
    <style>
    /* Fondo Gris Perla Profesional */
    .stApp { background-color: #F8F9FA; }
    
    /* Tipografías y Títulos */
    h1, h2, h3 { color: #1B2631 !important; font-family: 'Trebuchet MS', sans-serif; }
    
    /* Tarjetas de Métricas */
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; color: #1B2631; }
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #2E86C1;
    }
    
    /* Colores Específicos */
    .ingreso-text { color: #239B56; font-weight: bold; }
    .gasto-text { color: #CB4335; font-weight: bold; }
    
    /* Estilo de los Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #EAECEE;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #2E86C1 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE DATOS (BACKEND & GITHUB) ---
DB_FILE = "base_datos_curranteia.csv"
CONFIG_FILE = "config_aptos.txt"

def sincronizar_github(contenido):
    if "GITHUB_TOKEN" in st.secrets:
        try:
            g = Github(st.secrets["GITHUB_TOKEN"])
            repo = g.get_repo("pedrocamposgodoy/Mis-Cuentas")
            contents = repo.get_contents(DB_FILE)
            repo.update_file(contents.path, f"Update {datetime.now()}", contenido, contents.sha)
        except Exception as e:
            st.error(f"Error sincronizando con GitHub: {e}")

def cargar_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f: f.write("Abarqueros,Puerta Real,Huerto 1,Huerto 2,Huerto 3")
    with open(CONFIG_FILE, "r") as f: return f.read().split(",")

def guardar_config(lista):
    with open(CONFIG_FILE, "w") as f: f.write(",".join(lista))

# Inicialización de Datos
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["Fecha", "Apartamento", "Concepto", "Categoría", "Tipo", "Importe"]).to_csv(DB_FILE, index=False)

df = pd.read_csv(DB_FILE)
aptos_lista = cargar_config()
categorias_gasto = ["Suministros", "Limpieza", "Mantenimiento", "Impuestos", "Hipoteca", "Seguros", "Varios"]

# --- 3. ESTRUCTURA DE LA WEB (TABS) ---
st.title("🏙️ Curranteia v2.0: Gestión Patrimonial")
tab_global, tab_fichas, tab_libro, tab_config = st.tabs([
    "📊 Dashboard Global", "🏠 Fichas Independientes", "📝 Libro de Registro", "⚙️ Configuración"
])

# --- TAB 1: DASHBOARD GLOBAL ---
with tab_global:
    st.subheader("Estado Financiero de la Cartera")
    
    ing_t = df[df["Tipo"] == "Ingreso"]["Importe"].sum()
    gas_op = df[(df["Tipo"] == "Gasto") & (~df["Categoría"].isin(["Hipoteca", "Impuestos"]))]["Importe"].sum()
    gas_cap = df[df["Categoría"].isin(["Hipoteca", "Impuestos"])]["Importe"].sum()
    beneficio = ing_t - gas_op - gas_cap

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("INGRESOS BRUTOS", f"{ing_t:,.2f} €")
    m2.metric("GASTOS OP.", f"-{gas_op:,.2f} €")
    m3.metric("IMPUESTOS/BANCO", f"-{gas_cap:,.2f} €")
    m4.metric("BENEFICIO NETO (EL VICIO)", f"{beneficio:,.2f} €", delta=f"{(beneficio/ing_t*100 if ing_t>0 else 0):.1f}%")

    st.markdown("---")
    st.subheader("Rendimiento por Activo")
    
    # Grid de tarjetas por apartamento
    rows = [aptos_lista[i:i + 3] for i in range(0, len(aptos_lista), 3)]
    for row in rows:
        cols = st.columns(3)
        for i, apto in enumerate(row):
            d_a = df[df["Apartamento"] == apto]
            i_a = d_a[d_a["Tipo"] == "Ingreso"]["Importe"].sum()
            g_a = d_a[d_a["Tipo"] == "Gasto"]["Importe"].sum()
            n_a = i_a - g_a
            with cols[i]:
                with st.container(border=True):
                    st.markdown(f"### {apto}")
                    st.markdown(f"Neto: <span class='ingreso-text'>{n_a:,.2f} €</span>", unsafe_allow_html=True)
                    st.progress(min(max(n_a/i_a if i_a > 0 else 0, 0.0), 1.0))

# --- TAB 2: FICHAS INDEPENDIENTES ---
with tab_fichas:
    apto_sel = st.selectbox("Seleccione un inmueble para ver su detalle:", aptos_lista)
    df_a = df[df["Apartamento"] == apto_sel]
    
    col_f1, col_f2 = st.columns([1, 2])
    
    with col_f1:
        st.info(f"**Ficha Técnica: {apto_sel}**")
        i_f = df_a[df_a["Tipo"] == "Ingreso"]["Importe"].sum()
        g_f = df_a[df_a["Tipo"] == "Gasto"]["Importe"].sum()
        st.write(f"Ingresos Totales: {i_f:,.2f} €")
        st.write(f"Gastos Totales: {g_f:,.2f} €")
        st.write(f"Margen: {((i_f-g_f)/i_f*100 if i_f>0 else 0):.1f}%")
        
        # Gráfico de tarta de gastos
        if not df_a[df_a["Tipo"] == "Gasto"].empty:
            fig_pie = px.pie(df_a[df_a["Tipo"] == "Gasto"], values='Importe', names='Categoría', 
                            title="Distribución de Gastos", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_f2:
        st.write("**Últimos Movimientos Registrados**")
        st.dataframe(df_a.sort_values(by="Fecha", ascending=False), use_container_width=True)

# --- TAB 3: LIBRO DE REGISTRO ---
with tab_libro:
    col_reg1, col_reg2 = st.columns([1, 3])
    
    with col_reg1:
        st.subheader("Nueva Entrada")
        with st.form("form_registro", clear_on_submit=True):
            f_apto = st.selectbox("Apartamento", aptos_lista)
            f_tipo = st.radio("Tipo", ["Ingreso", "Gasto"], horizontal=True)
            f_cat = st.selectbox("Categoría", ["Renta", "Fianza"] if f_tipo == "Ingreso" else categorias_gasto)
            f_con = st.text_input("Concepto")
            f_imp = st.number_input("Importe (€)", min_value=0.0)
            
            if st.form_submit_button("Añadir al Libro Mayor"):
                nueva_f = pd.DataFrame([{"Fecha": datetime.now().strftime("%Y-%m-%d"), "Apartamento": f_apto, 
                                       "Concepto": f_con, "Categoría": f_cat, "Tipo": f_tipo, "Importe": f_imp}])
                df = pd.concat([df, nueva_f], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                sincronizar_github(df.to_csv(index=False))
                st.success("Guardado")
                st.rerun()

    with col_reg2:
        st.subheader("Libro Mayor (Edición Directa)")
        df_ed = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Sincronizar Cambios de Tabla"):
            df_ed.to_csv(DB_FILE, index=False)
            sincronizar_github(df_ed.to_csv(index=False))
            st.success("Base de Datos actualizada")
            st.rerun()

# --- TAB 4: CONFIGURACIÓN ---
with tab_config:
    st.subheader("Gestión de la Cartera de Activos")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        nuevo_apto = st.text_input("Nombre de nuevo apartamento")
        if st.button("Añadir Inmueble"):
            if nuevo_apto and nuevo_apto not in aptos_lista:
                aptos_lista.append(nuevo_apto)
                guardar_config(aptos_lista)
                st.rerun()
    
    with col_c2:
        apto_del = st.selectbox("Eliminar Inmueble", aptos_lista)
        if st.button("Eliminar"):
            aptos_lista.remove(apto_del)
            guardar_config(aptos_lista)
            st.rerun()

# --- BARRA LATERAL (SEGURIDAD) ---
with st.sidebar:
    st.title("🛡️ Seguridad")
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Backup CSV", data=csv_data, file_name=f'curranteia_backup_{datetime.now().strftime("%Y%m%d")}.csv')
    st.info("Utilice este botón semanalmente para guardar sus datos físicamente.")
