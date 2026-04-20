import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import requests
import json

# ─────────────────────────────────────────────
# 1. CONFIGURACIÓN VISUAL PREMIUM
# ─────────────────────────────────────────────
st.set_page_config(page_title="Nolasco Capital", layout="wide", page_icon="🏛️")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --ink:       #0D0F12;
    --parchment: #F7F4EF;
    --gold:      #C9A84C;
    --gold-lt:   #F0E0B0;
    --emerald:   #1B5E3B;
    --crimson:   #8B1A1A;
    --slate:     #4A5568;
    --card-bg:   #FFFFFF;
    --border:    #E8E2D9;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--parchment) !important;
    color: var(--ink);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
    border-right: 1px solid #222;
}
[data-testid="stSidebar"] * { color: #CCC !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase; }
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] { margin-bottom: 0.6rem; }

/* Header brand */
.brand-header {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: var(--ink);
    letter-spacing: -0.02em;
    line-height: 1;
    border-bottom: 2px solid var(--gold);
    padding-bottom: 0.4rem;
    margin-bottom: 0.2rem;
}
.brand-sub {
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--slate);
    margin-bottom: 1.5rem;
}

/* KPI cards */
.kpi-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-top: 3px solid var(--gold);
    border-radius: 4px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}
.kpi-label {
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--slate);
    margin-bottom: 0.3rem;
}
.kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 1.9rem;
    color: var(--ink);
    line-height: 1;
}
.kpi-value.positive { color: var(--emerald); }
.kpi-value.negative { color: var(--crimson); }

/* Asset cards */
.asset-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.1rem;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.asset-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--gold), transparent);
}
.asset-name {
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--slate);
    margin-bottom: 0.2rem;
}
.asset-tenant {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 0.8rem;
}
.asset-income { color: var(--emerald); font-weight: 600; font-size: 1.15rem; }
.asset-expense { color: var(--crimson); font-size: 0.9rem; margin-top: 0.2rem; }
.asset-net {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: var(--ink);
    border-top: 1px solid var(--border);
    margin-top: 0.7rem;
    padding-top: 0.5rem;
}

/* Section titles */
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: var(--ink);
    border-left: 3px solid var(--gold);
    padding-left: 0.7rem;
    margin: 1.5rem 0 1rem 0;
}

/* AI advisor box */
.ai-panel {
    background: var(--ink);
    color: #F0EAD6;
    border-radius: 6px;
    padding: 1.5rem;
    margin-top: 1rem;
    border-left: 4px solid var(--gold);
    font-size: 0.92rem;
    line-height: 1.7;
    white-space: pre-wrap;
}
.ai-panel b { color: var(--gold); }

/* Fiscal box */
.fiscal-panel {
    background: #F0F7F3;
    border: 1px solid #C3DDD0;
    border-radius: 4px;
    padding: 1.2rem;
    font-size: 0.88rem;
}

