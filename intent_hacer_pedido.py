from dataclasses import asdict, dataclass, field
import json
from typing import List

from clases import Cliente, Comercio, Producto
from backend.llm.query_llm import QueryLlm

try:
    from backend.data.lista_json import productos as cat_prod_default
except ImportError:
    cat_prod_default = []

@dataclass
class IntentHacerPedido:
    _cliente : Cliente = None
    _comercio : Comercio = None
    _message : str = None
    _prompt : str = None
    _lista_productos: list = field(default_factory=lambda: cat_prod_default)    
    _output_struct = f"""
Devolvé únicamente JSON válido.
No expliques nada.
No uses Markdown.
Devolvé únicamente el objeto JSON crudo. 
NO uses bloques de código (no uses ```json).
NO incluyas texto introductorio ni explicaciones.
El resultado debe empezar con '{' y terminar con '}'.
"""    
    
    
    def _generate_prompt(self):
        self._prompt = f"""Actúa como un analista de datos de pedidos para una pizzería/restaurant.
Tu trabajo es EXTRAER información del mensaje y mapearla al catálogo. NO resuelvas ambigüedades complejas, solo reporta lo que encuentras y lo que no.

Catálogo de productos (JSON):
{json.dumps(self._lista_productos, ensure_ascii=False)}

Mensaje del cliente: "{self._message}"

Debes analizar el mensaje palabra por palabra y devolver únicamente un JSON con esta estructura EXACTA:

{{
  "mensaje_original": "{{copiar literalmente el mensaje del cliente}}",
  "productos_completos": [
    {{
      "id_catalogo": "ID del catálogo",
      "nombre_detectado": "Nombre exacto del catálogo (no variaciones)",
      "cantidad": <número>,
      "talla": "<talla exacta del catálogo>" 
    }}
  ],
  "productos_parciales": [
    {{
      "texto_original": "{{lo que dijo el usuario, ej: 'dos diabolos'}}",
      "id_catalogo_match": "ID más parecido (si lo encontraste)",
      "nombre_sugerido": "Nombre exacto del catálogo",
      "cantidad_detectada": <número o null>,
      "falta_especificar": ["talla"] 
    }}
  ],
  "productos_no_encontrados": [
    "{{texto literal que dijo el usuario y no reconociste}}"
  ]
}}

REGLAS DE NEGOCIO Estrictas:
1. COINCIDENCIA EXACTA FUERTE: Solo asigna a 'productos_completos' si la coincidencia de nombre es alta (>90%) Y se indica cantidad.
2. TALLAS AMBIGUAS: Si el usuario dice "un diablo" y hay Diablo chico, mediano y grande, NO inventes una talla. Ponlo en 'productos_parciales' con falta_especificar=["talla"].
3. FALTA CANTIDAD: Si dice "quiero una coca de 1L" pero no dice cuántas (aunque sea "una", es singular), si no hay número explícito, ponlo parcial con falta ["cantidad"].

REGLAS AVANZADAS DE COMPRENSIÓN DE LENGUAJE (COREFERENCE):
Antes de buscar un producto en el catálogo, debes resolver los pronombres y sustantivos omitidos.
- Si ves "y una de carne", "otra", "dos más" o similares, identifica que se refieren al SUSTANTIVO PRINCIPAL del último producto mencionado.
  - Ejemplo: "Quiero una empanada de atún y una de carne". -> El segundo "una" se refiere a "empanada". Busca "empanada de carne".
  - Ejemplo: "Dos pizzas, una mozzarella y otra de pepperoni". -> "otra" = pizza.

REGLA CRÍTICA DE NORMALIZACIÓN Y TILDACIÓN:
- Ignorá errores ortográficos comunes en comida (ej: "muzzarela" = "mozzarella", "muzza" = "mozzarella").
- Ignorá adjetivos calificativos que no cambian el producto base. Si el catálogo dice "Pizza Mozzarella con Albahaca", considerá válido si el usuario pide:
  - "pizza mozzarella"
  - "muzzarela"
  - "piza mozza" (coincidencia alta)

INSTRUCCIÓN DE DESCOMPOSICIÓN DE NOMBRES (OBLIGATORIA):
Para buscar en el catálogo, descomponé los nombres de los productos en "Base" y "Sabor" antes de comparar.
- Ejemplo: Si el catálogo tiene "Empanada de Carne", "Empanada de Jamón", "Empanada de Atún":
  - El usuario pide "2 de carne".
  - Tu lógica debe entender que "de carne" implica la base "Empanada" (porque es la única base que usa preposición "de" + sabor en tu catálogo) y el sabor "Carne".
- Si tu catálogo tiene "Pizza Margarita", "Pizza Mozzarella":
  - El usuario pide "una de mozzarella".
  - Tu lógica debe entender que la base es "Pizza" y el sabor es "Mozzarella".

PROCEDIMIENTO DE BÚSQUEDA POR INFERENCIA:
1. Identificá los sustantivos del mensaje ("carne", "mozza").
2. Buscá en el catálogo qué productos contienen esa palabra exacta o fonéticamente similar dentro de su nombre.
3. Si encontrás solo un tipo de producto que contiene esa palabra (ej: solo empanadas tienen "de Carne"), asumiendo que la base es ese producto y la talla es la predeterminada (si existe).
  
REGLA DE EXCLUSIÓN DE VARIANTES INNECESARIAS:
- Si un producto en el catálogo es "X con [Ingrediente Adicional]", y el usuario pide "X", son EL MISMO PRODUCTO. Ignorá "[Ingrediente Adicional]" para la búsqueda.
- Ejemplo: "Pizza Mozzarella con Albahaca" coincide con "pizza mozzarella".

REGLA DE EXCLUSIÓN MUTUA ESTRICTA:
Cada ítem del mensaje debe caer en una ÚNICA categoría. Sigue este orden de decisión secuencial para cada producto:

1. ¿Encontraste un match seguro (>90% similitud) y la información es completa (ID, Nombre, Cantidad)?
   -> Envía a "productos_completos". FIN. (Prohibido tocar otras listas).

2. ¿Encontraste un match probable (>70% similitud) pero faltan datos críticos (talla, tipo de producto)?
   -> Envía a "productos_parciales". FIN. 
   -> IMPORTANTE: Aunque el nombre no sea exacto o falte el tipo (ej: "de carne" sin saber si es pizza o empanada), SI hay una posibilidad real de coincidencia en el catálogo, ESTO ES UN PARCIAL. NO es un inexistente.

3. ¿Es imposible encontrar relación alguna con el catálogo?
   -> Recién aquí envía a "inexistentes".

PROHIBICIÓN ABSOLUTA:
- Si un producto está en `parciales_con_talla_ambigua`, NUNCA puede estar también en `inexistentes`.
- Si un producto tiene `id_catalogo_match` = None pero hay palabras clave que existen en el catálogo (ej: "carne" existe en productos), va a PARCIAL, no a INEXISTENTE.

EJEMPLO CORRECTO DE TU CASO:
Texto: "mandame 2 de carne"
Interpretación Interna: El usuario quiere "empanadas de carne" o "pizzas de carne". Como "carne" es un ingrediente válido en mi catálogo, pero no sé el tipo (pizza vs empanada) ni la talla, esto es UN PARCIAL.
JSON Resultado para este ítem: Solo aparece UNA vez en `parciales_con_talla_ambigua`. NO aparece en `inexistentes`.

EJEMPLO DE CORRECCIÓN AUTOMÁTICA (NO INCLUIR EN SALIDA):
Usuario dice: "muzzarela"
Tu lógica interna debe mapear -> "Pizza Mozzarella con Albahaca" en el catálogo.

PROCEDIMIENTO OBLIGATORIO ANTES DE EXTRAER JSON:
1. Lee la frase completa.
2. Expande todos los pronombres (reemplaza "una", "otra", "uno" por el nombre del producto real).
3. Recién después de hacer esta corrección interna, busca en el catálogo.

EJEMPLO DE INTERPRETACIÓN CORRECTA:
Texto: "Dos gaseosas y una empanada de carne".
Interpretación Interna del Modelo (NO devolver esto):
   - Producto 1: "gaseosa", cantidad: 2
   - Producto 2: "empanada de carne", cantidad: 1

IMPORTANTE: Devuelve SOLO el JSON válido. Sin explicaciones.
"""

    def query(self, message: str, comercio: Comercio, cliente: Cliente):
        self._message = message
        self._comercio = comercio
        self._cliente = cliente
        self._generate_prompt()
        
        # Ejecutar la consulta
        query_llm = QueryLlm(prompt=self._prompt)
        respuesta_raw = query_llm.request_llm(message)
        
        return self._parse_response(respuesta_raw)

    def _parse_response(self, respuesta_raw):
        """Transforma el JSON de la IA al formato final"""
        try:
            # Check if the response is already a dictionary. 
            # If so, use it directly. Otherwise, parse it from string.
            if isinstance(respuesta_raw, dict):
                datos = respuesta_raw
            else:
                datos = json.loads(respuesta_raw)

            return {
                "completos": datos.get("productos_completos", []),
                "parciales_con_talla_ambigua": [p for p in datos.get("productos_parciales", []) if "talla" in p.get("falta_especificar")],
                "parciales_sin_cantidad": [p for p in datos.get("productos_parciales", []) if "cantidad" in p.get("falta_especificar")],
                "inexistentes": datos.get("productos_no_encontrados", []),
                "mensaje_original": datos.get("mensaje_original", "")
            }

        except (json.JSONDecodeError, AttributeError) as e:
            return {"error": f"Procesamiento de respuesta falló: {e}", "raw": respuesta_raw}            
        except json.JSONDecodeError:
            return {"error": "La IA no devolvió JSON válido", "raw": respuesta_raw}