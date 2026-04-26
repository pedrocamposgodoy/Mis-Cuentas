"""
supabase_db.py — Módulo de Base de Datos Supabase para Nolasco Capital
Reemplaza todas las operaciones CSV por llamadas a Supabase REST API.
"""
import requests
import pandas as pd
import json
import streamlit as st

# ─── CREDENCIALES ───────────────────────────────────────────────
# IMPORTANTE: Reemplaza con tus credenciales reales de Supabase
SUPABASE_URL = "https://odxixtgqcyddfqaapqgi.supabase.co"         # ← CAMBIA ESTO
SUPABASE_KEY = "sb_publishable_Obgti7yMfXw8wCUL2FbTtA_EWeyHuM9"   # ← CAMBIA ESTO

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ─── COLUMNAS ESPERADAS ─────────────────────────────────────────
COLS_INM = [
    "Nombre","Inquilino","Renta","Renta_Mercado","Comunidad","Valor_Construccion",
    "Año_Reforma","Año_Construccion","Mobiliario","Tipo","Ref_Catastral","Titular",
    "M2_Construidos","Habitaciones","CP","Planta","Parking","Estado",
    "Tipo_Arrendamiento","Cochera_Vinculada","Zona_Tensionada",
    "Fecha_Inicio_Contrato","Fecha_Vencimiento_Contrato",
    "NIF_Inquilino","Intereses_Hipoteca","IBI_Anual","Seguro_Anual",
    "Gastos_Juridicos","Retenciones_IRPF","Gastos_Formalizacion",
    "Gastos_Pendientes_Años_Ant","Servicios_Suministros"
]

COLS_MOV = ["Fecha","Apartamento","Concepto","Categoría","Tipo","Importe","Deducible"]

DEFAULTS_FISCAL = {
    "Tipo_Arrendamiento":"Larga Duración","Cochera_Vinculada":"N","Zona_Tensionada":"N",
    "Fecha_Inicio_Contrato":"2022-01-01","Fecha_Vencimiento_Contrato":"2027-01-01",
    "NIF_Inquilino":"","Intereses_Hipoteca":0,"IBI_Anual":0,"Seguro_Anual":0,
    "Gastos_Juridicos":0,"Retenciones_IRPF":0,"Gastos_Formalizacion":0,
    "Gastos_Pendientes_Años_Ant":0,"Servicios_Suministros":0
}

# ─── FUNCIONES DE AUTENTICACIÓN ──────────────────────────────

