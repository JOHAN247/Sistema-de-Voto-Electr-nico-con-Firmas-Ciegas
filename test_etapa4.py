# test_etapa4.py
from database.connection import inicializar_base_de_datos
from auth.repository import registrar_usuario, verificar_usuario
from election.repository import crear_eleccion, unirse_a_eleccion

print("=== PROBANDO CAPA DE AUTENTICACIÓN Y ELECCIONES ===")
inicializar_base_de_datos()

# 1. Probar Registro de dos usuarios
reg1 = registrar_usuario("juan", "clave123")
reg2 = registrar_usuario("maria", "segura456")
print(f"Registro Juan: {reg1} | Registro María: {reg2}")

# 2. Probar Login
login_ok = verificar_usuario("juan", "clave123")
login_fail = verificar_usuario("juan", "clave_erronea")
print(f"Login Juan Correcto (Esperado dict): {login_ok}")
print(f"Login Juan Incorrecto (Esperado None): {login_fail}")

# 3. Juan crea una elección (Simulación de ID de Juan = 1)
if login_ok:
    codigo_kahoot = crear_eleccion("Votación Representante Estudiantil", login_ok["id"])
    print(f"\n[Elección] Elección creada con éxito. Código generado: {codigo_kahoot}")
    
    # 4. María se une a la elección usando el código de Juan (ID de María = 2)
    datos_eleccion = unirse_a_eleccion(codigo_kahoot, 2)
    print(f"[Participante] María se unió a la elección: {datos_eleccion}")

print("==================================================")