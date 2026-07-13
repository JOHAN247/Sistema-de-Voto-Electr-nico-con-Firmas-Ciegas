import sqlite3
import time
import streamlit as st
from auth.repository import registrar_usuario, verificar_usuario
from crypto.rsa_blind import (
    cegar_mensaje,
    descegar_firma,
    generar_factor_cegado,
    generar_llaves_autoridad,
)
from database.connection import inicializar_base_de_datos, obtener_conexion
from election.repository import cambiar_estado_eleccion, unirse_a_eleccion
from services.voting_service import (
    obtener_resultados_escudriñados,
    procesar_solicitud_firma,
    registrar_voto_anonimo,
)
from utils.helpers import generar_codigo_eleccion


def crear_eleccion_directa(
    titulo: str, opciones_lista: list, creador_id: int
) -> str | None:
    titulo = titulo.strip()
    opciones_limpias = [o.strip() for o in opciones_lista if o.strip()]
    if not titulo or not opciones_limpias:
        return None
    opciones_str = ",".join(opciones_limpias)

    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        for _ in range(5):
            codigo = generar_codigo_eleccion()
            try:
                with conn:
                    cursor.execute(
                        "INSERT INTO elections (title, code, status, options, created_by) VALUES (?, ?, 'ACTIVE', ?, ?);",
                        (titulo, codigo, opciones_str, creador_id),
                    )
                cursor.execute(
                    "SELECT id FROM elections WHERE code = ?;", (codigo,)
                )
                row = cursor.fetchone()
                return (codigo, row[0]) if row else (codigo, None)
            except sqlite3.IntegrityError:
                continue
        return None
    finally:
        conn.close()


def consultar_estado_real_eleccion(eleccion_id):
    if not eleccion_id:
        return None
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, status, options, created_by FROM elections WHERE id = ?;",
            (eleccion_id,),
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "status": row[2],
                "options": row[3].split(","),
                "created_by": row[4],
            }
        return None
    finally:
        conn.close()


inicializar_base_de_datos()

st.set_page_config(
    page_title="Sistema de Votación Ciega", page_icon="🗳️", layout="centered"
)

if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "eleccion_actual" not in st.session_state:
    st.session_state.eleccion_actual = None

st.title("🗳️ Sistema Universitario de Votación Anónima")
st.caption(
    "Implementación de Firmas Ciegas de David Chaum - Matemáticas Discretas"
)
st.write("---")

if st.session_state.usuario is None:
    st.subheader("🔑 Acceso al Sistema")
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])

    with tab1:
        user_login = st.text_input("Usuario", key="login_user").strip()
        pass_login = st.text_input(
            "Contraseña", type="password", key="login_pass"
        )
        if st.button("Ingresar", use_container_width=True):
            user_data = verificar_usuario(user_login, pass_login)
            if user_data:
                st.session_state.usuario = user_data
                st.success(f"¡Bienvenido, {user_data['username']}!")
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")

    with tab2:
        user_reg = st.text_input("Elige un Usuario", key="reg_user").strip()
        pass_reg = st.text_input(
            "Elige una Contraseña", type="password", key="reg_pass"
        )
        if st.button("Crear Cuenta", use_container_width=True):
            if registrar_usuario(user_reg, pass_reg):
                st.success(
                    "Usuario registrado con éxito. Ya puedes iniciar sesión."
                )
            else:
                st.error("El usuario ya existe o los datos son inválidos.")

