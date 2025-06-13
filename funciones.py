from conexion import get_supabase_client


# Función para obtener todas las canchas con sus tipos y horarios
def obtener_canchas_disponibles():
    """
    Obtiene todas las canchas de la base de datos con sus tipos y horarios
    """
    supabase = get_supabase_client()
    
    try:
        # Consulta SQL para obtener todas las canchas con sus relaciones
        query = supabase.table("canchas").select(
            "id, nombre, disponible, tipos_cancha(nombre), horarios_disponibles(dia_semana, hora_inicio, hora_fin)"
        ).execute()
        
        if not query.data:
            return {"success": False, "message": "No hay canchas registradas en el sistema."}
        
        # Procesar los datos para limpiar el formato
        canchas_procesadas = []
        for cancha in query.data:
            # Extraer el nombre del tipo de cancha del objeto anidado
            tipo_cancha = cancha['tipos_cancha']['nombre'] if cancha['tipos_cancha'] else "Sin tipo"
            
            # Transformar el booleano en emoji
            disponible = "✅" if cancha['disponible'] else "❌"
            
            # Crear nuevo diccionario con datos procesados
            cancha_limpia = {
                'id': cancha['id'],
                'nombre': cancha['nombre'],
                'disponible': disponible,
                'tipos_cancha': tipo_cancha,
                'horarios_disponibles': procesar_horarios(cancha['horarios_disponibles'])

            }
            canchas_procesadas.append(cancha_limpia)
            
        # Devolver los datos procesados
        return {"success": True, "data": canchas_procesadas}
    
    except Exception as e:
        return {"success": False, "message": f"Error al obtener las canchas: {str(e)}"}

def procesar_horarios(horarios):
    """Helper function to process schedule data"""
    if not horarios:
        return "Sin horarios"
    
    # Procesar los horarios según tu necesidad
    # Por ejemplo, convertirlos a un formato más legible
    return ", ".join([f"{h['dia_semana']}: {h['hora_inicio']}-{h['hora_fin']}" for h in horarios])

def crear_cancha(nombre: str, tipo_id: int):
    """Crea una nueva cancha"""
    try:
        supabase = get_supabase_client()
        data = {
            "nombre": nombre,
            "id_tipo": tipo_id,  # Asegúrate que este nombre coincida con tu esquema
            "disponible": True
        }
        result = supabase.table("canchas").insert(data).execute()
        return {"success": True, "data": result.data[0]} if result.data else {"success": False, "message": "Error al crear"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def actualizar_disponibilidad(cancha_id: int, disponible: bool):
    """
    UPDATE canchas SET disponible = :disponible WHERE id = :cancha_id
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("canchas")\
            .update({"disponible": disponible})\
            .eq("id", cancha_id)\
            .execute()
        return {"success": True, "data": result.data[0]}
    except Exception as e:
        return {"success": False, "message": str(e)}

def actualizar_cancha(cancha_id: int, datos: dict):
    """
    Actualiza una cancha existente.
    
    Args:
        cancha_id (int): ID de la cancha a actualizar
        datos (dict): Diccionario con los campos a actualizar
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("canchas")\
            .update(datos)\
            .eq("id", cancha_id)\
            .execute()
            
        if not result.data:
            return {"success": False, "message": "Error al actualizar la cancha"}
            
        return {"success": True, "data": result.data[0]}
    except Exception as e:
        return {"success": False, "message": str(e)}

def eliminar_cancha(cancha_id: int):
    """
    DELETE FROM canchas WHERE id = :cancha_id
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("canchas")\
            .delete()\
            .eq("id", cancha_id)\
            .execute()
        return {"success": True, "message": "Cancha eliminada correctamente"}
    except Exception as e:
        return {"success": False, "message": str(e)}