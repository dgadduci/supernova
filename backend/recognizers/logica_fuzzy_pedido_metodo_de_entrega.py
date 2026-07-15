# Archivo: logica_fuzzy_metodo_de_entrega.py
#
# ══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
#   detectar_metodo_de_entrega(texto: str) -> str  (JSON string)
#
# DESCRIPCIÓN
#   Recibe el texto libre del cliente y devuelve el método de entrega detectado
#   con todos sus campos de lista_json. Si no se detecta ninguno, o el método
#   tiene activo=False, devuelve el método nulo.
#
# EJEMPLO
#   Entrada : "lo retiro yo"
#   Salida  : '{"id": 1, "descripcion": "retira_local", "activo": true}'
#
#   Entrada : "mándenlo a domicilio"
#   Salida  : '{"id": 2, "descripcion": "delivery", "activo": true}'
#
#   Entrada : "comemos en el salón" / método con activo=False / no detectado
#   Salida  : '{"id": 0, "descripcion": "metodo_entrega_no_seleccionado"}'
# ══════════════════════════════════════════════════════════════════════════════

from backend.data.lista_json import metodos_entrega as metodos_default
from rapidfuzz import fuzz, process
import re
import unicodedata

# ── Respuesta por defecto ─────────────────────────────────────────────────────

METODO_NO_SELECCIONADO = {"id": 0, "descripcion": "metodo_entrega_no_seleccionado"}

# ── Aliases y sinónimos de métodos de entrega ─────────────────────────────────
# Mapea variantes informales/abreviadas → descripcion canónica en lista_json.
# Agregá acá cualquier forma que use el cliente.

ALIASES_METODO_ENTREGA: dict[str, str] = {
    # retira_local
    "retiro":           "retira_local",
    "retira":           "retira_local",
    "busco":            "retira_local",
    "paso":             "retira_local",
    "voy":              "retira_local",
    "local":            "retira_local",
    "mostrador":        "retira_local",
    "personal":         "retira_local",
    "presencial":       "retira_local",
    "ahi":              "retira_local",
    "alla":             "retira_local",
    # delivery
    "delivery":         "delivery",
    "deliveri":         "delivery",
    "delibery":         "delivery",
    "deliberi":         "delivery",
    "envio":            "delivery",
    "enviar":           "delivery",
    "manden":           "delivery",
    "manda":            "delivery",
    "mandame":          "delivery",
    "mandalo":          "delivery",
    "mandamelo":        "delivery",
    "traigan":          "delivery",
    "traeme":           "delivery",
    "trae":             "delivery",
    "puerta":           "delivery",
    "abajo":            "delivery",
    "bajo":             "delivery",
    "domicilio":        "delivery",
    "casa":             "delivery",
    "direccion":        "delivery",
    "vivo":        "delivery",
    "calle":        "delivery",
    "avenida":        "delivery",
    "avda":        "delivery",
    # consume_salon
    "salon":            "consume_salon",
    "salón":            "consume_salon",
    "mesa":             "consume_salon",
    "aca":              "consume_salon",
    "aqui":             "consume_salon",
    "aquí":             "consume_salon",
    "adentro":          "consume_salon",
    "dentro":           "consume_salon",
    "comer":            "consume_salon",
    "lugar":            "consume_salon",
}

SCORE_MINIMO = 72

# ── Normalización ─────────────────────────────────────────────────────────────

def _normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def _tokens_relevantes(texto: str) -> list[str]:
    """Devuelve tokens del texto que pueden referirse a un método de entrega."""
    STOPWORDS = {
        "quiero", "por", "favor", "me", "lo", "un", "una", "el", "la",
        "de", "en", "a", "que", "con", "y", "es", "al", "para", "del",
        "por", "si", "lo", "las", "los", "nos",
    }
    return [t for t in _normalizar(texto).split() if t not in STOPWORDS and len(t) > 1]

# ── Catálogo de métodos de entrega ────────────────────────────────────────────

def _preparar_catalogo(metodos: list[dict]) -> list[dict]:
    """Precalcula la descripción normalizada de cada método de entrega."""
    return [
        {
            **metodo,
            "_descripcion_norm": _normalizar(metodo.get("descripcion", "")),
        }
        for metodo in metodos
    ]

# ── Matching ──────────────────────────────────────────────────────────────────

def _buscar_metodo(texto: str, metodos: list[dict]) -> dict | None:
    """
    Busca el método de entrega mencionado en el texto.
    Estrategia:
      1. Alias exacto por token.
      2. Fuzzy contra descripciones del catálogo.
    Devuelve el dict completo del método (sin _descripcion_norm) o None.
    """
    catalogo = _preparar_catalogo(metodos)
    tokens = _tokens_relevantes(texto)

    # 1. Alias exacto ─────────────────────────────────────────────
    for token in tokens:
        descripcion_canonica = ALIASES_METODO_ENTREGA.get(token)
        if descripcion_canonica:
            for metodo in catalogo:
                if _normalizar(metodo["descripcion"]) == _normalizar(descripcion_canonica):
                    return {k: v for k, v in metodo.items() if not k.startswith("_")}

    # 2. Fuzzy contra descripción ─────────────────────────────────
    descripciones = [m["_descripcion_norm"] for m in catalogo]
    texto_norm = " ".join(tokens)

    matches = process.extract(texto_norm, descripciones, scorer=fuzz.WRatio, limit=1)
    if matches:
        _, score, indice = matches[0]
        if score >= SCORE_MINIMO:
            metodo = catalogo[indice]
            return {k: v for k, v in metodo.items() if not k.startswith("_")}

    return None

# ── Punto de entrada público ──────────────────────────────────────────────────

def detectar_metodo_de_entrega(texto: str, metodos: list[dict] | None = None) -> str:
    """
    Recibe el texto libre del usuario y devuelve un JSON string con el método
    de entrega detectado y todos sus campos de lista_json.

    Reglas:
      - Si no se menciona ningún método → '{"id": 0, "descripcion": "metodo_entrega_no_seleccionado"}'
      - Si el método encontrado tiene activo=False → idem
      - Si se encuentra y está activo → JSON con todos los campos del método
    """
    import json

    metodos = metodos or metodos_default
    metodo  = _buscar_metodo(texto, metodos)

    if metodo is None:
        return json.dumps(METODO_NO_SELECCIONADO, ensure_ascii=False)

    activo = metodo.get("activo", True)
    no_activo = activo is False or str(activo).lower() in ("false", "0", "no")
    if no_activo:
        return json.dumps(METODO_NO_SELECCIONADO, ensure_ascii=False)

    return json.dumps(metodo, ensure_ascii=False)


if __name__ == "__main__":
    import json

    while True:
        texto = input("\nIngrese método de entrega (o 'exit' para salir): ")
        if texto.lower() == "exit":
            break
        resultado = detectar_metodo_de_entrega(texto)  # ya es JSON string
        # Pretty-print para legibilidad en consola
        print(json.dumps(json.loads(resultado), ensure_ascii=False, indent=2))
