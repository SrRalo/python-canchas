import streamlit as st
import pandas as pd
from conexion import get_supabase_client

def mostrar_business():
    """Muestra la vista de reportes de negocio"""
    st.title("📊 Business Analytics")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Reservas Totales", value="0")
    with col2:
        st.metric(label="Ingresos del Mes", value="$0")
    with col3:
        st.metric(label="Tasa de Ocupación", value="0%")
    
    # Gráficos y análisis
    st.subheader("Análisis de Tendencias")
    # Aquí va la lógica para mostrar gráficos y análisis