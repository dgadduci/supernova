# Archivo: logica_fuzzy_pedido_medios_de_pago.py
#
# ══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
#   detectar_medio_de_pago(texto: str) -> dict
#
# DESCRIPCIÓN
#   Recibe el texto libre del cliente y devuelve el medio de pago detectado
#   con todos sus campos de lista_json. Si no se detecta ninguno, o el medio
#   tiene activo=False, devuelve el medio nulo.
#
# EJEMPLO
#   Entrada : "quiero pagar con transferencia"
#   Salida  : {
#               "id": 2,
#               "id_tipo": 2,
#               "descripcion": "transferencia",
#               "titular": "Alberto Mosquera",
#               "alias": "alberto.mp",
#               "activo": True
#             }
#
#   Entrada : "pago en efectivo"
#   Salida  : {
#               "id": 1,
#               "id_tipo": 1,
#               "descripcion": "efectivo",
#               "titular": "",
#               "alias": "",
#               "activo": True
#             }
#
#   Entrada : "no sé" / medio con activo=False
#   Salida  : {"id": 0, "descripcion": "no_seleccionado"}
# ══════════════════════════════════════════════════════════════════════════════

from backend.data.lista_json import medios_de_pago as medios_default
from rapidfuzz import fuzz, process
import re
import unicodedata

# ── Respuesta por defecto ─────────────────────────────────────────────────────

MEDIO_NO_SELECCIONADO = {"id": 0, "descripcion": "no_seleccionado"}

# ── Aliases y sinónimos de medios de pago ────────────────────────────────────
# Mapea variantes informales/abreviadas → descripcion canónica en lista_json.
# Agregá acá cualquier forma que use el cliente.

ALIASES_MEDIO_PAGO: dict[str, str] = {
    # efectivo
    "efectivo":     "efectivo",
    "efect":        "efectivo",
    "efec":         "efectivo",
    "efvo":         "efectivo",
    "cash":         "efectivo",
    "plata":        "efectivo",
    "billetes":     "efectivo",
    "billete":      "efectivo",
    "metalico":     "efectivo",
    # transferencia
    "transferencia":"transferencia",
    "transfe":      "transferencia",
    "transfer":     "transferencia",
    "tranfer":      "transferencia",
    "transf":       "transferencia",
    "transfiero":   "transferencia",
    "trasnferencia":"transferencia",
    "alias":        "transferencia",
    "aleas":        "transferencia",
    "mercadopago":  "transferencia",
    "mercado":      "transferencia",
    "mp":           "transferencia",    
    "mpago":        "transferencia",    
    # tarjeta de débito
    "debito":       "debito",
    "débito":       "debito",
    "tarjeta":      "debito",
    "visa":         "debito",
    # tarjeta de crédito
    "credito":      "credito",
    "crédito":      "credito",
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
    """Devuelve tokens del texto que pueden referirse a un medio de pago."""
    STOPWORDS = {
        "quiero", "pago", "pagar", "con", "en", "por", "via", "mediante",
        "de", "el", "la", "un", "una", "y", "me", "lo", "voy", "a",
        "seria", "seria", "puede", "ser", "hacer",
    }
    return [t for t in _normalizar(texto).split() if t not in STOPWORDS and len(t) > 1]

# ── Catálogo de medios de pago ────────────────────────────────────────────────

def _preparar_catalogo(medios: list[dict]) -> list[dict]:
    """Precalcula la descripción normalizada de cada medio de pago."""
    return [
        {
            **medio,
            "_descripcion_norm": _normalizar(medio.get("descripcion", "")),
        }
        for medio in medios
    ]

# ── Matching ──────────────────────────────────────────────────────────────────

def _buscar_medio(texto: str, medios: list[dict]) -> dict | None:
    """
    Busca el medio de pago mencionado en el texto.
    Estrategia:
      1. Alias exacto por token (más rápido y preciso).
      2. Fuzzy contra descripciones del catálogo.
    Devuelve el dict completo del medio (sin _descripcion_norm) o None.
    """
    catalogo = _preparar_catalogo(medios)
    tokens = _tokens_relevantes(texto)

    # 1. Alias exacto —————————————————————————————————————————————
    for token in tokens:
        descripcion_canonica = ALIASES_MEDIO_PAGO.get(token)
        if descripcion_canonica:
            for medio in catalogo:
                if _normalizar(medio["descripcion"]) == _normalizar(descripcion_canonica):
                    return {k: v for k, v in medio.items() if not k.startswith("_")}

    # 2. Fuzzy contra descripción —————————————————————————————————
    descripciones = [m["_descripcion_norm"] for m in catalogo]
    texto_norm = " ".join(tokens)

    matches = process.extract(texto_norm, descripciones, scorer=fuzz.WRatio, limit=1)
    if matches:
        nombre_match, score, indice = matches[0]
        if score >= SCORE_MINIMO:
            medio = catalogo[indice]
            return {k: v for k, v in medio.items() if not k.startswith("_")}

    return None

# ── Punto de entrada público ──────────────────────────────────────────────────

def detectar_medio_de_pago(texto: str, medios: list[dict] | None = None) -> str:
    """
    Recibe el texto libre del usuario y devuelve un JSON string con el medio
    de pago detectado y todos sus campos de lista_json.

    Reglas:
      - Si no se menciona ningún medio → '{"id": 0, "descripcion": "no_seleccionado"}'
      - Si el medio encontrado tiene activo=False → idem
      - Si se encuentra y está activo → JSON con todos los campos del medio
    """
    import json

    medios = medios or medios_default
    medio  = _buscar_medio(texto, medios)

    if medio is None:
        return json.dumps(MEDIO_NO_SELECCIONADO, ensure_ascii=False)

    activo = medio.get("activo", True)
    no_activo = activo is False or str(activo).lower() in ("false", "0", "no")
    if no_activo:
        return json.dumps(MEDIO_NO_SELECCIONADO, ensure_ascii=False)

    return json.dumps(medio, ensure_ascii=False)


if __name__ == "__main__":
    import json

    while True:
        texto = input("\nIngrese forma de pago (o 'exit' para salir): ")
        if texto.lower() == "exit":
            break
        resultado = detectar_medio_de_pago(texto)  # ya es JSON string
        # Pretty-print para legibilidad en consola
        print(json.dumps(json.loads(resultado), ensure_ascii=False, indent=2))
