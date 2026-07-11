"""
Módulo: election/repository.py
Responsabilidad: Gestión de Base de Datos para la creación de votaciones,
                 unión de participantes y control de estado de elecciones.
"""
import sqlite3
from database.connection import obtener_conexion
from utils.helpers import generar_codigo_eleccion

def crear_eleccion(titulo: str, creador_id: int) -> str | None:
    """
    Crea una nueva votación generando un código único estilo Kahoot.
    Retorna el código de 6 dígitos generado o None si falla.
    """
    titulo = titulo.strip()
    if not titulo:
        return None
        
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        # Intentar generar un código y manejar colisiones de forma preventiva
        for _ in range(5):
            codigo = generar_codigo_eleccion()
            try:
                cursor.execute(
                    "INSERT INTO elections (title, code, created_by) VALUES (?, ?, ?);",
                    (titulo, codigo, creador_id)
                )
                conn.commit()
                return codigo
            except sqlite3.IntegrityError:
                continue # Si el código colisiona (raro), intenta con otro
        return None
    finally:
        conn.close()

def unirse_a_eleccion(codigo: str, usuario_id: int) -> dict | None:
    """
    Permite a un usuario unirse a una elección activa usando su código.
    Retorna los detalles de la elección si tiene éxito, o None si no existe/está cerrada.
    """
    codigo = codigo.strip().upper()
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        # 1. Buscar si la elección existe y está abierta
        cursor.execute("SELECT id, title, status FROM elections WHERE code = ?;", (codigo,))
        eleccion = cursor.fetchone()
        
        if not eleccion or eleccion["status"] == "FINISHED":
            return None
            
        eleccion_id = eleccion["id"]
        
        # 2. Registrar al usuario como participante (si ya está registrado, lo ignora de forma segura)
        try:
            cursor.execute(
                "INSERT INTO election_participants (election_id, user_id, has_voted) VALUES (?, ?, 0);",
                (eleccion_id, usuario_id)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # El usuario ya se había unido antes, lo cual es perfectamente válido
            pass
            
        return {"id": eleccion_id, "title": eleccion["title"], "status": eleccion["status"]}
    finally:
        conn.close()

def cambiar_estado_eleccion(eleccion_id: int, nuevo_estado: str) -> bool:
    """Cambia el estado de la elección: 'PENDING', 'ACTIVE', 'FINISHED'"""
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE elections SET status = ? WHERE id = ?;", (nuevo_estado, eleccion_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()