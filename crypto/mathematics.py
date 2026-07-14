def mcd(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return abs(a)


def euclides_extendido(a: int, b: int) -> tuple[int, int, int]:
    if a == 0:
        return b, 0, 1

    mcd_actual, x1, y1 = euclides_extendido(b % a, a)

    x = y1 - (b // a) * x1
    y = x1

    return mcd_actual, x, y


def inverso_modular(a: int, m: int) -> int:
    mcd_val, x, _ = euclides_extendido(a, m)
    if mcd_val != 1:
        raise ValueError(
            f"El inverso modular no existe porque MCD({a}, {m}) = {mcd_val} (no son coprimos)."
        )

    return x % m


def exponenciacion_modular(base: int, exponente: int, modulo: int) -> int:
    if modulo == 1:
        return 0

    resultado = 1
    base = base % modulo

    while exponente > 0:
        if exponente % 2 == 1:
            resultado = (resultado * base) % modulo

        exponente = exponente // 2
        base = (base * base) % modulo

    return resultado


def es_primo_basico(n: int) -> bool:
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True