"""
Módulo: services/voting_service.py
Responsabilidad: Orquestar el flujo de votación y la aplicación del protocolo 
                 de firmas ciegas entre la base de datos y el motor criptográfico.
"""

import sqlite3
from database.connection import obtener_conexion
from crypto.rsa_blind import generar_llaves_autoridad, firmar_ciego, verificar_firma

def procesar_solicitud_firma(eleccion_id: int, user_id: int, voto_cegado: int) -> int | None:
    """
    Paso 1 del Protocolo: El usuario autenticado solicita que la autoridad firme su voto ciego.
    Garantiza que el usuario solo pueda solicitar una firma por elección (Evita doble voto).
    """
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        
        # 1. Verificar si el participante está registrado y no ha votado aún
        cursor.execute(
            "SELECT has_voted FROM election_participants WHERE election_id = ? AND user_id = ?;",
            (eleccion_id, user_id)
        )
        participante = cursor.fetchone()
        
        if not participante or participante["has_voted"] == 1:
            return None  # No está inscrito o ya solicitó su firma (intento de fraude)
            
        # 2. Generar las llaves de la autoridad para esta firma (en el MVP usamos las fijas académicas)
        _, llave_privada = generar_llaves_autoridad()
        
        # 3. Firmar el voto cegado utilizando la llave privada de la autoridad
        firma_ciega = firmar_ciego(voto_cegado, llave_privada)
        
        # 4. Marcar al participante como "Ya votó" en la tabla de control
        cursor.execute(
            "UPDATE election_participants SET has_voted = 1 WHERE election_id = ? AND user_id = ?;",
            (eleccion_id, user_id)
        )
        conn.commit()
        
        return firma_ciega
    except sqlite3.Error:
        conn.rollback()
        return None
    finally:
        conn.close()


def registrar_voto_anonimo(eleccion_id: int, opcion_seleccionada: str, firma_descegada: int) -> bool:
    """
    Paso 2 del Protocolo: Registra el voto en el buzón de manera 100% anónima.
    Aquí NO se recibe el user_id. La legitimidad del voto depende ÚNICAMENTE de la matemática.
    """
    # 1. Convertir la opción seleccionada a su representación numérica para validación matemática
    # En el MVP usaremos la suma del valor ASCII de los caracteres de la opción como identificador estable
    mensaje_int = sum(ord(c) for c in opcion_seleccionada)
    
    # 2. Obtener la llave pública de la autoridad para auditar la firma
    llave_publica, _ = generar_llaves_autoridad()
    
    # 3. Validar matemáticamente si la firma descegada es legítima
    if not verificar_firma(mensaje_int, firma_descegada, llave_publica):
        print("[Escrutinio] Voto rechazado: La firma digital proporcionada es FALSA o INVÁLIDA.")
        return False
        
    # 4. Si es válida, meter el voto directamente a la urna anónima
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO votes (election_id, option_selected, signature) VALUES (?, ?, ?);",
            (eleccion_id, opcion_seleccionada, str(firma_descegada))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Esto previene ataques de repetición (Replay Attacks), la firma debe ser única
        print("[Escrutinio] Voto rechazado: Esta firma ya fue utilizada.")
        return False
    finally:
        conn.close()


def obtener_resultados_escudriñados(eleccion_id: int) -> dict[str, int]:
    """
    Realiza el conteo oficial de los votos depositados en la urna anónima.
    """
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT option_selected, COUNT(*) as total FROM votes WHERE election_id = ? GROUP BY option_selected;",
            (eleccion_id,)
        )
        filas = cursor.fetchall()
        return {fila["option_selected"]: fila["total"] for fila in filas}
    finally:
        conn.close()