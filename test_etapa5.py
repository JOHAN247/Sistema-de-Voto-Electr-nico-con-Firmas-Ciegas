# test_etapa5.py
from auth.repository import registrar_usuario, verificar_usuario
from election.repository import crear_eleccion, unirse_a_eleccion, cambiar_estado_eleccion
from crypto.rsa_blind import generar_llaves_autoridad, generar_factor_cegado, cegar_mensaje, descegar_firma
from services.voting_service import procesar_solicitud_firma, registrar_voto_anonimo, obtener_resultados_escudriñados

print("=== SIMULACIÓN COMPLETA DEL PROTOCOLO DE VOTACIÓN ===")

# 1. Preparar actores
registrar_usuario("carlos", "pass123")
user = verificar_usuario("carlos", "pass123")
llave_publica, _ = generar_llaves_autoridad()

# 2. Crear votación y activar carrera
cod = crear_eleccion("Elección de Personero", user["id"])
eleccion = unirse_a_eleccion(cod, user["id"])
cambiar_estado_eleccion(eleccion["id"], "ACTIVE")
print(f"Elección '{eleccion['title']}' activa y lista para recibir votos.")

# 3. PARTE LOCAL DEL CLIENTE (Simulación de la máquina del votante)
opcion = "Candidato A"
# Representación matemática del mensaje
mensaje_int = sum(ord(c) for c in opcion)
r = generar_factor_cegado(llave_publica[1])
voto_cegado = cegar_mensaje(mensaje_int, llave_publica, r)
print(f"\n[Cliente] Carlos quiere votar por '{opcion}' (id matemático: {mensaje_int})")
print(f"[Cliente] Envía paquete ciego a la autoridad: {voto_cegado}")

# 4. MOMENTO 1 EN EL SERVIDOR (Solicitar Firma)
firma_ciega_recibida = procesar_solicitud_firma(eleccion["id"], user["id"], voto_cegado)
print(f"[Servidor] Autoridad firma el paquete sin mirar y bloquea al usuario Carlos.")

# 5. PARTE LOCAL DEL CLIENTE (Descegar la firma obtenida)
firma_limpia = descegar_firma(firma_ciega_recibida, r, llave_publica[1])
print(f"[Cliente] Carlos limpia la firma localmente. Firma resultante: {firma_limpia}")

# 6. MOMENTO 2 EN EL SERVIDOR (Depósito en la Urna Anónima)
# Mandamos el voto con la firma limpia, sin mandar el id de Carlos
voto_exitoso = registrar_voto_anonimo(eleccion["id"], opcion, firma_limpia)
print(f"\n[Servidor] ¿Urna aceptó el voto anónimo?: {voto_exitoso}")

# 7. Intentar votar otra vez para probar seguridad
intento_fraude = procesar_solicitud_firma(eleccion["id"], user["id"], voto_cegado)
print(f"[Servidor] ¿Permitió a Carlos pedir otra firma?: {intento_fraude}")

# 8. Ver escrutinio final
resultados = obtener_resultados_escudriñados(eleccion["id"])
print(f"\n[Resultados Oficiales]: {resultados}")
print("=====================================================")