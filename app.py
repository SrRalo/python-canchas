import streamlit as st
from conexion import get_supabase_client
import bcrypt
from datetime import datetime
import re
from dashboard import mostrar_dashboard 

# Debe ser la primera llamada a Streamlit
st.set_page_config(
    page_title="Reservas Deportivas",
    page_icon="⚽",
    layout="wide", 
    initial_sidebar_state="expanded"
)

from session_manager import check_authentication, login_user, logout_user



def mostrar_formulario_login():
    with st.form("login_form"):
        st.subheader("🔐 Iniciar Sesión")
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Iniciar Sesión")
        
        if submitted:
            if email and password:
                supabase = get_supabase_client()
                res = supabase.table("usuarios").select("*").eq("email", email).execute()
                
                if not res.data:
                    st.error("❌ Usuario no encontrado")
                    return
                
                usuario = res.data[0]
                if bcrypt.checkpw(password.encode("utf-8"), usuario["password"].encode("utf-8")):
                    st.success(f"✅ Bienvenido, {usuario['nombre']}!")
                    login_user(usuario)
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta")
            else:
                st.warning("Por favor, complete todos los campos")

def validar_email(email):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_password(password):
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una mayúscula"
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una minúscula"
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    return True, ""

def mostrar_formulario_registro():
    with st.form("registro_form"):
        st.subheader("📝 Registro de Usuario")
        nombre = st.text_input("Nombre completo")
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        rol = st.selectbox(
            "Rol", 
            ["consultor", "operador_reservas", "registrador_eventos"]
        )  # admin se asigna manualmente por seguridad
        submitted = st.form_submit_button("Registrarse")
        
        if submitted:
            if not nombre or len(nombre) < 3:
                st.error("❌ El nombre debe tener al menos 3 caracteres")
                return
                
            if not validar_email(email):
                st.error("❌ El formato del correo electrónico no es válido")
                return
                
            es_valida, mensaje = validar_password(password)
            if not es_valida:
                st.error(f"❌ {mensaje}")
                return
                
            try:
                supabase = get_supabase_client()
                
                # Verificar si el correo ya existe
                existe = supabase.table("usuarios").select("id").eq("email", email).execute()
                if existe.data:
                    st.error("❌ Ya existe un usuario con ese correo")
                    return
                
                # Hashear la contraseña
                hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                
                # Preparar datos para inserción
                data = {
                    "nombre": nombre,
                    "email": email,
                    "password": hashed_pw,
                    "rol": rol  # Usando el rol seleccionado
                }
                
                # Insertar en Supabase
                resultado = supabase.table("usuarios").insert(data).execute()
                
                if resultado.data:
                    st.success("✅ Usuario registrado correctamente")
                    # Iniciar sesión automáticamente
                    st.session_state.usuario = resultado.data[0]
                    st.rerun()  # Cambio aquí
                else:
                    st.error("❌ Error al registrar el usuario")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

from dashboard import mostrar_dashboard  # Importar la función desde dashboard.py


def main():
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🏟️ Sistema de Reservas Deportivas")
    
    if not check_authentication():
        # Para login/registro, usamos un contenedor centrado
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                opcion = st.radio("Selecciona una opción", ["Iniciar sesión", "Registrarse"])
                if opcion == "Iniciar sesión":
                    mostrar_formulario_login()
                else:
                    mostrar_formulario_registro()
    else:
        # Si el usuario está logueado, mostrar dashboard
        st.query_params["layout"] = "wide"
        mostrar_dashboard()

if __name__ == "__main__":
    main()
