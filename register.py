import bcrypt
from getpass import getpass
from conexion import get_supabase_client
import re
import json
from datetime import datetime

def validar_email(email: str) -> bool:
    """Valida el formato del correo electrónico"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_password(password: str) -> tuple[bool, str]:
    """Valida los requisitos de la contraseña"""
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una mayúscula"
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una minúscula"
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    return True, ""

def registrar_usuario(rol: str = "cliente"):
    supabase = get_supabase_client()
    print("=== Sistema de Reservas de Canchas - Registro ===")

    # Recolectar datos
    nombre = input("Nombre completo: ").strip()
    email = input("Email: ").strip().lower()
    password = getpass("Contraseña: ").strip()
    confirmar = getpass("Confirmar contraseña: ").strip()

    # Validaciones
    if not nombre or len(nombre) < 3:
        return {
            "success": False,
            "message": "❌ El nombre debe tener al menos 3 caracteres."
        }

    if not validar_email(email):
        return {
            "success": False,
            "message": "❌ El formato del correo electrónico no es válido."
        }

    if password != confirmar:
        return {
            "success": False,
            "message": "❌ Las contraseñas no coinciden."
        }

    # Validar requisitos de la contraseña
    es_valida, mensaje = validar_password(password)
    if not es_valida:
        return {
            "success": False,
            "message": f"❌ {mensaje}"
        }

    try:
        # Verificar si el correo ya existe
        existe = supabase.table("usuarios").select("id").eq("email", email).execute()
        if existe.data:
            return {
                "success": False,
                "message": "❌ Ya existe un usuario con ese correo."
            }

        # Hashear la contraseña
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Preparar datos para inserción
        data = {
            "nombre": nombre,
            "email": email,
            "password": hashed_pw,
            "rol": rol,
            "fecha_registro": datetime.now().isoformat()
        }

        # Insertar en Supabase
        resultado = supabase.table("usuarios").insert(data).execute()
        
        if resultado.data:
            print(f"✅ Usuario {nombre} registrado correctamente.")
            return {
                "success": True,
                "message": "✅ Usuario registrado correctamente.",
                "user": {
                    "id": resultado.data[0]["id"],
                    "nombre": nombre,
                    "email": email,
                    "rol": rol
                }
            }
        else:
            return {
                "success": False,
                "message": "❌ Error al registrar el usuario en la base de datos."
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error al registrar: {str(e)}"
        }

if __name__ == "__main__":
    resultado = registrar_usuario()
    print(json.dumps(resultado, indent=2))
