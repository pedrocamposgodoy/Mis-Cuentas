mport requests
import json

# TUS CREDENCIALES
SUPABASE_URL = "https://odxixtgqcyddfqaapqgi.supabase.co"  # REEMPLAZA
SUPABASE_KEY = "sb_publishable_Obgti7yMfXw8wCUL2FbTtA_EWeyHuM9"        # REEMPLAZA

def fetch_inmuebles():
    """Traer inmuebles de Supabase"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/inmuebles?select=*",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception: {e}")
        return []

# TEST
if __name__ == "__main__":
    resultado = fetch_inmuebles()
    print(f"\n✅ Inmuebles encontrados: {len(resultado)}")
    if resultado:
        print(f"Primer inmueble: {resultado[0]}")
