import bcrypt
from getpass import getpass
from conexion import get_supabase_client
import webbrowser
from datetime import datetime, timedelta
import json

def login_usuario():

    supabase = get_supabase_client()
    print("=== Sistema de Reservas de Canchas - Login ===")

    email = input("Email: ").strip().lower()
    password = getpass("Contraseña: ").strip()

    try:
        # Buscar usuario y obtener datos necesarios
        res = supabase.table("usuarios").select(
            "id, email, nombre, password, rol"
        ).eq("email", email).execute()
        
        usuarios = res.data

        if not usuarios:
            return {"success": False, "message": "❌ Usuario no encontrado."}

        usuario = usuarios[0]
        hashed_pw = usuario.get("password")

        if bcrypt.checkpw(password.encode("utf-8"), hashed_pw.encode("utf-8")):
            # Generar token de sesión
            session_data = {
                "user_id": usuario["id"],
                "email": usuario["email"],
                "rol": usuario["rol"],
                "exp": (datetime.now() + timedelta(hours=24)).isoformat()
            }

            # Guardar token en Supabase
            token_res = supabase.table("tokens").insert({
                "usuario_id": usuario["id"],
                "token": json.dumps(session_data),
                "expiracion": session_data["exp"]
            }).execute()

            print(f"✅ Bienvenido, {usuario['nombre']}!")
            
            # Redirigir según el rol
            if usuario["rol"] == "admin":
                webbrowser.open("http://localhost:8501/admin")
            else:
                webbrowser.open("http://localhost:8501/dashboard")
                
            return {
                "success": True,
                "user": {
                    "id": usuario["id"],
                    "nombre": usuario["nombre"],
                    "email": usuario["email"],
                    "rol": usuario["rol"]
                },
                "token": token_res.data[0]["token"]
            }
        else:
            return {"success": False, "message": "❌ Contraseña incorrecta."}

    except Exception as e:
        return {"success": False, "message": f"❌ Error al iniciar sesión: {str(e)}"}

def logout_usuario(token):
    """
    Función para cerrar sesión y eliminar el token
    """
    try:
        supabase = get_supabase_client()
        supabase.table("tokens").delete().eq("token", token).execute()
        return {"success": True, "message": "Sesión cerrada correctamente"}
    except Exception as e:
        return {"success": False, "message": f"Error al cerrar sesión: {str(e)}"}

if __name__ == "__main__":
    resultado = login_usuario()
    print(json.dumps(resultado, indent=2))
