# ================================================================
# kpi_renderer.py
# Renderizar KPIs grandes y legibles como en Cash Flow
# Uso:
#   from kpi_renderer import render_kpi_large
#   render_kpi_large("Ingresos Registrados", "15,471 €", delta="↑ 2,896 €", color="#1a7a40")
# ================================================================

import streamlit as st

ACCENT = "#185FA5"
GREEN = "#1a7a40"
RED = "#C0392B"
AMBER = "#854F0B"


def render_kpi_large(label: str, value: str, delta: str = None, color: str = None, subtitle: str = None):
    """
    Renderiza un KPI grande y prominente.
    
    Args:
        label: Etiqueta superior (ej: "Ingresos Registrados")
        value: Valor principal (ej: "15,471 €")
        delta: Cambio opcional (ej: "↑ 2,896 €")
        color: Color del valor (default: ACCENT)
        subtitle: Subtítulo opcional
    """
    if color is None:
        color = ACCENT
    
    delta_html = f'<div style="font-size:11px;font-weight:600;color:{color};margin-top:4px;">{delta}</div>' if delta else ""
    subtitle_html = f'<div style="font-size:11px;color:#9CA3AF;margin-top:6px;">{subtitle}</div>' if subtitle else ""
    
    st.markdown(f"""
    <div style="background:#fff;border-radius:16px;padding:20px 24px;
                box-shadow:0 2px 12px rgba(0,0,0,0.06);
                border:0.5px solid rgba(0,0,0,0.05);">
        <p style="font-size:10px;font-weight:700;letter-spacing:0.1em;
                  text-transform:uppercase;color:#9CA3AF;margin:0 0 8px">
            {label}
        </p>
        <p style="font-family:'DM Serif Display',serif;font-size:2.2rem;font-weight:700;
                  color:{color};margin:0;line-height:1">
            {value}
        </p>
        {delta_html}
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


def render_kpi_row(kpis_data: list):
    """
    Renderiza múltiples KPIs en una fila.
    
    Args:
        kpis_data: Lista de dicts con keys: label, value, delta, color, subtitle
    """
    cols = st.columns(len(kpis_data))
    for col, kpi in zip(cols, kpis_data):
        with col:
            render_kpi_large(
                kpi.get("label", ""),
                kpi.get("value", ""),
                delta=kpi.get("delta"),
                color=kpi.get("color", ACCENT),
                subtitle=kpi.get("subtitle")
            )
