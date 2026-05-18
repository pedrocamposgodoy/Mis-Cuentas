# ================================================================
# cashflow_module.py
# Módulo Cash Flow — Nolasco Capital
#
# Uso en app.py:
#   from cashflow_module import render_cashflow
#   elif menu == "Cash Flow":
#       render_cashflow(df_mov, df_inm, df_gastos_rec, safe_float)
#
# Deps externas: streamlit, pandas, plotly, anthropic
# ================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
from sabio_patrimonial import render_sabio

# ──────────────────────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────────────────────
GREEN  = "#1a7a40"
RED    = "#C0392B"
ACCENT = "#185FA5"
MESES  = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]


# ──────────────────────────────────────────────────────────────
# HELPERS INTERNOS
# ──────────────────────────────────────────────────────────────
def _safe_float(v, d=0.0):
    try:
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return float(d)
        return float(v)
    except:
        return float(d)



# ──────────────────────────────────────────────────────────────
# CONSTRUCCIÓN DE DATOS
# ──────────────────────────────────────────────────────────────
def _construir_historico(df_mov: pd.DataFrame, año: int) -> pd.DataFrame:
    """
    Devuelve df con columnas: mes (1-12), ingresos, gastos, saldo
    Solo meses del año en curso con datos reales.
    """
    if df_mov is None or len(df_mov) == 0:
        return pd.DataFrame(columns=["mes","ingresos","gastos","saldo"])

    df = df_mov.copy()
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df[df["Fecha"].dt.year == año].dropna(subset=["Fecha"])

    rows = []
    mes_actual = datetime.now().month
    for m in range(1, mes_actual + 1):
        dm = df[df["Fecha"].dt.month == m]
        ing = _safe_float(dm[dm["Tipo"] == "Ingreso"]["Importe"].sum())
        gas = _safe_float(dm[dm["Tipo"] == "Gasto"]["Importe"].sum())
        rows.append({"mes": m, "ingresos": ing, "gastos": gas, "saldo": ing - gas})

    return pd.DataFrame(rows)


def _construir_proyeccion(df_inm: pd.DataFrame, df_gastos_rec: pd.DataFrame,
                           df_hist: pd.DataFrame, año: int) -> pd.DataFrame:
    """
    Proyecta meses restantes del año usando:
    - Ingresos: suma de rentas mensuales de inmuebles
    - Gastos: gastos_recurrentes activos + estimación proporcional de variables
    Solo meses futuros (mes_actual+1 … 12).
    """
    mes_actual = datetime.now().month

    # Ingresos proyectados = suma rentas
    ing_proy = _safe_float(df_inm["Renta"].apply(lambda x: _safe_float(x)).sum()) if df_inm is not None and len(df_inm) > 0 else 0

    # Gastos fijos proyectados = gastos_recurrentes mensuales
    gas_fijo = 0.0
    if df_gastos_rec is not None and len(df_gastos_rec) > 0:
        for _, gr in df_gastos_rec.iterrows():
            frecuencia = str(gr.get("Frecuencia", "Mensual")).lower()
            importe    = _safe_float(gr.get("Importe", 0))
            if frecuencia == "mensual":
                gas_fijo += importe
            elif frecuencia == "trimestral":
                gas_fijo += importe / 3
            elif frecuencia in ("anual", "año"):
                gas_fijo += importe / 12

    # Estimación gastos variables: promedio histórico de gastos menos fijos
    gas_variable_mensual = 0.0
    if len(df_hist) > 0:
        avg_gas_hist = df_hist["gastos"].mean()
        gas_variable_mensual = max(avg_gas_hist - gas_fijo, 0)

    gas_proy = gas_fijo + gas_variable_mensual

    rows = []
    for m in range(mes_actual + 1, 13):
        rows.append({
            "mes": m,
            "ingresos": ing_proy,
            "gastos": gas_proy,
            "saldo": ing_proy - gas_proy,
            "es_proyeccion": True
        })

    return pd.DataFrame(rows)