/* Buttons */
.stButton > button {
    background: var(--ink) !important;
    color: var(--gold) !important;
    border: 1px solid var(--gold) !important;
    border-radius: 3px !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 0.8rem;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: var(--gold) !important;
    color: var(--ink) !important;
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. BASE DE DATOS
# ─────────────────────────────────────────────
DB_INMUEBLES   = "nolasco_inmuebles.csv"
DB_MOVIMIENTOS = "nolasco_movimientos.csv"

def inicializar_bd(force=False):
    if force or not os.path.exists(DB_INMUEBLES):
        pd.DataFrame([
            {"Nombre": "Casa Abarqueros",  "Inquilino": "Victor Aguiluz", "Renta": 2200.0,  "Comunidad": 193.76, "Valor_Construccion": 150000.0},
            {"Nombre": "Paseo del Salón",  "Inquilino": "Pool Despachos",  "Renta": 1591.8,  "Comunidad": 175.18, "Valor_Construccion": 120000.0},
            {"Nombre": "Huerto Unidad 1",  "Inquilino": "Alain",           "Renta": 660.0,   "Comunidad": 74.62,  "Valor_Construccion": 45000.0},
            {"Nombre": "Huerto Unidad 2",  "Inquilino": "Laura/Alex",      "Renta": 800.0,   "Comunidad": 74.62,  "Valor_Construccion": 45000.0},
            {"Nombre": "Huerto Unidad 3",  "Inquilino": "Jose Manuel",     "Renta": 850.0,   "Comunidad": 74.63,  "Valor_Construccion": 45000.0},
        ]).to_csv(DB_INMUEBLES, index=False)

    if force or not os.path.exists(DB_MOVIMIENTOS):
        pd.DataFrame([
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Hipoteca Abarqueros",       "Categoría": "Financiero",   "Tipo": "Gasto", "Importe": 554.73},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Seguro MyBox",              "Categoría": "Seguros",      "Tipo": "Gasto", "Importe": 96.43},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Seguro Vida (Seviam)",      "Categoría": "Seguros",      "Tipo": "Gasto", "Importe": 55.93},
            {"Fecha": "2026-04-01", "Apartamento": "Casa Abarqueros", "Concepto": "Mantenimiento Ascensor",    "Categoría": "Mantenimiento","Tipo": "Gasto", "Importe": 65.44},
            {"Fecha": "2026-04-01", "Apartamento": "Global",          "Concepto": "Software Holded",           "Categoría": "Sistemas",     "Tipo": "Gasto", "Importe": 18.15},
            {"Fecha": "2026-04-01", "Apartamento": "Global",          "Concepto": "Autónomos (TGSS)",          "Categoría": "Impuestos",    "Tipo": "Gasto", "Importe": 314.00},
            {"Fecha": "2026-04-01", "Apartamento": "Global",          "Concepto": "Sueldo Pedro",              "Categoría": "Personal",     "Tipo": "Gasto", "Importe": 600.00},
            {"Fecha": "2026-04-01", "Apartamento": "Global",          "Concepto": "IRPF (Aplazamiento)",       "Categoría": "Impuestos",    "Tipo": "Gasto", "Importe": 1100.00},
            {"Fecha": "2026-04-01", "Apartamento": "Global",          "Concepto": "IVA (Cuota Fija)",          "Categoría": "Impuestos",    "Tipo": "Gasto", "Importe": 325.00},
        ]).to_csv(DB_MOVIMIENTOS, index=False)

inicializar_bd()
df_inm = pd.read_csv(DB_INMUEBLES)
df_mov = pd.read_csv(DB_MOVIMIENTOS)

# ─────────────────────────────────────────────
# 3. IA REAL — ASESOR DE RENTABILIDAD
# ─────────────────────────────────────────────
def construir_contexto(df_inm, df_mov):
    lineas = ["CARTERA NOLASCO — DATOS FINANCIEROS ACTUALES\n"]
    ing_total = df_inm["Renta"].sum()
    gas_total = df_inm["Comunidad"].sum() + df_mov[df_mov["Tipo"] == "Gasto"]["Importe"].sum()
    neto_total = ing_total - gas_total
    lineas.append(f"Ingresos brutos mensuales: {ing_total:,.2f} €")
    lineas.append(f"Gastos totales mensuales:  {gas_total:,.2f} €")
    lineas.append(f"Resultado neto mensual:    {neto_total:,.2f} €\n")
    lineas.append("ACTIVOS:")
    for _, r in df_inm.iterrows():
        g_esp = df_mov[(df_mov["Apartamento"] == r["Nombre"]) & (df_mov["Tipo"] == "Gasto")]["Importe"].sum()
        cargas = r["Comunidad"] + g_esp
        neto   = r["Renta"] - cargas
        margen = (neto / r["Renta"] * 100) if r["Renta"] else 0
        yield_anual = (r["Renta"] * 12 / r["Valor_Construccion"] * 100) if r["Valor_Construccion"] else 0
        lineas.append(
            f"  • {r['Nombre']} | Inquilino: {r['Inquilino']} | Renta: {r['Renta']:,.0f}€ "
            f"| Gastos: {cargas:,.0f}€ | Neto: {neto:,.0f}€ | Margen: {margen:.1f}% "
            f"| Yield bruto anual: {yield_anual:.2f}%"
        )
    lineas.append("\nGASTOS GLOBALES (no asignados a un activo):")
    df_global = df_mov[df_mov["Apartamento"] == "Global"]
    for _, g in df_global.iterrows():
        lineas.append(f"  • {g['Concepto']}: {g['Importe']:,.2f}€ ({g['Categoría']})")
    return "\n".join(lineas)

