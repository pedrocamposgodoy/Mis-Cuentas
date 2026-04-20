import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────
# 1. ARQUITECTURA VISUAL "NOLASCO CAPITAL V8.2"
# ─────────────────────────────────────────────
st.set_page_config(page_title="Nolasco Capital", layout="wide", page_icon="🏛️")

# Paleta de 6 colores fijos para identidad de activos
COLOR_PALETTE = ["#C9A84C", "#1B5E3B", "#8B1A1A", "#4A5568", "#0D0F12", "#2E86C1"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --ink:       #0D0F12;
    --parchment: #F7F4EF;
    --gold:      #C9A84C;
    --emerald:   #1B5E3B;
    --crimson:   #8B1A1A;
    --slate:     #4A5568;
    --card-bg:   #FFFFFF;
    --border:    #E8E2D9;
}

/* OPTIMIZACIÓN DE ESPACIO SUPERIOR */
.block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: var(--parchment) !important; color: var(--ink); }

/* BARRA LATERAL ESTILO BOUTIQUE */
[data-testid="stSidebar"] { background: var(--ink) !important; border-right: 1px solid #222; min-width: 280px !important; }
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { padding-top: 1.5rem; gap: 1rem; }

[data-testid="stSidebar"] .stRadio p {
    font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important; font-weight: 400 !important; color: #ADB5BD !important;
    letter-spacing: 0.02em !important; transition: all 0.3s ease; padding-left: 1rem; border-left: 0px solid var(--gold);
}
[data-testid="stSidebar"] .stRadio label[data-checked="true"] p { color: var(--gold) !important; font-weight: 500 !important; border-left: 3px solid var(--gold); padding-left: 1.2rem; }

/* Estructura de Títulos y Tarjetas */
.brand-header { font-family: 'DM Serif Display', serif; font-size: 2.3rem; color: var(--ink); border-bottom: 2px solid var(--gold); padding-bottom: 0.5rem; margin-bottom: 0.2rem; }
.brand-sub { font-size: 0.75rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--slate); margin-bottom: 1.5rem; }

.kpi-card { background: var(--card-bg); border: 1px solid var(--border); border-top: 3px solid var(--gold); border-radius: 4px; padding: 1.2rem; text-align: center; }
.kpi-label { font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--slate); margin-bottom: 0.2rem; }
.kpi-value { font-family: 'DM Serif Display', serif; font-size: 2rem; line-height: 1; }

.section-title { font-family: 'DM Serif Display', serif; font-size: 1.5rem; color: var(--ink); border-left: 3px solid var(--gold); padding-left: 0.7rem; margin: 1.5rem 0 1rem 0; }
.fiscal-panel { background: #F0F7F3; border: 1px solid #C3DDD0; border-radius: 6px; padding: 1.5rem; }

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. GESTIÓN DE DATOS (NÚCLEO ESTRATÉGICO)
# ─────────────────────────────────────────────
DB_INMUEBLES   = "nolasco_inmuebles_v8.csv"
DB_MOVIMIENTOS = "nolasco_movimientos_v8.csv"

def inicializar_bd(force=False):
    if force or not os.path.exists(DB_INMUEBLES):
        pd.DataFrame([
            {"Nombre": "Casa Abarqueros", "Inquilino": "Victor Aguiluz", "Renta": 2200.0, "Comunidad": 193.76, "Valor_Construccion": 150000.0, "Año_Reforma": 2018, "Mobiliario": "S", "Tipo": "Casa", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Paseo del Salón", "Inquilino": "Pool Despachos", "Renta": 1591.8, "Comunidad": 175.18, "Valor_Construccion": 120000.0, "Año_Reforma": 2020, "Mobiliario": "N", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 1", "Inquilino": "Alain", "Renta": 660.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0, "Año_Reforma": 2022, "Mobiliario": "S", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 2", "Inquilino": "Laura/Alex", "Renta": 800.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0, "Año_Reforma": 2022, "Mobiliario": "S", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 3", "Inquilino": "Jose Manuel", "Renta": 850.0, "Comunidad": 74.63, "Valor_Construccion": 45000.0, "Año_Reforma": 2021, "Mobiliario": "S", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"},
            {"Nombre": "Huerto Unidad 4", "Inquilino": "Pendiente", "Renta": 600.0, "Comunidad": 74.62, "Valor_Construccion": 45000.0, "Año_Reforma": 2024, "Mobiliario": "S", "Tipo": "Piso", "Ref_Catastral": "", "Titular": "Pedro Nolasco"}
        ]).to_csv(DB_INMUEBLES, index=False)
    
    if force or not os.path.exists(DB_MOVIMIENTOS):
        pd.DataFrame([
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Hipoteca (Intereses)", "Categoría": "Financiero", "Tipo": "Gasto", "Importe": 250.00, "Deducible": "S"},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Hipoteca (Capital)", "Categoría": "Financiero", "Tipo": "Gasto", "Importe": 304.73, "Deducible": "N"},
            {"Fecha": "2026-04-01", "Apartamento": "Global", "Concepto": "Sueldo Pedro", "Categoría": "Personal", "Tipo": "Gasto", "Importe": 600.00, "Deducible": "N"}
        ]).to_csv(DB_MOVIMIENTOS, index=False)

inicializar_bd()
df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)

