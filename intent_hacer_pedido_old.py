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
class IntentHacerPedido :
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
        self._prompt = f"""Sos un despachador de pedidos de un comercio de comidas.

Catálogo de productos disponible (para normalizar nombres y tamaños):
{json.dumps(self._lista_productos, ensure_ascii=False)}

Datos del comercio de comidas
{json.dumps(asdict(self._comercio), ensure_ascii=False)}

Datos del cliente que hace el pedido
{json.dumps(asdict(self._cliente), ensure_ascii=False)}

message
{self._message}

Instrucciones
-Debes armar el pedido que se te solicita en el message, usando la lista de productos que se te provee 
-Los campos de los productos deben respetar el de lista de productos y debes incluir 
Id
nombre_producto
cantidad
tamanio (si corresponde)
-Tambien debes devolver el message recibido

Estructura obligatoria de salida:
{self._output_struct}

json devuelto:
    mensaje : mensaje recibido
    productos_validos : Lista de productos validos (id, nombre_producto, cantidad, tamanio(si corresponde))
    productos_inexistentes: producto inexistente
    productos_no_disponibles: incluir únicamente productos cuya variante exacta solicitada exista en el catálogo pero tenga disponible=false. No incluir variantes de otro tamaño.
    productos_a_confirmar_tamanio (solicitado, posible id, posible nombre_producto, posible_Cantidad, posible tamanio)
    productos_a_confirmar_descripcion (solicitado, posible id, posible nombre_producto, posible_Cantidad, posible tamanio)

Reglas:
- Usa en el json que generas los nombres exactos del catálogo para 'producto_normalizado'.
- Si la cantidad no es explícita, usá 1.
- Orden a seguir para guardar en el json los productos del pedido (solo puede ser guardado en una sola key, es decir que una vez que lo guardas en una posible key del json, debes seguir con el proximo producto. 

REGLA PRIORITARIA DE NORMALIZACIÓN:
Antes de clasificar un producto como inexistente, corregí errores ortográficos, fonéticos o de tipeo del mensaje del cliente.
Ejemplos:
- "diabola" debe considerarse equivalente a "Diavola"
- "muzza" debe considerarse equivalente a "Mozzarella"
- "coca" debe considerarse equivalente a "Coca Cola"
Si el producto solicitado tiene una coincidencia razonable con un nombre_producto del catálogo, NO puede agregarse a productos_inexistentes.
Un producto solo puede ir a productos_inexistentes cuando no exista ninguna coincidencia razonable, ni exacta, ni aproximada, ni fonética, ni por error ortográfico con ningún producto del catálogo.

ÁRBOL DE DECISIÓN OBLIGATORIO PARA CADA PRODUCTO SOLICITADO:

1. Extraer el producto solicitado del mensaje.
2. Normalizar el texto corrigiendo errores ortográficos, abreviaturas, nombres coloquiales y equivalencias fonéticas.
3. Buscar coincidencias exactas o razonables en el catálogo por nombre_producto.
4. Si hay una o más coincidencias razonables:
   a) Si existe una sola variante:
      - si disponible=true, agregar a productos_validos.
      - si disponible=false, agregar a productos_no_disponibles.
   b) Si existen varias variantes:
      - si el cliente indicó tamaño, elegir solo la variante de ese tamaño.
      - si el cliente no indicó tamaño, agregar todas las variantes posibles a productos_a_confirmar_tamanio.
   c) Prohibido agregar ese producto a productos_inexistentes.
5. Si no hay ninguna coincidencia razonable, agregar recién ahí a productos_inexistentes.

REGLA DE EXCLUSIÓN ABSOLUTA:
Cada producto solicitado debe terminar en una sola categoría del JSON.
Si un producto fue agregado a:
- productos_validos
- productos_no_disponibles
- productos_a_confirmar_tamanio
- productos_a_confirmar_descripcion
entonces queda prohibido agregarlo también a productos_inexistentes.
productos_inexistentes solo debe usarse cuando no haya ningún posible producto del catálogo relacionado con lo pedido.

Regla de resolución de productos:
- Por cada producto solicitado en el mensaje, primero identificar todos los productos del catálogo que coincidan con el nombre normalizado.
- Luego, si el cliente indicó tamaño, elegir únicamente el producto cuyo tamanio coincida exactamente o sea equivalente semánticamente con el tamaño solicitado.
- Una vez encontrada una coincidencia exacta de nombre y tamaño, NO seguir comparando ese producto solicitado contra otros tamaños del mismo producto.
- Cada producto solicitado puede aparecer en una sola key del JSON y una sola vez.
- Los tamaños distintos al solicitado NO deben agregarse a productos_no_disponibles si existe una variante del mismo producto con el tamaño solicitado.
- Solo usar productos_a_confirmar_tamanio cuando el producto existe pero el cliente no indicó tamaño y hay más de una variante posible.
- Solo usar productos_no_disponibles cuando la variante exacta solicitada existe en el catálogo pero tiene disponible=false.
- Solo usar productos_inexistentes cuando no existe ningún producto del catálogo que coincida razonablemente con el producto solicitado.

REGLA PRIORITARIA SOBRE TAMAÑO:
Si el producto solicitado existe en el catálogo con más de un tamanio posible y el cliente NO indicó tamaño en el mensaje, NO elegir ningún tamaño por defecto.
En ese caso:
- NO agregar ningún producto a productos_validos.
- Agregar TODAS las variantes disponibles de ese producto a productos_a_confirmar_tamanio.
- El producto solicitado debe quedar únicamente en productos_a_confirmar_tamanio.
- No asumir "chico", "grande", "unidad", "lata" ni ningún otro tamaño si no fue dicho explícitamente por el cliente.

Los campos de los productos deben respetar el de lista de productos y debes incluir 
Id
nombre_producto
cantidad
tamanio (si corresponde)
antes de incluir en el json devuelto, confirmar que no haya sido agregado antes al json. Si ya existe en el json, no agregar
"""
    
    def query(self, message: str, comercio: Comercio, cliente: Cliente) :
        self._message = message
        self._comercio = comercio
        self._cliente = cliente
        self._generate_prompt()
        print(self._prompt)
        query_llm = QueryLlm(prompt=self._prompt)
        return query_llm.request_llm(message)
