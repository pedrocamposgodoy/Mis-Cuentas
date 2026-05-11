# ================================================================
# sabio_patrimonial.py
# Sabio Patrimonial — Asistente IA conversacional de Nolasco Capital
#
# Conversación compartida entre secciones.
# Contexto dinámico según la sección activa.
# Solo análisis y sugerencias — no modifica datos (MVP).
#
# USO en app.py / cashflow_module.py / asesoramiento_ia.py:
#
#   from sabio_patrimonial import render_sabio
#
#   render_sabio("fichas", contexto_dict)
#   render_sabio("cashflow", contexto_dict)
#   render_sabio("asesor", contexto_dict)
# ================================================================

import streamlit as st
import anthropic
import os

# ──────────────────────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────────────────────
ACCENT       = "#185FA5"
ACCENT_LIGHT = "#EAF1FB"
TEXT_PRI     = "#1A1A2E"
TEXT_SEC     = "#5A7A9A"


# ──────────────────────────────────────────────────────────────
# SYSTEM PROMPTS POR SECCIÓN
# ──────────────────────────────────────────────────────────────
SYSTEM_PROMPTS = {

    "fichas": """Eres el Sabio Patrimonial de Nolasco Capital. El propietario está revisando la ficha detallada de uno de sus inmuebles.

DATOS DEL INMUEBLE ACTIVO:
{contexto}

TU MISIÓN EN ESTA SECCIÓN:
- Comparar renta actual vs renta de mercado y decir si hay margen de subida
- Detectar si el contrato está próximo a vencer y qué hacer
- Identificar si los gastos son elevados para ese tipo de inmueble
- Sugerir si vale la pena reformar, renegociar o vender

REGLAS:
- Máximo 3 frases por respuesta. Directas y con números reales.
- Si el contrato vence en menos de 90 días, prioriza eso.
- Si la renta está más de 10% bajo mercado, prioriza eso.
- Tono cálido y útil. Es su patrimonio real.
- No puedes modificar datos ni ejecutar acciones. Solo analizas.""",

    "cashflow": """Eres el Sabio Patrimonial de Nolasco Capital. El propietario está revisando su Cash Flow anual.

DATOS DE TESORERÍA:
{contexto}

TU MISIÓN EN ESTA SECCIÓN:
- Identificar los meses con más y menos margen disponible
- Calcular cuánto puede gastar en mantenimiento sin comprometer la liquidez
- Detectar si hay tendencia de mejora o empeoramiento
- Alertar si algún mes el saldo proyectado cae por debajo de un colchón razonable (500€)

REGLAS:
- Máximo 3 frases. Con números concretos (meses, euros).
- Si preguntan sobre mantenimiento: calcula saldo proyectado - gastos fijos = margen real.
- Tono directo. El propietario quiere saber cuándo puede gastar sin riesgo.
- No puedes modificar datos. Solo analizas.""",

    "asesor": """Eres el Sabio Patrimonial de Nolasco Capital. El propietario está en la sección de Asesoramiento, donde ve los problemas detectados en su cartera.

PROBLEMAS Y DATOS DETECTADOS:
{contexto}

TU MISIÓN EN ESTA SECCIÓN:
- Priorizar qué problema atacar primero (mayor impacto económico)
- Explicar en términos simples qué significa cada problema
- Sugerir si la mejor acción es renegociar, vender, o esperar
- Aclarar dudas sobre el proceso de contactar con una inmobiliaria

REGLAS:
- Máximo 3 frases. Con impacto económico concreto en euros.
- Si hay varios problemas, di cuál resolver primero y por qué.
- Tono empático pero directo. El propietario puede estar indeciso.
- No puedes enviar datos ni ejecutar acciones. Solo orientas.""",
}

# Chips rápidos por sección
CHIPS = {
    "fichas": [
        "¿Puedo subir la renta?",
        "¿Cuándo vence el contrato?",
        "¿Vale la pena reformar?",
    ],
    "cashflow": [
        "¿Cuándo puedo gastar más?",
        "¿Qué mes es más ajustado?",
        "Margen para mantenimiento",
    ],
    "asesor": [
        "¿Por qué problema empiezo?",
        "¿Qué es un lead?",
        "¿Cuánto me cuesta no actuar?",
    ],
}

