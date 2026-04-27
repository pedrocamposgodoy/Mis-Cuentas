# ================================================================
# ASESORAMIENTO IA — MÓDULO B2B2C COMPLETO
# Flujo: Semáforo → Árbol decisión → Resumen → RGPD + Inmobiliaria
# Capa 1: actualizar zona_stats (agregados sin datos personales)
# Capa 2: leads con consentimiento RGPD
# ================================================================
import streamlit as st
import pandas as pd
import hashlib
import json
from datetime import datetime, date

# ── Supabase ────────────────────────────────────────────────────
try:
    from supabase_db import _headers, SUPA_URL
    import requests
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

# ── Constantes ──────────────────────────────────────────────────
RENTABILIDAD_MERCADO = {
    "18001": 8.2, "18002": 7.8, "18003": 7.2, "18004": 7.5,
    "18005": 7.9, "18006": 7.0, "18007": 6.8, "18008": 7.3,
    "18009": 6.5, "18010": 7.1, "18011": 7.0, "18012": 6.9,
    "18013": 6.6, "18014": 6.7, "18015": 6.4,
}

PRECIOS_M2 = {
    "18001": 12.5, "18002": 11.8, "18003": 10.2, "18004": 10.8,
    "18005": 11.2, "18006": 10.0, "18007": 9.5,  "18008": 10.4,
    "18009": 8.2,  "18010": 9.8,  "18011": 10.1, "18012": 9.6,
    "18013": 9.0,  "18014": 9.3,  "18015": 8.8,
}

TEXTO_LEGAL = """
AUTORIZACIÓN DE CESIÓN DE DATOS PERSONALES (RGPD)

De conformidad con el Reglamento General de Protección de Datos (RGPD UE 2016/679)
y la Ley Orgánica 3/2018 de Protección de Datos Personales (LOPDGDD), usted autoriza
expresamente a NOLASCO CAPITAL a ceder sus datos personales (nombre, email, teléfono,
situación patrimonial) a las inmobiliarias seleccionadas, únicamente con la finalidad
de recibir asesoramiento profesional sobre su patrimonio inmobiliario.

Esta autorización es voluntaria, granular (por inmobiliaria) y revocable en cualquier
momento desde la sección "Privacidad y Consentimientos" de la aplicación. Las
inmobiliarias solo podrán usar sus datos para contactarle sobre el servicio solicitado.

Responsable del tratamiento: Nolasco Capital | Granada
Derechos: Acceso, rectificación, supresión, portabilidad y oposición (RGPD Art. 15-21)
"""

HASH_LEGAL = hashlib.sha256(TEXTO_LEGAL.encode()).hexdigest()

# ── Colores ─────────────────────────────────────────────────────
SIDEBAR_BG = "#0F2744"
ACCENT     = "#185FA5"
CARD_BG    = "#FFFFFF"
TEXT_PRI   = "#0D1B2A"
TEXT_SEC   = "#5A7A9A"
GREEN      = "#1a7a40"
RED        = "#C0392B"
BORDER     = "#D0DFF0"


# ================================================================
# HELPERS
# ================================================================
def safe_float(v, d=0):
    try:
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return float(d)
        return float(v)
    except Exception:
        return float(d)


def tasacion_renta(row):
    """Renta de mercado estimada según CP y m2."""
    p  = PRECIOS_M2.get(str(row.get("CP", "18005")), 10.0)
    m2 = safe_float(row.get("M2_Construidos", 80))
    am = 1.05 if row.get("Mobiliario") == "S" else 1.0
    ap = 1.04 if row.get("Parking")    == "S" else 1.0
    ae = {"Reformado": 1.08, "Bueno": 1.0, "Regular": 0.92}.get(
        row.get("Estado", "Bueno"), 1.0)
    return round(p * m2 * am * ap * ae, 2)


def dias_vencimiento(row):
    try:
        fv = str(row.get("Fecha_Vencimiento_Contrato", ""))
        return (datetime.strptime(fv, "%Y-%m-%d").date() - date.today()).days
    except Exception:
        return None


def rentabilidad_bruta(row):
    renta = safe_float(row.get("Renta", 0))
    valor = safe_float(row.get("Valor_Construccion", 1))
    if valor <= 0:
        return 0
    return round(renta * 12 / valor * 100, 2)


