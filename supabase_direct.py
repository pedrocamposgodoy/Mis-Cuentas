import requests

# TUS CREDENCIALES (de supabase_keys.txt)
SUPABASE_URL = "https://odxixtgqcyddfqaapqgi.supabase.co"
SUPABASE_KEY = "sb_publishable_Obgti7yMfXw8wCUL2FbTtA_EWeyHuM9"

def fetch_inmuebles():
    """Traer inmuebles de Supabase"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}'
    }
    
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/inmuebles",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

# TEST
if __name__ == "__main__":
    resultado = fetch_inmuebles()
    print(f"✅ Conexión OK - Inmuebles encontrados: {len(resultado)}")