# Labels por sección
LABELS = {
    "fichas":   "✦ Sabio · Análisis de Ficha",
    "cashflow": "✦ Sabio · Cash Flow",
    "asesor":   "✦ Sabio · Asesoramiento",
}


# ──────────────────────────────────────────────────────────────
# API
# ──────────────────────────────────────────────────────────────
def _get_api_key() -> str:
    try:
        return st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY", "")
    except Exception:
        return os.getenv("ANTHROPIC_API_KEY", "")


def _llamar_claude(system_prompt: str, pregunta: str, max_tokens: int = 300) -> str:
    api_key = _get_api_key()
    if not api_key:
        return "Configura ANTHROPIC_API_KEY en los secrets de Streamlit para activar el Sabio."
    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": pregunta}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"El Sabio no está disponible ahora ({str(e)[:60]})."


# ──────────────────────────────────────────────────────────────
# INSIGHT PROACTIVO
# Cacheado por sección en session_state.
# Se regenera solo si cambia la sección.
# ──────────────────────────────────────────────────────────────
def _insight_proactivo(seccion: str, contexto: dict) -> str:
    cache_key = f"sabio_insight_{seccion}"

    # Cache: si ya existe para esta sección, devuelve sin llamar API
    if cache_key in st.session_state and st.session_state[cache_key]:
        return st.session_state[cache_key]

    prompts_proactivos = {
        "fichas": "Analiza el inmueble y detecta el punto más urgente a atender (renta, contrato, gastos). Una frase accionable con números reales.",
        "cashflow": "Analiza el cash flow y detecta el mes más crítico o la oportunidad de gasto disponible. Máximo 2 frases con números concretos.",
        "asesor": "Analiza los problemas detectados y di cuál es el más urgente y cuánto cuesta no actuar. Una frase directa.",
    }

    system = SYSTEM_PROMPTS.get(seccion, SYSTEM_PROMPTS["asesor"]).format(contexto=contexto)
    pregunta_proactiva = prompts_proactivos.get(seccion, "Resume la situación en una frase.")

    resultado = _llamar_claude(system, pregunta_proactiva, max_tokens=150)
    st.session_state[cache_key] = resultado
    return resultado


