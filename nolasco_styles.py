"""
nolasco_styles.py — Estilos Nolasco Capital para Streamlit
============================================================
Uso:

    import streamlit as st
    from nolasco_styles import inject_styles

    st.set_page_config(page_title="Nolasco Capital", layout="wide")
    inject_styles()

Después puedes usar las clases en cualquier st.markdown(..., unsafe_allow_html=True):

    st.markdown('<div class="nc-brand-header">Torre de Control</div>', unsafe_allow_html=True)
    st.markdown('<div class="nc-brand-sub">Granada · Resumen patrimonial</div>', unsafe_allow_html=True)

    st.markdown(f'''
      <div class="nc-kpi">
        <div class="nc-kpi__label">Renta mensual</div>
        <div class="nc-kpi__value">{renta:,.0f} €</div>
        <div class="nc-kpi__sub">{n} inmuebles activos</div>
      </div>
    ''', unsafe_allow_html=True)

Clases disponibles:
  .nc-brand-header   título grande con underline azul
  .nc-brand-sub      eyebrow MAYÚSCULAS bajo el título
  .nc-section-title  subtítulo con left-rail azul
  .nc-kpi            card KPI blanca (añade .is-highlight para fondo azul)
    .nc-kpi__label   label MAYÚSCULAS
    .nc-kpi__value   número grande en serif
    .nc-kpi__sub     subtítulo gris
  .nc-pill           pill pequeño (--red / --amber / --green)
  .nc-status         alert con left-rail 5px (--red / --amber / --green)
"""

import streamlit as st


def inject_styles() -> None:
    """Inyecta tokens y clases del Design System Nolasco Capital."""
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --nc-accent:       #185FA5;
  --nc-accent-soft:  #60B4FF;
  --nc-sidebar-bg:   #0F2744;
  --nc-sidebar-line: #1a3a5c;
  --nc-sidebar-mute: #3a6a8a;
  --nc-sidebar-link: #8ab4d4;

  --nc-bg:           #F4F7FB;
  --nc-card:         #FFFFFF;
  --nc-card-hover:   #F0F6FF;
  --nc-border:       #D0DFF0;

  --nc-text:         #0D1B2A;
  --nc-text-mute:    #5A7A9A;
  --nc-text-on-dark: #FFFFFF;
  --nc-text-on-dark-mute: #B5D4F4;

  --nc-green:        #1a7a40;
  --nc-green-bg:     #EDF7F1;
  --nc-green-pill-bg:#EAF3DE;
  --nc-green-pill-fg:#3B6D11;

  --nc-red:          #C0392B;
  --nc-red-bg:       #FDECEA;
  --nc-red-pill-bg:  #FCEBEB;
  --nc-red-pill-fg:  #A32D2D;

  --nc-amber:        #854F0B;
  --nc-amber-strong: #F39C12;
  --nc-amber-bg:     #FFF9E6;
  --nc-amber-pill-bg:#FAEEDA;
  --nc-amber-pill-fg:#854F0B;

  --nc-blue-info-bg: #F0F8FF;

  --nc-font-display: 'DM Serif Display', Georgia, serif;
  --nc-font-ui:      'DM Sans', -apple-system, system-ui, sans-serif;
}

/* ── Streamlit overrides ─────────────────────────────────── */
html, body, .stApp, [class*="css"] { font-family: var(--nc-font-ui) !important; color: var(--nc-text); }
.stApp { background: var(--nc-bg); }
section[data-testid="stSidebar"] { background: var(--nc-sidebar-bg); }
section[data-testid="stSidebar"] * { color: var(--nc-sidebar-link); }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: var(--nc-accent-soft) !important; font-family: var(--nc-font-display) !important; }
.block-container { padding-top: 2.5rem !important; }

