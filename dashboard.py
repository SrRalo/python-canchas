import streamlit as st
import pandas as pd
from funciones import obtener_canchas_disponibles
from bitacora_view import mostrar_bitacora
from reportes_view import mostrar_reportes
from business_view import mostrar_business
from funciones import crear_cancha, actualizar_cancha, eliminar_cancha, actualizar_disponibilidad

def mostrar_dashboard():
    """Muestra el dashboard principal con la lista de canchas disponibles"""
    # Verificar si hay sesión activa
    if 'usuario' not in st.session_state:
        st.warning("🔒 Debes iniciar sesión para acceder al panel.")
        st.stop()

    usuario = st.session_state['usuario']
    
    # Barra de navegación
    st.sidebar.title("Navegación")
    
    # Botones de navegación
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'
        
    if st.sidebar.button("🏠 Dashboard"):
        st.session_state.page = 'dashboard'
        
    if st.sidebar.button("📋 Reportes"):
        st.session_state.page = 'reportes'
        
    if st.sidebar.button("📊 Business"):
        st.session_state.page = 'business'
        
    # Solo mostrar botón de bitácora para administradores
    if usuario['rol'] == 'admin':
        if st.sidebar.button("📝 Bitácora"):
            st.session_state.page = 'bitacora'
    
    # Mostrar la página correspondiente
    if st.session_state.page == 'dashboard':
        mostrar_contenido_dashboard(usuario)
    elif st.session_state.page == 'reportes':
        mostrar_reportes()
    elif st.session_state.page == 'business':
        mostrar_business()
    elif st.session_state.page == 'bitacora' and usuario['rol'] == 'admin':
        mostrar_bitacora()

