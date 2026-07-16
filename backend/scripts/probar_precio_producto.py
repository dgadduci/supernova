from backend.database.connection import SessionLocal
from backend.services.producto_presentacion_service import (
    PrecioInvalidoError,
    PrecioSinCambiosError,
    ProductoPresentacionNoExisteError,
    establecer_precio,
    obtener_historial_precios,
)


ID_PRODUCTO_PRESENTACION = 1


def main() -> None:
    with SessionLocal() as session:
        try:
            precio = establecer_precio(
                session,
                id_producto_presentacion=ID_PRODUCTO_PRESENTACION,
                precio="13500.00",
            )

            print("Precio registrado correctamente")
            print(f"ID: {precio.id}")
            print(f"Precio: {precio.precio}")
            print(f"Vigencia desde: {precio.vigencia_desde}")

        except ProductoPresentacionNoExisteError as exc:
            print(f"Error: {exc}")
            return

        except PrecioInvalidoError as exc:
            print(f"Error: {exc}")
            return

        except PrecioSinCambiosError as exc:
            print(f"Sin cambios: {exc}")
            return

    with SessionLocal() as session:
        historial = obtener_historial_precios(
            session,
            ID_PRODUCTO_PRESENTACION,
        )

        print("\nHistorial de precios:")

        for registro in historial:
            print(
                f"- ${registro.precio} | "
                f"desde={registro.vigencia_desde} | "
                f"hasta={registro.vigencia_hasta}"
            )


if __name__ == "__main__":
    main()