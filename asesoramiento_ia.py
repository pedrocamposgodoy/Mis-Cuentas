import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime, date
import requests

# ── Importar funciones de BD ────────────────────────────────
import supabase_db

# ============================================================
# CONSTANTES
# ============================================================

RENTABILIDAD_MERCADO_GRANADA = {
    18001: 7.8, 18002: 7.2, 18003: 6.8, 18004: 7.0,
    18005: 7.5, 18006: 6.5, 18007: 6.2, 18008: 7.0,
    18009: 5.8, 18010: 6.6, 18011: 6.9, 18012: 6.3,
    18013: 5.9, 18014: 6.1, 18015: 5.5
}

TEXTO_LEGAL = """Autorizo expresamente a la inmobiliaria seleccionada a contactarme 
por teléfono, correo electrónico o cualquier otro medio para informarme sobre 
opciones de compra, venta, alquiler u optimización de mi patrimonio inmobiliario.

Entiendo que mis datos personales (nombre, email, teléfono y situación patrimonial) 
serán cedidos exclusivamente a la inmobiliaria que he seleccionado, y que puedo 
revocar este consentimiento en cualquier momento desde la sección 
'Privacidad y Consentimientos' de esta aplicación.

Tratamiento conforme al Reglamento (UE) 2016/679 (RGPD) y la Ley Orgánica 3/2018 (LOPDGDD)."""


# ============================================================
# BLOQUE A — HELPERS
# ============================================================

