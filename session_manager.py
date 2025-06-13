import streamlit as st
from bitacora import Bitacora

def check_authentication():
    """Verifica si hay una sesión activa"""
    return bool(st.session_state.get('usuario', None))

def login_user(usuario):
    """Establece la sesión del usuario"""
    st.session_state.authentication_status = True
    st.session_state.usuario = usuario
    # Iniciar registro en bitácora
    st.session_state.bitacora = Bitacora(
        usuario_id=usuario["id"],
        nombre_usuario=usuario["nombre"]
    )

def logout_user():
    """Cierra la sesión del usuario"""
    if "bitacora" in st.session_state:
        st.session_state.bitacora.cierre_sesion()
    st.session_state.authentication_status = False
    st.session_state.usuario = None
    del st.session_state.bitacora
    st.rerun()


