"""
Módulo: database/connection.py
Responsabilidad: Administrar la conexión a la base de datos SQLite,
                 asegurar la ejecución del esquema inicial y proveer un contexto seguro.
"""

import sqlite3
import os

DB_PATH = "database/voting_system.db"
SCHEMA_PATH = "database/schema.sql"

def obtener_conexion() -> sqlite3.Connection:
    """
    Establece y retorna una conexión activa a la base de datos SQLite.
    Activa el soporte de llaves foráneas.
    """
    # Asegurar que el directorio database exista
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    # Requisito para que SQLite respete los FOREIGN KEY
    conn.execute("PRAGMA foreign_keys = ON;")
    # Retornar filas como diccionarios para facilitar el mapeo en los servicios
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_base_de_datos() -> None:
    """
    Lee el archivo schema.sql e inicializa todas las tablas necesarias
    si no existen previamente.
    """
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"No se encontró el archivo de esquema en: {SCHEMA_PATH}")
        
    conn = obtener_conexion()
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            script_sql = f.read()
            
        # Ejecutar el script completo de creación de tablas
        conn.executescript(script_sql)
        conn.commit()
        print("[Database] Base de datos inicializada y tablas verificadas correctamente.")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"[Database] Error crítico inicializando la base de datos: {e}")
        raise e
    finally:
        conn.close()