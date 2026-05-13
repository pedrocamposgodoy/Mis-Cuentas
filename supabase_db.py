"""
supabase_db.py — Módulo de Base de Datos Supabase para Nolasco Capital
VERSIÓN FINAL - Usa access_token del usuario para pasar correctamente el RLS
"""
import requests
import pandas as pd
import streamlit as st

# ─── CREDENCIALES ───────────────────────────────────────────────
SUPABASE_URL = "https://odxixtgqcyddfqaapqgi.supabase.co"
SUPABASE_KEY = "sb_publishable_Obgti7yMfXw8wCUL2FbTtA_EWeyHuM9"

# ─── COLUMNAS ESPERADAS ─────────────────────────────────────────
COLS_INM = [
    "Nombre","Direccion","Inquilino","Renta","Renta_Mercado","Comunidad","Valor_Construccion",
    "Año_Reforma","Año_Construccion","Mobiliario","Tipo","Ref_Catastral","Titular",
    "M2_Construidos","Habitaciones","CP","Planta","Parking","Estado",
    "Tipo_Arrendamiento","Cochera_Vinculada","Zona_Tensionada",
    "Fecha_Inicio_Contrato","Fecha_Vencimiento_Contrato",
    "NIF_Inquilino","Intereses_Hipoteca","IBI_Anual","Seguro_Anual",
    "Gastos_Juridicos","Retenciones_IRPF","Gastos_Formalizacion",
    "Gastos_Pendientes_Años_Ant","Servicios_Suministros",
    "Fecha_Adquisicion","Precio_Compra","Impuestos_Compra","Gastos_Compra",
    "Valor_Catastral","Valor_Catastral_Piso","Pct_Suelo","Pct_Construccion",
    "Valor_Real_Construccion","Amortizacion_Fiscal","Seguro_Vida",
    "Gasto_Ascensor","Ref_Catastral_Cochera","IBI_Cocheras","Comunidad_Cocheras",
    "IVA_Aplicable","Tipo_IVA","Retencion_IRPF_Pct","Dias_Arrendados_Anio",
    "Imputacion_Rentas"
]

COLS_MOV = ["Fecha","Apartamento","Concepto","Categoría","Tipo","Importe","Deducible"]

DEFAULTS_FISCAL = {
    "Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N","Zona_Tensionada":"N",
    "Fecha_Inicio_Contrato":"2022-01-01","Fecha_Vencimiento_Contrato":"2027-01-01",
    "NIF_Inquilino":"","Intereses_Hipoteca":0,"IBI_Anual":0,"Seguro_Anual":0,
    "Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,
    "Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0,
    "Fecha_Adquisicion":None,"Precio_Compra":0,"Impuestos_Compra":0,"Gastos_Compra":0,
    "Valor_Catastral":0,"Valor_Catastral_Piso":0,"Pct_Suelo":0.25,"Pct_Construccion":0.75,
    "Valor_Real_Construccion":0,"Amortizacion_Fiscal":0,"Seguro_Vida":0,
    "Gasto_Ascensor":0,"Ref_Catastral_Cochera":"","IBI_Cocheras":0,"Comunidad_Cocheras":0,
    "IVA_Aplicable":False,"Tipo_IVA":21,"Retencion_IRPF_Pct":0,"Dias_Arrendados_Anio":365,
    "Direccion":"","Imputacion_Rentas":0
}

# ─── HELPER: CABECERAS CON TOKEN DE USUARIO ──────────────────────
def _headers(access_token=None):
    """
    Devuelve cabeceras correctas.
    - Si hay access_token del usuario → lo usa (pasa RLS correctamente)
    - Si no → usa la anon key (solo lectura pública)
    """
    token = access_token or st.session_state.get("access_token") or SUPABASE_KEY
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

# ─── FUNCIONES DE AUTENTICACIÓN ──────────────────────────────────

def login_usuario(email, password):
    """Autentica usuario y guarda access_token en session_state."""
    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={'apikey': SUPABASE_KEY, 'Content-Type': 'application/json'},
            json={'email': email, 'password': password}
        )
        if r.status_code == 200:
            data = r.json()
            access_token = data.get('access_token', '')
            # Guardar el token en session_state para usarlo en todas las peticiones
            st.session_state['access_token'] = access_token
            return {
                'success': True,
                'user_id': data['user']['id'],
                'email': data['user']['email'],
                'access_token': access_token
            }
        else:
            err = r.json()
            msg = err.get('error_description') or err.get('msg') or 'Email o contraseña incorrectos'
            return {'success': False, 'error': msg}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def registrar_usuario(email, password):
    """Registra nuevo usuario."""
    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers={'apikey': SUPABASE_KEY, 'Content-Type': 'application/json'},
            json={'email': email, 'password': password}
        )
        data = r.json()
        if r.status_code in [200, 201] and data.get('user'):
            return {
                'success': True,
                'user_id': data['user']['id'],
                'email': data['user']['email']
            }
        else:
            msg = data.get('error_description') or data.get('msg') or 'Error al registrar usuario'
            return {'success': False, 'error': msg}
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ─── RENAME MAPS ─────────────────────────────────────────────────

