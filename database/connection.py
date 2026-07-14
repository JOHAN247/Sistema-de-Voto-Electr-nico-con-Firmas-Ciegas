import os
import sqlite3

DB_PATH = "database/voting_system.db"
SCHEMA_PATH = "database/schema.sql"


def obtener_conexion() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_base_de_datos() -> None:
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(
            f"No se encontró el archivo de esquema en: {SCHEMA_PATH}"
        )

    conn = obtener_conexion()
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            script_sql = f.read()

        with conn:
            conn.executescript(script_sql)
        print(
            "[Database] Base de datos inicializada y tablas verificadas correctamente."
        )
    except sqlite3.Error as e:
        print(f"[Database] Error crítico inicializando la base de datos: {e}")
        raise e
    finally:
        conn.close()