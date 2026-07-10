from dataclasses import dataclass

from query_llm import QueryLlm


@dataclass
class IntentClassifier :
    _message : str = None
    _prompt : str = None
    _intents = """
* Si el cliente saluda = `saludo`
* Si el cliente agradece = `agradecimiento`
* Si el cliente se despide o da por terminada la conversación = `despedida`
* Si responde afirmativamente a una pregunta previa = `respuesta_afirmativa`
* Si responde negativamente a una pregunta previa = `respuesta_negativa`
* Si quiere ver la carta o menú = `ver_menu`
* Si consulta por un producto, precio, tamaño, variante, ingredientes o disponibilidad = `consultar_producto`
* Si consulta por los medios de pago aceptados = `ver_metodos_de_pago`
* Si consulta por las formas de entrega disponibles = `ver_metodos_de_entrega`
* Si consulta el domicilio o ubicación del comercio = `consultar_domicilio_comercio`
* Si consulta los días u horarios de atención = `consultar_horarios_comercio`
* Si quiere comenzar un pedido pero todavía no indica productos = `iniciar_pedido`
* Si quiere agregar uno o más productos al pedido = `agregar_producto`
* Si quiere quitar uno o más productos del pedido = `quitar_producto`
* Si quiere sustituir o modifiar un producto por otro producto distinto, se deben generar dos intents, en este orden:
  1. `quitar_producto`, con el producto que desea retirar.
  2. `agregar_producto`, con el nuevo producto que desea incorporar.
* Si quiere eliminar todos los productos del pedido actual = `vaciar_pedido`
* Si quiere agregar, modificar o eliminar una aclaración sobre un producto = `set_observacion_producto`
* Si quiere agregar, modificar o eliminar una aclaración general del pedido = `set_observacion_pedido`
* Si quiere consultar los productos cargados, cantidades, subtotal o resumen del pedido actual = `consultar_resumen_pedido`
* Si establece o cambia la forma de entrega, como delivery, retiro en local o consumo en salón = `set_metodo_de_entrega`
* Si establece o cambia el domicilio de entrega = `set_direccion_entrega`
* Si establece, cambia o elimina la fecha u hora programada del pedido = `set_fecha_hora_entrega`
* Si establece o cambia el medio de pago = `set_metodo_de_pago`
* Si quiere confirmar y enviar definitivamente el pedido = `confirmar_pedido`
* Si consulta el estado de un pedido ya confirmado = `consultar_estado_pedido`
* Si quiere cancelar un pedido ya confirmado = `cancelar_pedido`
* Si el mensaje no puede interpretarse con suficiente seguridad = `desconocida`

* Las intents deben conservar el orden en que deben ejecutarse.

Ejemplo:

Mensaje:

`Cambiame la pizza de mozzarella por una napolitana`

Salida:

```json
{
  "intents": [
    {
      "intent": "quitar_producto",
      "mensaje": "pizza de mozzarella"
    },
    {
      "intent": "agregar_producto",
      "mensaje": "pizza napolitana"
    }
  ],
  "mensaje": "Cambiame la pizza de mozzarella por una napolitana"
}
```

"""
    _output_struct = """
Devolvé únicamente JSON válido.
No expliques nada.
No uses Markdown.
ejemplo: 
{
    "intents": [
        {
            "intent": "agregar_producto",
            "mensaje: "una empanada de carne"
        },
        {
            "intent": "agregar_producto",
            "mensaje: "dos pizzas de mozzarella"
        },
        {
            "intent": "set_metodo_de_envio",
            "mensaje: " me la envies a tilcara 2020."
        },{
            "intent": "set_forma_de_pago",
            "mensaje": "Pago en efectivo"            
        }
    ]
    "mensaje" : "quiero una empanada de carne y dos pizzas de mozzarella y que me la envies a tilcara 2020. Pago en efectivo"
}
"""    
    
    def _generate_prompt(self):
        self._prompt = f"""
Catálogo de posibles intents:
{self._intents}

message
{self._message}

Instrucciones
Debes devolver del Catalogo de intents, los intent que mejor se adapten al mensaje, siguiendo la estructura json que te envio de ejemplo
Tambien debes devolver el message recibido
Si el mensaje incluye varios intents, envialos como en el ejemplo del json
Cuando detectes que se pide reemplazar un producto por otro, genera dos intentes: uno para quitar el producto que se quiere reemplazar y otro para agregar el producto con el que sera reemplazado
Cuando se trate de productos, separalos por producto y cantidad (si se especifica) en distintos intents
{self._output_struct}
"""
    
    def query(self, message: str) :
        self._message = message
        self._generate_prompt()
        query_llm = QueryLlm(prompt=self._prompt)
        return query_llm.request_llm(message)

if __name__ == "__main__":
    classifier = IntentClassifier()
    while True :
        mensaje = input("Mensaje:")
        intent = classifier.query(mensaje)
        print(intent)
    