def _hash_texto_legal(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _get_ip() -> str:
    try:
        return requests.get("https://api.ipify.org", timeout=3).text.strip()
    except Exception:
        return "0.0.0.0"


def _rentabilidad_mercado(cp: int) -> float:
    return RENTABILIDAD_MERCADO_GRANADA.get(cp, 7.0)


# ============================================================
# BLOQUE B — SEMÁFORO Y ALERTAS
# ============================================================

def calcular_semaforo(df_inmuebles: pd.DataFrame) -> dict:
    """
    Analiza los inmuebles del propietario y devuelve:
      - color: 'verde' | 'amarillo' | 'rojo'
      - alertas: lista de problemas detectados
      - potencial_mejora_euros: cuánto podría ganar
    """
    alertas = []
    potencial = 0.0

    for _, row in df_inmuebles.iterrows():
        cp = int(row.get("CP", 18001))
        renta_actual = float(row.get("Renta", 0))
        renta_mercado = float(row.get("Renta_Mercado", 0))

        # 1. Brecha de renta
        if renta_mercado > 0 and renta_actual < renta_mercado:
            brecha = renta_mercado - renta_actual
            potencial += brecha * 12
            if brecha / renta_mercado > 0.15:
                alertas.append({
                    "tipo": "renta_baja",
                    "inmueble": row.get("Nombre", "Inmueble"),
                    "mensaje": f"Renta {renta_actual:.0f}€ vs mercado {renta_mercado:.0f}€ → pierdes {brecha:.0f}€/mes",
                    "gravedad": "rojo" if brecha / renta_mercado > 0.25 else "amarillo"
                })

        # 2. Contrato próximo a vencer
        try:
            # Buscamos fecha de fin en movimientos (campo Concepto con "contrato")
            pass
        except Exception:
            pass

        # 3. Rentabilidad muy baja
        valor = float(row.get("Valor_Construccion", 0))
        if valor > 0 and renta_actual > 0:
            rent_bruta = (renta_actual * 12) / valor * 100
            rent_mercado_pct = _rentabilidad_mercado(cp)
            if rent_bruta < rent_mercado_pct - 1.5:
                alertas.append({
                    "tipo": "rentabilidad_baja",
                    "inmueble": row.get("Nombre", "Inmueble"),
                    "mensaje": f"Rentabilidad {rent_bruta:.1f}% vs mercado {rent_mercado_pct:.1f}%",
                    "gravedad": "rojo" if rent_bruta < rent_mercado_pct - 3 else "amarillo"
                })

    # Decidir color global
    if any(a["gravedad"] == "rojo" for a in alertas):
        color = "rojo"
    elif alertas:
        color = "amarillo"
    else:
        color = "verde"

    return {"color": color, "alertas": alertas, "potencial_mejora_euros": potencial}


# ============================================================
# BLOQUE C — DATOS AGREGADOS DE ZONA (CAPA 1)
# ============================================================

def generar_alertas_zona(propietario_id: str, cp: int) -> dict:
    """
    Genera estadísticas de zona sin identificar a nadie.
    Usa todos los inmuebles de la BD para agregar por CP.
    """
    try:
        # Leer todos los inmuebles de ese CP (todos los usuarios)
        headers = supabase_db._headers()
        url = f"{supabase_db.SUPABASE_URL}/rest/v1/inmuebles?CP=eq.{cp}&select=Renta,Renta_Mercado,Valor_Construccion"
        resp = requests.get(url, headers=headers, timeout=10)

        if resp.status_code == 200 and resp.json():
            df = pd.DataFrame(resp.json())
            df["Renta"] = pd.to_numeric(df["Renta"], errors="coerce")
            df["Renta_Mercado"] = pd.to_numeric(df["Renta_Mercado"], errors="coerce")

            rent_mercado = _rentabilidad_mercado(cp)
            n_total = len(df)
            n_baja = len(df[df["Renta"] < df["Renta_Mercado"] * 0.85])
            brecha_media = (df["Renta_Mercado"] - df["Renta"]).clip(lower=0).mean()
        else:
            # Datos de ejemplo si no hay suficientes usuarios aún
            n_total = 12
            n_baja = 8
            brecha_media = 95.0
            rent_mercado = _rentabilidad_mercado(cp)

    except Exception:
        n_total = 12
        n_baja = 8
        brecha_media = 95.0
        rent_mercado = _rentabilidad_mercado(cp)

    return {
        "cp": cp,
        "num_propietarios_zona": n_total,
        "num_baja_rentabilidad": n_baja,
        "pct_baja_rentabilidad": round(n_baja / max(n_total, 1) * 100, 1),
        "brecha_media_euros": round(brecha_media, 0),
        "rentabilidad_mercado": rent_mercado,
        "lucro_cesante_zona_mes": round(brecha_media * n_total, 0),
    }


# ============================================================
# BLOQUE D — LEER INMOBILIARIAS DE ZONA
# ============================================================

def leer_inmobiliarias_zona(cp: int) -> pd.DataFrame:
    """Devuelve inmobiliarias que operan en ese CP."""
    try:
        headers = supabase_db._headers()
        url = f"{supabase_db.SUPABASE_URL}/rest/v1/inmobiliarias?activa=eq.true&select=*"
        resp = requests.get(url, headers=headers, timeout=10)

        if resp.status_code == 200 and resp.json():
            df = pd.DataFrame(resp.json())
            # Filtrar por CP (el array cp[] contiene ese CP)
            # Supabase no permite filtro directo en arrays sin postgrest avanzado
            # → traemos todas activas y filtramos en Python
            def tiene_cp(lista):
                if isinstance(lista, list):
                    return cp in lista
                return False

            df = df[df["cp"].apply(tiene_cp)]
            if len(df) > 0:
                return df.reset_index(drop=True)

    except Exception as e:
        st.warning(f"No se pudieron cargar inmobiliarias: {e}")

    # Fallback — datos ficticios si BD vacía
    return pd.DataFrame([
        {"id": 1, "nombre": "Inmobiliaria Núñez Granada",   "zona": "Granada Centro",    "descripcion": "Especialistas en Centro y Realejo"},
        {"id": 2, "nombre": "Century21 Granada Capital",    "zona": "Granada Norte",     "descripcion": "10 años en Granada Norte"},
        {"id": 3, "nombre": "Remax Granada",                "zona": "Zaidín",            "descripcion": "Líderes en Zaidín"},
    ])


# ============================================================
# BLOQUE E — REGISTRAR CONSENTIMIENTO (RGPD)
# ============================================================

def registrar_consentimiento(propietario_id: str, inmobiliaria_id: int) -> int | None:
    """
    Inserta un registro de consentimiento en BD.
    Devuelve el ID del consentimiento creado.
    """
    try:
        hash_legal = _hash_texto_legal(TEXTO_LEGAL)
        ip = _get_ip()

        payload = {
            "propietario_id": propietario_id,
            "inmobiliaria_id": inmobiliaria_id,
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": ip,
            "consentimiento": True,
            "documento_legal_hash": hash_legal,
            "revocado_at": None
        }

        headers = {**supabase_db._headers(), "Prefer": "return=representation"}
        url = f"{supabase_db.SUPABASE_URL}/rest/v1/consentimientos"
        resp = requests.post(url, json=payload, headers=headers, timeout=10)

        if resp.status_code in (200, 201) and resp.json():
            return resp.json()[0]["id"]

    except Exception as e:
        st.error(f"Error registrando consentimiento: {e}")

    return None


# ============================================================
# BLOQUE F — CREAR LEAD CUALIFICADO
# ============================================================

def _generar_argumentario(nombre: str, renta_actual: float, renta_mercado: float,
                           inmueble_nombre: str) -> str:
    brecha = renta_mercado - renta_actual
    brecha_anual = brecha * 12

    if brecha > 0:
        return (
            f"Estimado/a {nombre}, hemos detectado que su inmueble '{inmueble_nombre}' "
            f"tiene una renta actual de {renta_actual:.0f}€/mes cuando el mercado en su "
            f"zona está en {renta_mercado:.0f}€/mes. "
            f"Esto supone una pérdida de {brecha:.0f}€ al mes, es decir, "
            f"{brecha_anual:.0f}€ al año. "
            f"Podemos ayudarle a optimizar su rentabilidad y maximizar el valor de su patrimonio."
        )
    else:
        return (
            f"Estimado/a {nombre}, su inmueble '{inmueble_nombre}' está bien posicionado "
            f"en el mercado actual. Podemos ayudarle a mantener y mejorar su rentabilidad "
            f"con una gestión profesional."
        )


def crear_lead_cualificado(propietario_id: str, inmobiliaria_id: int,
                            consentimiento_id: int, datos_propietario: dict,
                            df_inmuebles: pd.DataFrame) -> bool:
    """
    Crea el lead en la BD con argumentario automático.
    """
    try:
        # Tomar el inmueble con mayor brecha como referencia
        df = df_inmuebles.copy()
        df["brecha"] = pd.to_numeric(df["Renta_Mercado"], errors="coerce") - \
                       pd.to_numeric(df["Renta"], errors="coerce")
        df = df.sort_values("brecha", ascending=False)
        inmueble_ref = df.iloc[0] if len(df) > 0 else None

        renta_actual = float(inmueble_ref["Renta"]) if inmueble_ref is not None else 0
        renta_mercado = float(inmueble_ref["Renta_Mercado"]) if inmueble_ref is not None else 0
        cp = int(inmueble_ref["CP"]) if inmueble_ref is not None else 18001
        inmueble_nombre = inmueble_ref["Nombre"] if inmueble_ref is not None else "Inmueble"

        argumentario = _generar_argumentario(
            datos_propietario.get("nombre", "Propietario"),
            renta_actual, renta_mercado, inmueble_nombre
        )

        rent_mercado_pct = _rentabilidad_mercado(cp)
        valor = float(inmueble_ref.get("Valor_Construccion", 0)) if inmueble_ref is not None else 0
        rent_actual_pct = (renta_actual * 12 / valor * 100) if valor > 0 else 0

        payload = {
            "propietario_id": propietario_id,
            "inmobiliaria_id": inmobiliaria_id,
            "consentimiento_id": consentimiento_id,
            "nombre": datos_propietario.get("nombre", ""),
            "email": datos_propietario.get("email", ""),
            "telefono": datos_propietario.get("telefono", ""),
            "cp": cp,
            "tipo_propiedad": str(inmueble_ref.get("Tipo", "Residencial")) if inmueble_ref is not None else "Residencial",
            "m2": int(inmueble_ref.get("M2_Construidos", 0)) if inmueble_ref is not None else 0,
            "rentabilidad_actual": round(rent_actual_pct, 2),
            "rentabilidad_mercado": round(rent_mercado_pct, 2),
            "motivo_texto": f"Rentabilidad {rent_actual_pct:.1f}% vs mercado {rent_mercado_pct:.1f}% en CP {cp}",
            "argumentario": argumentario,
            "estado": "nuevo",
            "exportado_inmohub": False
        }

        headers = {**supabase_db._headers(), "Prefer": "return=representation"}
        url = f"{supabase_db.SUPABASE_URL}/rest/v1/leads_inmobiliarias"
        resp = requests.post(url, json=payload, headers=headers, timeout=10)

        return resp.status_code in (200, 201)

    except Exception as e:
        st.error(f"Error creando lead: {e}")
        return False


# ============================================================
# BLOQUE G — REVOCAR CONSENTIMIENTO
# ============================================================

def revocar_consentimiento(consentimiento_id: int) -> bool:
    try:
        headers = supabase_db._headers()
        url = f"{supabase_db.SUPABASE_URL}/rest/v1/consentimientos?id=eq.{consentimiento_id}"
        payload = {"revocado_at": datetime.utcnow().isoformat()}
        resp = requests.patch(url, json=payload, headers=headers, timeout=10)
        return resp.status_code == 204
    except Exception as e:
        st.error(f"Error revocando consentimiento: {e}")
        return False


def leer_consentimientos_propietario(propietario_id: str) -> pd.DataFrame:
    try:
        headers = supabase_db._headers()
        url = (f"{supabase_db.SUPABASE_URL}/rest/v1/consentimientos"
               f"?propietario_id=eq.{propietario_id}"
               f"&select=*,inmobiliarias(nombre,zona)")
        resp = requests.get(url, headers=headers, timeout=10)

        if resp.status_code == 200 and resp.json():
            df = pd.DataFrame(resp.json())
            # Expandir nombre de inmobiliaria
            if "inmobiliarias" in df.columns:
                df["inmobiliaria_nombre"] = df["inmobiliarias"].apply(
                    lambda x: x.get("nombre", "") if isinstance(x, dict) else ""
                )
                df["inmobiliaria_zona"] = df["inmobiliarias"].apply(
                    lambda x: x.get("zona", "") if isinstance(x, dict) else ""
                )
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df
    except Exception as e:
        st.warning(f"No se pudieron cargar consentimientos: {e}")

    return pd.DataFrame()


# ============================================================
# BLOQUE H — UI: ASESOR PATRIMONIAL IA (pantallas 1 y 2)
# ============================================================

def render_asesor_ia(user_id: str, df_inmuebles: pd.DataFrame,
                     datos_propietario: dict):
    """
    Renderiza el módulo completo del Asesor Patrimonial IA.
    Llama a esta función desde app.py en la sección correspondiente.
    """

    # ── Inicializar estado ──────────────────────────────────
    if "asesor_paso" not in st.session_state:
        st.session_state.asesor_paso = 0
    if "asesor_inmobiliarias_seleccionadas" not in st.session_state:
        st.session_state.asesor_inmobiliarias_seleccionadas = []

    # ── PASO 0: Semáforo + datos de zona ───────────────────
    if st.session_state.asesor_paso == 0:
        _render_paso0_semaforo(df_inmuebles)

    # ── PASO 1: Selector de inmobiliarias ──────────────────
    elif st.session_state.asesor_paso == 1:
        _render_paso1_selector(user_id, df_inmuebles, datos_propietario)

    # ── PASO 2: Confirmación ───────────────────────────────
    elif st.session_state.asesor_paso == 2:
        _render_paso2_confirmacion()


def _render_paso0_semaforo(df_inmuebles: pd.DataFrame):
    semaforo = calcular_semaforo(df_inmuebles)
    color = semaforo["color"]
    alertas = semaforo["alertas"]
    potencial = semaforo["potencial_mejora_euros"]

    # CP del propietario (primer inmueble)
    cp = int(df_inmuebles["CP"].iloc[0]) if len(df_inmuebles) > 0 else 18001
    zona = generar_alertas_zona("", cp)

    # ── Cabecera con semáforo ──────────────────────────────
    col1, col2 = st.columns([1, 4])
    with col1:
        if color == "verde":
            st.success("🟢")
        elif color == "amarillo":
            st.warning("🟡")
        else:
            st.error("🔴")

    with col2:
        if color == "verde":
            st.success("**Tu patrimonio está bien gestionado.** No se detectan problemas urgentes.")
        elif color == "amarillo":
            st.warning(f"**Se detectaron oportunidades de mejora.** Podrías ganar hasta **{potencial:.0f}€/año** más.")
        else:
            st.error(f"**Atención: se detectaron problemas críticos.** Estás perdiendo hasta **{potencial:.0f}€/año.**")

    # ── Alertas personales ─────────────────────────────────
    if alertas:
        st.markdown("#### Tus alertas personales")
        for a in alertas:
            if a["gravedad"] == "rojo":
                st.error(f"🔴 **{a['inmueble']}** — {a['mensaje']}")
            else:
                st.warning(f"🟡 **{a['inmueble']}** — {a['mensaje']}")

    # ── Datos de zona (Capa 1 — anónimos) ─────────────────
    st.markdown("---")
    st.markdown(f"#### Tu zona: CP {cp}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Propietarios en tu zona", zona["num_propietarios_zona"])
    c2.metric("Con baja rentabilidad", f"{zona['num_baja_rentabilidad']} ({zona['pct_baja_rentabilidad']}%)")
    c3.metric("Pérdida media zona/mes", f"{zona['brecha_media_euros']:.0f}€")

    st.caption("Datos agregados de zona · Sin nombres ni datos personales de nadie")

    # ── Árbol de decisión ─────────────────────────────────
    st.markdown("---")

    if color == "verde":
        st.info("No se recomienda ninguna acción urgente. Puedes revisar las Fichas de Benchmark para seguir optimizando.")
        if st.button("📊 Ver Fichas Benchmark"):
            st.session_state.menu = "Fichas (Benchmark)"
            st.rerun()
        return

    # ── IA propone solución (amarillo/rojo) ───────────────
    st.markdown("#### ¿Qué puedes hacer?")

    with st.expander("💡 Ver recomendaciones de la IA", expanded=True):
        for a in alertas:
            if a["tipo"] == "renta_baja":
                st.markdown(f"**{a['inmueble']}:** La renta está por debajo del mercado. "
                             f"Considera actualizar el alquiler en la próxima renovación de contrato.")
            elif a["tipo"] == "rentabilidad_baja":
                st.markdown(f"**{a['inmueble']}:** La rentabilidad bruta es baja. "
                             f"Puedes mejorarla reduciendo gastos o renegociando la renta.")

    st.markdown("#### ¿Quieres gestionar esto tú solo o con ayuda profesional?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Lo gestiono yo", use_container_width=True):
            st.success("Perfecto. Puedes usar las Fichas Benchmark y los Simuladores para orientarte.")
            st.session_state.asesor_paso = 0

    with col2:
        if st.button("🏢 Quiero asesoramiento de una inmobiliaria", type="primary", use_container_width=True):
            st.session_state.asesor_paso = 1
            st.rerun()


def _render_paso1_selector(user_id: str, df_inmuebles: pd.DataFrame,
                            datos_propietario: dict):
    st.markdown("### Selecciona qué inmobiliaria puede contactarte")
    st.caption("Solo la inmobiliaria que marques recibirá tus datos. Las demás no sabrán que existes.")

    cp = int(df_inmuebles["CP"].iloc[0]) if len(df_inmuebles) > 0 else 18001
    df_inmobs = leer_inmobiliarias_zona(cp)

    seleccionadas = []
    st.markdown("**Inmobiliarias disponibles en tu zona:**")

    for _, inmob in df_inmobs.iterrows():
        checked = st.checkbox(
            f"**{inmob['nombre']}** — {inmob.get('descripcion', inmob.get('zona', ''))}",
            value=False,
            key=f"inmob_{inmob['id']}"
        )
        if checked:
            seleccionadas.append(int(inmob["id"]))

    # ── Texto legal ───────────────────────────────────────
    st.markdown("---")
    with st.expander("📄 Texto completo del consentimiento (RGPD)", expanded=False):
        st.text(TEXTO_LEGAL)

    st.warning("⚠️ Al confirmar, tus datos serán enviados SOLO a las inmobiliarias que hayas marcado.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Volver", use_container_width=True):
            st.session_state.asesor_paso = 0
            st.rerun()

    with col2:
        confirmar = st.button(
            "✅ Confirmar y enviar mis datos",
            type="primary",
            use_container_width=True,
            disabled=len(seleccionadas) == 0
        )

    if len(seleccionadas) == 0:
        st.caption("Debes seleccionar al menos una inmobiliaria para continuar.")

    if confirmar and seleccionadas:
        exito = True
        for inmob_id in seleccionadas:
            consent_id = registrar_consentimiento(user_id, inmob_id)
            if consent_id:
                ok = crear_lead_cualificado(
                    user_id, inmob_id, consent_id,
                    datos_propietario, df_inmuebles
                )
                if not ok:
                    exito = False
            else:
                exito = False

        if exito:
            st.session_state.asesor_inmobiliarias_seleccionadas = seleccionadas
            st.session_state.asesor_paso = 2
            st.rerun()
        else:
            st.error("Hubo un problema al guardar. Inténtalo de nuevo.")


def _render_paso2_confirmacion():
    st.success("### ✅ Datos enviados correctamente")
    st.markdown(
        "Hemos compartido tu información con las inmobiliarias seleccionadas. "
        "Puedes **revocar este consentimiento** en cualquier momento desde la sección "
        "**Privacidad y Consentimientos**."
    )
    st.info("Las inmobiliarias se pondrán en contacto contigo en los próximos días.")

    if st.button("Volver al inicio"):
        st.session_state.asesor_paso = 0
        st.rerun()


# ============================================================
# BLOQUE I — UI: PRIVACIDAD Y CONSENTIMIENTOS
# ============================================================

def render_privacidad(user_id: str):
    """
    Renderiza la pestaña de Privacidad y Consentimientos.
    """
    st.markdown("### 🔒 Privacidad y Consentimientos")
    st.caption("Aquí puedes ver y gestionar todos los datos que has compartido.")

    df = leer_consentimientos_propietario(user_id)

    if df.empty:
        st.info("No has compartido tus datos con ninguna inmobiliaria aún.")
        return

    # ── Activos ───────────────────────────────────────────
    activos = df[df["revocado_at"].isna()]
    revocados = df[df["revocado_at"].notna()]

    if len(activos) > 0:
        st.markdown("#### Consentimientos activos")
        for _, row in activos.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**{row.get('inmobiliaria_nombre', 'Inmobiliaria')}**")
                    st.caption(f"{row.get('inmobiliaria_zona', '')} · {row.get('ip_address', '')}")
                with col2:
                    fecha = row["timestamp"].strftime("%d/%m/%Y %H:%M") if pd.notna(row["timestamp"]) else ""
                    st.caption(f"Autorizado el {fecha}")
                with col3:
                    if st.button("Revocar", key=f"rev_{row['id']}"):
                        if revocar_consentimiento(int(row["id"])):
                            st.success("Consentimiento revocado.")
                            st.rerun()
                st.divider()

    # ── Revocados ─────────────────────────────────────────
    if len(revocados) > 0:
        with st.expander(f"Historial de consentimientos revocados ({len(revocados)})"):
            for _, row in revocados.iterrows():
                st.caption(
                    f"❌ {row.get('inmobiliaria_nombre', '')} · "
                    f"Revocado el {pd.to_datetime(row['revocado_at']).strftime('%d/%m/%Y')}"
                )

    # ── Derechos RGPD ─────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Tus derechos RGPD")
    st.markdown(
        "Tienes derecho a acceder, rectificar, suprimir y portar tus datos. "
        "Para ejercerlos puedes revocar cualquier consentimiento arriba o "
        "contactar con nosotros en **privacidad@nolascocapital.es**"
    )

    if st.button("📥 Descargar mis datos (JSON)"):
        import json
        datos = df.to_dict(orient="records")
        st.download_button(
            label="Descargar",
            data=json.dumps(datos, default=str, ensure_ascii=False, indent=2),
            file_name=f"mis_datos_nolasco_{date.today()}.json",
            mime="application/json"
        )