else:
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.write(
            f"👤 Sesión activa: **{st.session_state.usuario['username'].upper()}**"
        )
    with col_logout:
        if st.button("Salir", type="secondary", use_container_width=True):
            st.session_state.usuario = None
            st.session_state.eleccion_actual = None
            st.rerun()

    st.write("---")

    if st.session_state.eleccion_actual is None:
        col_crear, col_unirse = st.columns(2)

        with col_crear:
            st.markdown("### ➕ Crear una Elección")
            titulo_elec = st.text_input(
                "Título o Pregunta de la Votación",
                placeholder="Ej: ¿Quién debe ser Representante?",
            )
            opciones_raw = st.text_input(
                "Opciones (separadas por comas)",
                placeholder="Ej: Juan Perez, Maria Gomez",
            )

            if st.button(
                "Generar Votación (Estilo Kahoot)", use_container_width=True
            ):
                res_creacion = crear_eleccion_directa(
                    titulo_elec,
                    opciones_raw.split(","),
                    st.session_state.usuario["id"],
                )
                if res_creacion:
                    codigo_generado, nuevo_id = res_creacion
                    st.success(
                        f"¡Votación Creada! Código: **{codigo_generado}**"
                    )
                    lista_ops_limpias = [
                        o.strip()
                        for o in opciones_raw.split(",")
                        if o.strip()
                    ]

                    st.session_state.eleccion_actual = {
                        "id": nuevo_id,
                        "title": titulo_elec,
                        "status": "ACTIVE",
                        "options": lista_ops_limpias,
                        "created_by": st.session_state.usuario["id"],
                    }
                    st.info(
                        "Ingresa el código a la derecha para entrar directo al escrutinio."
                    )
                else:
                    st.error(
                        "Error: Asegúrate de poner un título y opciones válidas."
                    )

        with col_unirse:
            st.markdown("### 🎲 Unirse a Votación")
            codigo_ingresado = st.text_input(
                "Ingresa el Código de 6 dígitos", placeholder="Ej: XF83BA"
            ).strip()
            if st.button("Entrar a la Sala", use_container_width=True):
                eleccion_data = unirse_a_eleccion(
                    codigo_ingresado, st.session_state.usuario["id"]
                )
                if eleccion_data:
                    st.session_state.eleccion_actual = eleccion_data
                    st.rerun()
                else:
                    st.error("Código inválido o la elección ya finalizó.")

    else:
        info_fresca = consultar_estado_real_eleccion(
            st.session_state.eleccion_actual["id"]
        )
        if info_fresca:
            st.session_state.eleccion_actual["status"] = info_fresca["status"]

        st.subheader(f"Sala: {st.session_state.eleccion_actual['title']}")

        if st.session_state.eleccion_actual["status"] == "ACTIVE":
            st.success("🟢 ESTADO: Urna abierta. Esperando votos...")
        else:
            st.error("🔴 ESTADO: Votación Finalizada. Urna Clausurada.")

        opciones_voto = st.session_state.eleccion_actual["options"]
        eleccion_id_actual = st.session_state.eleccion_actual["id"]
        es_creador = (
            st.session_state.usuario["id"]
            == st.session_state.eleccion_actual.get("created_by")
        )

        st.write("---")
        st.markdown("#### ⚙️ Controles de Sala")

        if es_creador:
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "⏹️ Cerrar Urna y Contar Votos",
                    use_container_width=True,
                    type="primary",
                ):
                    cambiar_estado_eleccion(eleccion_id_actual, "FINISHED")
                    st.session_state.eleccion_actual["status"] = "FINISHED"
                    st.rerun()
            with col2:
                if st.button(
                    "↩️ Abandonar Sala (Reset)", use_container_width=True
                ):
                    st.session_state.eleccion_actual = None
                    st.rerun()
        else:
            if st.button("↩️ Salir de esta Sala", use_container_width=True):
                st.session_state.eleccion_actual = None
                st.rerun()

        if st.session_state.eleccion_actual["status"] == "ACTIVE":
            st.markdown("### 🗳️ Emite tu Voto Anónimo")
            st.caption(
                "💡 Si el administrador cierra la votación, la pantalla se actualizará automáticamente al presionar el botón de enviar o verificar."
            )

            seleccion = st.radio(
                "Selecciona tu opción:",
                opciones_voto,
                key=f"voto_radio_{eleccion_id_actual}",
            )

            if st.button(
                "🔒 Enviar Voto Seguro (Aplicar Firmas Ciegas)",
                use_container_width=True,
                key=f"btn_voto_{eleccion_id_actual}",
            ):
                verificar_sala = consultar_estado_real_eleccion(
                    eleccion_id_actual
                )
                if (
                    verificar_sala
                    and verificar_sala["status"] == "FINISHED"
                ):
                    st.error(
                        "⚠️ Demasiado tarde. El administrador cerró la sala antes de recibir tu voto."
                    )
                    st.session_state.eleccion_actual["status"] = "FINISHED"
                    st.rerun()

                mensaje_int = sum(ord(c) for c in seleccion)
                llave_pub, _ = generar_llaves_autoridad()
                r = generar_factor_cegado(llave_pub[1])
                voto_cegado = cegar_mensaje(mensaje_int, llave_pub, r)

                with st.spinner(
                    "Ejecutando operaciones matemáticas en el backend..."
                ):
                    firma_ciega = procesar_solicitud_firma(
                        eleccion_id_actual,
                        st.session_state.usuario["id"],
                        voto_cegado,
                    )

                    if firma_ciega is None:
                        st.error(
                            "❌ Transacción Denegada: Ya registraste participación en esta encuesta específica."
                        )
                    else:
                        firma_limpia = descegar_firma(
                            firma_ciega, r, llave_pub[1]
                        )
                        voto_exitoso = registrar_voto_anonimo(
                            eleccion_id_actual, seleccion, firma_limpia
                        )

                        if voto_exitoso:
                            st.balloons()
                            st.success(
                                "¡Voto depositado de forma 100% anónima!"
                            )
                            st.info(
                                "Tu navegador está listo. Espera a que el administrador cierre la urna para ver los gráficos totales."
                            )
                        else:
                            st.error(
                                "El buzón rechazó la firma digital por duplicidad o invalidez."
                            )

            if not es_creador:
                time.sleep(0.5)
                if st.button(
                    "🔄 Comprobar si el Admin ya cerró la sala",
                    use_container_width=True,
                ):
                    st.rerun()

        elif st.session_state.eleccion_actual["status"] == "FINISHED":
            st.markdown("### 📊 Resultados Oficiales del Escrutinio")
            st.warning(
                "🔒 La urna ha sido cerrada. Se calculan los votos validados matemáticamente por David Chaum:"
            )

            if eleccion_id_actual:
                resultados = obtener_resultados_escudriñados(
                    eleccion_id_actual
                )
                if resultados:
                    for opcion, conteo in resultados.items():
                        st.metric(
                            label=f"Opción: {opcion}",
                            value=f"{conteo} votos legítimos",
                        )
                else:
                    st.info(
                        "No se registraron votos válidos o la urna quedó vacía."
                    )
            else:
                st.error(
                    "Falta el ID único de la elección para computar los resultados."
                )