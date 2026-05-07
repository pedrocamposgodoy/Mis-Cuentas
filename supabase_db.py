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
    "Nombre","Inquilino","Renta","Renta_Mercado","Comunidad","Valor_Construccion",
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
    "IVA_Aplicable","Tipo_IVA","Retencion_IRPF_Pct","Dias_Arrendados_Anio"
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
    "IVA_Aplicable":False,"Tipo_IVA":21,"Retencion_IRPF_Pct":0,"Dias_Arrendados_Anio":365
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
    'retencion_irpf_pct': 'Retencion_IRPF_Pct', 'dias_arrendados_anio': 'Dias_Arrendados_Anio'
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


def guardar_inmuebles(df, user_id):
    """Borra inmuebles del usuario y los reinserta."""
    try:
        h = _headers()

        # 1. Borrar
        requests.delete(
            f"{SUPABASE_URL}/rest/v1/inmuebles?user_id=eq.{user_id}",
            headers=h
        )

        if df is None or len(df) == 0:
            return True

        # 2. Preparar registros
        records = _df_inm_to_records(df, user_id)
        if not records:
            return True

        # 3. Insertar
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/inmuebles",
            headers=h,
            json=records
        )
        if r.status_code not in [200, 201]:
            st.error(f"❌ Error insertando inmuebles: {r.status_code} — {r.text[:300]}")
            return False
        return True
    except Exception as e:
        st.error(f"Error guardando inmuebles: {e}")
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
    """Convierte DataFrame de inmuebles a lista de dicts para Supabase."""
    df2 = df.copy()
    df2 = df2.rename(columns={k: v for k, v in RENAME_INM_TO_DB.items() if k in df2.columns})
    cols_db = [v for v in RENAME_INM_TO_DB.values()]
    cols_presentes = [c for c in cols_db if c in df2.columns]
    df2 = df2[cols_presentes]
    df2 = df2.where(pd.notna(df2), None)
    records = df2.to_dict(orient='records')
    for r in records:
        r['user_id'] = user_id
    return records


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
        "Tipo_IVA", "Retencion_IRPF_Pct", "Dias_Arrendados_Anio"
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
            json={"propietario_id": propietario_id, "codigo": codigo, "activo": True},
            timeout=8
        )
        if r.status_code in (200, 201):
            return {"success": True, "codigo": codigo}
        return {"success": False, "error": f"Error {r.status_code}"}
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
