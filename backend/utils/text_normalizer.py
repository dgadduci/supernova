import re
import unicodedata


def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto para búsquedas y comparaciones.

    Operaciones:
    - elimina espacios al principio y al final;
    - convierte a minúsculas;
    - elimina tildes y diacríticos;
    - reemplaza espacios repetidos por uno solo.

    No modifica signos de puntuación ni otros caracteres.
    """

    if not isinstance(texto, str):
        raise TypeError("El valor recibido debe ser una cadena de texto")

    texto = texto.strip().lower()

    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    texto = re.sub(r"\s+", " ", texto)

    return texto