def _calcular_kpis(df_hist: pd.DataFrame, df_proy: pd.DataFrame):
    """Devuelve dict con KPIs del año completo."""
    todos_saldos = list(df_hist["saldo"]) + list(df_proy["saldo"]) if len(df_proy) > 0 else list(df_hist["saldo"])
    todos_ingresos = list(df_hist["ingresos"]) + list(df_proy["ingresos"]) if len(df_proy) > 0 else list(df_hist["ingresos"])
    todos_gastos = list(df_hist["gastos"]) + list(df_proy["gastos"]) if len(df_proy) > 0 else list(df_hist["gastos"])

    if not todos_saldos:
        return {"saldo_medio": 0, "mejor_mes": 0, "peor_mes": 0, "tendencia": 0,
                "total_ingresos": 0, "total_gastos": 0}

    return {
        "saldo_medio":    round(sum(todos_saldos) / len(todos_saldos), 0),
        "mejor_mes":      round(max(todos_saldos), 0),
        "peor_mes":       round(min(todos_saldos), 0),
        "tendencia":      round(todos_saldos[-1] - todos_saldos[0], 0) if len(todos_saldos) > 1 else 0,
        "total_ingresos": round(sum(todos_ingresos), 0),
        "total_gastos":   round(sum(todos_gastos), 0),
    }


# ──────────────────────────────────────────────────────────────
# GRÁFICO PLOTLY
# ──────────────────────────────────────────────────────────────
def _render_grafico(df_hist: pd.DataFrame, df_proy: pd.DataFrame):
    """
    Histograma comparativo mensual:
    - Barras agrupadas: Ingresos (verde) | Gastos (rojo) — datos reales
    - Barras punteadas/semitransparentes: proyección meses futuros
    - Línea de Saldo encima (azul)
    """
    fig = go.Figure()

    # ── Combinar etiquetas (histórico + proyección) ─────────
    meses_hist = [MESES[int(m)-1] for m in df_hist["mes"]] if len(df_hist) > 0 else []
    meses_proy = [MESES[int(m)-1] for m in df_proy["mes"]] if len(df_proy) > 0 else []
    todos_meses = meses_hist + meses_proy

    # ── BARRAS HISTÓRICAS ───────────────────────────────────
    if len(df_hist) > 0:
        fig.add_trace(go.Bar(
            x=meses_hist,
            y=df_hist["ingresos"],
            name="Ingresos reales",
            marker_color=GREEN,
            marker_line_width=0,
            opacity=0.9,
            offsetgroup="A",
            hovertemplate="<b>%{x}</b><br>Ingresos: %{y:,.0f} €<extra></extra>"
        ))
        fig.add_trace(go.Bar(
            x=meses_hist,
            y=df_hist["gastos"],
            name="Gastos reales",
            marker_color=RED,
            marker_line_width=0,
            opacity=0.9,
            offsetgroup="B",
            hovertemplate="<b>%{x}</b><br>Gastos: %{y:,.0f} €<extra></extra>"
        ))

    # ── BARRAS PROYECTADAS (semitransparentes) ──────────────
    if len(df_proy) > 0:
        fig.add_trace(go.Bar(
            x=meses_proy,
            y=df_proy["ingresos"],
            name="Ingresos estimados",
            marker_color=GREEN,
            marker_line_color=GREEN,
            marker_line_width=1.5,
            opacity=0.35,
            offsetgroup="A",
            hovertemplate="<b>%{x}</b><br>Ingresos est.: %{y:,.0f} €<extra></extra>"
        ))
        fig.add_trace(go.Bar(
            x=meses_proy,
            y=df_proy["gastos"],
            name="Gastos estimados",
            marker_color=RED,
            marker_line_color=RED,
            marker_line_width=1.5,
            opacity=0.35,
            offsetgroup="B",
            hovertemplate="<b>%{x}</b><br>Gastos est.: %{y:,.0f} €<extra></extra>"
        ))

    # ── LÍNEA DE SALDO (encima de las barras) ───────────────
    if len(df_hist) > 0:
        saldos_hist = list(df_hist["saldo"])
        saldos_proy = list(df_proy["saldo"]) if len(df_proy) > 0 else []

        # Colores del marcador de saldo: verde si positivo, rojo si negativo
        colores_saldo = [GREEN if s >= 0 else RED for s in saldos_hist + saldos_proy]

        fig.add_trace(go.Scatter(
            x=todos_meses,
            y=saldos_hist + saldos_proy,
            name="Saldo neto",
            mode="lines+markers",
            line=dict(color=ACCENT, width=2.5, dash="solid"),
            marker=dict(
                size=9,
                color=colores_saldo,
                line=dict(color="white", width=1.5)
            ),
            hovertemplate="<b>%{x}</b><br>Saldo: %{y:,.0f} €<extra></extra>",
            yaxis="y"
        ))

    # ── LÍNEA CERO ──────────────────────────────────────────
    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="rgba(0,0,0,0.15)",
        line_width=1
    )

    # ── SEPARADOR real/proyección (add_shape — compatible eje categórico) ──
    if len(df_hist) > 0 and len(df_proy) > 0:
        total_meses = len(df_hist) + len(df_proy)
        x_rel = (len(df_hist) - 0.5) / total_meses
        fig.add_shape(
            type="line",
            xref="paper", yref="paper",
            x0=x_rel, x1=x_rel,
            y0=0, y1=1,
            line=dict(color="rgba(0,0,0,0.18)", width=1.5, dash="dash"),
        )
        fig.add_annotation(
            xref="paper", yref="paper",
            x=x_rel + 0.01, y=0.97,
            text="← Real | Estimado →",
            showarrow=False,
            font=dict(size=10, color="#9CA3AF"),
            xanchor="left",
        )

    fig.update_layout(
        barmode="group",
        bargap=0.18,
        bargroupgap=0.04,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=40),
        height=380,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=12, family="DM Sans"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.05)",
            tickformat=",.0f",
            ticksuffix=" €",
            tickfont=dict(size=11),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        ),
        hovermode="x unified",
        font=dict(family="DM Sans", size=12),
    )

    st.plotly_chart(fig, use_container_width=True)


