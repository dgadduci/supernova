from clases import Cliente, Comercio
from intent_classifier import IntentClassifier
from intent_hacer_pedido import IntentHacerPedido


if __name__ == "__main__":
    try:
        """
        classifier = IntentClassifier()
        result = classifier.query(
            message="quiero agregar 1 empanada al pedido"
        )
        print(result)
        print(result["intent"])
        """
        
        while True:
            entrada = input("Ingresa un string (o 'exit' para salir): ")
            
            if entrada == "exit":
                break
            comercio = Comercio(
                    id = 1,
                    nombre="Supernova"
                )
            cliente = Cliente(id=10, nombre="Diego",calle="Montiel",numeracion="5104")
            
            #Recien lo voy a llamar cuando tengo el pedido resuelto
            """
            new_pedido = IntentHacerPedido()
            a = new_pedido.query(
                message = entrada,
                comercio = comercio ,
                cliente= cliente
            )
            print(a)
            """
            
    except Exception as e:
        print("Error:",e)