RENAME_INM_TO_APP = {
    'nombre': 'Nombre', 'inquilino': 'Inquilino', 'renta': 'Renta',
    'renta_mercado': 'Renta_Mercado', 'comunidad': 'Comunidad',
    'valor_construccion': 'Valor_Construccion', 'ano_reforma': 'Año_Reforma',
    'ano_construccion': 'Año_Construccion', 'mobiliario': 'Mobiliario',
    'tipo': 'Tipo', 'ref_catastral': 'Ref_Catastral', 'titular': 'Titular',
    'm2_construidos': 'M2_Construidos', 'habitaciones': 'Habitaciones',
    'cp': 'CP', 'planta': 'Planta', 'parking': 'Parking', 'estado': 'Estado',
    'tipo_arrendamiento': 'Tipo_Arrendamiento', 'cochera_vinculada': 'Cochera_Vinculada',
    'zona_tensionada': 'Zona_Tensionada', 'fecha_inicio_contrato': 'Fecha_Inicio_Contrato',
    'fecha_vencimiento_contrato': 'Fecha_Vencimiento_Contrato', 'nif_inquilino': 'NIF_Inquilino',
    'intereses_hipoteca': 'Intereses_Hipoteca', 'ibi_anual': 'IBI_Anual',
    'seguro_anual': 'Seguro_Anual', 'gastos_juridicos': 'Gastos_Juridicos',
    'retenciones_irpf': 'Retenciones_IRPF', 'gastos_formalizacion': 'Gastos_Formalizacion',
    'gastos_pendientes_anos_ant': 'Gastos_Pendientes_Años_Ant',
    'servicios_suministros': 'Servicios_Suministros', 'direccion': 'Direccion',
    'fecha_adquisicion': 'Fecha_Adquisicion', 'precio_compra': 'Precio_Compra',
    'impuestos_compra': 'Impuestos_Compra', 'gastos_compra': 'Gastos_Compra',
    'valor_catastral': 'Valor_Catastral', 'valor_catastral_piso': 'Valor_Catastral_Piso',
    'pct_suelo': 'Pct_Suelo', 'pct_construccion': 'Pct_Construccion',
    'valor_real_construccion': 'Valor_Real_Construccion',
    'amortizacion_fiscal': 'Amortizacion_Fiscal', 'seguro_vida': 'Seguro_Vida',
    'gasto_ascensor': 'Gasto_Ascensor', 'ref_catastral_cochera': 'Ref_Catastral_Cochera',
    'ibi_cocheras': 'IBI_Cocheras', 'comunidad_cocheras': 'Comunidad_Cocheras',
    'iva_aplicable': 'IVA_Aplicable', 'tipo_iva': 'Tipo_IVA',
    'retencion_irpf_pct': 'Retencion_IRPF_Pct', 'dias_arrendados_anio': 'Dias_Arrendados_Anio',
    'imputacion_rentas': 'Imputacion_Rentas'
}

RENAME_INM_TO_DB = {v: k for k, v in RENAME_INM_TO_APP.items()}

RENAME_MOV_TO_APP = {
    'fecha': 'Fecha', 'apartamento': 'Apartamento', 'concepto': 'Concepto',
    'categoria': 'Categoría', 'tipo': 'Tipo', 'importe': 'Importe', 'deducible': 'Deducible'
}
RENAME_MOV_TO_DB = {v: k for k, v in RENAME_MOV_TO_APP.items()}


# ─── FUNCIONES DE LECTURA ────────────────────────────────────────

def leer_inmuebles(user_id=None):
    """Lee inmuebles del usuario desde Supabase."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/inmuebles?select=*&order=id.asc"
        if user_id:
            url += f"&user_id=eq.{user_id}"

        r = requests.get(url, headers=_headers())
        if r.status_code == 200:
            data = r.json()
            if data:
                df = pd.DataFrame(data)
                df = df.rename(columns={k: v for k, v in RENAME_INM_TO_APP.items() if k in df.columns})
                for col in COLS_INM:
                    if col not in df.columns:
                        df[col] = DEFAULTS_FISCAL.get(col, "")
                _limpiar_numericos_inm(df)
                return df
            else:
                # Usuario nuevo sin inmuebles — devolver DataFrame vacío
                return pd.DataFrame(columns=COLS_INM)
        else:
            return pd.DataFrame(columns=COLS_INM)
    except Exception as e:
        st.error(f"Error leyendo inmuebles: {e}")
        return pd.DataFrame(columns=COLS_INM)


def leer_movimientos(user_id=None):
    """Lee movimientos del usuario desde Supabase."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/movimientos?select=*&order=fecha.desc"
        if user_id:
            url += f"&user_id=eq.{user_id}"

        r = requests.get(url, headers=_headers())
        if r.status_code == 200:
            data = r.json()
            if data:
                df = pd.DataFrame(data)
                df = df.rename(columns={k: v for k, v in RENAME_MOV_TO_APP.items() if k in df.columns})
                for col in COLS_MOV:
                    if col not in df.columns:
                        df[col] = ""
                if "Importe" in df.columns:
                    df["Importe"] = pd.to_numeric(df["Importe"], errors='coerce').fillna(0)
                return df
            else:
                return pd.DataFrame(columns=COLS_MOV)
        else:
            return pd.DataFrame(columns=COLS_MOV)
    except Exception as e:
        st.error(f"Error leyendo movimientos: {e}")
        return pd.DataFrame(columns=COLS_MOV)


# ─── FUNCIONES DE ESCRITURA ──────────────────────────────────────

