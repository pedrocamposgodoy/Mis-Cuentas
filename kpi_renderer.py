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


def render_kpi_row(kpis_data: list):
    """
    Renderiza múltiples KPIs en una fila.
    kpis_data: lista de dicts con keys: label, value, color, subtitle (opcional)
    """
    cols = st.columns(len(kpis_data))
    for col, kpi in zip(cols, kpis_data):
        label    = kpi.get("label", "")
        value    = kpi.get("value", "")
        color    = kpi.get("color", ACCENT)
        subtitle = kpi.get("subtitle", "")
        sub_html = (
            f'<p style="font-size:10px;color:#9CA3AF;margin:5px 0 0;">{subtitle}</p>'
            if subtitle else ""
        )
        col.markdown(f"""
        <div style="background:#fff;border-radius:14px;padding:16px 18px;
                    box-shadow:0 2px 12px rgba(0,0,0,0.06);
                    border:0.5px solid rgba(0,0,0,0.05);height:100%">
            <p style="font-size:10px;font-weight:600;letter-spacing:0.08em;
                      text-transform:uppercase;color:#9CA3AF;margin:0 0 6px">{label}</p>
            <p style="font-family:'DM Serif Display',serif;font-size:1.5rem;font-weight:700;
                      color:{color};margin:0;line-height:1">{value}</p>
            {sub_html}
        </div>
        """, unsafe_allow_html=True)