def _render_kpis(kpis: dict):
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "Saldo medio mensual", kpis["saldo_medio"],
         "#185FA5", kpis["saldo_medio"] >= 0),
        (c2, "Mejor mes del año", kpis["mejor_mes"],
         "#1a7a40", True),
        (c3, "Peor mes del año", kpis["peor_mes"],
         "#C0392B", kpis["peor_mes"] >= 0),
        (c4, "Tendencia anual", kpis["tendencia"],
         "#1a7a40" if kpis["tendencia"] >= 0 else "#C0392B",
         kpis["tendencia"] >= 0),
    ]
    for col, label, valor, color, positivo in cards:
        flecha = "▲" if positivo else "▼"
        col.markdown(f"""
        <div style="background:#fff;border-radius:14px;padding:16px 18px;
                    box-shadow:0 2px 12px rgba(0,0,0,0.06);
                    border:0.5px solid rgba(0,0,0,0.05);height:100%">
            <p style="font-size:10px;font-weight:600;letter-spacing:0.08em;
                      text-transform:uppercase;color:#9CA3AF;margin:0 0 6px">{label}</p>
            <p style="font-family:'DM Serif Display',serif;font-size:1.5rem;font-weight:700;
                      color:{color};margin:0;line-height:1">{flecha} {abs(valor):,.0f} €</p>
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# TABLA MES A MES
# ──────────────────────────────────────────────────────────────
def _render_tabla(df_hist: pd.DataFrame, df_proy: pd.DataFrame):
    st.markdown('<div style="font-size:0.75rem;font-weight:600;letter-spacing:0.08em;'
                'text-transform:uppercase;color:#9CA3AF;margin:20px 0 8px">Detalle mensual</div>',
                unsafe_allow_html=True)

    filas = []
    for _, r in df_hist.iterrows():
        filas.append({
            "Mes": MESES[int(r["mes"]) - 1],
            "Ingresos €": f"{r['ingresos']:,.0f}",
            "Gastos €": f"{r['gastos']:,.0f}",
            "Saldo €": f"{r['saldo']:,.0f}",
            "Tipo": "Real"
        })
    for _, r in df_proy.iterrows():
        filas.append({
            "Mes": MESES[int(r["mes"]) - 1],
            "Ingresos €": f"{r['ingresos']:,.0f}",
            "Gastos €": f"{r['gastos']:,.0f}",
            "Saldo €": f"{r['saldo']:,.0f}",
            "Tipo": "Proyección"
        })

    if not filas:
        st.info("Sin datos para mostrar.")
        return

    df_tabla = pd.DataFrame(filas)
    st.dataframe(
        df_tabla,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tipo": st.column_config.TextColumn(""),
            "Saldo €": st.column_config.TextColumn("Saldo €"),
        }
    )


# ──────────────────────────────────────────────────────────────
# BOCADILLO IA eliminado — ahora usa sabio_patrimonial.render_sabio()
# ──────────────────────────────────────────────────────────────
def _generar_insight_cashflow(contexto: dict) -> str:
    """Genera insight inicial sobre el cash flow. Cacheado en session_state."""
    cache_key = "sabio_insight_cashflow"
    if cache_key in st.session_state and st.session_state[cache_key]:
        return st.session_state[cache_key]

    api_key = _get_api_key()
    if not api_key:
        return "Configura ANTHROPIC_API_KEY para activar el Sabio Patrimonial."

    try:
        client = anthropic.Anthropic(api_key=api_key)
        system = """Eres el Sabio Patrimonial de Nolasco Capital. Analizas el cash flow del propietario.
Detecta el insight más útil en máximo 2 frases. Usa los números reales. Sé específico y directo.
Ejemplo: 'Tu saldo cae en agosto por comunidades de verano. Tienes margen de 800€ para mantenimiento en junio.'"""

        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=150,
            system=system,
            messages=[{"role": "user", "content": str(contexto)}]
        )
        resultado = msg.content[0].text
        st.session_state[cache_key] = resultado
        return resultado
    except Exception as e:
        return f"El Sabio no está disponible ahora ({str(e)[:60]})."


def _chat_sabio_cashflow(pregunta: str, contexto: dict) -> str:
    """Responde preguntas sobre el cash flow con datos reales del usuario."""
    api_key = _get_api_key()
    if not api_key:
        return "Configura ANTHROPIC_API_KEY en los secrets de Streamlit."

    try:
        client = anthropic.Anthropic(api_key=api_key)
        system = f"""Eres el Sabio Patrimonial de Nolasco Capital. El propietario te pregunta sobre su cash flow.

DATOS REALES DEL USUARIO:
{contexto}

REGLAS:
- Responde en máximo 3 frases. Sin rodeos.
- Usa los números reales del contexto.
- Si preguntan sobre mantenimiento, calcula margen disponible (saldo - gastos fijos).
- Tono: directo, útil, cálido. Es su dinero real.
- No puedes modificar datos. Solo analizas y sugieres."""

        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system=system,
            messages=[{"role": "user", "content": pregunta}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"Error al consultar al Sabio: {str(e)[:80]}"


def render_bocadillo_sabio_cashflow(contexto: dict):
    """
    Bocadillo IA fijo en la parte inferior izquierda de la pantalla.
    CSS position:fixed — siempre visible, fuera de la zona de trabajo.
    """

    # CSS del bocadillo flotante
    st.markdown("""
    <style>
    #sabio-cf-container {
        position: fixed;
        bottom: 24px;
        left: 270px; /* ancho sidebar Streamlit */
        z-index: 9999;
        width: 320px;
    }
    #sabio-cf-toggle {
        background: #185FA5;
        color: white;
        border: none;
        border-radius: 24px;
        padding: 10px 18px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 16px rgba(24,95,165,0.35);
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'DM Sans', sans-serif;
        transition: background 0.15s;
    }
    #sabio-cf-toggle:hover { background: #0F4A8A; }
    #sabio-cf-panel {
        background: white;
        border: 1.5px solid #185FA5;
        border-radius: 16px 16px 4px 16px;
        padding: 16px;
        margin-bottom: 10px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        display: none;
        max-height: 420px;
        overflow-y: auto;
    }
    #sabio-cf-panel.open { display: block; }
    .sabio-label {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #185FA5;
        margin-bottom: 8px;
    }
    .sabio-insight {
        font-size: 12.5px;
        color: #1A1A2E;
        line-height: 1.6;
        background: #EAF1FB;
        border-radius: 10px;
        padding: 10px 12px;
        border-left: 3px solid #185FA5;
        margin-bottom: 10px;
    }
    </style>

    <div id="sabio-cf-container">
        <div id="sabio-cf-panel">
            <p class="sabio-label">✦ Sabio Patrimonial · Cash Flow</p>
            <div class="sabio-insight" id="sabio-insight-text">Cargando análisis...</div>
        </div>
        <button id="sabio-cf-toggle" onclick="toggleSabio()">
            🧠 Sabio Patrimonial
        </button>
    </div>
    <script>
    function toggleSabio() {
        const panel = document.getElementById('sabio-cf-panel');
        const btn = document.getElementById('sabio-cf-toggle');
        panel.classList.toggle('open');
        btn.textContent = panel.classList.contains('open') ? '✕ Cerrar Sabio' : '🧠 Sabio Patrimonial';
    }
    </script>
    """, unsafe_allow_html=True)

    # Chat interactivo (Streamlit nativo, dentro del flujo principal pero colapsable)
    with st.expander("🧠 Sabio Patrimonial · Cash Flow", expanded=False):
        st.markdown("""
        <div style="background:#EAF1FB;border-radius:10px;padding:10px 12px;
                    border-left:3px solid #185FA5;font-size:12.5px;color:#1A1A2E;
                    line-height:1.6;margin-bottom:12px">
            <strong style="font-size:10px;text-transform:uppercase;letter-spacing:0.08em;
                           color:#185FA5;">✦ Sabio Patrimonial</strong><br>
        """, unsafe_allow_html=True)

        # Insight proactivo
        if "sabio_insight_cf_mostrado" not in st.session_state:
            with st.spinner("Analizando tu cash flow..."):
                insight = _generar_insight_cashflow(contexto)
            st.session_state["sabio_insight_cf_mostrado"] = insight
        else:
            insight = st.session_state["sabio_insight_cf_mostrado"]

        st.markdown(f"<p style='font-size:13px;color:#1A1A2E;margin:0'>{insight}</p></div>",
                    unsafe_allow_html=True)

        # Historial de conversación
        if "sabio_cf_history" not in st.session_state:
            st.session_state["sabio_cf_history"] = []

        for msg in st.session_state["sabio_cf_history"]:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="text-align:right;margin:6px 0">
                    <span style="background:#EAF1FB;color:#1A1A2E;padding:7px 12px;
                                 border-radius:14px 14px 4px 14px;font-size:12px;
                                 display:inline-block;max-width:90%">{msg['content']}</span>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#F0F2F5;border-radius:4px 14px 14px 14px;
                            padding:10px 12px;font-size:12px;color:#1A1A2E;
                            line-height:1.6;margin:6px 0;border-left:2px solid #185FA5">
                    {msg['content']}
                </div>""", unsafe_allow_html=True)

        # Input
        col_q, col_btn = st.columns([0.78, 0.22])
        with col_q:
            pregunta = st.text_input(
                "", key="sabio_cf_input",
                placeholder="¿Tengo margen para una reforma?",
                label_visibility="collapsed"
            )
        with col_btn:
            enviar = st.button("Enviar", key="sabio_cf_btn", use_container_width=True)

        # Chips rápidos
        chips = ["¿Cuándo puedo gastar más?", "¿Qué mes es más ajustado?", "Margen para mantenimiento"]
        chip_html = "".join([
            f'<span style="background:#EAF1FB;color:#185FA5;font-size:10px;font-weight:500;'
            f'padding:3px 10px;border-radius:20px;margin-right:5px;display:inline-block;'
            f'margin-bottom:4px;cursor:pointer">{c}</span>' for c in chips
        ])
        st.markdown(f'<div style="margin:4px 0 10px">{chip_html}</div>', unsafe_allow_html=True)

        if enviar and pregunta.strip():
            with st.spinner("Pensando..."):
                respuesta = _chat_sabio_cashflow(pregunta.strip(), contexto)
            st.session_state["sabio_cf_history"].append({"role": "user", "content": pregunta.strip()})
            st.session_state["sabio_cf_history"].append({"role": "assistant", "content": respuesta})
            st.rerun()

        if st.button("🗑️ Limpiar conversación", key="sabio_cf_clear"):
            st.session_state["sabio_cf_history"] = []
            if "sabio_insight_cf_mostrado" in st.session_state:
                del st.session_state["sabio_insight_cf_mostrado"]
            st.rerun()


