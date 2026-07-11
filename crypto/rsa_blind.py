"""
Módulo: crypto/rsa_blind.py
Responsabilidad: Implementación del protocolo de Firmas Ciegas de David Chaum
                 utilizando el motor matemático modular interno.
"""

import secrets
from crypto.mathematics import (
    mcd, 
    inverso_modular, 
    exponenciacion_modular, 
    es_primo_basico
)

def generar_llaves_autoridad() -> tuple[tuple[int, int], tuple[int, int]]:
    """
    Genera un par de llaves RSA académicas completas (pública y privada).
    Para el MVP, usamos primos controlados y estables.
    
    Retorna:
    tuple: ((e, n), (d, n)) -> Llave pública y Llave privada.
    """
    # Primos estables de tamaño académico elegidos para evitar desbordamiento 
    # y garantizar unicidad en pruebas repetitivas
    p = 61
    sig_primo = 101
    
    n = p * sig_primo
    phi = (p - 1) * (sig_primo - 1)
    
    # Exponente público estándar común
    e = 17
    while mcd(e, phi) != 1:
        e += 2
        
    # Calcular exponente privado
    d = inverso_modular(e, phi)
    
    return (e, n), (d, n)


def generar_factor_cegado(n: int) -> int:
    """
    Genera un factor aleatorio 'r' que sea coprimo con el módulo 'n'.
    """
    while True:
        # Generar un entero aleatorio seguro en el rango [2, n-1]
        r = secrets.randbelow(n - 2) + 2
        if mcd(r, n) == 1:
            return r


def cegar_mensaje(mensaje_int: int, llave_publica: tuple[int, int], r: int) -> int:
    """
    Aplica el algoritmo de Blinding: m' = (m * r^e) mod n
    
    Parámetros:
    mensaje_int (int): El mensaje representativo (ej. hash del voto).
    llave_publica (tuple): (e, n) de la Autoridad.
    r (int): Factor de cegado aleatorio coprimo con n.
    """
    e, n = llave_publica
    # r_e = r^e mod n
    r_e = exponenciacion_modular(r, e, n)
    # m_prime = (m * r^e) mod n
    m_prime = (mensaje_int * r_e) % n
    return m_prime


def firmar_ciego(m_prime: int, llave_privada: tuple[int, int]) -> int:
    """
    La autoridad firma el mensaje cegado sin conocer el contenido original: s' = (m')^d mod n
    """
    d, n = llave_privada
    s_prime = exponenciacion_modular(m_prime, d, n)
    return s_prime


def descegar_firma(s_prime: int, r: int, n: int) -> int:
    """
    Remueve el factor de cegado de la firma recibida: s = (s' * r^-1) mod n
    """
    r_inv = inverso_modular(r, n)
    s = (s_prime * r_inv) % n
    return s


def verificar_firma(mensaje_int: int, firma: int, llave_publica: tuple[int, int]) -> bool:
    """
    Verifica si una firma descegada corresponde al mensaje original usando la llave pública.
    Cumple con: m == s^e mod n
    """
    e, n = llave_publica
    mensaje_recuperado = exponenciacion_modular(firma, e, n)
    return mensaje_int == mensaje_recuperado