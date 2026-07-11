# test_etapa3.py
from database.connection import inicializar_base_de_datos, obtener_conexion
import os

print("=== PROBANDO LA CAPA DE DATOS ===")

# 1. Inicializar base de datos
inicializar_base_de_datos()

# 2. Verificar que el archivo .db se creó
db_existe = os.path.exists("database/voting_system.db")
print(f"¿Archivo binario SQLite creado?: {db_existe}")

# 3. Intentar una consulta rápida de verificación sobre las tablas creadas
conn = obtener_conexion()
cursor = conn.cursor()

try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = [fila["name"] for fila in cursor.fetchall()]
    print(f"Tablas detectadas en el sistema: {tablas}")
    
    # Comprobar que están las 4 fundamentales
    tablas_esperadas = {"users", "elections", "election_participants", "votes"}
    if tablas_esperadas.issubset(set(tablas)):
        print("¡Verificación exitosa! El esquema físico coincide con el diseño lógico.")
    else:
         print("Error: Faltan tablas críticas en el esquema.")
except Exception as e:
    print(f"Error durante la prueba de lectura: {e}")
finally:
    conn.close()

print("=========================================")