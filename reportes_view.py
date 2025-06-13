import streamlit as st
import pandas as pd
from conexion import get_supabase_client

def mostrar_reportes():
    """Muestra la vista de reportes generales"""
    st.title("📋 Reportes")
    
    # Tabs para diferentes tipos de reportes
    tab1, tab2, tab3 = st.tabs(["Reservas", "Canchas", "Usuarios"])
    
    with tab1:
        st.header("Reporte de Reservas")
        # Aquí va la lógica para mostrar reportes de reservas
        
    with tab2:
        st.header("Reporte de Canchas")
        # Aquí va la lógica para mostrar reportes de canchas
        
    with tab3:
        st.header("Reporte de Usuarios")
        # Aquí va la lógica para mostrar reportes de usuarios