def llamar_claude(contexto, pregunta, api_key):
    """Llama a la API de Anthropic con los datos de la cartera."""
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    system = (
        "Eres un asesor inmobiliario y financiero experto para carteras de alquiler en España. "
        "Analizas rentabilidades, detectas ineficiencias, propones optimizaciones fiscales y "
        "estratégicas. Respondes en español, de forma directa y ejecutiva. "
        "Estructura tus respuestas con puntos clave y una conclusión accionable."
    )
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 900,
        "system": system,
        "messages": [
            {"role": "user", "content": f"{contexto}\n\nPREGUNTA DEL PROPIETARIO:\n{pregunta}"}
        ]
    }
    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=40)
    resp.raise_for_status()
    data = resp.json()
    return data["content"][0]["text"]

# ─────────────────────────────────────────────
# 4. SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1.5rem 0 1rem 0;'>
        <div style='font-family:"DM Serif Display",serif; font-size:1.4rem; color:#C9A84C; letter-spacing:-0.01em;'>
            NOLASCO
        </div>
        <div style='font-size:0.6rem; letter-spacing:0.2em; color:#888; text-transform:uppercase; margin-top:2px;'>
            Capital · Gestión de Activos
        </div>
    </div>
    <hr style='border-color:#333; margin-bottom:1rem;'>
    """, unsafe_allow_html=True)

    menu = st.radio("", [
        "📊  Torre de Control",
        "🏠  Fichas de Activos",
        "🤖  Asesor IA",
        "📝  Diario de Operaciones",
        "⚙️  Configuración",
    ], label_visibility="collapsed")

    st.markdown("<hr style='border-color:#333; margin-top:2rem;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.6rem;color:#555;text-transform:uppercase;letter-spacing:0.1em;'>API Key Anthropic</div>", unsafe_allow_html=True)
    api_key = st.text_input("", type="password", placeholder="sk-ant-...", label_visibility="collapsed")

# ─────────────────────────────────────────────
# 5. PÁGINAS
# ─────────────────────────────────────────────

# ── TORRE DE CONTROL ──────────────────────────
if "Torre" in menu:
    st.markdown('<div class="brand-header">Torre de Control</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Cartera Nolasco · Resumen Mensual</div>', unsafe_allow_html=True)

    ing_b       = df_inm["Renta"].sum()
    comu_total  = df_inm["Comunidad"].sum()
    gastos_adic = df_mov[df_mov["Tipo"] == "Gasto"]["Importe"].sum()
    gas_total   = comu_total + gastos_adic
    neto        = ing_b - gas_total
    margen_pct  = neto / ing_b * 100 if ing_b else 0

    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        ("Ingresos Brutos",   f"{ing_b:,.0f} €",        "positive"),
        ("Gastos Totales",    f"{gas_total:,.0f} €",     "negative"),
        ("Resultado Neto",    f"{neto:,.0f} €",          "positive" if neto > 0 else "negative"),
        ("Margen Neto",       f"{margen_pct:.1f} %",     "positive" if margen_pct > 30 else ""),
    ]
    for col, (label, val, cls) in zip([c1, c2, c3, c4], kpis):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value {cls}">{val}</div>
        </div>""", unsafe_allow_html=True)

    # Activos
    st.markdown('<div class="section-title">Balance por Activo</div>', unsafe_allow_html=True)
    cols_apto = st.columns(len(df_inm))
    for i, row in df_inm.iterrows():
        g_esp      = df_mov[(df_mov["Apartamento"] == row["Nombre"]) & (df_mov["Tipo"] == "Gasto")]["Importe"].sum()
        cargas     = row["Comunidad"] + g_esp
        neto_apto  = row["Renta"] - cargas
        margen_a   = neto_apto / row["Renta"] * 100 if row["Renta"] else 0
        color_neto = "var(--emerald)" if neto_apto >= 0 else "var(--crimson)"
        with cols_apto[i]:
            st.markdown(f"""
            <div class="asset-card">
                <div class="asset-name">{row['Nombre']}</div>
                <div class="asset-tenant">{row['Inquilino']}</div>
                <div class="asset-income">+{row['Renta']:,.0f} €</div>
                <div class="asset-expense">−{cargas:,.0f} €</div>
                <div class="asset-net" style="color:{color_neto};">{neto_apto:,.0f} €</div>
                <div style="font-size:0.7rem;color:var(--slate);margin-top:0.3rem;">{margen_a:.0f}% margen</div>
            </div>""", unsafe_allow_html=True)

    # Gráficos
    st.markdown('<div class="section-title">Distribución de Costes</div>', unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        df_cat = df_mov.groupby("Categoría")["Importe"].sum().reset_index().sort_values("Importe", ascending=True)
        fig_bar = go.Figure(go.Bar(
            x=df_cat["Importe"], y=df_cat["Categoría"],
            orientation="h",
            marker=dict(color="#C9A84C", opacity=0.85),
            text=df_cat["Importe"].apply(lambda x: f"{x:,.0f}€"),
            textposition="outside"
        ))
        fig_bar.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=10, r=60, t=10, b=10),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(tickfont=dict(family="DM Sans", size=11)),
            height=260,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_r:
        nombres = df_inm["Nombre"].tolist()
        rentas  = df_inm["Renta"].tolist()
        fig_pie = go.Figure(go.Pie(
            labels=nombres, values=rentas,
            hole=0.55,
            marker=dict(colors=["#C9A84C","#1B5E3B","#8B1A1A","#4A5568","#0D0F12"]),
            textinfo="label+percent",
            textfont=dict(family="DM Sans", size=10),
        ))
        fig_pie.update_layout(
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            height=260,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ── FICHAS DE ACTIVOS ────────────────────────
elif "Fichas" in menu:
    st.markdown('<div class="brand-header">Fichas de Activos</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Expedientes · Detalle por Inmueble</div>', unsafe_allow_html=True)

    sel = st.selectbox("Seleccionar inmueble:", df_inm["Nombre"].tolist())
    f   = df_inm[df_inm["Nombre"] == sel].iloc[0]

    df_g_apto = df_mov[(df_mov["Apartamento"] == sel) & (df_mov["Tipo"] == "Gasto")]
    resumen   = pd.concat([
        pd.DataFrame([{"Concepto": "Comunidad", "Importe": f["Comunidad"]}]),
        df_g_apto[["Concepto", "Importe"]]
    ]).reset_index(drop=True)
    total_gastos = resumen["Importe"].sum()
    neto_mensual = f["Renta"] - total_gastos
    margen       = neto_mensual / f["Renta"] * 100 if f["Renta"] else 0
    amort_mensual= (f["Valor_Construccion"] * 0.03) / 12
    yield_bruto  = (f["Renta"] * 12 / f["Valor_Construccion"] * 100) if f["Valor_Construccion"] else 0

    c1, c2, c3 = st.columns(3)
    for col, (lbl, val, cls) in zip([c1, c2, c3], [
        ("Renta Mensual",  f"{f['Renta']:,.2f} €", "positive"),
        ("Gastos Totales", f"{total_gastos:,.2f} €", "negative"),
        ("Neto Mensual",   f"{neto_mensual:,.2f} €", "positive" if neto_mensual >= 0 else "negative"),
    ]):
        col.markdown(f'<div class="kpi-card"><div class="kpi-label">{lbl}</div><div class="kpi-value {cls}">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    c_left, c_right = st.columns([3, 2])
    with c_left:
        st.markdown('<div class="section-title">Desglose de Gastos</div>', unsafe_allow_html=True)
        st.markdown(f"**Inquilino:** {f['Inquilino']}")
        st.dataframe(
            resumen.style.format({"Importe": "{:,.2f} €"}).set_properties(**{"font-size": "0.85rem"}),
            use_container_width=True, hide_index=True
        )

    with c_right:
        st.markdown('<div class="section-title">Indicadores Fiscales</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="fiscal-panel">
            <div style="margin-bottom:0.8rem;">
                <div style="font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;color:#4A5568;">Amortización deducible (3%/año)</div>
                <div style="font-size:1.4rem;font-family:'DM Serif Display',serif;color:#1B5E3B;">{amort_mensual:,.2f} €/mes</div>
            </div>
            <div style="margin-bottom:0.8rem;">
                <div style="font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;color:#4A5568;">Yield bruto anual</div>
                <div style="font-size:1.4rem;font-family:'DM Serif Display',serif;">{yield_bruto:.2f}%</div>
            </div>
            <div>
                <div style="font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;color:#4A5568;">Margen neto mensual</div>
                <div style="font-size:1.4rem;font-family:'DM Serif Display',serif;">{margen:.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── ASESOR IA ─────────────────────────────────
elif "Asesor" in menu:
    st.markdown('<div class="brand-header">Asesor IA</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Análisis Inteligente · Rentabilidad y Optimización</div>', unsafe_allow_html=True)

    if not api_key:
        st.warning("⚠️ Introduce tu API Key de Anthropic en el menú lateral para activar el asesor.")
    else:
        contexto = construir_contexto(df_inm, df_mov)

        # Preguntas rápidas predefinidas
        st.markdown('<div class="section-title">Consultas Rápidas</div>', unsafe_allow_html=True)
        preguntas_rapidas = [
            "¿Cuál es el activo más rentable y por qué?",
            "¿Qué gastos debería revisar o negociar primero?",
            "¿Cómo puedo mejorar el yield global de la cartera?",
            "¿Hay riesgos de concentración o dependencia en esta cartera?",
        ]
        cols_q = st.columns(2)
        pregunta_sel = None
        for i, pq in enumerate(preguntas_rapidas):
            with cols_q[i % 2]:
                if st.button(pq, key=f"pq_{i}"):
                    pregunta_sel = pq

        # Pregunta personalizada
        st.markdown('<div class="section-title">Pregunta Personalizada</div>', unsafe_allow_html=True)
        pregunta_custom = st.text_area("Escribe tu consulta al asesor:", height=90,
                                        placeholder="Ej: ¿Conviene refinanciar la hipoteca de Abarqueros este año?")

        pregunta_final = pregunta_sel or (pregunta_custom.strip() if pregunta_custom.strip() else None)

        if pregunta_final:
            with st.spinner("Analizando cartera..."):
                try:
                    respuesta = llamar_claude(contexto, pregunta_final, api_key)
                    st.markdown(f"""
                    <div style="font-size:0.75rem;letter-spacing:0.1em;text-transform:uppercase;color:#4A5568;margin-bottom:0.4rem;">
                        Consulta: {pregunta_final}
                    </div>
                    <div class="ai-panel">{respuesta}</div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error al conectar con Claude: {e}")

        # Mostrar contexto enviado (expandible)
        with st.expander("📄 Ver datos enviados a la IA"):
            st.code(contexto, language="text")

# ── DIARIO DE OPERACIONES ────────────────────
elif "Diario" in menu:
    st.markdown('<div class="brand-header">Diario de Operaciones</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Registro Contable · Movimientos</div>', unsafe_allow_html=True)

    df_ed = st.data_editor(df_mov, num_rows="dynamic", use_container_width=True)
    if st.button("💾  Sincronizar"):
        df_ed.to_csv(DB_MOVIMIENTOS, index=False)
        st.success("✓ Cambios guardados correctamente.")

# ── CONFIGURACIÓN ────────────────────────────
elif "Config" in menu:
    st.markdown('<div class="brand-header">Configuración</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Administración del Sistema</div>', unsafe_allow_html=True)

    st.markdown("### Activos")
    df_inm_ed = st.data_editor(df_inm, num_rows="dynamic", use_container_width=True)
    if st.button("💾  Guardar Activos"):
        df_inm_ed.to_csv(DB_INMUEBLES, index=False)
        st.success("✓ Activos actualizados.")

    st.divider()
    st.markdown("### Reinicio del Sistema")
    st.caption("Restaura todos los datos a los valores iniciales.")
    if st.button("⚠️  Reiniciar Sistema"):
        inicializar_bd(force=True)
        st.rerun()
