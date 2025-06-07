from conexion import get_supabase_client

try:
    supabase = get_supabase_client()
    # Si llega aquí, el cliente se creó correctamente
    print("✅ Cliente Supabase creado correctamente")
except Exception as e:
    print("❌ Error en la creación del cliente Supabase:", e)