def guardar_movimientos_completo(df, user_id):
    """
    Borra todos los movimientos del usuario y los reinserta.
    Usa el access_token del usuario para pasar RLS.
    """
    try:
        h = _headers()

        # 1. Borrar movimientos del usuario
        del_r = requests.delete(
            f"{SUPABASE_URL}/rest/v1/movimientos?user_id=eq.{user_id}",
            headers=h
        )
        if del_r.status_code not in [200, 204]:
            st.warning(f"⚠️ Delete status: {del_r.status_code} — {del_r.text[:200]}")

        if df is None or len(df) == 0:
            return True

        # 2. Preparar registros
        records = _df_mov_to_records(df, user_id)
        if not records:
            return True

        # 3. Insertar
        ins_r = requests.post(
            f"{SUPABASE_URL}/rest/v1/movimientos",
            headers=h,
            json=records
        )
        if ins_r.status_code not in [200, 201]:
            st.error(f"❌ Error insertando movimientos: {ins_r.status_code} — {ins_r.text[:300]}")
            return False
        return True

    except Exception as e:
        st.error(f"Error guardando movimientos: {e}")
        return False


def agregar_movimientos(nuevos, user_id):
    """Agrega nuevos movimientos sin borrar los existentes."""
    try:
        if not nuevos:
            return True

        records = []
        for mov in nuevos:
            record = {}
            for k, v in mov.items():
                db_key = RENAME_MOV_TO_DB.get(k, k.lower())
                record[db_key] = v
            record['user_id'] = user_id
            # Eliminar campos que no existen en la tabla
            record.pop('estado', None)
            records.append(record)

        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/movimientos",
            headers=_headers(),
            json=records
        )
        if r.status_code not in [200, 201]:
            st.error(f"❌ Error agregando movimientos: {r.status_code} — {r.text[:300]}")
            return False
        return True
    except Exception as e:
        st.error(f"Error agregando movimientos: {e}")
        return False


def eliminar_inmueble(nombre, user_id):
    """Elimina un inmueble por nombre."""
    try:
        r = requests.delete(
            f"{SUPABASE_URL}/rest/v1/inmuebles?nombre=eq.{nombre}&user_id=eq.{user_id}",
            headers=_headers()
        )
        return r.status_code in [200, 204]
    except Exception as e:
        st.error(f"Error eliminando inmueble: {e}")
        return False


# ─── HELPERS INTERNOS ────────────────────────────────────────────

