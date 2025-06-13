import platform
import socket
import httpagentparser
from datetime import datetime
from conexion import get_supabase_client

class Bitacora:
    def __init__(self, usuario_id, nombre_usuario):
        self.supabase = get_supabase_client()
        self.usuario_id = usuario_id
        self.nombre_usuario = nombre_usuario
        self.inicio_sesion()
    
    def get_info_sistema(self, user_agent=None):
        """Obtiene información del sistema y navegador"""
        return {
            "navegador": httpagentparser.detect(user_agent)["browser"]["name"] if user_agent else "Desconocido",
            "ip_acceso": socket.gethostbyname(socket.gethostname()),
            "nombre_maquina": platform.node()
        }
    
    def inicio_sesion(self):
        """Registra el inicio de sesión"""
        try:
            info_sistema = self.get_info_sistema()
            data = {
                "usuario_id": self.usuario_id,
                "nombre_usuario": self.nombre_usuario,
                "navegador": info_sistema["navegador"],
                "ip_acceso": info_sistema["ip_acceso"],
                "nombre_maquina": info_sistema["nombre_maquina"],
                "tipo_accion": "LOGIN",
                "descripcion": f"Inicio de sesión del usuario {self.nombre_usuario}"
            }
            self.supabase.table("bitacora").insert(data).execute()
        except Exception as e:
            print(f"Error al registrar inicio de sesión: {e}")
    
    def cierre_sesion(self):
        """Registra el cierre de sesión"""
        try:
            # Actualizar último registro de login con hora de salida
            self.supabase.table("bitacora")\
                .update({"fecha_hora_salida": datetime.now().isoformat()})\
                .eq("usuario_id", self.usuario_id)\
                .is_("fecha_hora_salida", None)\
                .execute()
        except Exception as e:
            print(f"Error al registrar cierre de sesión: {e}")
    
    def registrar_accion(self, tabla, accion, descripcion):
        """Registra una acción del usuario"""
        try:
            data = {
                "usuario_id": self.usuario_id,
                "nombre_usuario": self.nombre_usuario,
                "tabla_afectada": tabla,
                "tipo_accion": accion,
                "descripcion": descripcion
            }
            self.supabase.table("bitacora").insert(data).execute()
        except Exception as e:
            print(f"Error al registrar acción: {e}")