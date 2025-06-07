import streamlit as st
import pandas as pd
from conexion import get_supabase_client

def obtener_canchas():
    """Obtiene las canchas disponibles de la base de datos"""
    try:
        supabase = get_supabase_client()
        
        # Consulta SQL: SELECT * FROM tipos_cancha
        # Esta consulta obtiene todos los tipos de cancha registrados en el sistema
        tipos = supabase.table("tipos_cancha").select("*").execute()
        if not tipos.data:
            st.warning("No hay tipos de cancha registrados.")
            return pd.DataFrame()

        # Consulta SQL compleja con INNER JOIN:
        # SELECT c.id, c.nombre, c.disponible, tc.nombre as tipo_cancha, 
        # hd.dia_semana, hd.hora_inicio, hd.hora_fin
        # FROM canchas c
        # INNER JOIN tipos_cancha tc ON c.tipo_id = tc.id
        # LEFT JOIN horarios_disponibles hd ON c.id = hd.cancha_id
        # Esta consulta obtiene las canchas junto con su tipo y horarios disponibles
        query = supabase.table("canchas").select(
            "id, nombre, disponible, tipos_cancha!inner(nombre), horarios_disponibles(dia_semana, hora_inicio, hora_fin)"
        ).execute()
        
        if not query.data:
            st.info("No hay canchas registradas en el sistema.")
            return pd.DataFrame()
        
        # Convertir los datos principales a DataFrame
        df = pd.DataFrame(query.data)
        
        # Procesar tipo de cancha
        if 'tipos_cancha' in df.columns:
            df['tipo'] = df['tipos_cancha'].apply(lambda x: x['nombre'] if x else 'No especificado')
            df = df.drop(columns=['tipos_cancha'])
            
        # Procesar horarios disponibles
        def format_horarios(horarios):
            if not horarios:
                return "No disponible"
            return ", ".join([f"{h['dia_semana']}: {h['hora_inicio']}-{h['hora_fin']}" for h in horarios])
        
        if 'horarios_disponibles' in df.columns:
            df['horarios'] = df['horarios_disponibles'].apply(format_horarios)
            df = df.drop(columns=['horarios_disponibles'])
        
        # Renombrar columnas para mejor visualización
        df = df.rename(columns={
            'id': 'ID',
            'nombre': 'Nombre',
            'disponible': 'Disponible',
            'tipo': 'Tipo de Cancha',
            'horarios': 'Horarios Disponibles'
        })
        
        return df
    except Exception as e:
        st.error(f"Error al obtener las canchas: {str(e)}")
        return pd.DataFrame()

def mostrar_dashboard():
    # Verificar si hay sesión activa
    if "usuario" not in st.session_state:
        st.warning("🔒 Debes iniciar sesión para acceder al panel.")
        st.stop()

    usuario = st.session_state.usuario

    # Encabezado
    st.write(f"👤 Bienvenido **{usuario['nombre']}**")
    st.write(f"🔑 Rol: `{usuario['rol']}`")

    st.divider()    # Sección de Canchas
    st.subheader("⚽ Canchas Disponibles")
    
    # Botón para recargar
    if st.button("🔄 Actualizar lista"):
        st.rerun()
    
    # Obtener y mostrar las canchas
    canchas_df = obtener_canchas()
    
    if not canchas_df.empty:
        # Aplicar estilo condicional para la columna Disponible            
        st.dataframe(
                canchas_df,
                column_config={
                    "ID": st.column_config.NumberColumn(
                        "Cancha #",
                        help="Número de cancha",
                        width="small",
                    ),
                    "Nombre": st.column_config.TextColumn(
                        "Nombre",
                        help="Nombre de la cancha",
                        width="medium",
                    ),
                    "Tipo de Cancha": st.column_config.TextColumn(
                        "Tipo",
                        help="Tipo de cancha (Fútbol, Pádel, etc.)",
                        width="medium",
                    ),
                    "Disponible": st.column_config.CheckboxColumn(
                        "Disponible",
                        help="Indica si la cancha está disponible",
                        width="small",
                    ),
                    "Horarios Disponibles": st.column_config.TextColumn(
                        "Horarios",
                        help="Días y horarios disponibles",
                        width="large",
                    ),
                },
                hide_index=True,
                use_container_width=True
            )
    else:
        st.warning("👀 No se encontraron canchas registradas en el sistema.")
            
    
    st.divider()

    # Botón de cerrar sesión al final
    if st.button("Cerrar sesión", type="primary"):
        st.session_state.clear()
        st.rerun()
