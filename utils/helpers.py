"""
Módulo: utils/helpers.py
Responsabilidad: Funciones utilitarias del sistema, como la generación 
                 de códigos únicos para las votaciones estilo Kahoot.
"""
import secrets
import string

def generar_codigo_eleccion(longitud: int = 6) -> str:
    """
    Genera un código alfanumérico aleatorio y en mayúsculas de alta entropía.
    Evita caracteres confusos como 'I', 'O', '0', '1'.
    """
    caracteres_limpios = "".join(
        c for c in string.ascii_uppercase + string.digits 
        if c not in "IO01"
    )
    return "".join(secrets.choice(caracteres_limpios) for _ in range(longitud))