# ================================================================
# CAPA 1 — ACTUALIZAR ZONA STATS EN SUPABASE
# Se llama cada vez que el propietario guarda/modifica inmuebles
# ================================================================
def actualizar_zona_stats(df_inmuebles: pd.DataFrame):
    """Agrega datos por CP y los sube a zona_stats (sin datos personales)."""
    if not SUPABASE_OK or df_inmuebles.empty:
        return

    año_actual = datetime.now().year

    for cp, grupo in df_inmuebles.groupby("CP"):
        cp = str(cp)
        rentas_actuales = grupo["Renta"].apply(lambda x: safe_float(x)).tolist()
        rentas_mercado  = grupo.apply(tasacion_renta, axis=1).tolist()
        rentabilidades  = grupo.apply(rentabilidad_bruta, axis=1).tolist()

        brecha_euros = [max(0, m - a) for a, m in zip(rentas_actuales, rentas_mercado)]
        brecha_pcts  = [
            (m - a) / m * 100 if m > 0 else 0
            for a, m in zip(rentas_actuales, rentas_mercado)
        ]

        vencen_30  = sum(
            1 for _, r in grupo.iterrows()
            if (d := dias_vencimiento(r)) is not None and 0 <= d <= 30
        )
        vencen_90  = sum(
            1 for _, r in grupo.iterrows()
            if (d := dias_vencimiento(r)) is not None and 0 <= d <= 90
        )

        precio_m2s = [PRECIOS_M2.get(cp, 10.0)] * len(grupo)

        stats = {
            "cp":                  cp,
            "num_propietarios":    len(grupo),
            "rentabilidad_media":  round(sum(rentabilidades) / len(rentabilidades), 2),
            "brecha_renta_media":  round(sum(brecha_euros) / len(brecha_euros), 2),
            "brecha_pct_media":    round(sum(brecha_pcts) / len(brecha_pcts), 2),
            "contratos_vencen_30d": vencen_30,
            "contratos_vencen_90d": vencen_90,
            "precio_m2_medio":     round(sum(precio_m2s) / len(precio_m2s), 2),
            "renta_media_actual":  round(sum(rentas_actuales) / len(rentas_actuales), 2),
            "renta_media_mercado": round(sum(rentas_mercado) / len(rentas_mercado), 2),
            "lucro_cesante_total": round(sum(brecha_euros), 2),
            "updated_at":          datetime.now().isoformat(),
        }

        try:
            url = f"{SUPA_URL}/rest/v1/zona_stats"
            requests.post(
                url,
                headers={**_headers(), "Prefer": "resolution=merge-duplicates"},
                json=stats,
                timeout=5,
            )
        except Exception:
            pass  # No bloquear la app si falla el stats


# ================================================================
# CAPA 2 — CONSENTIMIENTO Y LEAD
# ================================================================
def _leer_inmobiliarias_zona(cp: str):
    """Devuelve inmobiliarias activas para ese CP."""
    if not SUPABASE_OK:
        return _inmobiliarias_fallback(cp)
    try:
        url = f"{SUPA_URL}/rest/v1/inmobiliarias?activa=eq.true&select=*"
        r = requests.get(url, headers=_headers(), timeout=5)
        todas = r.json() if r.status_code == 200 else []
        # Filtrar por CP (el array cp[] contiene el CP del propietario)
        filtradas = [i for i in todas if isinstance(i.get("cp"), list) and cp in i["cp"]]
        return filtradas if filtradas else todas[:4]
    except Exception:
        return _inmobiliarias_fallback(cp)


def _inmobiliarias_fallback(cp):
    return [
        {"id": "demo-1", "nombre": "Núñez Inmobiliaria",       "descripcion": "Especialista zona centro",  "cp": [cp]},
        {"id": "demo-2", "nombre": "Century21 Granada Centro", "descripcion": "Red nacional presente",     "cp": [cp]},
        {"id": "demo-3", "nombre": "Remax Granada",            "descripcion": "Cobertura completa Granada","cp": [cp]},
    ]


def _registrar_consentimiento(propietario_id, inmobiliaria_id):
    if not SUPABASE_OK:
        return {"id": "demo-consent"}
    try:
        url = f"{SUPA_URL}/rest/v1/consentimientos"
        payload = {
            "propietario_id":      propietario_id,
            "inmobiliaria_id":     inmobiliaria_id,
            "consentimiento":      True,
            "documento_legal_hash": HASH_LEGAL,
            "timestamp":           datetime.now().isoformat(),
        }
        r = requests.post(
            url,
            headers={**_headers(), "Prefer": "return=representation,resolution=merge-duplicates"},
            json=payload,
            timeout=5,
        )
        if r.status_code not in (200, 201):
            st.warning(f"⚠️ Error al guardar consentimiento: {r.status_code} - {r.text}")
            return {}
        data = r.json()
        return data[0] if isinstance(data, list) and data else {}
    except Exception as e:
        st.warning(f"⚠️ Error técnico: {str(e)}")
        return {}


def _crear_lead(propietario_id, inmobiliaria_id, consentimiento_id,
                datos_prop, resumen_problemas, argumentario):
    if not SUPABASE_OK:
        st.warning("⚠️ Supabase no conectado — usando modo demo")
        return True
    try:
        url = f"{SUPA_URL}/rest/v1/leads_inmobiliarias"
        payload = {
            "propietario_id":      propietario_id,
            "inmobiliaria_id":     inmobiliaria_id,
            "consentimiento_id":   consentimiento_id,
            "nombre":              datos_prop.get("nombre", ""),
            "email":               datos_prop.get("email", ""),
            "telefono":            datos_prop.get("telefono", ""),
            "motivo_texto":        resumen_problemas,
            "argumentario":        argumentario,
            "estado":              "nuevo",
            "exportado_inmohub":   False,
        }
        r = requests.post(
            url,
            headers={**_headers(), "Prefer": "return=representation"},
            json=payload,
            timeout=5,
        )
        if r.status_code not in (200, 201):
            st.error(f"❌ Error al crear lead: {r.status_code}")
            st.error(f"Respuesta: {r.text}")
            return False
        st.success("✅ Lead guardado en Supabase")
        return True
    except Exception as e:
        st.error(f"❌ Error técnico: {str(e)}")
        return False