# ──────────────────────────────────────────────────────────────
# RENDER PRINCIPAL
# ──────────────────────────────────────────────────────────────
def render_sabio(seccion: str, contexto: dict):
    """
    Punto de entrada desde cualquier sección de la app.

    seccion: "fichas" | "cashflow" | "asesor"
    contexto: dict con datos reales de esa sección

    Conversación compartida entre secciones (sabio_history global).
    Insight proactivo cacheado por sección.
    """

    # ── Guardar sección activa (para contexto en respuestas) ──
    st.session_state["sabio_seccion_activa"] = seccion

    # ── Inicializar historial compartido ──────────────────────
    if "sabio_history" not in st.session_state:
        st.session_state["sabio_history"] = []

    label = LABELS.get(seccion, "✦ Sabio Patrimonial")

    # ── Expander fijo al fondo ─────────────────────────────────
    with st.expander(f"🧠 {label}", expanded=False):

        # Insight proactivo
        with st.spinner("El Sabio está analizando..."):
            insight = _insight_proactivo(seccion, contexto)

        st.markdown(f"""
        <div style="background:{ACCENT_LIGHT};border-radius:12px;padding:14px 18px;
                    border-left:3px solid {ACCENT};margin-bottom:16px;">
            <p style="font-size:11px;font-weight:700;letter-spacing:0.1em;
                      text-transform:uppercase;color:{ACCENT};margin:0 0 8px">
                {label}
            </p>
            <p style="font-size:14px;color:{TEXT_PRI};line-height:1.7;margin:0">
                {insight}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ── Historial de conversación ──────────────────────────
        for msg in st.session_state["sabio_history"]:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="text-align:right;margin:6px 0">
                    <span style="background:{ACCENT_LIGHT};color:{TEXT_PRI};
                                 padding:7px 13px;border-radius:14px 14px 4px 14px;
                                 font-size:12.5px;display:inline-block;max-width:88%">
                        {msg['content']}
                    </span>
                </div>""", unsafe_allow_html=True)
            else:
                # Mostrar badge de sección donde se generó la respuesta
                badge_seccion = msg.get("seccion", seccion)
                badge_label = LABELS.get(badge_seccion, "Sabio").replace("✦ Sabio · ", "")
                st.markdown(f"""
                <div style="background:#F8FAFC;border-radius:4px 14px 14px 14px;
                            padding:12px 16px;font-size:13.5px;color:{TEXT_PRI};
                            line-height:1.7;margin:8px 0;
                            border-left:2px solid {ACCENT};">
                    <span style="font-size:9px;text-transform:uppercase;letter-spacing:0.08em;
                                 color:{TEXT_SEC};font-weight:600;">{badge_label}</span><br>
                    {msg['content']}
                </div>""", unsafe_allow_html=True)

        # ── Input + botón ──────────────────────────────────────
        col_q, col_btn = st.columns([0.78, 0.22])
        with col_q:
            pregunta = st.text_input(
                "",
                key=f"sabio_input_{seccion}",
                placeholder=_placeholder(seccion),
                label_visibility="collapsed"
            )
        with col_btn:
            enviar = st.button("Enviar", key=f"sabio_btn_{seccion}", use_container_width=True)

        # ── Chips rápidos ──────────────────────────────────────
        chips = CHIPS.get(seccion, [])
        chip_html = "".join([
            f'<span style="background:{ACCENT_LIGHT};color:{ACCENT};font-size:10px;'
            f'font-weight:500;padding:3px 10px;border-radius:20px;'
            f'margin-right:5px;display:inline-block;margin-bottom:4px">{c}</span>'
            for c in chips
        ])
        st.markdown(f'<div style="margin:4px 0 10px">{chip_html}</div>',
                    unsafe_allow_html=True)

        # ── Procesar pregunta ──────────────────────────────────
        if enviar and pregunta.strip():
            system = SYSTEM_PROMPTS.get(seccion, SYSTEM_PROMPTS["asesor"]).format(
                contexto=str(contexto)
            )
            with st.spinner("Pensando..."):
                respuesta = _llamar_claude(system, pregunta.strip())

            st.session_state["sabio_history"].append({
                "role": "user",
                "content": pregunta.strip(),
                "seccion": seccion,
            })
            st.session_state["sabio_history"].append({
                "role": "assistant",
                "content": respuesta,
                "seccion": seccion,
            })
            st.rerun()

        # ── Controles ──────────────────────────────────────────
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("🗑️ Limpiar conversación", key=f"sabio_clear_{seccion}",
                         use_container_width=True):
                st.session_state["sabio_history"] = []
                # Limpiar insights cacheados de todas las secciones
                for s in ["fichas", "cashflow", "asesor"]:
                    k = f"sabio_insight_{s}"
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()
        with col_c2:
            if st.button("🔄 Regenerar análisis", key=f"sabio_regen_{seccion}",
                         use_container_width=True):
                cache_key = f"sabio_insight_{seccion}"
                if cache_key in st.session_state:
                    del st.session_state[cache_key]
                st.rerun()

        # ── Nota de contexto ───────────────────────────────────
        n_msgs = len(st.session_state["sabio_history"])
        if n_msgs > 0:
            st.markdown(
                f'<p style="font-size:10px;color:#C0C8D0;margin:8px 0 0;text-align:right">'
                f'{n_msgs // 2} pregunta{"s" if n_msgs // 2 != 1 else ""} en esta sesión · '
                f'La conversación se mantiene entre secciones</p>',
                unsafe_allow_html=True
            )


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
def _placeholder(seccion: str) -> str:
    return {
        "fichas":   "¿Puedo subir la renta el año que viene?",
        "cashflow": "¿Cuándo tengo margen para una reforma?",
        "asesor":   "¿Por qué problema empiezo?",
    }.get(seccion, "Pregunta al Sabio...")


def limpiar_insight_seccion(seccion: str):
    """
    Útil si el propietario cambia de inmueble en Fichas:
    fuerza regeneración del insight.
    Llama desde app.py cuando cambia st.session_state.ficha_sel.
    """
    cache_key = f"sabio_insight_{seccion}"
    if cache_key in st.session_state:
        del st.session_state[cache_key]