def _df_mov_to_records(df, user_id):
    """Convierte DataFrame de movimientos a lista de dicts para Supabase."""
    df2 = df.copy()
    df2 = df2.rename(columns={k: v for k, v in RENAME_MOV_TO_DB.items() if k in df2.columns})
    # Solo columnas válidas de la tabla
    cols_db = ['fecha', 'apartamento', 'concepto', 'categoria', 'tipo', 'importe', 'deducible']
    cols_presentes = [c for c in cols_db if c in df2.columns]
    df2 = df2[cols_presentes]
    df2 = df2.where(pd.notna(df2), None)
    # Convertir fechas a string
    if 'fecha' in df2.columns:
        df2['fecha'] = pd.to_datetime(df2['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
    records = df2.to_dict(orient='records')
    for r in records:
        r['user_id'] = user_id
    return records


def _df_inm_to_records(df, user_id):
    """Convierte DataFrame de inmuebles a lista de dicts para Supabase.
    Acepta columnas tanto en formato app (Nombre, Renta...) como en formato DB (nombre, renta...).
    Aplica defaults correctos por tipo para evitar errores NOT NULL.
    """
    df2 = df.copy()

    MAP_APP_TO_DB = {
        'Nombre': 'nombre', 'Inquilino': 'inquilino', 'Renta': 'renta',
        'Renta_Mercado': 'renta_mercado', 'Comunidad': 'comunidad',
        'Valor_Construccion': 'valor_construccion', 'Año_Reforma': 'ano_reforma',
        'Año_Construccion': 'ano_construccion', 'Mobiliario': 'mobiliario',
        'Tipo': 'tipo', 'Ref_Catastral': 'ref_catastral', 'Titular': 'titular',
        'M2_Construidos': 'm2_construidos', 'Habitaciones': 'habitaciones',
        'CP': 'cp', 'Planta': 'planta', 'Parking': 'parking', 'Estado': 'estado',
        'Tipo_Arrendamiento': 'tipo_arrendamiento',
        'Cochera_Vinculada': 'cochera_vinculada',
        'Zona_Tensionada': 'zona_tensionada',
        'Fecha_Inicio_Contrato': 'fecha_inicio_contrato',
        'Fecha_Vencimiento_Contrato': 'fecha_vencimiento_contrato',
        'NIF_Inquilino': 'nif_inquilino',
        'Intereses_Hipoteca': 'intereses_hipoteca',
        'IBI_Anual': 'ibi_anual', 'Seguro_Anual': 'seguro_anual',
        'Gastos_Juridicos': 'gastos_juridicos',
        'Retenciones_IRPF': 'retenciones_irpf',
        'Gastos_Formalizacion': 'gastos_formalizacion',
        'Gastos_Pendientes_Años_Ant': 'gastos_pendientes_anos_ant',
        'Servicios_Suministros': 'servicios_suministros',
        'Direccion': 'direccion',
        'Fecha_Adquisicion': 'fecha_adquisicion',
        'Precio_Compra': 'precio_compra',
        'Impuestos_Compra': 'impuestos_compra',
        'Gastos_Compra': 'gastos_compra',
        'Valor_Catastral': 'valor_catastral',
        'Valor_Catastral_Piso': 'valor_catastral_piso',
        'Pct_Suelo': 'pct_suelo', 'Pct_Construccion': 'pct_construccion',
        'Valor_Real_Construccion': 'valor_real_construccion',
        'Amortizacion_Fiscal': 'amortizacion_fiscal',
        'Seguro_Vida': 'seguro_vida', 'Gasto_Ascensor': 'gasto_ascensor',
        'Ref_Catastral_Cochera': 'ref_catastral_cochera',
        'IBI_Cocheras': 'ibi_cocheras', 'Comunidad_Cocheras': 'comunidad_cocheras',
        'IVA_Aplicable': 'iva_aplicable', 'Tipo_IVA': 'tipo_iva',
        'Retencion_IRPF_Pct': 'retencion_irpf_pct',
        'Dias_Arrendados_Anio': 'dias_arrendados_anio',
        'Imputacion_Rentas': 'imputacion_rentas',
        'Cochera_Incluida_Arrendamiento': 'cochera_incluida_arrendamiento',
        'Inmueble_No_Arrendado': 'inmueble_no_arrendado',
    }

    # Campos INTEGER en Supabase → mandar int, nunca float
    CAMPOS_INTEGER = {
        'ano_reforma', 'ano_construccion', 'm2_construidos', 'habitaciones',
        'planta', 'dias_arrendados_anio',
    }

    # Campos NUMERIC/FLOAT en Supabase → mandar float
    CAMPOS_FLOAT = {
        'renta', 'renta_mercado', 'comunidad', 'valor_construccion',
        'intereses_hipoteca', 'ibi_anual', 'seguro_anual',
        'gastos_juridicos', 'retenciones_irpf', 'gastos_formalizacion',
        'gastos_pendientes_anos_ant', 'servicios_suministros',
        'precio_compra', 'impuestos_compra', 'gastos_compra',
        'valor_catastral', 'valor_catastral_piso', 'pct_suelo', 'pct_construccion',
        'valor_real_construccion', 'amortizacion_fiscal', 'seguro_vida',
        'gasto_ascensor', 'ibi_cocheras', 'comunidad_cocheras',
        'tipo_iva', 'retencion_irpf_pct', 'imputacion_rentas',
    }

    CAMPOS_NUMERICOS_DEFAULT_0 = CAMPOS_INTEGER | CAMPOS_FLOAT

    # Campos texto con valor por defecto obligatorio (NOT NULL en Supabase)
    CAMPOS_TEXTO_DEFAULT = {
        'mobiliario': 'N',
        'parking': 'N',
        'estado': 'Bueno',
        'tipo_arrendamiento': 'Larga Duración',
        'cochera_vinculada': 'N',
        'zona_tensionada': 'N',
        'fecha_inicio_contrato': '2024-01-01',
        'fecha_adquisicion': '2024-01-01',
    }

    # Campos booleanos → DEFAULT False
    CAMPOS_BOOLEANOS_DEFAULT_FALSE = {
        'iva_aplicable', 'cochera_incluida_arrendamiento', 'inmueble_no_arrendado',
    }

    # Campos de texto que SÍ pueden ser NULL (no forzar default)
    # direccion, inquilino, ref_catastral, titular, cp, tipo, nif_inquilino,
    # renta_mercado (puede ser 0 o null), fecha_vencimiento_contrato, ref_catastral_cochera

    def _es_nulo(val):
        if val is None:
            return True
        if isinstance(val, float) and pd.isna(val):
            return True
        if isinstance(val, str) and val.strip() in ('', 'None', 'nan', 'NaN'):
            return True
        return False

    records = []
    for _, row in df2.iterrows():
        rec = {'user_id': user_id}

        # Inicializar todas las columnas con sus defaults correctos
        for col_db in set(MAP_APP_TO_DB.values()):
            if col_db in CAMPOS_INTEGER:
                rec[col_db] = 0          # int
            elif col_db in CAMPOS_FLOAT:
                rec[col_db] = 0.0        # float
            elif col_db in CAMPOS_BOOLEANOS_DEFAULT_FALSE:
                rec[col_db] = False
            elif col_db in CAMPOS_TEXTO_DEFAULT:
                rec[col_db] = CAMPOS_TEXTO_DEFAULT[col_db]
            else:
                rec[col_db] = None       # texto nullable

        # Sobrescribir con el valor real si existe y no es nulo
        for col_app, col_db in MAP_APP_TO_DB.items():
            val = None
            if col_app in row.index:
                val = row[col_app]
            elif col_db in row.index:
                val = row[col_db]

            if _es_nulo(val):
                # Mantener el default ya asignado arriba
                pass
            else:
                # Conversiones de tipo seguras
                if col_db in CAMPOS_NUMERICOS_DEFAULT_0:
                    try:
                        if col_db in CAMPOS_INTEGER:
                            rec[col_db] = int(float(val))   # INTEGER en Supabase
                        else:
                            rec[col_db] = float(val)         # NUMERIC/FLOAT en Supabase
                    except (ValueError, TypeError):
                        rec[col_db] = 0
                elif col_db in CAMPOS_BOOLEANOS_DEFAULT_FALSE:
                    if isinstance(val, bool):
                        rec[col_db] = val
                    else:
                        rec[col_db] = str(val).strip().lower() in ('true', '1', 's', 'si', 'sí', 'yes')
                else:
                    rec[col_db] = str(val).strip() if val is not None else None

        records.append(rec)
    return records


def guardar_inmuebles(df, user_id):
    """Guarda inmuebles usando upsert — nunca borra, solo crea o actualiza."""
    try:
        h = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates,return=minimal'
        }

        if df is None or len(df) == 0:
            return True

        # ── FIX CRÍTICO: asegurar user_id en TODAS las filas ──────
        # Cuando el data_editor añade filas nuevas, user_id llega NaN/None
        df2 = df.copy()
        if 'user_id' in df2.columns:
            mask_vacio = df2['user_id'].isna() | (df2['user_id'].astype(str).str.strip().isin(['', 'None', 'nan']))
            df2.loc[mask_vacio, 'user_id'] = user_id
        # Eliminar filas sin nombre (filas vacías del data_editor)
        if 'Nombre' in df2.columns:
            df2 = df2[df2['Nombre'].notna() & (df2['Nombre'].astype(str).str.strip() != '')]
        elif 'nombre' in df2.columns:
            df2 = df2[df2['nombre'].notna() & (df2['nombre'].astype(str).str.strip() != '')]

        records = _df_inm_to_records(df2, user_id)
        if not records:
            st.error("❌ No se generaron registros para guardar.")
            return False

        # Upsert registro a registro — evita PGRST102 por claves desiguales entre filas
        errores = []
        ok_count = 0
        for rec in records:
            # NUNCA enviar 'id' ni 'created_at' — los genera Supabase
            rec.pop('id', None)
            rec.pop('created_at', None)
            import json as _json
            payload_str = _json.dumps(rec, default=str)
            r = requests.post(
                f"{SUPABASE_URL}/rest/v1/inmuebles?on_conflict=nombre,user_id",
                headers=h,
                json=rec,
                timeout=15
            )
            if r.status_code not in [200, 201, 204]:
                errores.append(
                    f"**{rec.get('nombre','?')}** — HTTP {r.status_code}\n"
                    f"Respuesta: {r.text[:400]}\n"
                    f"Payload enviado: {payload_str[:600]}"
                )
            else:
                ok_count += 1

        if errores:
            # Guardar en session_state para que persistan tras st.rerun()
            st.session_state["_errores_guardar_inm"] = errores
            st.session_state["_ok_guardar_inm"] = ok_count
            return False
        st.session_state.pop("_errores_guardar_inm", None)
        return True
    except Exception as e:
        st.error(f"Error guardando inmuebles: {e}")
        return False


def _limpiar_numericos_inm(df):
    """Limpia columnas numéricas de inmuebles in-place."""
    cols_num = [
        "Renta", "Renta_Mercado", "Comunidad", "Valor_Construccion",
        "Año_Reforma", "Año_Construccion", "M2_Construidos", "Habitaciones",
        "Planta", "Intereses_Hipoteca", "IBI_Anual", "Seguro_Anual",
        "Gastos_Juridicos", "Retenciones_IRPF", "Gastos_Formalizacion",
        "Gastos_Pendientes_Años_Ant", "Servicios_Suministros",
        "Precio_Compra", "Impuestos_Compra", "Gastos_Compra",
        "Valor_Catastral", "Valor_Catastral_Piso", "Pct_Suelo", "Pct_Construccion",
        "Valor_Real_Construccion", "Amortizacion_Fiscal", "Seguro_Vida",
        "Gasto_Ascensor", "IBI_Cocheras", "Comunidad_Cocheras",
        "Tipo_IVA", "Retencion_IRPF_Pct", "Dias_Arrendados_Anio", "Imputacion_Rentas"
    ]
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)