def login_usuario(email, password):
    """Autentica usuario con email y contraseña."""
    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={'apikey': SUPABASE_KEY, 'Content-Type': 'application/json'},
            json={'email': email, 'password': password}
        )
        if r.status_code == 200:
            data = r.json()
            return {
                'success': True,
                'user_id': data['user']['id'],
                'email': data['user']['email'],
                'access_token': data['access_token']
            }
        else:
            return {'success': False, 'error': 'Email o contraseña incorrectos'}
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
        if r.status_code == 200:
            data = r.json()
            return {
                'success': True,
                'user_id': data['user']['id'],
                'email': data['user']['email']
            }
        else:
            return {'success': False, 'error': 'Error al registrar usuario'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ─── FUNCIONES DE LECTURA ────────────────────────────────────────

def leer_inmuebles(user_id=None):
    """Lee todos los inmuebles de Supabase y devuelve DataFrame."""
    try:
        # Filtrar por user_id si se proporciona
        url = f"{SUPABASE_URL}/rest/v1/inmuebles?select=*"
        if user_id:
            url += f"&user_id=eq.{user_id}"
        
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            data = r.json()
            if data:
                df = pd.DataFrame(data)
                # Renombrar columnas de Supabase a las que usa la app
                rename_map = {
                    'nombre': 'Nombre', 'inquilino': 'Inquilino', 'renta': 'Renta',
                    'renta_mercado': 'Renta_Mercado', 'comunidad': 'Comunidad',
                    'valor_construccion': 'Valor_Construccion', 'ano_reforma': 'Año_Reforma',
                    'ano_construccion': 'Año_Construccion', 'mobiliario': 'Mobiliario',
                    'tipo': 'Tipo', 'ref_catastral': 'Ref_Catastral', 'titular': 'Titular',
                    'm2_construidos': 'M2_Construidos', 'habitaciones': 'Habitaciones',
                    'cp': 'CP', 'planta': 'Planta', 'parking': 'Parking', 'estado': 'Estado',
                    'tipo_arrendamiento': 'Tipo_Arrendamiento',
                    'cochera_vinculada': 'Cochera_Vinculada',
                    'zona_tensionada': 'Zona_Tensionada',
                    'fecha_inicio_contrato': 'Fecha_Inicio_Contrato',
                    'fecha_vencimiento_contrato': 'Fecha_Vencimiento_Contrato',
                    'nif_inquilino': 'NIF_Inquilino',
                    'intereses_hipoteca': 'Intereses_Hipoteca',
                    'ibi_anual': 'IBI_Anual', 'seguro_anual': 'Seguro_Anual',
                    'gastos_juridicos': 'Gastos_Juridicos',
                    'retenciones_irpf': 'Retenciones_IRPF',
                    'gastos_formalizacion': 'Gastos_Formalizacion',
                    'gastos_pendientes_anos_ant': 'Gastos_Pendientes_Años_Ant',
                    'servicios_suministros': 'Servicios_Suministros',
                    'direccion': 'Direccion'
                }
                df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
                # Asegurar que todas las columnas esperadas existan
                for col in COLS_INM:
                    if col not in df.columns:
                        df[col] = DEFAULTS_FISCAL.get(col, "")
                # Limpiar campos numéricos — nunca None
                cols_numericas = [
                    "Renta","Renta_Mercado","Comunidad","Valor_Construccion",
                    "Año_Reforma","Año_Construccion","M2_Construidos","Habitaciones",
                    "Planta","Intereses_Hipoteca","IBI_Anual","Seguro_Anual",
                    "Gastos_Juridicos","Retenciones_IRPF","Gastos_Formalizacion",
                    "Gastos_Pendientes_Años_Ant","Servicios_Suministros"
                ]
                for col in cols_numericas:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                # Limpiar campos texto — nunca None
                cols_texto = [
                    "Nombre","Inquilino","Tipo","Estado","Mobiliario","Parking",
                    "Ref_Catastral","Titular","CP","Planta","Titular",
                    "Tipo_Arrendamiento","Cochera_Vinculada","Zona_Tensionada",
                    "Fecha_Inicio_Contrato","Fecha_Vencimiento_Contrato","NIF_Inquilino"
                ]
                for col in cols_texto:
                    if col in df.columns:
                        df[col] = df[col].fillna("")
                return df
            else:
                # Si no hay inmuebles para este usuario, devolver DataFrame vacío
                return pd.DataFrame(columns=COLS_INM)
        else:
            st.error(f"Error Supabase inmuebles: {r.status_code}")
            return pd.DataFrame(columns=COLS_INM)
    except Exception as e:
        st.error(f"Error conexión Supabase: {e}")
        return pd.DataFrame(columns=COLS_INM)


def leer_movimientos(user_id=None):
    """Lee todos los movimientos de Supabase y devuelve DataFrame."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/movimientos?select=*"
        if user_id:
            url += f"&user_id=eq.{user_id}"
        
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            data = r.json()
            if data:
                df = pd.DataFrame(data)
                rename_map = {
                    'fecha': 'Fecha', 'apartamento': 'Apartamento',
                    'concepto': 'Concepto', 'categoria': 'Categoría',
                    'tipo': 'Tipo', 'importe': 'Importe', 'deducible': 'Deducible'
                }
                df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
                for col in COLS_MOV:
                    if col not in df.columns:
                        df[col] = ""
                return df
            else:
                return _crear_movimientos_iniciales()
        else:
            st.error(f"Error Supabase movimientos: {r.status_code}")
            return pd.DataFrame(columns=COLS_MOV)
    except Exception as e:
        st.error(f"Error conexión Supabase: {e}")
        return pd.DataFrame(columns=COLS_MOV)


# ─── FUNCIONES DE ESCRITURA ──────────────────────────────────────

def guardar_inmuebles(df, user_id=None):
    """Guarda inmuebles en Supabase uno a uno."""
    rename_map = {
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
    }
    try:
        df_sb = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
        cols_validas = [c for c in df_sb.columns if c in rename_map.values()]
        df_sb = df_sb[cols_validas]
        df_sb = df_sb.where(pd.notna(df_sb), None)
        records = df_sb.to_dict(orient='records')

        # Añadir user_id a cada record
        if user_id:
            for record in records:
                record['user_id'] = user_id

        # Obtener IDs existentes por nombre (solo del user actual)
        url = f"{SUPABASE_URL}/rest/v1/inmuebles?select=id,nombre"
        if user_id:
            url += f"&user_id=eq.{user_id}"
        r_all = requests.get(url, headers=HEADERS)
        existentes = {}
        if r_all.status_code == 200:
            for item in r_all.json():
                if item.get('nombre'):
                    existentes[item['nombre']] = item['id']

        h_patch = {**HEADERS, 'Prefer': 'return=minimal'}
        h_insert = {**HEADERS, 'Prefer': 'return=minimal'}

        for record in records:
            nombre = record.get('nombre', '')
            if not nombre:
                continue
            if nombre in existentes:
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/inmuebles?id=eq.{existentes[nombre]}",
                    headers=h_patch,
                    json=record
                )
            else:
                requests.post(
                    f"{SUPABASE_URL}/rest/v1/inmuebles",
                    headers=h_insert,
                    json=record
                )
        return True
    except Exception as e:
        st.error(f"Error guardando inmueble: {e}")
        return False


def eliminar_inmueble(nombre):
    """Elimina un inmueble de Supabase por nombre."""
    try:
        # Buscar el inmueble por nombre
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/inmuebles?nombre=eq.{nombre}&select=id",
            headers=HEADERS
        )
        if r.status_code == 200:
            results = r.json()
            if results:
                inm_id = results[0]['id']
                # Eliminar por ID
                requests.delete(
                    f"{SUPABASE_URL}/rest/v1/inmuebles?id=eq.{inm_id}",
                    headers={**HEADERS, 'Prefer': 'return=minimal'}
                )
                return True
        return False
    except Exception as e:
        st.error(f"Error eliminando inmueble: {e}")
        return False


def guardar_movimientos_completo(df):
    """Guarda DataFrame de movimientos COMPLETO en Supabase (borra y reinserta)."""
    try:
        requests.delete(
            f"{SUPABASE_URL}/rest/v1/movimientos?id=gt.0",
            headers=HEADERS
        )
        rename_map = {
            'Fecha': 'fecha', 'Apartamento': 'apartamento',
            'Concepto': 'concepto', 'Categoría': 'categoria',
            'Tipo': 'tipo', 'Importe': 'importe', 'Deducible': 'deducible'
        }
        df_sb = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
        cols_validas = [c for c in df_sb.columns if c in rename_map.values()]
        df_sb = df_sb[cols_validas]
        df_sb = df_sb.where(pd.notna(df_sb), None)
        records = df_sb.to_dict(orient='records')
        if records:
            r = requests.post(
                f"{SUPABASE_URL}/rest/v1/movimientos",
                headers=HEADERS,
                json=records
            )
            return r.status_code in [200, 201]
        return True
    except Exception as e:
        st.error(f"Error guardando movimientos: {e}")
        return False


def agregar_movimientos(nuevos):
    """Agrega nuevos movimientos (lista de dicts) sin borrar los existentes."""
    try:
        rename_map = {
            'Fecha': 'fecha', 'Apartamento': 'apartamento',
            'Concepto': 'concepto', 'Categoría': 'categoria',
            'Tipo': 'tipo', 'Importe': 'importe', 'Deducible': 'deducible'
        }
        records = []
        for mov in nuevos:
            record = {}
            for k, v in mov.items():
                key = rename_map.get(k, k.lower())
                record[key] = v
            records.append(record)
        if records:
            r = requests.post(
                f"{SUPABASE_URL}/rest/v1/movimientos",
                headers=HEADERS,
                json=records
            )
            return r.status_code in [200, 201]
        return True
    except Exception as e:
        st.error(f"Error agregando movimientos: {e}")
        return False


# ─── DATOS INICIALES ─────────────────────────────────────────────

def _crear_inmuebles_iniciales():
    """Crea los 6 inmuebles de Pedro si la tabla está vacía."""
    rows = [
        {"nombre":"Casa Abarqueros","inquilino":"Victor Aguiluz","renta":2200.0,"renta_mercado":2600.0,"comunidad":193.76,"valor_construccion":150000.0,"ano_reforma":2018,"ano_construccion":1975,"mobiliario":"S","tipo":"Casa","ref_catastral":"00XX0001","titular":"Pedro Nolasco","m2_construidos":180,"habitaciones":5,"cp":"18001","planta":0,"parking":"N","estado":"Reformado","tipo_arrendamiento":"Larga Duración","cochera_vinculada":"N","zona_tensionada":"N","fecha_inicio_contrato":"2022-01-01","fecha_vencimiento_contrato":"2027-01-01","nif_inquilino":"12345678A","intereses_hipoteca":0,"ibi_anual":800,"seguro_anual":250,"gastos_juridicos":0,"retenciones_irpf":0,"gastos_formalizacion":0,"gastos_pendientes_anos_ant":0,"servicios_suministros":0},
        {"nombre":"Paseo del Salón","inquilino":"Pool Despachos","renta":1591.8,"renta_mercado":1650.0,"comunidad":175.18,"valor_construccion":120000.0,"ano_reforma":2020,"ano_construccion":1990,"mobiliario":"N","tipo":"Piso","ref_catastral":"00XX0002","titular":"Pedro Nolasco","m2_construidos":130,"habitaciones":4,"cp":"18005","planta":3,"parking":"S","estado":"Bueno","tipo_arrendamiento":"Larga Duración","cochera_vinculada":"S","zona_tensionada":"N","fecha_inicio_contrato":"2021-06-01","fecha_vencimiento_contrato":"2026-06-01","nif_inquilino":"B87654321","intereses_hipoteca":0,"ibi_anual":600,"seguro_anual":200,"gastos_juridicos":0,"retenciones_irpf":286.0,"gastos_formalizacion":0,"gastos_pendientes_anos_ant":0,"servicios_suministros":0},
        {"nombre":"Huerto Unidad 1","inquilino":"Alain","renta":660.0,"renta_mercado":800.0,"comunidad":74.62,"valor_construccion":45000.0,"ano_reforma":2022,"ano_construccion":2005,"mobiliario":"S","tipo":"Piso","ref_catastral":"00XX0003","titular":"Pedro Nolasco","m2_construidos":60,"habitaciones":2,"cp":"18008","planta":1,"parking":"N","estado":"Reformado","tipo_arrendamiento":"Larga Duración","cochera_vinculada":"N","zona_tensionada":"S","fecha_inicio_contrato":"2023-03-01","fecha_vencimiento_contrato":"2028-03-01","nif_inquilino":"87654321B","intereses_hipoteca":0,"ibi_anual":300,"seguro_anual":150,"gastos_juridicos":0,"retenciones_irpf":0,"gastos_formalizacion":0,"gastos_pendientes_anos_ant":0,"servicios_suministros":0},
        {"nombre":"Huerto Unidad 2","inquilino":"Laura/Alex","renta":800.0,"renta_mercado":800.0,"comunidad":74.62,"valor_construccion":45000.0,"ano_reforma":2022,"ano_construccion":2005,"mobiliario":"S","tipo":"Piso","ref_catastral":"00XX0004","titular":"Pedro Nolasco","m2_construidos":65,"habitaciones":2,"cp":"18008","planta":2,"parking":"N","estado":"Reformado","tipo_arrendamiento":"Temporada","cochera_vinculada":"N","zona_tensionada":"S","fecha_inicio_contrato":"2024-09-01","fecha_vencimiento_contrato":"2025-08-31","nif_inquilino":"23456789C","intereses_hipoteca":0,"ibi_anual":300,"seguro_anual":150,"gastos_juridicos":0,"retenciones_irpf":0,"gastos_formalizacion":0,"gastos_pendientes_anos_ant":0,"servicios_suministros":0},
        {"nombre":"Huerto Unidad 3","inquilino":"Jose Manuel","renta":850.0,"renta_mercado":800.0,"comunidad":74.63,"valor_construccion":45000.0,"ano_reforma":2021,"ano_construccion":2005,"mobiliario":"S","tipo":"Piso","ref_catastral":"00XX0005","titular":"Pedro Nolasco","m2_construidos":68,"habitaciones":3,"cp":"18008","planta":3,"parking":"N","estado":"Bueno","tipo_arrendamiento":"Larga Duración","cochera_vinculada":"N","zona_tensionada":"N","fecha_inicio_contrato":"2022-11-01","fecha_vencimiento_contrato":"2027-11-01","nif_inquilino":"34567890D","intereses_hipoteca":0,"ibi_anual":300,"seguro_anual":150,"gastos_juridicos":0,"retenciones_irpf":0,"gastos_formalizacion":0,"gastos_pendientes_anos_ant":0,"servicios_suministros":0},
        {"nombre":"Huerto Unidad 4","inquilino":"Pendiente","renta":600.0,"renta_mercado":800.0,"comunidad":74.62,"valor_construccion":45000.0,"ano_reforma":2024,"ano_construccion":2005,"mobiliario":"S","tipo":"Piso","ref_catastral":"00XX0006","titular":"Pedro Nolasco","m2_construidos":62,"habitaciones":2,"cp":"18008","planta":4,"parking":"N","estado":"Reformado","tipo_arrendamiento":"Vacacional","cochera_vinculada":"N","zona_tensionada":"N","fecha_inicio_contrato":"2025-01-01","fecha_vencimiento_contrato":"2026-12-31","nif_inquilino":"","intereses_hipoteca":0,"ibi_anual":300,"seguro_anual":150,"gastos_juridicos":0,"retenciones_irpf":0,"gastos_formalizacion":0,"gastos_pendientes_anos_ant":0,"servicios_suministros":0},
    ]
    # Insertar en Supabase
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/inmuebles",
            headers=HEADERS,
            json=rows
        )
    except:
        pass
    # Devolver como DataFrame con nombres de columna de la app
    df = pd.DataFrame(rows)
    rename_map = {
        'nombre': 'Nombre', 'inquilino': 'Inquilino', 'renta': 'Renta',
        'renta_mercado': 'Renta_Mercado', 'comunidad': 'Comunidad',
        'valor_construccion': 'Valor_Construccion', 'ano_reforma': 'Año_Reforma',
        'ano_construccion': 'Año_Construccion', 'mobiliario': 'Mobiliario',
        'tipo': 'Tipo', 'ref_catastral': 'Ref_Catastral', 'titular': 'Titular',
        'm2_construidos': 'M2_Construidos', 'habitaciones': 'Habitaciones',
        'cp': 'CP', 'planta': 'Planta', 'parking': 'Parking', 'estado': 'Estado',
        'tipo_arrendamiento': 'Tipo_Arrendamiento',
        'cochera_vinculada': 'Cochera_Vinculada',
        'zona_tensionada': 'Zona_Tensionada',
        'fecha_inicio_contrato': 'Fecha_Inicio_Contrato',
        'fecha_vencimiento_contrato': 'Fecha_Vencimiento_Contrato',
        'nif_inquilino': 'NIF_Inquilino',
        'intereses_hipoteca': 'Intereses_Hipoteca',
        'ibi_anual': 'IBI_Anual', 'seguro_anual': 'Seguro_Anual',
        'gastos_juridicos': 'Gastos_Juridicos',
        'retenciones_irpf': 'Retenciones_IRPF',
        'gastos_formalizacion': 'Gastos_Formalizacion',
        'gastos_pendientes_anos_ant': 'Gastos_Pendientes_Años_Ant',
        'servicios_suministros': 'Servicios_Suministros'
    }
    df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
    return df


def _crear_movimientos_iniciales():
    """Crea movimientos de ejemplo si la tabla está vacía."""
    rows = [
        {"fecha":"2026-04-01","apartamento":"Casa Abarqueros","concepto":"Renta Mensual","categoria":"Ingresos","tipo":"Ingreso","importe":2200.00,"deducible":"N"},
        {"fecha":"2026-04-01","apartamento":"Casa Abarqueros","concepto":"Comunidad","categoria":"Comunidad","tipo":"Gasto","importe":193.76,"deducible":"S"},
    ]
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/movimientos",
            headers=HEADERS,
            json=rows
        )
    except:
        pass
    df = pd.DataFrame(rows)
    rename_map = {
        'fecha': 'Fecha', 'apartamento': 'Apartamento',
        'concepto': 'Concepto', 'categoria': 'Categoría',
        'tipo': 'Tipo', 'importe': 'Importe', 'deducible': 'Deducible'
    }
    df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
    return df


# ─── FUNCIÓN DE BACKUP (CSV DESCARGABLE) ────────────────────────

def generar_csv_backup(df, nombre_archivo):
    """Genera un CSV en memoria para descarga (backup)."""
    return df.to_csv(index=False).encode('utf-8')
