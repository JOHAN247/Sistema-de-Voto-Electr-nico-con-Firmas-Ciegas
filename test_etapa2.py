# test_etapa2.py
from crypto.rsa_blind import (
    generar_llaves_autoridad, 
    generar_factor_cegado, 
    cegar_mensaje, 
    firmar_ciego, 
    descegar_firma, 
    verificar_firma
)

print("=== PROBANDO PROTOCOLO DE FIRMAS CIEGAS ===")

# 1. Generar llaves de la Mesa de Votación (Autoridad)
publica, privada = generar_llaves_autoridad()
e, n = publica
print(f"[Autoridad] Llave Pública (e, n): ({e}, {n})")
print(f"[Autoridad] Llave Privada (d, n): ({privada[0]}, {n})")

# 2. El votante define su opción (Candidato 1 -> convertido a número entero, ej: 42)
voto_original = 42
print(f"\n[Votante] Voto secreto original (m): {voto_original}")

# 3. El votante genera su factor r y ciega su voto
r = generar_factor_cegado(n)
voto_cegado = cegar_mensaje(voto_original, publica, r)
print(f"[Votante] Factor de cegado aleatorio (r): {r}")
print(f"[Votante] Voto cegado enviado a la autoridad (m'): {voto_cegado}")

# 4. La autoridad firma el voto cegado sin ver qué contiene
firma_ciega = firmar_ciego(voto_cegado, privada)
print(f"\n[Autoridad] Firma devuelta al votante (s'): {firma_ciega}")

# 5. El votante desciega la firma en su máquina local usando r
firma_final = descegar_firma(firma_ciega, r, n)
print(f"\n[Votante] Firma descegada obtenida (s): {firma_final}")

# 6. Verificación final (lo que hará el sistema cuando se envíe el voto al buzón anónimo)
es_valido = verificar_firma(voto_original, firma_final, publica)
print(f"\n[Escrutinio] ¿La firma descegada es matemáticamente válida?: {es_valido}")
print("=========================================")