def _inmuebles_iniciales_df(user_id):
    """DataFrame con inmuebles de ejemplo (sin insertar en BD)."""
    rows = [
        {"Nombre":"Casa Abarqueros","Inquilino":"Victor Aguiluz","Renta":2200.0,"Renta_Mercado":2600.0,"Comunidad":193.76,"Valor_Construccion":150000.0,"Año_Reforma":2018,"Año_Construccion":1975,"Mobiliario":"S","Tipo":"Casa","Ref_Catastral":"","Titular":"Pedro Nolasco","M2_Construidos":180,"Habitaciones":5,"CP":"18001","Planta":0,"Parking":"N","Estado":"Reformado","Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N","Zona_Tensionada":"N","Fecha_Inicio_Contrato":"2022-01-01","Fecha_Vencimiento_Contrato":"2027-01-01","NIF_Inquilino":"","Intereses_Hipoteca":0,"IBI_Anual":800,"Seguro_Anual":250,"Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0},
        {"Nombre":"Paseo del Salón","Inquilino":"Pool Despachos","Renta":1591.8,"Renta_Mercado":1650.0,"Comunidad":175.18,"Valor_Construccion":120000.0,"Año_Reforma":2020,"Año_Construccion":1990,"Mobiliario":"N","Tipo":"Piso","Ref_Catastral":"","Titular":"Pedro Nolasco","M2_Construidos":130,"Habitaciones":4,"CP":"18005","Planta":3,"Parking":"S","Estado":"Bueno","Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"S","Zona_Tensionada":"N","Fecha_Inicio_Contrato":"2021-06-01","Fecha_Vencimiento_Contrato":"2026-06-01","NIF_Inquilino":"","Intereses_Hipoteca":0,"IBI_Anual":600,"Seguro_Anual":200,"Gastos_Juridicos":0,"Retenciones_IRPF":286.0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0},
        {"Nombre":"Huerto Unidad 1","Inquilino":"Alain","Renta":660.0,"Renta_Mercado":800.0,"Comunidad":74.62,"Valor_Construccion":45000.0,"Año_Reforma":2022,"Año_Construccion":2005,"Mobiliario":"S","Tipo":"Piso","Ref_Catastral":"","Titular":"Pedro Nolasco","M2_Construidos":60,"Habitaciones":2,"CP":"18008","Planta":1,"Parking":"N","Estado":"Reformado","Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N","Zona_Tensionada":"S","Fecha_Inicio_Contrato":"2023-03-01","Fecha_Vencimiento_Contrato":"2028-03-01","NIF_Inquilino":"","Intereses_Hipoteca":0,"IBI_Anual":300,"Seguro_Anual":150,"Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0},
        {"Nombre":"Huerto Unidad 2","Inquilino":"Laura/Alex","Renta":800.0,"Renta_Mercado":800.0,"Comunidad":74.62,"Valor_Construccion":45000.0,"Año_Reforma":2022,"Año_Construccion":2005,"Mobiliario":"S","Tipo":"Piso","Ref_Catastral":"","Titular":"Pedro Nolasco","M2_Construidos":65,"Habitaciones":2,"CP":"18008","Planta":2,"Parking":"N","Estado":"Reformado","Tipo_Arrendamiento":"Temporada","Cochera_Vinculada":"N","Zona_Tensionada":"S","Fecha_Inicio_Contrato":"2024-09-01","Fecha_Vencimiento_Contrato":"2025-08-31","NIF_Inquilino":"","Intereses_Hipoteca":0,"IBI_Anual":300,"Seguro_Anual":150,"Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0},
        {"Nombre":"Huerto Unidad 3","Inquilino":"Jose Manuel","Renta":850.0,"Renta_Mercado":800.0,"Comunidad":74.63,"Valor_Construccion":45000.0,"Año_Reforma":2021,"Año_Construccion":2005,"Mobiliario":"S","Tipo":"Piso","Ref_Catastral":"","Titular":"Pedro Nolasco","M2_Construidos":68,"Habitaciones":3,"CP":"18008","Planta":3,"Parking":"N","Estado":"Bueno","Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N","Zona_Tensionada":"N","Fecha_Inicio_Contrato":"2022-11-01","Fecha_Vencimiento_Contrato":"2027-11-01","NIF_Inquilino":"","Intereses_Hipoteca":0,"IBI_Anual":300,"Seguro_Anual":150,"Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0},
        {"Nombre":"Huerto Unidad 4","Inquilino":"Pendiente","Renta":600.0,"Renta_Mercado":800.0,"Comunidad":74.62,"Valor_Construccion":45000.0,"Año_Reforma":2024,"Año_Construccion":2005,"Mobiliario":"S","Tipo":"Piso","Ref_Catastral":"","Titular":"Pedro Nolasco","M2_Construidos":62,"Habitaciones":2,"CP":"18008","Planta":4,"Parking":"N","Estado":"Reformado","Tipo_Arrendamiento":"Vacacional","Cochera_Vinculada":"N","Zona_Tensionada":"N","Fecha_Inicio_Contrato":"2025-01-01","Fecha_Vencimiento_Contrato":"2026-12-31","NIF_Inquilino":"","Intereses_Hipoteca":0,"IBI_Anual":300,"Seguro_Anual":150,"Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,"Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0},
    ]
    return pd.DataFrame(rows)


# ─── BACKUP CSV ──────────────────────────────────────────────────

def generar_csv_backup(df, nombre_archivo):
    """Genera CSV en memoria para descarga."""
    return df.to_csv(index=False).encode('utf-8')


# ─── GASTOS RECURRENTES ──────────────────────────────────────────

GASTOS_FIJOS_DEFAULT = [
    {"inmueble": "Casa Abarqueros",  "concepto": "Comunidad",                "categoria": "Comunidad",    "importe": 193.76, "deducible": "S"},
    {"inmueble": "Casa Abarqueros",  "concepto": "Hipoteca (Intereses)",     "categoria": "Financiero",   "importe": 554.73, "deducible": "S"},
    {"inmueble": "Casa Abarqueros",  "concepto": "Seguro MyBox Hogar/Alarma","categoria": "Seguros",      "importe": 96.43,  "deducible": "S"},
    {"inmueble": "Casa Abarqueros",  "concepto": "Seguro Seviam Vida",       "categoria": "Seguros",      "importe": 55.93,  "deducible": "S"},
    {"inmueble": "Casa Abarqueros",  "concepto": "Mantenimiento Ascensor",   "categoria": "Mantenimiento","importe": 65.44,  "deducible": "S"},
    {"inmueble": "Paseo del Salón",  "concepto": "Comunidad",                "categoria": "Comunidad",    "importe": 175.18, "deducible": "S"},
    {"inmueble": "Huerto Unidad 1",  "concepto": "Comunidad (parte)",        "categoria": "Comunidad",    "importe": 74.62,  "deducible": "S"},
    {"inmueble": "Huerto Unidad 2",  "concepto": "Comunidad (parte)",        "categoria": "Comunidad",    "importe": 74.62,  "deducible": "S"},
    {"inmueble": "Huerto Unidad 3",  "concepto": "Comunidad (parte)",        "categoria": "Comunidad",    "importe": 74.63,  "deducible": "S"},
]

BASE_GR = f"{SUPABASE_URL}/rest/v1/gastos_recurrentes"


def leer_gastos_recurrentes(user_id: str) -> pd.DataFrame:
    """Lee gastos recurrentes del usuario. Si no tiene, inserta los defaults."""
    try:
        url = f"{BASE_GR}?user_id=eq.{user_id}&order=inmueble.asc,concepto.asc&select=*"
        r = requests.get(url, headers=_headers(), timeout=10)
        data = r.json() if r.status_code == 200 else []
        if data:
            df = pd.DataFrame(data)
            df["importe"] = pd.to_numeric(df["importe"], errors="coerce").fillna(0)
            return df
        # Primera vez — insertar defaults
        for g in GASTOS_FIJOS_DEFAULT:
            row = {**g, "user_id": user_id, "activo": True}
            requests.post(BASE_GR, json=row, headers=_headers(), timeout=10)
        r2 = requests.get(url, headers=_headers(), timeout=10)
        data2 = r2.json() if r2.status_code == 200 else []
        df = pd.DataFrame(data2) if data2 else pd.DataFrame()
        if not df.empty:
            df["importe"] = pd.to_numeric(df["importe"], errors="coerce").fillna(0)
        return df
    except Exception as e:
        print(f"[leer_gastos_recurrentes] Error: {e}")
        return pd.DataFrame()


def guardar_gasto_recurrente(user_id: str, inmueble: str, concepto: str,
                              categoria: str, importe: float, deducible: str = "S") -> bool:
    """Inserta un nuevo gasto recurrente."""
    try:
        row = {
            "user_id": user_id, "inmueble": inmueble, "concepto": concepto,
            "categoria": categoria, "importe": importe,
            "deducible": deducible, "activo": True
        }
        r = requests.post(BASE_GR, json=row, headers=_headers(), timeout=10)
        return r.status_code in (200, 201)
    except Exception as e:
        print(f"[guardar_gasto_recurrente] Error: {e}")
        return False


def actualizar_gasto_recurrente(id_gasto: int, importe: float = None,
                                 activo: bool = None, concepto: str = None) -> bool:
    """Actualiza importe, concepto o estado activo de un gasto recurrente."""
    try:
        payload = {}
        if importe  is not None: payload["importe"]  = importe
        if activo   is not None: payload["activo"]   = activo
        if concepto is not None: payload["concepto"] = concepto
        if not payload:
            return False
        url = f"{BASE_GR}?id=eq.{id_gasto}"
        r = requests.patch(url, json=payload, headers=_headers(), timeout=10)
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"[actualizar_gasto_recurrente] Error: {e}")
        return False


def eliminar_gasto_recurrente(id_gasto: int) -> bool:
    """Elimina permanentemente un gasto recurrente."""
    try:
        url = f"{BASE_GR}?id=eq.{id_gasto}"
        r = requests.delete(url, headers=_headers(), timeout=10)
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"[eliminar_gasto_recurrente] Error: {e}")
        return False


# ================================================================
# ACCESOS ASESOR — Compartir patrimonio con asesor/inmobiliaria
# ================================================================

def generar_codigo_acceso(propietario_id: str) -> dict:
    """Genera un código de 6 dígitos para compartir patrimonio."""
    import random, string
    try:
        # Obtener email del usuario logueado
        email = st.session_state.get("user_email", "")
        nombre = email.split("@")[0].title() if email else "Propietario"

        # Desactivar código anterior si existe
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/accesos_asesor?propietario_id=eq.{propietario_id}",
            headers={**_headers(), "Prefer": "return=minimal"},
            json={"activo": False}, timeout=8
        )
        # Generar nuevo código único
        codigo = ''.join(random.choices(string.digits, k=6))
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/accesos_asesor",
            headers={**_headers(), "Prefer": "return=representation"},
            json={"propietario_id": propietario_id, "codigo": codigo,
                  "activo": True, "email": email, "nombre": nombre},
            timeout=8
        )
        if r.status_code in (200, 201):
            return {"success": True, "codigo": codigo}
        return {"success": False, "error": f"Error {r.status_code}: {r.text[:100]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def obtener_codigo_activo(propietario_id: str) -> str | None:
    """Devuelve el código activo del propietario o None."""
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/accesos_asesor?propietario_id=eq.{propietario_id}&activo=eq.true&select=codigo",
            headers=_headers(), timeout=8
        )
        data = r.json()
        return data[0]["codigo"] if data else None
    except:
        return None


def revocar_codigo_acceso(propietario_id: str) -> bool:
    """Revoca el código activo del propietario."""
    try:
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/accesos_asesor?propietario_id=eq.{propietario_id}",
            headers={**_headers(), "Prefer": "return=minimal"},
            json={"activo": False}, timeout=8
        )
        return r.status_code in (200, 204)
    except:
        return False