# ================================================================
# ANÁLISIS DE PROBLEMAS — CORAZÓN DEL ASESOR
# ================================================================
def detectar_problemas(df_inmuebles: pd.DataFrame) -> list:
    """
    Detecta todos los problemas de la cartera y los ordena por €/mes de impacto.
    Cada problema tiene: inmueble, tipo, descripcion, impacto_euros,
    coste_solucion, tipo_ayuda ('solo'|'dinero'|'inmobiliaria')
    """
    año_actual = datetime.now().year
    problemas = []

    for _, row in df_inmuebles.iterrows():
        nombre     = row.get("Nombre", "Inmueble")
        renta_act  = safe_float(row.get("Renta", 0))
        renta_mer  = tasacion_renta(row)
        valor_con  = safe_float(row.get("Valor_Construccion", 0))
        año_ref    = int(safe_float(row.get("Año_Reforma", año_actual - 3), año_actual - 3))
        años_sin_reforma = año_actual - año_ref
        dias_vec   = dias_vencimiento(row)
        rent_bruta = rentabilidad_bruta(row)
        rent_mer_pct = RENTABILIDAD_MERCADO.get(str(row.get("CP", "18005")), 7.5)

        # 1. RENTA BAJO MERCADO (>10% de diferencia)
        if renta_mer > 0 and (renta_mer - renta_act) / renta_mer > 0.10:
            brecha_mes = round(renta_mer - renta_act, 2)
            problemas.append({
                "inmueble":      nombre,
                "tipo":          "renta_baja",
                "emoji":         "📉",
                "titulo":        f"Renta bajo mercado",
                "descripcion":   f"Cobras {renta_act:,.0f}€/mes pero el mercado paga {renta_mer:,.0f}€/mes",
                "impacto_euros": brecha_mes,
                "coste_solucion": 0,
                "tipo_ayuda":    "inmobiliaria" if (dias_vec is not None and dias_vec < 60) else "solo",
                "detalle_ayuda": "Renegociar en la próxima renovación" if (dias_vec is None or dias_vec >= 60)
                                 else "El contrato vence pronto, una inmobiliaria puede ayudarte a renegociar",
            })

        # 2. CONTRATO VENCIDO O MUY PRÓXIMO
        if dias_vec is not None:
            if dias_vec < 0:
                problemas.append({
                    "inmueble":      nombre,
                    "tipo":          "contrato_vencido",
                    "emoji":         "⚠️",
                    "titulo":        "Contrato vencido",
                    "descripcion":   f"El contrato venció hace {abs(dias_vec)} días",
                    "impacto_euros": round(renta_mer - renta_act, 2) if renta_mer > renta_act else 50,
                    "coste_solucion": 0,
                    "tipo_ayuda":    "inmobiliaria",
                    "detalle_ayuda": "Necesitas renovar o buscar nuevo inquilino",
                })
            elif dias_vec <= 60:
                problemas.append({
                    "inmueble":      nombre,
                    "tipo":          "contrato_pronto",
                    "emoji":         "🔔",
                    "titulo":        f"Contrato vence en {dias_vec} días",
                    "descripcion":   f"Tienes {dias_vec} días para preparar la renovación",
                    "impacto_euros": round(renta_mer - renta_act, 2) if renta_mer > renta_act else 30,
                    "coste_solucion": 0,
                    "tipo_ayuda":    "inmobiliaria",
                    "detalle_ayuda": "Momento ideal para renegociar al precio de mercado",
                })

        # 3. REFORMA PENDIENTE (más de 7 años sin reformar)
        if años_sin_reforma >= 7 and valor_con > 0:
            coste_reforma = round(valor_con * 0.05)  # 5% del valor de construcción
            riesgo_caida  = round(renta_act * 0.18)  # riesgo de perder 18% de renta
            problemas.append({
                "inmueble":      nombre,
                "tipo":          "reforma",
                "emoji":         "🔧",
                "titulo":        f"Reforma pendiente ({años_sin_reforma} años sin reformar)",
                "descripcion":   f"Última reforma en {año_ref}. Riesgo de degradación y caída de renta.",
                "impacto_euros": riesgo_caida,
                "coste_solucion": coste_reforma,
                "tipo_ayuda":    "dinero",
                "detalle_ayuda": f"Necesitas aproximadamente {coste_reforma:,.0f}€ para la reforma",
            })

        # 4. RENTABILIDAD BAJA VS MERCADO (más de 2 puntos)
        if rent_bruta > 0 and (rent_mer_pct - rent_bruta) > 2:
            perdida_anual = round((rent_mer_pct - rent_bruta) / 100 * valor_con)
            problemas.append({
                "inmueble":      nombre,
                "tipo":          "rentabilidad_baja",
                "emoji":         "📊",
                "titulo":        f"Rentabilidad baja ({rent_bruta:.1f}% vs {rent_mer_pct:.1f}% mercado)",
                "descripcion":   f"Tu ROI es {rent_bruta:.1f}%, el mercado da {rent_mer_pct:.1f}%",
                "impacto_euros": round(perdida_anual / 12),
                "coste_solucion": 0,
                "tipo_ayuda":    "inmobiliaria",
                "detalle_ayuda": "Puede ser mejor vender y reinvertir en activo de mayor rentabilidad",
            })

    # Ordenar por impacto económico descendente
    problemas.sort(key=lambda x: x["impacto_euros"], reverse=True)
    return problemas


def generar_argumentario(datos_prop: dict, problemas: list) -> str:
    nombre = datos_prop.get("nombre") or datos_prop.get("email", "propietario")
    total_perdida = sum(p["impacto_euros"] for p in problemas)
    resumen = "\n".join([f"- {p['emoji']} {p['inmueble']}: {p['titulo']}" for p in problemas])
    return (
        f"Propietario {nombre} con {len(problemas)} situación(es) que requieren atención. "
        f"Impacto económico estimado: {total_perdida:,.0f}€/mes.\n\n"
        f"Situaciones detectadas:\n{resumen}"
    )