def mostrar_contenido_dashboard(usuario):
    """Muestra el contenido principal del dashboard"""
    st.write(f"👤 Bienvenido **{usuario['nombre']}**")
    st.write(f"🔑 Rol: `{usuario['rol']}`")
    
    st.divider()
    
    # Obtener canchas
    response = obtener_canchas_disponibles()
    
    if response["success"]:
        df = pd.DataFrame(response["data"])
        
        # Crear una fila con búsqueda y botones de ordenar
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            # Barra de búsqueda
            search = st.text_input("🔍 Buscar cancha por nombre o tipo", 
                                 placeholder="Ejemplo: Fútbol, Cancha 1...")
        
        with col2:
            # Botón de ordenar por horarios
            if st.button("⏰", help="Ordenar por horarios"):
                df['hora_num'] = df['horarios_disponibles'].str.extract('(\d{2}):(\d{2})').astype(float).iloc[:, 0]
                df = df.sort_values('hora_num')
                df = df.drop('hora_num', axis=1)
        
        with col3:
            # Botón de ordenar por tipo
            if st.button("🎯", help="Ordenar por tipo de cancha"):
                df = df.sort_values('tipos_cancha')
        
        # Filtrar el DataFrame si hay texto en la búsqueda
        if search:
            mask = (df['nombre'].str.contains(search, case=False, na=False)) | \
                  (df['tipos_cancha'].str.contains(search, case=False, na=False))
            df = df[mask]
            
            if df.empty:
                st.info("No se encontraron canchas que coincidan con la búsqueda.")
        
        # Mostrar tabla filtrada
        st.dataframe(
            df,
            column_config={
                "id": st.column_config.NumberColumn(
                    "Cancha #",
                    help="Número de cancha",
                    disabled=True
                ),
                "nombre": st.column_config.TextColumn(
                    "Nombre",
                    help="Nombre de la cancha",
                    disabled=usuario['rol'] not in ['admin']
                ),
                "tipos_cancha": st.column_config.TextColumn(
                    "Tipo de Cancha",
                    help="Tipo de cancha",
                    disabled=usuario['rol'] not in ['admin']
                ),
                "disponible": st.column_config.TextColumn(
                    "Disponible",
                    help="Estado de la cancha",
                    disabled=usuario['rol'] not in ['admin', 'consultor']
                )
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning(response["message"])

        # Modal de edición
        if 'editing_cancha' in st.session_state:
            show_edit_modal(st.session_state.editing_cancha, df)

    # Formulario para agregar/editar cancha (solo admin y registrador)
    if usuario['rol'] in ['admin', 'registrador']:
        st.divider()
        
        # Selector de modo (crear/editar)
        modo = st.radio("Seleccione una acción:", ["Crear Nueva Cancha", "Editar Cancha Existente"])
        
        with st.form(key="court_form"):
            st.subheader("📝 Gestión de Canchas")
            
            if modo == "Editar Cancha Existente":
                # Selector de cancha a editar
                cancha_id = st.selectbox(
                    "Seleccione la cancha a editar",
                    options=df['id'].tolist(),
                    format_func=lambda x: f"Cancha #{x} - {df[df['id']==x]['nombre'].iloc[0]}"
                )
                # Obtener datos de la cancha seleccionada
                cancha_actual = df[df['id'] == cancha_id].iloc[0]
            else:
                cancha_actual = None

            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input(
                    "Nombre de la cancha", 
                    value=cancha_actual['nombre'] if cancha_actual is not None else "",
                    placeholder="Ejemplo: Cancha Principal"
                )
                # Obtener tipos de cancha desde la base de datos
                tipos_cancha = {
                    1: "Fútbol",
                    2: "Tenis",
                    3: "Pádel"
                }
                tipo_id = st.selectbox(
                    "Tipo de Cancha",
                    options=list(tipos_cancha.keys()),
                    format_func=lambda x: tipos_cancha[x],
                    help="Selecciona el tipo de cancha"
                )
            
            with col2:
                dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                dia_semana = st.selectbox(
                    "Día disponible",
                    options=dias_semana
                )
                hora_inicio = st.time_input("Hora de inicio", value=None)
                hora_fin = st.time_input("Hora de fin", value=None)
            
            # Botón submit del formulario
            submitted = st.form_submit_button(
                "Guardar Cambios" if modo == "Editar Cancha Existente" else "Agregar Cancha"
            )
            
            if submitted:
                if not nombre:
                    st.error("❌ El nombre de la cancha es obligatorio")
                elif hora_inicio >= hora_fin:
                    st.error("❌ La hora de fin debe ser mayor a la hora de inicio")
                else:
                    try:
                        datos = {
                            "nombre": nombre,
                            "id_tipo": tipo_id,
                            "disponible": True
                        }
                        
                        if modo == "Editar Cancha Existente":
                            result = actualizar_cancha(cancha_id, datos)
                            mensaje = "actualizada"
                        else:
                            result = crear_cancha(nombre, tipo_id)
                            mensaje = "creada"

                        if result["success"]:
                            st.success(f"✅ Cancha {mensaje} correctamente")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result['message']}")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    st.divider()
      # Botón de cerrar sesión
    if st.button("Cerrar sesión", type="primary"):
        from session_manager import logout_user
        logout_user()

def set_editing_cancha(cancha_id):
    """Helper function para establecer la cancha en edición"""
    st.session_state.editing_cancha = cancha_id
    st.rerun()

def delete_cancha(cancha_id):
    """Helper function para eliminar cancha"""
    if eliminar_cancha(cancha_id)["success"]:
        st.success("Cancha eliminada correctamente")
        st.rerun()

def show_edit_modal(cancha_id, df):
    """Helper function para mostrar el modal de edición"""
    cancha = df[df['id'] == cancha_id].iloc[0]
    
    with st.form(key=f"edit_form_{cancha_id}"):
        st.subheader(f"Editar Cancha {cancha_id}")
        nuevo_nombre = st.text_input("Nombre", value=cancha['nombre'])
        nuevo_tipo = st.selectbox(
            "Tipo de Cancha",
            options=[1, 2, 3],
            format_func=lambda x: "Fútbol" if x == 1 else "Tenis" if x == 2 else "Pádel"
        )
        nueva_disponibilidad = st.checkbox("Disponible", value=cancha['disponible'] == "✅")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Guardar"):
                actualizar_cancha(cancha_id, {
                    "nombre": nuevo_nombre,
                    "tipo_id": nuevo_tipo,
                    "disponible": nueva_disponibilidad
                })
                del st.session_state.editing_cancha
                st.rerun()
        with col2:
            if st.form_submit_button("Cancelar"):
                del st.session_state.editing_cancha
                st.rerun()
            else:
                st.warning(response["message"])
    
    st.divider()
      # Botón de cerrar sesión
    if st.button("Cerrar sesión", type="primary"):
        from session_manager import logout_user
        logout_user()

def handle_table_change(original_df, edited_df, rol):
    """Maneja los cambios en la tabla según el rol del usuario"""
    changes = edited_df.compare(original_df)
    if changes.empty:
        return

    for idx in changes.index:
        cancha_id = original_df.loc[idx, 'id']
        
        if rol == 'admin':
            # Administradores pueden editar todo
            datos_actualizados = {
                col: edited_df.loc[idx, col] 
                for col in changes.columns.levels[0] 
                if col not in ['id', 'acciones']
            }
            actualizar_cancha(cancha_id, datos_actualizados)
            
        elif rol == 'consultor':
            # Consultores solo pueden cambiar disponibilidad
            if 'disponible' in changes.columns.levels[0]:
                nuevo_estado = edited_df.loc[idx, 'disponible']
                actualizar_disponibilidad(cancha_id, nuevo_estado == "✅")

    st.success("✅ Cambios guardados correctamente")
    st.rerun()