def buscar_propietario_por_codigo(codigo: str) -> dict | None:
    """Busca el propietario asociado a un código de acceso activo."""
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/accesos_asesor?codigo=eq.{codigo}&activo=eq.true&select=propietario_id",
            headers=_headers(), timeout=8
        )
        data = r.json()
        if not data:
            return None
        propietario_id = data[0]["propietario_id"]
        # Leer datos del propietario
        inmuebles = leer_inmuebles(user_id=propietario_id)
        movimientos = leer_movimientos(user_id=propietario_id)
        # Obtener nombre del propietario desde tabla usuarios
        ru = requests.get(
            f"{SUPABASE_URL}/rest/v1/usuarios?user_id=eq.{propietario_id}&select=nombre,email",
            headers=_headers(), timeout=8
        )
        usuario = ru.json()
        nombre = usuario[0].get("nombre", "Propietario") if usuario else "Propietario"
        email  = usuario[0].get("email", "") if usuario else ""
        return {
            "propietario_id": propietario_id,
            "nombre": nombre,
            "email": email,
            "inmuebles": inmuebles,
            "movimientos": movimientos
        }
    except Exception as e:
        return None


def upsert_inmueble(registro: dict, user_id: str) -> dict:
    """
    Inserta o actualiza UN inmueble sin tocar los demás.
    Usa upsert nativo de Supabase (POST con Prefer: resolution=merge-duplicates).
    Requiere restricción UNIQUE (nombre, user_id) en la tabla.
    """
    try:
        nombre = registro.get("Nombre") or registro.get("nombre", "")
        if not nombre:
            return {"ok": False, "error": "Registro sin nombre"}

        # Convertir claves a formato base de datos
        # Mapa completo App→DB — cubre TODOS los campos para evitar fallback k.lower()
        # que convierte Año_Reforma → año_reforma (ñ inválida en PostgreSQL)
        MAP_APP_TO_DB = {
            'Nombre': 'nombre', 'Direccion': 'direccion',
            'Inquilino': 'inquilino', 'Renta': 'renta',
            'Renta_Mercado': 'renta_mercado', 'Comunidad': 'comunidad',
            'Valor_Construccion': 'valor_construccion',
            'Año_Reforma': 'ano_reforma', 'Año_Construccion': 'ano_construccion',
            'Mobiliario': 'mobiliario', 'Tipo': 'tipo',
            'Ref_Catastral': 'ref_catastral', 'Titular': 'titular',
            'M2_Construidos': 'm2_construidos', 'Habitaciones': 'habitaciones',
            'CP': 'cp', 'Planta': 'planta', 'Parking': 'parking', 'Estado': 'estado',
            'Tipo_Arrendamiento': 'tipo_arrendamiento',
            'Cochera_Vinculada': 'cochera_vinculada',
            'Zona_Tensionada': 'zona_tensionada',
            'Fecha_Inicio_Contrato': 'fecha_inicio_contrato',
            'Fecha_Vencimiento_Contrato': 'fecha_vencimiento_contrato',
            'NIF_Inquilino': 'nif_inquilino',
            'Intereses_Hipoteca': 'intereses_hipoteca',
            'IBI_Anual': 'ibi_anual', 'Seguro_Anual': 'seguro_anual',
            'Gastos_Juridicos': 'gastos_juridicos',
            'Retenciones_IRPF': 'retenciones_irpf',
            'Gastos_Formalizacion': 'gastos_formalizacion',
            'Gastos_Pendientes_Años_Ant': 'gastos_pendientes_anos_ant',
            'Servicios_Suministros': 'servicios_suministros',
            'Fecha_Adquisicion': 'fecha_adquisicion',
            'Precio_Compra': 'precio_compra',
            'Impuestos_Compra': 'impuestos_compra',
            'Gastos_Compra': 'gastos_compra',
            'Valor_Catastral': 'valor_catastral',
            'Valor_Catastral_Piso': 'valor_catastral_piso',
            'Pct_Suelo': 'pct_suelo', 'Pct_Construccion': 'pct_construccion',
            'Valor_Real_Construccion': 'valor_real_construccion',
            'Amortizacion_Fiscal': 'amortizacion_fiscal',
            'Seguro_Vida': 'seguro_vida', 'Gasto_Ascensor': 'gasto_ascensor',
            'Ref_Catastral_Cochera': 'ref_catastral_cochera',
            'IBI_Cocheras': 'ibi_cocheras', 'Comunidad_Cocheras': 'comunidad_cocheras',
            'IVA_Aplicable': 'iva_aplicable', 'Tipo_IVA': 'tipo_iva',
            'Retencion_IRPF_Pct': 'retencion_irpf_pct',
            'Dias_Arrendados_Anio': 'dias_arrendados_anio',
            'Imputacion_Rentas': 'imputacion_rentas',
        }

        # Columnas INTEGER en Supabase — enviar como int, no float
        COLS_INT_DB = {
            'ano_reforma', 'ano_construccion', 'habitaciones', 'planta',
            'dias_arrendados_anio'
        }
        rec_db = {}
        for k, v in registro.items():
            k_db = MAP_APP_TO_DB.get(k)
            if k_db is None:
                continue  # clave no reconocida — ignorar
            if v is not None and str(v) not in ("nan", "None", ""):
                try:
                    if k_db in COLS_INT_DB:
                        rec_db[k_db] = int(float(v))  # 2000.0 → 2000
                    elif isinstance(v, bool):
                        rec_db[k_db] = v  # booleanos primero (bool es subclase de int)
                    elif isinstance(v, (int, float)):
                        rec_db[k_db] = float(v)
                    else:
                        rec_db[k_db] = v
                except:
                    rec_db[k_db] = v
        rec_db["user_id"] = user_id
        rec_db["nombre"]  = nombre

        h_base = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {st.session_state.get('access_token', SUPABASE_KEY)}",
            "Content-Type": "application/json",
        }
        nombre_encoded = requests.utils.quote(nombre, safe='')

        # 1. Intentar PATCH — actualiza si ya existe (no necesita restricción UNIQUE)
        r_patch = requests.patch(
            f"{SUPABASE_URL}/rest/v1/inmuebles?nombre=eq.{nombre_encoded}&user_id=eq.{user_id}",
            headers={**h_base, "Prefer": "return=minimal"},
            json=rec_db,
            timeout=10
        )
        if r_patch.status_code in (200, 204):
            return {"ok": True, "accion": "actualizado"}

        # 2. Si el PATCH no encontró filas (204 sin efecto) o falla, hacer POST (insertar nuevo)
        # Verificar si realmente existe antes de insertar
        r_check = requests.get(
            f"{SUPABASE_URL}/rest/v1/inmuebles?nombre=eq.{nombre_encoded}&user_id=eq.{user_id}&select=id",
            headers=h_base,
            timeout=10
        )
        existe = r_check.status_code == 200 and len(r_check.json()) > 0

        if existe:
            # Ya existe pero el PATCH falló — devolver el error del PATCH
            return {"ok": False, "error": f"PATCH {r_patch.status_code}: {r_patch.text[:300]}"}

        # No existe → INSERT
        r_post = requests.post(
            f"{SUPABASE_URL}/rest/v1/inmuebles",
            headers={**h_base, "Prefer": "return=minimal"},
            json=rec_db,
            timeout=10
        )
        if r_post.status_code in (200, 201, 204):
            return {"ok": True, "accion": "creado"}
        return {"ok": False, "error": f"POST {r_post.status_code}: {r_post.text[:300]}"}

    except Exception as e:
        return {"ok": False, "error": str(e)}
