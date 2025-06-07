from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv()

# Obtener variables de entorno
SUPABASE_URL = f"https://{os.getenv('SUPABASE_HOST')}"
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

# Crear cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client():
    return supabase
