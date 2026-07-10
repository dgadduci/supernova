from logica_fuzzy_pedido_productos import detectar_productos
import json

def main():
    pedido = None
    def make_pedido_productos() -> dict:
        """
        Loop interactivo que resuelve ambigüedades hasta completar el pedido.
        - Muestra items encontrados (únicos) y los agrupa en productos_final
        - Si hay ambigüedades (encontrados_posibles), pide aclaración por teclado
        - Si hay no_disponibles o no_encontrados, también pide aclaración
        - Finaliza cuando todos los items son unívocos y se encontraron
        """

        productos_final = {
            "encontrados":               [],
            "encontrados_no_disponibles": [],
            "no_encontrados":            []
        }

        input_usuario = input("Ingrese su pedido: ")

        while True:
            # Llamamos al sistema de fuzzy matching - passing productos as keyword argument
            resultado_json = detectar_productos(input_usuario)
            pedido_temp = json.loads(resultado_json)

            # Items que podemos aceptar definitivamente (unívocos y disponibles)
            encontrados_actual = pedido_temp.get("encontrados", [])
            encontrados_no_disponibles_actual = pedido_temp.get("encontrados_no_disponibles", [])
            no_encontrados_actual = pedido_temp.get("no_encontrados", [])

            # Los agregamos al acumulado final
            productos_final["encontrados"].extend(encontrados_actual)
            #productos_final["encontrados_no_disponibles"].extend(encontrados_no_disponibles_actual)
            #productos_final["no_encontrados"].extend(no_encontrados_actual)

            # Limpiamos de pedido_temp lo que ya procesamos
            if "encontrados" in pedido_temp: del pedido_temp["encontrados"]
            if "encontrados_no_disponibles" in pedido_temp: del pedido_temp["encontrados_no_disponibles"]
            if "no_encontrados" in pedido_temp: del pedido_temp["no_encontrados"]

            encontrados_posibles = pedido_temp.get("encontrados_posibles", [])

            # ¿Seguimos o terminamos?
            hay_problemas = (
                len(encontrados_posibles) > 0 or
                len(no_encontrados_actual) > 0 or
                len(encontrados_no_disponibles_actual) > 0
            )

#            if not hay_problemas:
#                # Pedido resuelto completamente
#                break

            # --- Mostrar lo que necesita atención y pedir aclaración ---

            print("\n══════════════════════════════════════════════════")
            print("SE NECESITA ACLARACIÓN\n" + "="*48)

            # 1. Ambigüedades (más de una opción)
            if encontrados_posibles:
                print("\n⚠️  Ambigüedad detectada – elegí una opción por cada frase:\n")
                for grupo in encontrados_posibles:
                    texto_origen = grupo["texto_origen"]
                    opciones = grupo["productos"]
                    print(f"   Para el pedido: '{texto_origen}'\n")
                    for i, opt in enumerate(opciones, 1):
                        p = opt
                        nombre = p["nombre_producto"]
                        tamanio = f", {p['tamanio']}" if "tamanio" in p else ""
                        precio = p.get("precio", "N/A")
                        print(f"     {i}) {nombre}{tamanio} (${precio})")
                    # Input numérico simple para elegir
                    while True:
                        eleccion = input(f"\n   ¿Cuál elegís (1-{len(opciones)})? ").strip()
                        if eleccion.isdigit() and 1 <= int(eleccion) <= len(opciones):
                            indice_elegido = int(eleccion) - 1
                            elegido = opciones[indice_elegido]
                            productos_final["encontrados"].append(elegido)
                            break
                        print("   ❌ Opción inválida, intentá de nuevo.")

            # 2. Items no disponibles pero detectados (pregunta si quiere reescribir s/n)
            if encontrados_no_disponibles_actual:
                print("\n⚠️  Productos NO DISPONIBLES:\n")
                for p in encontrados_no_disponibles_actual:
                    nombre = p["nombre_producto"]
                    tamanio = f", {p['tamanio']}" if "tamanio" in p else ""
                    print(f"   • {nombre}{tamanio}")
                
                # Pregunta s/n igual que en no_encontrados
                respuesta = input("\n¿Deseás cambiarlo por otro producto? (s/n) ").lower().strip()
                if respuesta == "s":
                    input_usuario = input("Re-escribí el pedido con otros productos: ")
                    continue

            # 3. Frases no encontradas en catálogo
            if no_encontrados_actual:
                print("\n❌ No pudimos encontrar lo siguiente:\n")
                for item in no_encontrados_actual:
                    texto_origen = item.get("texto_origen", "")
                    print(f"   • '{texto_origen}'")
                
                respuesta = input("\n¿Querés re-escribirlos? (s/n) ").lower().strip()
                if respuesta == "s":
                    input_usuario = input("Re-escribí el pedido con otra redacción: ")
                    continue

            print("\n══════════════════════════════════════════════════")

            # Si seguimos aquí, queremos más aclaraciones en general (por ejemplo,
            # el usuario corrigió la ambigüedad pero todavía quedan items no encontrados)
            input_usuario = input("Agrega un nuevo producto o 'fin' para terminar: ")
            if input_usuario.lower() == "fin":
                break

        # ── Salida final ───────────────────────────────────────────────────────
        print("\n" + "="*60)
        print("PRODUCTOS DEL PEDIDO\n" + "="*60)
        print(json.dumps(productos_final, indent=2, ensure_ascii=False))
        return productos_final
        
    pedido = make_pedido_productos()
    print("\n" + "="*60)
    print("PEDIDO COMPLETO\n" + "="*60)
    print(json.dumps(pedido, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
