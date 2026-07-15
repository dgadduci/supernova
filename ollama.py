import requests
import json
from backend.data.lista_json import productos

# Configuration Constants
OLLAMA_URL = "http://100.113.65.40:11434/api/generate"
MODEL = "qwen-27b-coding:latest"

# Example input payload for testing purposes
entrada = {
    "mensaje": "mandame 4 empanadas de verdura",
    "cliente_id": 123,
    "canal": "whatsapp"
}


def extraer_json(texto: str) -> dict:
    """
    Extracts a valid JSON object from the raw text response of an LLM.
    """
    texto = texto.strip()

    if not texto:
        raise ValueError("La respuesta del modelo vino vacía.")

    try:
        # Attempt direct parse (works for clean JSON)
        return json.loads(texto)
    except json.JSONDecodeError:
        inicio = texto.find("{")
        fin = texto.rfind("}")

        if inicio == -1 or fin == -1 or fin <= inicio:
            raise ValueError("No se encontró un objeto JSON en la respuesta del modelo.")

        # Extract substring between first '{' and last '}' to remove markdown/filler
        return json.loads(texto[inicio:fin + 1])


def consultar_ollama(entrada: dict) -> dict:
    """
    Sends a classification request to the Ollama API.

    Args:
        entrada (dict): A dictionary containing customer input details with keys:
            - mensaje (str): The raw text message from the user.
            - cliente_id (int/str): Unique identifier for the client.
            - canal (str): Communication channel (e.g., "whatsapp", "web").

    Returns:
        dict: A structured dictionary containing:
            - intencion (str): The detected intent ("hacer_pedido", "ver_menu", etc.).
            - producto_normalizado (str): Standardized product name.
            - cantidad (int): Number of items requested.
            - tamano (str|null): Size of the item or null if not specified.
            - observaciones (str|null): Additional notes or null.
    """
    
    # Constructing a strict prompt to ensure JSON output and handle specific business rules
    prompt = f"""Sos un clasificador de pedidos para una pizzería.
Devolvé únicamente JSON válido.
No expliques nada.
No uses Markdown.

Catálogo disponible (para normalizar nombres y tamaños):
{json.dumps(productos, ensure_ascii=False)}

JSON de entrada:
{json.dumps(entrada, ensure_ascii=False)}

Reglas:
- Si quiere ver la carta o menú: intencion = "ver_menu".
- Si quiere comprar o pedir comida: intencion = "hacer_pedido".
- Si pregunta por un pedido ya hecho: intencion = "consultar_estado".
- Si no se entiende: intencion = "desconocida".
- Usa los nombres exactos del catálogo para 'producto_normalizado'.
- Si la cantidad no es explícita, usá 1.
- Si el tamaño no está en el pedido o no coincide con el catálogo, usá "grande" por defecto (a menos que se especifique).

Estructura obligatoria de salida:
{{
    "intencion": "hacer_pedido",
    "producto_normalizado": "nombre_exacto_del_catalogo",
    "cantidad": 1,
    "tamano": "grande",
    "observaciones": null
}}
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,          # Disable streaming for simpler response handling
        "keep_alive": "2h",       # Keep the model loaded in memory to reduce latency
        "think": False,           # Disable chain-of-thought output if supported by backend
        "format": "json",         # Request JSON format from Ollama (if available)
        "options": {
            "temperature": 0,     # Deterministic output for consistency
            "num_predict": 150,   # Limit token generation to save resources/time
            "num_ctx": 8192       # Context window size
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180  # Long timeout for large models or network latency
    )

    # Raise an exception if the HTTP request returned a status code indicating failure (4xx/5xx)
    response.raise_for_status()

    data = response.json()
    
    # Extract the 'response' field which contains the generated text from Ollama
    texto = data.get("response", "")

    return extraer_json(texto)


# Entry point for testing when running as a script
if __name__ == "__main__":
    try:
        resultado = consultar_ollama(entrada)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    except Exception as e:
        # Catch-all for network errors, JSON parsing errors, or model issues
        print("Error:", e)