/* ── Componentes del Design System ───────────────────────── */
.nc-brand-header {
  font-family: var(--nc-font-display);
  font-size: 2rem;
  color: var(--nc-text);
  border-bottom: 2px solid var(--nc-accent);
  padding-bottom: 0.4rem;
  margin-bottom: 0.2rem;
}
.nc-brand-sub {
  font-size: 0.7rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--nc-text-mute);
  margin-bottom: 1.2rem;
}
.nc-section-title {
  font-family: var(--nc-font-display);
  font-size: 1.35rem;
  color: var(--nc-text);
  border-left: 3px solid var(--nc-accent);
  padding-left: 0.7rem;
  margin: 1.5rem 0 1rem 0;
}

.nc-kpi {
  background: var(--nc-card);
  border: 1px solid var(--nc-border);
  border-radius: 10px;
  padding: 1.2rem 1.3rem;
}
.nc-kpi.is-highlight { background: var(--nc-accent); border-color: var(--nc-accent); color: #fff; }
.nc-kpi__label {
  font-size: 0.62rem;
  letter-spacing: 0.10em;
  text-transform: uppercase;
  color: var(--nc-text-mute);
  font-weight: 600;
}
.nc-kpi.is-highlight .nc-kpi__label { color: var(--nc-text-on-dark-mute); }
.nc-kpi__value {
  font-family: var(--nc-font-display);
  font-size: 2rem;
  line-height: 1;
  color: var(--nc-text);
  margin-top: 0.4rem;
}
.nc-kpi.is-highlight .nc-kpi__value { color: #fff; }
.nc-kpi__sub { font-size: 0.72rem; color: var(--nc-text-mute); margin-top: 0.3rem; }
.nc-kpi.is-highlight .nc-kpi__sub { color: var(--nc-text-on-dark-mute); }

.nc-pill { display: inline-block; font-size: 0.62rem; padding: 2px 7px; border-radius: 20px; font-weight: 600; }
.nc-pill--red    { background: var(--nc-red-pill-bg);   color: var(--nc-red-pill-fg); }
.nc-pill--amber  { background: var(--nc-amber-pill-bg); color: var(--nc-amber-pill-fg); }
.nc-pill--green  { background: var(--nc-green-pill-bg); color: var(--nc-green-pill-fg); }

.nc-status        { padding: 1.2rem; border-radius: 6px; }
.nc-status--red   { background: var(--nc-red-bg);   border-left: 5px solid var(--nc-red); }
.nc-status--amber { background: var(--nc-amber-bg); border-left: 5px solid var(--nc-amber-strong); }
.nc-status--green { background: var(--nc-green-bg); border-left: 5px solid var(--nc-green); }

/* ── Sidebar buttons ─────────────────────────────────────── */
section[data-testid="stSidebar"] .stButton > button {
  background: rgba(96,180,255,0.08) !important;
  border: none !important;
  border-left: 3px solid transparent !important;
  border-radius: 0 6px 6px 0 !important;
  color: #8ab4d4 !important;
  font-family: var(--nc-font-ui) !important;
  font-size: 0.88rem !important;
  font-weight: 400 !important;
  text-align: left !important;
  padding: 0.55rem 1rem !important;
  width: 100% !important;
  margin-bottom: 2px !important;
  box-shadow: none !important;
  transition: all 0.15s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(96,180,255,0.15) !important;
  border-left: 3px solid rgba(96,180,255,0.5) !important;
  color: #ffffff !important;
}

/* Ocultar menu Streamlit y footer */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* ── Radio button login (Iniciar Sesión / Registrarse) ───── */
div[data-testid="stRadio"] > label { display: none; }
div[data-testid="stRadio"] > div {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.2rem;
}
div[data-testid="stRadio"] > div > label {
  display: flex !important;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  color: #ffffff !important;
  padding: 0.4rem 1rem;
  border-radius: 6px;
  border: 1.5px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.05);
}
div[data-testid="stRadio"] > div > label:has(input:checked) {
  color: white !important;
  border-color: #185FA5 !important;
  background: #185FA5 !important;
}
div[data-testid="stRadio"] > div > label > div:first-child {
  display: none !important;
}

/* Plotly title font */
.js-plotly-plot text { font-family: var(--nc-font-ui) !important; }
</style>
"""
