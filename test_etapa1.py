# test_etapa1.py
from crypto.mathematics import mcd, inverso_modular, exponenciacion_modular

print("=== PROBANDO EL MOTOR MATEMÁTICO BASE ===")

# 1. Probar MCD
print(f"MCD(35, 14) esperado: 7 | Obtenido: {mcd(35, 14)}")

# 2. Probar Inverso Modular
# Buscamos inverso de 3 mod 11. (3 * 4 = 12 = 1 mod 11) -> Debería ser 4
try:
    inv = inverso_modular(3, 11)
    print(f"Inverso modular de 3 mod 11 esperado: 4 | Obtenido: {inv}")
except ValueError as e:
    print(f"Error: {e}")

# 3. Probar Exponenciación Modular Rápida
# 7^3 mod 13 = 343 mod 13. (13 * 26 = 338. 343 - 338 = 5) -> Debería ser 5
exp = exponenciacion_modular(7, 3, 13)
print(f"Exponenciación 7^3 mod 13 esperada: 5 | Obtenida: {exp}")

print("=========================================")