# ──────────────────────────────────────────────────────────────
# RENDER PRINCIPAL — punto de entrada desde app.py
# ──────────────────────────────────────────────────────────────
def render_cashflow(df_mov: pd.DataFrame, df_inm: pd.DataFrame,
                    df_gastos_rec: pd.DataFrame, safe_float_fn=None):
    """
    Punto de entrada principal.
    Llama desde app.py:
        from cashflow_module import render_cashflow
        render_cashflow(df_mov, df_inm, df_gastos_rec, safe_float)
    """
    año = datetime.now().year

    # ── CABECERA ────────────────────────────────────────────
    st.markdown('<div class="nc-brand-header">Cash Flow · Tesorería</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="nc-brand-sub">Histórico real + proyección · {año} completo · '
        f'El latido de tu tesorería</div>',
        unsafe_allow_html=True
    )

    # ── DATOS ───────────────────────────────────────────────
    df_hist = _construir_historico(df_mov, año)
    df_proy = _construir_proyeccion(df_inm, df_gastos_rec, df_hist, año)
    kpis    = _calcular_kpis(df_hist, df_proy)

    # ── ALERTA si no hay datos históricos ──────────────────
    if len(df_hist) == 0:
        st.warning("⚠️ No hay movimientos registrados en el Diario Contable para el año en curso. "
                   "Registra ingresos y gastos en el Diario para ver el Cash Flow real.")
        if df_inm is not None and len(df_inm) > 0:
            st.info("📊 Mostrando proyección basada en tus rentas y gastos recurrentes.")
        df_hist = pd.DataFrame(columns=["mes", "ingresos", "gastos", "saldo"])

    # ── KPI CARDS ───────────────────────────────────────────
    _render_kpis(kpis)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── GRÁFICO ─────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.75rem;font-weight:600;letter-spacing:0.08em;'
        'text-transform:uppercase;color:#9CA3AF;margin-bottom:8px">'
        'Ingresos · Gastos · Saldo — año en curso</div>',
        unsafe_allow_html=True
    )
    _render_grafico(df_hist, df_proy)

    # ── LEYENDA proyección ──────────────────────────────────
    if len(df_proy) > 0:
        mes_proy_inicio = MESES[int(df_proy.iloc[0]["mes"]) - 1]
        ing_proy_val = df_proy.iloc[0]["ingresos"]
        gas_proy_val = df_proy.iloc[0]["gastos"]
        st.markdown(
            f'<p style="font-size:11px;color:#9CA3AF;margin:0 0 4px">'
            f'· · · Proyección desde {mes_proy_inicio}: '
            f'{ing_proy_val:,.0f} € ingresos / {gas_proy_val:,.0f} € gastos estimados</p>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── TABLA ───────────────────────────────────────────────
    _render_tabla(df_hist, df_proy)

    # ── CONTEXTO PARA IA ────────────────────────────────────
    contexto_ia = {
        "año": año,
        "saldo_medio_mensual": kpis["saldo_medio"],
        "mejor_mes": kpis["mejor_mes"],
        "peor_mes": kpis["peor_mes"],
        "tendencia_anual": kpis["tendencia"],
        "total_ingresos_proyectados": kpis["total_ingresos"],
        "total_gastos_proyectados": kpis["total_gastos"],
        "meses_historicos": len(df_hist),
        "meses_proyectados": len(df_proy),
        "inmuebles": [
            {
                "nombre": row.get("Nombre", ""),
                "renta": _safe_float(row.get("Renta", 0)),
                "comunidad": _safe_float(row.get("Comunidad", 0)),
                "fecha_vencimiento": row.get("Fecha_Vencimiento_Contrato", ""),
            }
            for _, row in df_inm.iterrows()
        ] if df_inm is not None and len(df_inm) > 0 else [],
        "detalle_historico": [
            {"mes": MESES[int(r["mes"]) - 1],
             "ingresos": r["ingresos"],
             "gastos": r["gastos"],
             "saldo": r["saldo"]}
            for _, r in df_hist.iterrows()
        ] if len(df_hist) > 0 else [],
    }

    # ── SABIO PATRIMONIAL ───────────────────────────────────
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    render_sabio("cashflow", contexto_ia)
