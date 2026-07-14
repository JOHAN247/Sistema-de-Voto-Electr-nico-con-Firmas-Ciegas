import sqlite3
from crypto.rsa_blind import generar_llaves_autoridad, firmar_ciego, verificar_firma
from database.connection import obtener_conexion


def procesar_solicitud_firma(
    eleccion_id: int, user_id: int, voto_cegado: int
) -> int | None:
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT has_voted FROM election_participants WHERE election_id = ? AND user_id = ?;",
            (eleccion_id, user_id),
        )
        participante = cursor.fetchone()

        if not participante or participante["has_voted"] == 1:
            return None

        _, llave_privada = generar_llaves_autoridad()

        firma_ciega = firmar_ciego(voto_cegado, llave_privada)

        with conn:
            cursor.execute(
                "UPDATE election_participants SET has_voted = 1 WHERE election_id = ? AND user_id = ?;",
                (eleccion_id, user_id),
            )

        return firma_ciega
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def registrar_voto_anonimo(
    eleccion_id: int, opcion_seleccionada: str, firma_descegada: int
) -> bool:
    mensaje_int = sum(ord(c) for c in opcion_seleccionada)

    llave_publica, _ = generar_llaves_autoridad()

    if not verificar_firma(mensaje_int, firma_descegada, llave_publica):
        return False

    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        with conn:
            cursor.execute(
                "INSERT INTO votes (election_id, option_selected, signature) VALUES (?, ?, ?);",
                (eleccion_id, opcion_seleccionada, str(firma_descegada)),
            )
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def obtener_resultados_escudriñados(eleccion_id: int) -> dict[str, int]:
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT option_selected, COUNT(*) as total FROM votes WHERE election_id = ? GROUP BY option_selected;",
            (eleccion_id,),
        )
        filas = cursor.fetchall()
        return {fila["option_selected"]: fila["total"] for fila in filas}
    finally:
        conn.close()