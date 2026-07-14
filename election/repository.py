import sqlite3
from database.connection import obtener_conexion
from utils.helpers import generar_codigo_eleccion


def crear_eleccion(
    titulo: str, opciones_lista: list[str], creador_id: int
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
                        "INSERT INTO elections (title, code, options, created_by) VALUES (?, ?, ?, ?);",
                        (titulo, codigo, opciones_str, creador_id),
                    )
                return codigo
            except sqlite3.IntegrityError:
                continue
        return None
    finally:
        conn.close()


def unirse_a_eleccion(codigo: str, usuario_id: int) -> dict | None:
    codigo = codigo.strip().upper()
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, status, options, created_by FROM elections WHERE code = ?;",
            (codigo,),
        )
        eleccion = cursor.fetchone()

        if not eleccion or eleccion["status"] == "FINISHED":
            return None

        eleccion_id = eleccion["id"]

        try:
            with conn:
                cursor.execute(
                    "INSERT INTO election_participants (election_id, user_id, has_voted) VALUES (?, ?, 0);",
                    (eleccion_id, usuario_id),
                )
        except sqlite3.IntegrityError:
            pass

        lista_opciones = eleccion["options"].split(",")

        return {
            "id": eleccion_id,
            "title": eleccion["title"],
            "status": eleccion["status"],
            "options": lista_opciones,
            "created_by": eleccion["created_by"],
        }
    finally:
        conn.close()


def cambiar_estado_eleccion(eleccion_id: int, nuevo_estado: str) -> bool:
    conn = obtener_conexion()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE elections SET status = ? WHERE id = ?;",
                (nuevo_estado, eleccion_id),
            )
        return cursor.rowcount > 0
    finally:
        conn.close()