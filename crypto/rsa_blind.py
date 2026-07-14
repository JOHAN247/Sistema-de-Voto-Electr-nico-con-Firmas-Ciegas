import secrets
from crypto.mathematics import (
    mcd,
    inverso_modular,
    exponenciacion_modular,
)


def generar_llaves_autoridad() -> tuple[tuple[int, int], tuple[int, int]]:
    p = 61
    sig_primo = 101

    n = p * sig_primo
    phi = (p - 1) * (sig_primo - 1)

    e = 17
    while mcd(e, phi) != 1:
        e += 2

    d = inverso_modular(e, phi)

    return (e, n), (d, n)


def generar_factor_cegado(n: int) -> int:
    while True:
        r = secrets.randbelow(n - 2) + 2
        if mcd(r, n) == 1:
            return r


def cegar_mensaje(
    mensaje_int: int, llave_publica: tuple[int, int], r: int
) -> int:
    e, n = llave_publica
    r_e = exponenciacion_modular(r, e, n)
    m_prime = (mensaje_int * r_e) % n
    return m_prime


def firmar_ciego(m_prime: int, llave_privada: tuple[int, int]) -> int:
    d, n = llave_privada
    s_prime = exponenciacion_modular(m_prime, d, n)
    return s_prime


def descegar_firma(s_prime: int, r: int, n: int) -> int:
    r_inv = inverso_modular(r, n)
    s = (s_prime * r_inv) % n
    return s


def verificar_firma(
    mensaje_int: int, firma: int, llave_publica: tuple[int, int]
) -> bool:
    e, n = llave_publica
    mensaje_recuperado = exponenciacion_modular(firma, e, n)
    return mensaje_int == mensaje_recuperado