import streamlit as st
import pandas as pd
from conexion import get_supabase_client

def mostrar_bitacora():
    """Muestra la vista de bitácora (solo para administradores)"""
    st.title("📝 Bitácora del Sistema")
    
    if st.session_state.usuario['rol'] != 'admin':
        st.error("⛔ No tienes permisos para ver esta sección")
        st.stop()
        
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("bitacora")\
            .select("*")\
            .order("fecha_hora_ingreso", desc=True)\
            .execute()
            
        if response.data:
            df = pd.DataFrame(response.data)
            st.dataframe(
                df,
                column_config={
                    "nombre_usuario": st.column_config.TextColumn("Usuario"),
                    "fecha_hora_ingreso": st.column_config.DatetimeColumn("Ingreso"),
                    "fecha_hora_salida": st.column_config.DatetimeColumn("Salida"),
                    "tipo_accion": st.column_config.TextColumn("Acción"),
                    "descripcion": st.column_config.TextColumn("Descripción")
                },
                hide_index=True
            )
        else:
            st.info("No hay registros en la bitácora")
            
    except Exception as e:
        st.error(f"Error al cargar la bitácora: {str(e)}")