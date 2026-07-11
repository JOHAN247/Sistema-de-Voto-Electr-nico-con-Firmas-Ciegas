"""
Módulo: crypto/mathematics.py
Responsabilidad: Implementación desde cero de funciones matemáticas de aritmética modular
                 y teoría de números para el soporte de criptografía RSA y Firmas Ciegas.
No se utilizan librerías criptográficas externas. Todo se resuelve mediante enteros puros.
"""

def mcd(a: int, b: int) -> int:
    """
    Calcula el Máximo Común Divisor de dos números mediante el Algoritmo de Euclides.
    
    Parámetros:
    a (int): Primer entero.
    b (int): Segundo entero.
    
    Retorna:
    int: El MCD de a y b.
    """
    while b != 0:
        a, b = b, a % b
    return abs(a)


def euclides_extendido(a: int, b: int) -> tuple[int, int, int]:
    """
    Implementa el Algoritmo de Euclides Extendido.
    Encuentra los coeficientes de Bézout (x, y) tales que: a*x + b*y = mcd(a, b)
    
    Parámetros:
    a (int): Primer entero.
    b (int): Segundo entero (usualmente el módulo).
    
    Retorna:
    tuple[int, int, int]: (mcd, x, y)
    """
    if a == 0:
        return b, 0, 1
    
    mcd_actual, x1, y1 = euclides_extendido(b % a, a)
    
    # Actualización de los coeficientes basándose en la recursión
    x = y1 - (b // a) * x1
    y = x1
    
    return mcd_actual, x, y


def inverso_modular(a: int, m: int) -> int:
    """
    Calcula el inverso modular de 'a' bajo el módulo 'm' (a^-1 mod m).
    Cumple con: (a * x) % m == 1
    
    Parámetros:
    a (int): Número al que se le busca el inverso.
    m (int): Módulo.
    
    Retorna:
    int: El inverso modular positivo.
    
    Lanza:
    ValueError: Si el inverso no existe (a y m no son coprimos).
    """
    mcd_val, x, _ = euclides_extendido(a, m)
    if mcd_val != 1:
        raise ValueError(f"El inverso modular no existe porque MCD({a}, {m}) = {mcd_val} (no son coprimos).")
    
    # Asegurar que el resultado sea un número positivo dentro del grupo modular
    return (x % m + m) % m


def exponenciacion_modular(base: int, exponente: int, modulo: int) -> int:
    """
    Calcula de manera eficiente (base^exponente) % modulo utilizando
    el algoritmo de Exponenciación Binaria (Square-and-Multiply).
    Evita el desbordamiento de memoria al aplicar el módulo en cada paso.
    
    Parámetros:
    base (int): Base de la potencia.
    exponente (int): Exponente al que se eleva la base.
    modulo (int): Módulo de la operación.
    
    Retorna:
    int: Resultado de la operación matemática.
    """
    if modulo == 1:
        return 0
    
    resultado = 1
    base = base % modulo  # Ajustar base si es mayor al módulo
    
    while exponente > 0:
        # Si el bit menos significativo es 1, multiplicar por la base actual
        if exponente % 2 == 1:
            resultado = (resultado * base) % modulo
        
        # Desplazamiento de bit (exponente // 2) y elevación al cuadrado de la base
        exponente = exponente // 2
        base = (base * base) % modulo
        
    return resultado


def es_primo_basico(n: int) -> bool:
    """
    Verifica si un número es primo mediante divisiones sucesivas optimizadas.
    Apropiado para el control de llaves académicas del proyecto.
    """
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