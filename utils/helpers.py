import secrets
import string

def generar_codigo_eleccion(longitud: int = 6) -> str:

    caracteres_limpios = "".join(
        c for c in string.ascii_uppercase + string.digits 
        if c not in "IO01"
    )
    return "".join(secrets.choice(caracteres_limpios) for _ in range(longitud))