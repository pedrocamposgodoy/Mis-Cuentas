"""
test_design.py — Prueba del Design System Nolasco Capital
Ejecutar: streamlit run test_design.py
"""

import streamlit as st
from nolasco_styles import inject_styles

st.set_page_config(page_title="Test Design System", layout="wide")
inject_styles()

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════

st.markdown('<div class="nc-brand-header">Torre de Control</div>', unsafe_allow_html=True)
st.markdown('<div class="nc-brand-sub">Granada · Resumen patrimonial · Mayo 2026</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 4 KPIs
# ══════════════════════════════════════════════════════════════

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('''
    <div class="nc-kpi">
      <div class="nc-kpi__label">Inmuebles activos</div>
      <div class="nc-kpi__value">5</div>
      <div class="nc-kpi__sub">3 alquilados · 2 vacíos</div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown('''
    <div class="nc-kpi">
      <div class="nc-kpi__label">Renta mensual</div>
      <div class="nc-kpi__value">6.102 €</div>
      <div class="nc-kpi__sub">Recaudación bruta</div>
    </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown('''
    <div class="nc-kpi is-highlight">
      <div class="nc-kpi__label">Lucro cesante</div>
      <div class="nc-kpi__value">−205 €</div>
      <div class="nc-kpi__sub">vs renta de mercado</div>
    </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown('''
    <div class="nc-kpi">
      <div class="nc-kpi__label">Rentabilidad bruta</div>
      <div class="nc-kpi__value">6.8 %</div>
      <div class="nc-kpi__sub">vs 7.9 % mercado</div>
    </div>
    ''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECCIÓN 1: PILLS
# ══════════════════════════════════════════════════════════════

st.markdown('<div class="nc-section-title">Estado de cada inmueble</div>', unsafe_allow_html=True)

col_pills = st.columns(3)

with col_pills[0]:
    st.markdown('''
    <span class="nc-pill nc-pill--green">🟢 Al mercado</span>
    ''', unsafe_allow_html=True)
    st.caption("Paseo del Salón · rentabilidad óptima")

with col_pills[1]:
    st.markdown('''
    <span class="nc-pill nc-pill--amber">🟡 −7% mercado</span>
    ''', unsafe_allow_html=True)
    st.caption("Casa Abarqueros · renegociar")

with col_pills[2]:
    st.markdown('''
    <span class="nc-pill nc-pill--red">🔴 −18% mercado</span>
    ''', unsafe_allow_html=True)
    st.caption("Huerto Unidad 1 · acción urgente")

# ══════════════════════════════════════════════════════════════
# SECCIÓN 2: ALERTAS (STATUS BLOCKS)
# ══════════════════════════════════════════════════════════════

st.markdown('<div class="nc-section-title">Alertas y notificaciones</div>', unsafe_allow_html=True)

st.markdown('''
<div class="nc-status nc-status--red">
  <strong>🔴 Alerta urgente</strong>
  <div style="font-size:0.85rem;margin-top:4px;line-height:1.45;">
    Huerto Unidad 1 · contrato vence en 42 días y la renta está un 18% por debajo del mercado.
  </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="nc-status nc-status--amber">
  <strong>🟡 Atención</strong>
  <div style="font-size:0.85rem;margin-top:4px;line-height:1.45;">
    Casa Abarqueros · la renta actual es 15% inferior al mercado. Considera renegociar.
  </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="nc-status nc-status--green">
  <strong>🟢 Todo bien</strong>
  <div style="font-size:0.85rem;margin-top:4px;line-height:1.45;">
    Paseo del Salón · rentabilidad óptima y contrato vigente hasta 2028.
  </div>
</div>
''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECCIÓN 3: EJEMPLOS DE CARDS
# ══════════════════════════════════════════════════════════════

st.markdown('<div class="nc-section-title">Detalles por inmueble</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown('''
    <div class="nc-kpi" style="margin-bottom:1rem;">
      <div class="nc-kpi__label">Casa Abarqueros</div>
      <div style="margin-top:0.6rem;font-size:0.9rem;color:#0D1B2A;">
        <div><strong>Renta actual:</strong> 2.200 €/mes</div>
        <div style="color:#5A7A9A;"><strong>Renta mercado:</strong> 2.540 €/mes</div>
        <div style="margin-top:0.4rem;"><strong>Brecha:</strong> −340 €/mes (−13.4%)</div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

with col_b:
    st.markdown('''
    <div class="nc-kpi" style="margin-bottom:1rem;">
      <div class="nc-kpi__label">Paseo del Salón</div>
      <div style="margin-top:0.6rem;font-size:0.9rem;color:#0D1B2A;">
        <div><strong>Renta actual:</strong> 1.591 €/mes</div>
        <div style="color:#5A7A9A;"><strong>Renta mercado:</strong> 1.580 €/mes</div>
        <div style="margin-top:0.4rem;"><strong>Brecha:</strong> +11 €/mes (+0.7%)</div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════

st.divider()

st.markdown("""
**✅ Test completado**

Si ves:
- Colores correctos (azul marino en sidebar, azul cielo en headers)
- KPIs con tipografía serif grande
- Pills con semáforos (rojo/amarillo/verde)
- Status blocks con left-rail azul

→ El design system funciona perfectamente. Listo para integrar en `app.py`.
""")
