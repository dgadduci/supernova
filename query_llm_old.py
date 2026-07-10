import requests
import json
from dataclasses import dataclass, field
# Asumiendo que este módulo sigue existiendo en tu entorno
try:
    from data.lista_json import productos as cat_prod_default
except ImportError:
    cat_prod_default = []


@dataclass
class OllamaClassifier:
    """
    Clase para interactuar con la API de Ollama y clasificar pedidos de una pizzería.
    
    Attributes:
        url (str): URL del endpoint de generación de Ollama.
        model_name (str): Nombre del modelo a utilizar.
        productos (list): Lista de productos disponibles para normalización.
        entrada (dict | None): Datos de la solicitud actual.
        prompt (str): Prompt generado dinámicamente.
        payload (dict): Payload enviado a la API.
    """

    # Campos con valores por defecto
    url: str = "http://100.113.65.40:11434/api/generate" 
    model_name: str = "qwen-27b-coding:latest"
    
    # Usamos field para inicializar con el valor cargado dinámicamente o vacío si falla
    productos: list = field(default_factory=lambda: cat_prod_default)
    
    entrada: dict | None = None
    prompt: str = ""
    payload: dict = field(default_factory=dict)

    def __post_init__(self):
        """
        Se ejecuta automáticamente después de la inicialización del dataclass.
        Aquí podemos añadir lógica extra si fuera necesario, 
        aunque en este caso los valores por defecto ya manejan el import seguro.
        Si se requiere recargar productos dinámicamente al iniciar:
        """
        # Opcional: Reintentar importar aquí si la carga inicial falló pero queremos ser más estrictos
        if not self.productos and hasattr(self, 'productos'):
            try:
                from data.lista_json import productos as prod_temp
                object.__setattr__(self, 'productos', prod_temp) # Forzar asignación en dataclass inmutable si fuera necesario (no es el caso aquí por default_factory)
            except ImportError:
                print("Advertencia: No se pudo importar 'lista_json'. Usando catálogo vacío.")

    def extraer_json(self, texto: str) -> dict:
        """
        Extrae un objeto JSON válido de la respuesta cruda del LLM.
        
        Args:
            texto (str): Respuesta textual que puede contener Markdown o ruido.
            
        Returns:
            dict: Objeto JSON parseado.
            
        Raises:
            ValueError: Si no se encuentra JSON válido en el texto.
        """
        texto = texto.strip()

        if not texto:
            raise ValueError("La respuesta del modelo vino vacía.")

        try:
            # Intento de parse directo (funciona si la salida es limpia)
            return json.loads(texto)
        except json.JSONDecodeError:
            inicio = texto.find("{")
            fin = texto.rfind("}")

            if inicio == -1 or fin == -1 or fin <= inicio:
                raise ValueError("No se encontró un objeto JSON en la respuesta del modelo.")

            # Extrae substring entre el primer '{' y el último '}' para eliminar Markdown/relleno
            return json.loads(texto[inicio:fin + 1])

    def consultar_ollama(self, entrada_dict: dict) -> dict:
        """
        Envía una solicitud de clasificación a la API de Ollama.
        
        Args:
            entrada_dict (dict): Diccionario con los detalles del input del cliente.
            
        Returns:
            dict: Estructura JSON procesada por el modelo y extraída.
        """
        # Actualizamos el atributo de instancia para trazabilidad si es necesario
        self.entrada = entrada_dict

        prompt_template = f"""Sos un clasificador de pedidos para una pizzería.
Devolvé únicamente JSON válido.
No expliques nada.
No uses Markdown.

Catálogo disponible (para normalizar nombres y tamaños):
{json.dumps(self.productos, ensure_ascii=False)}

JSON de entrada:
{json.dumps(entrada_dict, ensure_ascii=False)}

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

        self.prompt = prompt_template
        
        payload_data = {
            "model": self.model_name, # Usamos el atributo del dataclass
            "prompt": self.prompt,
            "stream": False,          
            "keep_alive": "2h",       
            "think": False,           
            "format": "json",         
            "options": {
                "temperature": 0,     
                "num_predict": 150,   
                "num_ctx": 8192       
            }
        }

        self.payload = payload_data
        response = requests.post(
            self.url, # Usamos el atributo del dataclass
            json=payload_data,
            timeout=180  
        )

        # Levantar excepción si el código de estado HTTP indica fallo (4xx/5xx)
        response.raise_for_status()

        data = response.json()
        
        # Extraer el campo 'response' que contiene el texto generado por Ollama
        texto_respuesta = data.get("response", "")

        return self.extraer_json(texto_respuesta)

    def query(self, mensaje: str, cliente_id=None, canal="whatsapp") -> dict:
        """
        Punto de entrada (entry point). Prepara la estructura de entrada y ejecuta la consulta.
        
        Args:
            mensaje (str): Mensaje del usuario.
            cliente_id (int | str, optional): ID único del cliente. Defaults to None.
            canal (str, optional): Canal de comunicación. Defaults to "whatsapp".
            
        Returns:
            dict: Resultado procesado por el modelo.
            
        Raises:
            Exception: Propaga cualquier error de red o procesamiento interno.
        """
        entrada_data = {
            "mensaje": mensaje,
            "cliente_id": cliente_id if cliente_id is not None else 0, # Default a 0 si no se pasa
            "canal": canal
        }

        return self.consultar_ollama(entrada_data)


# Ejemplo de uso como script principal
if __name__ == "__main__":
    try:
        # Inicializar la clase (ahora es un dataclass, se puede pasar argumentos nombrados fácilmente)
        classifier = OllamaClassifier()

        # Simular una consulta usando el método query
        resultado = classifier.query(
            mensaje="mandame 4 empanadas de verdura", 
            cliente_id=123, 
            canal="whatsapp"
        )
        
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    except Exception as e:
        # Capturar errores de red, parsing JSON o problemas del modelo
        print("Error:", e)