# ================================================================
# UI — RENDER PRINCIPAL
# ================================================================
def render_asesor_ia(user_id: str, df_inmuebles: pd.DataFrame, datos_propietario: dict):

    # Inicializar session_state
    for key, val in [
        ("asesor_paso", 0),
        ("asesor_problema_idx", 0),
        ("asesor_decisiones", {}),   # {idx: 'solo'|'inmobiliaria'|'skip'}
        ("asesor_mostrar_rgpd", False),
        ("asesor_inmos_seleccionadas", []),
        ("asesor_enviado", False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = val

    paso = st.session_state.asesor_paso

    # Detectar problemas (siempre)
    problemas = detectar_problemas(df_inmuebles)
    # Actualizar zona_stats en background (Capa 1)
    actualizar_zona_stats(df_inmuebles)

    # ── PASO 0: SEMÁFORO GLOBAL ──────────────────────────────────
    if paso == 0:
        _render_semaforo(problemas, df_inmuebles)

    # ── PASO 1: ÁRBOL DE DECISIONES ─────────────────────────────
    elif paso == 1:
        _render_arbol(problemas, df_inmuebles)

    # ── PASO 2: RESUMEN DEL PLAN ─────────────────────────────────
    elif paso == 2:
        _render_resumen(problemas)

    # ── PASO 3: RGPD + INMOBILIARIAS ────────────────────────────
    elif paso == 3:
        _render_rgpd(user_id, df_inmuebles, datos_propietario, problemas)


# ================================================================
# PASO 0 — SEMÁFORO GLOBAL
# ================================================================
def _render_semaforo(problemas, df_inmuebles):
    total_perdida = sum(p["impacto_euros"] for p in problemas)
    num_inm = len(df_inmuebles)

    if not problemas:
        st.markdown(f"""
        <div style='background:#EDF7F1;border-left:5px solid #1a7a40;
            border-radius:8px;padding:1.2rem;margin-bottom:1rem;'>
            <div style='font-size:1.1rem;font-weight:600;color:#1a7a40;'>
                🟢 Tu cartera está en buen estado
            </div>
            <div style='color:#2d5a3d;margin-top:6px;font-size:0.9rem;'>
                No detectamos problemas urgentes en tus {num_inm} inmuebles.
                Vuelve a consultar cuando se acerquen renovaciones de contrato.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Determinar color global
    criticos = [p for p in problemas if p["tipo_ayuda"] == "inmobiliaria"]
    color = "#C0392B" if criticos else "#F39C12"
    emoji = "🔴" if criticos else "🟡"

    st.markdown(f"""
    <div style='background:{"#FDECEA" if criticos else "#FFF9E6"};
        border-left:5px solid {color};border-radius:8px;
        padding:1.2rem;margin-bottom:1.5rem;'>
        <div style='font-size:1.1rem;font-weight:600;color:{color};'>
            {emoji} Detectamos {len(problemas)} situación(es) en tu cartera
        </div>
        <div style='color:{TEXT_PRI};margin-top:6px;font-size:0.9rem;'>
            Impacto económico estimado: <strong>{total_perdida:,.0f}€/mes</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 Situaciones ordenadas por impacto")

    for i, p in enumerate(problemas):
        color_p = "#C0392B" if p["tipo_ayuda"] == "inmobiliaria" else (
                  "#D97706" if p["tipo_ayuda"] == "dinero" else "#185FA5")
        st.markdown(f"""
        <div style='background:{CARD_BG};border-left:3px solid {color_p};
            border-radius:6px;padding:0.8rem 1rem;margin-bottom:0.5rem;
            display:flex;justify-content:space-between;align-items:center;'>
            <div>
                <div style='font-weight:600;color:{TEXT_PRI};font-size:0.9rem;'>
                    {p["emoji"]} {p["inmueble"]} — {p["titulo"]}
                </div>
                <div style='color:{TEXT_SEC};font-size:0.8rem;margin-top:3px;'>
                    {p["descripcion"]}
                </div>
            </div>
            <div style='text-align:right;min-width:100px;'>
                <div style='font-weight:700;color:{color_p};font-size:1rem;'>
                    -{p["impacto_euros"]:,.0f}€/mes
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"🔵 **Puedes resolver tú solo:** {sum(1 for p in problemas if p['tipo_ayuda']=='solo')} situaciones")
    with col2:
        st.warning(f"🏢 **Necesitas ayuda profesional:** {sum(1 for p in problemas if p['tipo_ayuda'] in ('dinero','inmobiliaria'))} situaciones")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔍 Analizar cada situación →", type="primary", use_container_width=True, key="btn_analizar"):
        st.session_state.asesor_paso = 1
        st.session_state.asesor_problema_idx = 0
        st.session_state.asesor_decisiones = {}
        st.rerun()


# ================================================================
# PASO 1 — ÁRBOL DE DECISIONES PROBLEMA A PROBLEMA
# ================================================================
def _render_arbol(problemas, df_inmuebles):
    idx   = st.session_state.asesor_problema_idx
    total = len(problemas)

    if idx >= total:
        # Todos procesados → ir al resumen
        st.session_state.asesor_paso = 2
        st.rerun()
        return

    # Comprobar si estamos en modo revisión (ya hay decisiones tomadas)
    en_revision = len(st.session_state.asesor_decisiones) > 0

    p = problemas[idx]

    # Barra de progreso
    st.markdown(f"""
    <div style='background:{BORDER};border-radius:20px;height:6px;margin-bottom:1rem;'>
        <div style='background:{ACCENT};border-radius:20px;height:6px;
            width:{int((idx/total)*100)}%;'></div>
    </div>
    <div style='font-size:0.75rem;color:{TEXT_SEC};margin-bottom:1.2rem;'>
        Situación {idx+1} de {total}
    </div>
    """, unsafe_allow_html=True)

    # Mostrar decisión previa si ya había una (modo revisión)
    decision_previa = st.session_state.asesor_decisiones.get(idx)
    if decision_previa:
        etiquetas = {
            "solo": ("✅ Decidiste: resolverlo tú solo", "#1a7a40", "#EDF7F1"),
            "inmobiliaria": ("🏢 Decidiste: pedir asesoramiento profesional", "#C0392B", "#FDECEA"),
            "skip": ("⏭️ Decidiste: aplazarlo para más adelante", "#888", "#F8F8F8"),
        }
        etiqueta, color, bg = etiquetas.get(decision_previa, ("", "#888", "#F8F8F8"))
        st.markdown(f"""
        <div style='background:{bg};border-left:3px solid {color};border-radius:6px;
            padding:0.5rem 1rem;margin-bottom:0.8rem;font-size:0.85rem;font-weight:600;color:{color};'>
            {etiqueta} — puedes cambiarla abajo
        </div>
        """, unsafe_allow_html=True)

    # Tarjeta del problema
    color_p = "#C0392B" if p["tipo_ayuda"] == "inmobiliaria" else (
              "#D97706" if p["tipo_ayuda"] == "dinero" else "#185FA5")

    st.markdown(f"""
    <div style='background:{CARD_BG};border-left:4px solid {color_p};
        border-radius:8px;padding:1.2rem;margin-bottom:1.2rem;'>
        <div style='font-size:1rem;font-weight:700;color:{TEXT_PRI};'>
            {p["emoji"]} {p["inmueble"]} — {p["titulo"]}
        </div>
        <div style='color:{TEXT_SEC};font-size:0.85rem;margin-top:6px;'>
            {p["descripcion"]}
        </div>
        <div style='margin-top:10px;font-size:0.9rem;font-weight:600;color:{color_p};'>
            Impacto: -{p["impacto_euros"]:,.0f}€/mes
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Lógica según tipo de ayuda
    if p["tipo_ayuda"] == "solo":
        # IA puede resolverlo — muestra recomendación directa
        st.markdown(f"""
        <div style='background:#EDF7F1;border-radius:8px;padding:1rem;margin-bottom:1rem;'>
            <div style='font-weight:600;color:#1a7a40;'>✅ Puedes resolverlo tú solo</div>
            <div style='color:{TEXT_PRI};margin-top:6px;font-size:0.88rem;'>
                {p["detalle_ayuda"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Entendido, lo gestiono", use_container_width=True, key=f"solo_{idx}"):
                st.session_state.asesor_decisiones[idx] = "solo"
                st.session_state.asesor_problema_idx = idx + 1
                st.rerun()
        with col2:
            if st.button("🏢 Prefiero ayuda profesional", use_container_width=True, key=f"prof_{idx}"):
                st.session_state.asesor_decisiones[idx] = "inmobiliaria"
                st.session_state.asesor_problema_idx = idx + 1
                st.rerun()

    elif p["tipo_ayuda"] == "dinero":
        # Necesita dinero — pregunta si lo tiene
        coste = p["coste_solucion"]
        st.markdown(f"""
        <div style='background:#FFF9E6;border-radius:8px;padding:1rem;margin-bottom:1rem;'>
            <div style='font-weight:600;color:#D97706;'>💰 Para resolver esto necesitas {coste:,.0f}€</div>
            <div style='color:{TEXT_PRI};margin-top:6px;font-size:0.88rem;'>
                {p["detalle_ayuda"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**¿Tienes ese presupuesto disponible?**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✅ Sí, tengo {coste:,.0f}€", use_container_width=True, key=f"si_{idx}"):
                st.session_state.asesor_decisiones[idx] = "solo"
                st.session_state.asesor_problema_idx = idx + 1
                st.rerun()
        with col2:
            if st.button("❌ No tengo ese presupuesto", use_container_width=True, key=f"no_{idx}"):
                st.session_state.asesor_decisiones[idx] = "inmobiliaria"
                st.session_state.asesor_problema_idx = idx + 1
                st.rerun()

    elif p["tipo_ayuda"] == "inmobiliaria":
        # Directamente necesita inmobiliaria
        st.markdown(f"""
        <div style='background:#FDECEA;border-radius:8px;padding:1rem;margin-bottom:1rem;'>
            <div style='font-weight:600;color:#C0392B;'>🏢 Esta situación requiere ayuda profesional</div>
            <div style='color:{TEXT_PRI};margin-top:6px;font-size:0.88rem;'>
                {p["detalle_ayuda"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏢 Quiero asesoramiento", use_container_width=True,
                         type="primary", key=f"inmo_{idx}"):
                st.session_state.asesor_decisiones[idx] = "inmobiliaria"
                st.session_state.asesor_problema_idx = idx + 1
                st.rerun()
        with col2:
            if st.button("⏭️ Lo dejo para más adelante", use_container_width=True, key=f"skip_{idx}"):
                st.session_state.asesor_decisiones[idx] = "skip"
                st.session_state.asesor_problema_idx = idx + 1
                st.rerun()

    # Botón volver solo si no es el primero
    if idx > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Volver a la situación anterior", key=f"back_{idx}"):
            st.session_state.asesor_problema_idx = idx - 1
            # Eliminar decisión del problema actual
            st.session_state.asesor_decisiones.pop(idx, None)
            st.rerun()


# ================================================================
# PASO 2 — RESUMEN DEL PLAN COMPLETO
# ================================================================
def _render_resumen(problemas):
    decisiones = st.session_state.asesor_decisiones
    solos       = [problemas[i] for i, d in decisiones.items() if d == "solo"]
    inmos       = [problemas[i] for i, d in decisiones.items() if d == "inmobiliaria"]
    skips       = [problemas[i] for i, d in decisiones.items() if d == "skip"]

    total_resuelto  = sum(p["impacto_euros"] for p in solos)
    total_delegado  = sum(p["impacto_euros"] for p in inmos)
    total_aplazado  = sum(p["impacto_euros"] for p in skips)

    st.markdown("### 📊 Resumen de tu plan patrimonial")

    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("✅ Resuelves tú", f"{len(solos)} situaciones", f"-{total_resuelto:,.0f}€/mes recuperados")
    c2.metric("🏢 Con inmobiliaria", f"{len(inmos)} situaciones", f"-{total_delegado:,.0f}€/mes a resolver")
    c3.metric("⏭️ Aplazado", f"{len(skips)} situaciones", f"-{total_aplazado:,.0f}€/mes pendientes")

    st.markdown("<br>", unsafe_allow_html=True)

    if solos:
        st.markdown("#### ✅ Lo que puedes hacer tú solo")
        for p in solos:
            st.markdown(f"""
            <div style='background:#EDF7F1;border-radius:6px;padding:0.7rem 1rem;
                margin-bottom:0.4rem;border-left:3px solid #1a7a40;'>
                <strong>{p["emoji"]} {p["inmueble"]}</strong> — {p["titulo"]}
                <div style='font-size:0.8rem;color:#5A7A9A;margin-top:3px;'>
                    {p["detalle_ayuda"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    if inmos:
        st.markdown("#### 🏢 Donde una inmobiliaria puede ayudarte")
        for p in inmos:
            st.markdown(f"""
            <div style='background:#FDECEA;border-radius:6px;padding:0.7rem 1rem;
                margin-bottom:0.4rem;border-left:3px solid #C0392B;'>
                <strong>{p["emoji"]} {p["inmueble"]}</strong> — {p["titulo"]}
                <div style='font-size:0.8rem;color:#5A7A9A;margin-top:3px;'>
                    {p["detalle_ayuda"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    if skips:
        st.markdown("#### ⏭️ Aplazado para más adelante")
        for p in skips:
            st.markdown(f"""
            <div style='background:#F8F8F8;border-radius:6px;padding:0.7rem 1rem;
                margin-bottom:0.4rem;border-left:3px solid #aaa;opacity:0.7;'>
                <strong>{p["emoji"]} {p["inmueble"]}</strong> — {p["titulo"]}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 Puedes revisar cualquier decisión volviendo al análisis situación por situación.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Revisar mis decisiones", use_container_width=True, key="back_resumen"):
            # Vuelve al árbol manteniendo las decisiones ya tomadas para poder cambiarlas
            st.session_state.asesor_paso = 1
            st.session_state.asesor_problema_idx = 0
            # NO reseteamos asesor_decisiones — así el usuario ve lo que ya eligió
            st.rerun()
    with col2:
        if inmos:
            if st.button("🏢 Solicitar asesoramiento profesional →",
                         type="primary", use_container_width=True, key="btn_rgpd"):
                st.session_state.asesor_paso = 3
                st.rerun()
        else:
            st.success("✅ ¡Perfecto! Puedes resolver todo tú solo.")
            if st.button("🔄 Nueva consulta", use_container_width=True, key="reset_ok"):
                _reset_asesor()
                st.rerun()


# ================================================================
# PASO 3 — RGPD + SELECTOR INMOBILIARIAS
# ================================================================
def _render_rgpd(user_id, df_inmuebles, datos_propietario, problemas):
    decisiones = st.session_state.asesor_decisiones
    inmos_prob  = [problemas[i] for i, d in decisiones.items() if d == "inmobiliaria"]

    if st.session_state.asesor_enviado:
        st.markdown(f"""
        <div style='background:#EDF7F1;border-left:5px solid #1a7a40;
            border-radius:8px;padding:1.5rem;text-align:center;'>
            <div style='font-size:1.3rem;font-weight:700;color:#1a7a40;margin-bottom:8px;'>
                ✅ Solicitud enviada correctamente
            </div>
            <div style='color:{TEXT_PRI};font-size:0.9rem;'>
                Las inmobiliarias seleccionadas se pondrán en contacto contigo.<br>
                Puedes gestionar o revocar este consentimiento en cualquier momento
                desde <strong>Privacidad y Consentimientos</strong>.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Nueva consulta", use_container_width=True, key="reset_final"):
            _reset_asesor()
            st.rerun()
        return

    # Argumentario
    argumentario = generar_argumentario(datos_propietario, inmos_prob)
    resumen_txt  = "\n".join([f"- {p['emoji']} {p['inmueble']}: {p['titulo']}" for p in inmos_prob])

    st.markdown("### 🏢 Solicitar asesoramiento profesional")

    # Mostrar resumen de lo que se va a pedir
    st.markdown(f"""
    <div style='background:{CARD_BG};border:1px solid {BORDER};
        border-radius:8px;padding:1rem;margin-bottom:1.2rem;'>
        <div style='font-weight:600;color:{TEXT_PRI};margin-bottom:8px;'>
            📋 Vas a solicitar ayuda con:
        </div>
        {chr(10).join([
            f"<div style='font-size:0.88rem;color:{TEXT_SEC};padding:3px 0;'>"
            f"{p['emoji']} <strong>{p['inmueble']}</strong> — {p['titulo']}</div>"
            for p in inmos_prob
        ])}
    </div>
    """, unsafe_allow_html=True)

    # Datos de contacto
    st.markdown("#### 👤 Tus datos de contacto")
    col1, col2 = st.columns(2)
    with col1:
        nombre_contacto = st.text_input("Nombre completo", key="rgpd_nombre",
            value=datos_propietario.get("nombre", ""))
        telefono = st.text_input("Teléfono", key="rgpd_telefono",
            value=datos_propietario.get("telefono", ""))
    with col2:
        email = st.text_input("Email", key="rgpd_email",
            value=datos_propietario.get("email", ""))

    # CP del primer inmueble para filtrar inmobiliarias
    cp_ref = str(df_inmuebles.iloc[0].get("CP", "18001")) if not df_inmuebles.empty else "18001"
    inmobiliarias = _leer_inmobiliarias_zona(cp_ref)

    # Selector de inmobiliarias
    st.markdown("#### 🏢 Selecciona las inmobiliarias que pueden contactarte")
    st.caption("Solo las inmobiliarias que marques recibirán tus datos.")

    seleccionadas = []
    for inmo in inmobiliarias:
        checked = st.checkbox(
            f"**{inmo['nombre']}** — {inmo.get('descripcion', '')}",
            key=f"chk_{inmo['id']}",
            value=False  # Nunca premarcado (RGPD)
        )
        if checked:
            seleccionadas.append(inmo)

    # Texto legal RGPD
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📜 Ver texto legal completo (RGPD)"):
        st.text(TEXTO_LEGAL)

    # Checkbox de consentimiento
    st.markdown("<br>", unsafe_allow_html=True)
    consentimiento_ok = st.checkbox(
        "✅ He leído y acepto la política de protección de datos. "
        "Autorizo expresamente el envío de mis datos a las inmobiliarias seleccionadas.",
        key="chk_consentimiento",
        value=False
    )

    # Botones
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Volver al resumen", use_container_width=True, key="back_rgpd"):
            st.session_state.asesor_paso = 2
            st.rerun()
    with col2:
        btn_disabled = not (consentimiento_ok and seleccionadas and nombre_contacto and email)
        if st.button(
            "📨 CONFIRMAR Y ENVIAR MIS DATOS",
            type="primary",
            use_container_width=True,
            key="btn_confirmar",
            disabled=btn_disabled
        ):
            datos_ok = {
                "nombre":   nombre_contacto,
                "email":    email,
                "telefono": telefono,
            }
            debug_msgs = []
            exito = True

            # Verificar conexión Supabase
            url_preview = SUPA_URL[:40]
            inmo_nombres = [i["nombre"] for i in seleccionadas]
            debug_msgs.append(f"🔌 SUPABASE_OK: {SUPABASE_OK}")
            debug_msgs.append(f"🔑 URL: {url_preview}...")
            debug_msgs.append(f"👤 user_id: {user_id}")
            debug_msgs.append(f"🏢 Inmobiliarias: {inmo_nombres}")

            for inmo in seleccionadas:
                debug_msgs.append(f"--- Procesando: {inmo['nombre']} (id={inmo['id']}) ---")

                # Test directo de escritura en leads sin pasar por consentimiento
                try:
                    url = f"{SUPA_URL}/rest/v1/leads_inmobiliarias"
                    payload = {
                        "propietario_id":    user_id,
                        "inmobiliaria_id":   inmo["id"],
                        "nombre":            nombre_contacto,
                        "email":             email,
                        "telefono":          telefono,
                        "motivo_texto":      resumen_txt,
                        "argumentario":      argumentario,
                        "estado":            "nuevo",
                        "exportado_inmohub": False,
                    }
                    import requests as req
                    r = req.post(
                        url,
                        headers={
                            "apikey":        SUPA_KEY,
                            "Authorization": f"Bearer {SUPA_KEY}",
                            "Content-Type":  "application/json",
                            "Prefer":        "return=representation",
                        },
                        json=payload,
                        timeout=10,
                    )
                    debug_msgs.append(f"HTTP status: {r.status_code}")
                    debug_msgs.append(f"Respuesta: {r.text[:300]}")
                    if r.status_code in (200, 201):
                        debug_msgs.append(f"✅ Lead creado OK")
                    else:
                        debug_msgs.append(f"❌ Error HTTP {r.status_code}")
                        exito = False
                except Exception as e:
                    debug_msgs.append(f"❌ Excepción: {str(e)}")
                    exito = False

            # Mostrar debug siempre
            with st.expander("🔍 Debug técnico", expanded=True):
                for msg in debug_msgs:
                    st.text(msg)

            if exito:
                st.session_state.asesor_enviado = True
                # No rerun inmediato — dejamos ver el debug
                st.success("✅ Leads enviados. Recarga la página para ver la confirmación.")
            else:
                st.error("⚠️ Hay errores. Revisa el debug técnico arriba.")

    if btn_disabled and not st.session_state.get("chk_consentimiento"):
        st.caption("Para enviar: selecciona al menos una inmobiliaria, completa tus datos y acepta el consentimiento.")


# ================================================================
# PRIVACIDAD — GESTIÓN RGPD
# ================================================================
def render_privacidad(user_id: str):
    st.markdown("### 🔒 Tus consentimientos activos")

    if not SUPABASE_OK:
        st.warning("⚠️ Conexión con base de datos no disponible.")
        return

    try:
        url = (f"{SUPA_URL}/rest/v1/consentimientos"
               f"?propietario_id=eq.{user_id}&select=*,inmobiliarias(nombre)&order=created_at.desc")
        r = requests.get(url, headers=_headers(), timeout=5)
        consentimientos = r.json() if r.status_code == 200 else []
    except Exception:
        consentimientos = []

    activos  = [c for c in consentimientos if not c.get("revocado_at")]
    revocados = [c for c in consentimientos if c.get("revocado_at")]

    if not consentimientos:
        st.info("No has dado ningún consentimiento todavía.")
    else:
        # Activos
        if activos:
            st.markdown(f"#### ✅ Activos ({len(activos)})")
            for c in activos:
                nombre_inmo = c.get("inmobiliarias", {}).get("nombre", "Inmobiliaria")
                fecha = c.get("created_at", "")[:10]
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div style='background:{CARD_BG};border:1px solid {BORDER};
                        border-radius:6px;padding:0.7rem 1rem;'>
                        <strong>{nombre_inmo}</strong>
                        <div style='font-size:0.78rem;color:{TEXT_SEC};'>Dado el {fecha}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("🗑️ Revocar", key=f"rev_{c['id']}", use_container_width=True):
                        try:
                            url_rev = f"{SUPA_URL}/rest/v1/consentimientos?id=eq.{c['id']}"
                            requests.patch(
                                url_rev,
                                headers=_headers(),
                                json={"revocado_at": datetime.now().isoformat()},
                                timeout=5
                            )
                            st.success("✅ Consentimiento revocado.")
                            st.rerun()
                        except Exception:
                            st.error("Error al revocar.")

        # Revocados
        if revocados:
            st.markdown(f"#### ❌ Revocados ({len(revocados)})")
            for c in revocados:
                nombre_inmo = c.get("inmobiliarias", {}).get("nombre", "Inmobiliaria")
                fecha_rev = c.get("revocado_at", "")[:10]
                st.markdown(f"""
                <div style='background:#F8F8F8;border:1px solid {BORDER};
                    border-radius:6px;padding:0.7rem 1rem;margin-bottom:4px;
                    opacity:0.6;'>
                    <strong>{nombre_inmo}</strong>
                    <span style='font-size:0.78rem;color:{TEXT_SEC};margin-left:8px;'>
                        Revocado el {fecha_rev}
                    </span>
                </div>
                """, unsafe_allow_html=True)

    # Descargar datos (derecho RGPD)
    st.markdown("<br>")
    st.markdown("#### 📥 Descargar tus datos (Art. 20 RGPD)")
    datos_export = {
        "user_id": user_id,
        "consentimientos": consentimientos,
        "exportado_en": datetime.now().isoformat(),
    }
    st.download_button(
        "📥 Descargar mis datos en JSON",
        data=json.dumps(datos_export, indent=2, default=str),
        file_name=f"mis_datos_nolasco_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json",
        use_container_width=True,
    )


# ================================================================
# DIAGNÓSTICO POR INMUEBLE (para usar en Fichas)
# ================================================================
def render_diagnostico_inmueble(row: dict):
    """Mini-diagnóstico para mostrar al final de cada ficha benchmark."""
    problemas = detectar_problemas(pd.DataFrame([row]))
    if not problemas:
        st.markdown(f"""
        <div style='background:#EDF7F1;border-left:3px solid #1a7a40;
            border-radius:6px;padding:0.7rem 1rem;margin-top:1rem;'>
            <span style='color:#1a7a40;font-weight:600;'>🟢 Sin alertas detectadas</span>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div style='margin-top:1rem;padding:0.5rem 0;border-top:1px solid {BORDER};'>
        <div style='font-size:0.75rem;letter-spacing:0.1em;text-transform:uppercase;
            color:{TEXT_SEC};margin-bottom:0.5rem;'>🔍 Diagnóstico</div>
    </div>
    """, unsafe_allow_html=True)

    for p in problemas:
        color_p = "#C0392B" if p["tipo_ayuda"] == "inmobiliaria" else "#D97706"
        st.markdown(f"""
        <div style='background:#FFF8F5;border-left:3px solid {color_p};
            border-radius:4px;padding:0.5rem 0.8rem;margin-bottom:4px;'>
            <div style='font-size:0.82rem;font-weight:600;color:{color_p};'>
                {p["emoji"]} {p["titulo"]}
            </div>
            <div style='font-size:0.75rem;color:{TEXT_SEC};'>
                -{p["impacto_euros"]:,.0f}€/mes
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🧠 Ver en Asesor Patrimonial IA →",
                 key=f"goto_asesor_{row.get('Nombre','')}", use_container_width=True):
        st.session_state.menu = "Asesor Patrimonial IA"
        st.rerun()


# ================================================================
# HELPERS
# ================================================================
def _reset_asesor():
    for key in ["asesor_paso", "asesor_problema_idx", "asesor_decisiones",
                "asesor_mostrar_rgpd", "asesor_inmos_seleccionadas", "asesor_enviado"]:
        if key in st.session_state:
            del st.session_state[key]