# ─────────────────────────────────────────────
# 3. NAVEGACIÓN
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='padding-bottom: 1rem;'><div style='font-family:\"DM Serif Display\",serif; font-size:2.2rem; color:#C9A84C; line-height:1;'>NOLASCO</div></div>", unsafe_allow_html=True)
    menu = st.radio("", ["📊 Torre de Control", "🏠 Fichas de Activos", "🤖 Auditoría IA", "📝 Diario Contable", "📂 Datos y Backups"], label_visibility="collapsed")

# ── TORRE DE CONTROL (DASHBOARD) ──────────────
if "Torre" in menu:
    st.markdown('<div class="brand-header">Torre de Control</div>', unsafe_allow_html=True)
    
    ing_b = df_inm["Renta"].sum()
    gas_caja = df_mov[df_mov["Tipo"]=="Gasto"]["Importe"].sum() + df_inm["Comunidad"].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-label">Ingresos Totales</div><div class="kpi-value" style="color:var(--emerald)">{ing_b:,.0f}€</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-label">Gastos Operativos</div><div class="kpi-value" style="color:var(--crimson)">-{gas_caja:,.0f}€</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-label">Beneficio Neto</div><div class="kpi-value">{ing_b - gas_caja:,.0f}€</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Rentabilidad Detallada por Activo</div>', unsafe_allow_html=True)
    cols = st.columns(len(df_inm))
    for i, row in df_inm.iterrows():
        g_esp = df_mov[(df_mov["Apartamento"] == row["Nombre"])]["Importe"].sum()
        gastos_unit = row['Comunidad'] + g_esp
        beneficio_unit = row['Renta'] - gastos_unit
        with cols[i]:
            st.markdown(f"""
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:4px; border-top:4px solid {COLOR_PALETTE[i % 6]}; padding:1.2rem 0.8rem; text-align:center; height:100%;">
                <div style="font-size:0.75rem; font-weight:600; text-transform:uppercase; color:var(--slate); margin-bottom:8px;">{row['Nombre']}</div>
                <div style="font-size:1.15rem; font-weight:600; color:var(--emerald);">+{row['Renta']:,.0f}€</div>
                <div style="font-size:0.85rem; font-weight:500; color:var(--crimson); margin-top:2px;">-{gastos_unit:,.0f}€</div>
                <div style="font-family:'DM Serif Display',serif; font-size:1.45rem; color:#D35400; border-top:1px solid #eee; margin-top:8px; padding-top:5px;">{beneficio_unit:,.0f}€</div>
            </div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<h3 style='font-family: \"DM Serif Display\", serif; font-size: 1.5rem; color: var(--ink); margin: 2rem 0 1rem 0; border-left: 3px solid var(--gold); padding-left: 0.7rem;'>📋 Desglose de Gastos</h3>", unsafe_allow_html=True)
        df_cat = df_mov.groupby("Categoría")["Importe"].sum().reset_index().sort_values("Importe", ascending=False)
        st.dataframe(df_cat.style.format({"Importe": "{:,.2f} €"}).set_properties(**{'font-size': '1.1rem', 'padding': '12px'}), hide_index=True, use_container_width=True)
    
    with col_r:
        st.markdown("<h3 style='font-family: \"DM Serif Display\", serif; font-size: 1.5rem; color: var(--ink); margin: 2rem 0 1rem 0; border-left: 3px solid var(--gold); padding-left: 0.7rem;'>🍰 Composición de la Cartera</h3>", unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=df_inm["Nombre"], 
            values=df_inm["Renta"], 
            hole=0.4, 
            marker=dict(colors=COLOR_PALETTE),
            textinfo="label+percent",
            textposition="outside",
            textfont=dict(size=13, family="DM Sans")
        ))
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=80,r=80,t=30,b=30), showlegend=False, height=420)
        st.plotly_chart(fig_pie, use_container_width=True)

# ── FICHAS DE ACTIVOS (CRIBADO FISCAL) ────────
elif "Fichas" in menu:
    st.markdown('<div class="brand-header">Análisis Individual</div>', unsafe_allow_html=True)
    sel = st.selectbox("Inmueble a analizar:", df_inm["Nombre"].tolist())
    f = df_inm[df_inm["Nombre"] == sel].iloc[0]
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        df_g = df_mov[df_mov["Apartamento"] == sel]
        resumen = pd.concat([pd.DataFrame([{"Concepto": "Comunidad", "Importe": f["Comunidad"], "Deducible": "S"}]), df_g[["Concepto", "Importe", "Deducible"]]])
        total_suma = resumen["Importe"].sum()
        resumen_final = pd.concat([resumen, pd.DataFrame([{"Concepto": "TOTAL GASTOS (CAJA)", "Importe": total_suma, "Deducible": "-"}])])
        st.dataframe(resumen_final.style.format({"Importe": "{:,.2f}€"}), hide_index=True, use_container_width=True)
        
    with col_b:
        st.markdown('<div class="fiscal-panel">', unsafe_allow_html=True)
        amort = (f["Valor_Construccion"] * 0.03) / 12
        gastos_fisc = resumen[resumen['Deducible']=='S']['Importe'].sum()
        st.write(f"**Gastos Deducibles IRPF:** {gastos_fisc:,.2f}€")
        st.write(f"**Amortización (3% s/Const.):** {amort:,.2f}€")
        st.divider()
        st.write(f"**Base Imponible Real:** {f['Renta'] - gastos_fisc - amort:,.2f}€")
        st.markdown('</div>', unsafe_allow_html=True)

# ── AUDITORÍA IA (MANTENIMIENTO) ──────────────
elif "Auditor" in menu:
    st.markdown('<div class="brand-header">Auditoría de Activos</div>', unsafe_allow_html=True)
    año_act = datetime.now().year
    total_unidades = len(df_inm)
    for i, row in df_inm.reset_index().iterrows():
        st.markdown(f"### 📍 {row['Nombre']}")
        consejos = []
        if año_act - int(row["Año_Reforma"]) > 6: consejos.append(f"🎨 **Renovación:** Ciclo de pintura vencido ({año_act - int(row['Año_Reforma'])} años).")
        if row["Mobiliario"] == "S": consejos.append("🔌 **Equipamiento:** Revisar amortización de electrodomésticos.")
        if row["Tipo"] == "Casa": consejos.append("🏠 **Estructura:** Inspección de tejados recomendada.")
        st.write("  \n".join(consejos) if consejos else "✅ Estado de conservación óptimo.")
        if i < total_unidades - 1:
            st.markdown("<hr style='border: 0; border-top: 1px solid var(--gold); margin: 1.5rem 0;'>", unsafe_allow_html=True)

# ── DIARIO CONTABLE (CON DESPLEGABLES) ────────
elif "Diario" in menu:
    st.markdown('<div class="brand-header">Registro de Operaciones</div>', unsafe_allow_html=True)
    
    # Listados para los desplegables (aseguran consistencia contable)
    lista_inmuebles = df_inm["Nombre"].tolist() + ["Global"]
    lista_conceptos = [
        "Renta Mensual", "Hipoteca (Intereses)", "Hipoteca (Capital)", 
        "IBI", "Comunidad", "Seguro Hogar", "Seguro Vida", 
        "Suministros (Luz/Agua)", "Reparaciones", "Mantenimiento", 
        "Sueldo Pedro", "Impuestos (IVA/IRPF)", "Otros"
    ]
    
    # Análisis de Sumas Dinámicas
    # Nota: Usamos el dataframe editado para que la suma cambie en tiempo real al escribir
    col_metric1, col_metric2, col_metric3 = st.columns(3)
    
    # Configuración de columnas con desplegables
    config_columnas = {
        "Apartamento": st.column_config.SelectboxColumn(
            "Inmueble", help="Selecciona el activo", options=lista_inmuebles, required=True
        ),
        "Concepto": st.column_config.SelectboxColumn(
            "Concepto", options=lista_conceptos, required=True
        ),
        "Tipo": st.column_config.SelectboxColumn(
            "Tipo", options=["Ingreso", "Gasto"], required=True
        ),
        "Deducible": st.column_config.SelectboxColumn(
            "Fiscal", help="¿Es deducible en IRPF?", options=["S", "N"], required=True
        ),
        "Importe": st.column_config.NumberColumn(
            "Importe (€)", format="%.2f", min_value=0
        )
    }

    st.markdown("<br>", unsafe_allow_html=True)
    
    # El editor de datos ahora tiene los desplegables configurados
    df_ed = st.data_editor(
        df_mov, 
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=True,
        column_config=config_columnas
    )

    # Cálculos de los totales para las métricas superiores (basados en lo que hay en pantalla)
    total_ing_act = df_ed[df_ed["Tipo"] == "Ingreso"]["Importe"].sum()
    total_gas_act = df_ed[df_ed["Tipo"] == "Gasto"]["Importe"].sum()
    balance_act   = total_ing_act - total_gas_act

    col_metric1.metric("Ingresos Diario", f"{total_ing_act:,.2f} €")
    col_metric2.metric("Gastos Diario", f"-{total_gas_act:,.2f} €")
    col_metric3.metric("Balance Diario", f"{balance_act:,.2f} €", delta=f"{balance_act:,.2f} €")

    if st.button("Guardar Cambios en el Diario"):
        df_ed.to_csv(DB_MOVIMIENTOS, index=False)
        st.success("✓ Registro de operaciones actualizado y guardado.")
        st.rerun()
# ── DATOS Y BACKUPS (SEGURIDAD) ───────────────
elif "Datos" in menu:
    st.markdown('<div class="brand-header">Gestión de Datos y Backups</div>', unsafe_allow_html=True)
    st.subheader("Configuración de Cartera")
    df_inm_ed = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True, hide_index=True)
    if st.button("Actualizar Cartera"):
        df_inm_ed.to_csv(DB_INMUEBLES, index=False)
        st.rerun()

    st.markdown('<div class="section-title">Copias de Seguridad</div>', unsafe_allow_html=True)
    colb1, colb2 = st.columns(2)
    with colb1:
        with open(DB_INMUEBLES, "rb") as f_i: st.download_button("📥 Backup Inmuebles (CSV)", f_i, "inmuebles_backup.csv")
    with colb2:
        with open(DB_MOVIMIENTOS, "rb") as f_m: st.download_button("📥 Backup Movimientos (CSV)", f_m, "movimientos_backup.csv")
