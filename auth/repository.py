"""
Módulo: auth/repository.py
Responsabilidad: Comunicación directa con SQLite para el registro y 
                 verificación de usuarios utilizando hash seguro (bcrypt).
"""
import sqlite3
import bcrypt
from database.connection import obtener_conexion

def registrar_usuario(username: str, password_plana: str) -> bool:
    """
    Registra un nuevo usuario aplicando hashing seguro a la contraseña.
    Retorna True si el registro fue exitoso, False si el usuario ya existe.
    """
    username = username.strip().lower()
    if not username or not password_plana:
        return False
        
    # Generar Hash seguro con sal aleatoria
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_plana.encode('utf-8'), salt).decode('utf-8')
    
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?);",
            (username, password_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # El username ya existe debido a la restricción UNIQUE
        return False
    finally:
        conn.close()

def verificar_usuario(username: str, password_plana: str) -> dict | None:
    """
    Verifica las credenciales del usuario.
    Retorna un diccionario con los datos básicos del usuario si es válido, o None.
    """
    username = username.strip().lower()
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?;", (username,))
        usuario = cursor.fetchone()
        
        if usuario:
            # Verificar si la contraseña coincide con el hash
            hash_guardado = usuario["password_hash"].encode('utf-8')
            if bcrypt.checkpw(password_plana.encode('utf-8'), hash_guardado):
                return {"id": usuario["id"], "username": usuario["username"]}
                
        return None
    finally:
        conn.close()