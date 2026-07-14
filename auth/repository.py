import sqlite3
import bcrypt
from database.connection import obtener_conexion


def registrar_usuario(username: str, password_plana: str) -> bool:
    username = username.strip().lower()
    if not username or not password_plana:
        return False

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(
        password_plana.encode("utf-8"), salt
    ).decode("utf-8")

    conn = obtener_conexion()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?);",
                (username, password_hash),
            )
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verificar_usuario(username: str, password_plana: str) -> dict | None:
    username = username.strip().lower()
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?;",
            (username,),
        )
        usuario = cursor.fetchone()

        if usuario:
            hash_guardado = usuario["password_hash"].encode("utf-8")
            if bcrypt.checkpw(password_plana.encode("utf-8"), hash_guardado):
                return {"id": usuario["id"], "username": usuario["username"]}

        return None
    finally:
        conn.close()