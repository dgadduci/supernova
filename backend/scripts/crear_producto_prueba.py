from sqlalchemy import select

from backend.database.connection import SessionLocal
from backend.models.categoria_producto import CategoriaProducto
from backend.models.comercio import Comercio
from backend.services.producto_service import (
    ProductoDuplicadoError,
    ProductoService,
)


COMERCIO_SLUG = "supernova-pizza"
CATEGORIA_DESCRIPCION = "Pizzas"


def main() -> None:
    try:
        with SessionLocal() as session:
            with session.begin():
                comercio = session.scalar(
                    select(Comercio).where(
                        Comercio.slug == COMERCIO_SLUG
                    )
                )

                if comercio is None:
                    raise RuntimeError(
                        f"No existe el comercio {COMERCIO_SLUG!r}"
                    )

                categoria = session.scalar(
                    select(CategoriaProducto).where(
                        CategoriaProducto.id_comercio == comercio.id,
                        CategoriaProducto.descripcion
                        == CATEGORIA_DESCRIPCION,
                    )
                )

                if categoria is None:
                    raise RuntimeError(
                        f"No existe la categoría "
                        f"{CATEGORIA_DESCRIPCION!r}"
                    )

                service = ProductoService(session)

                producto = service.crear_producto(
                    id_categoria_producto=categoria.id,
                    nombre="Pizza Mozzarella",
                    descripcion=(
                        "Pizza con salsa de tomate y mozzarella"
                    ),
                    activo=True,
                    disponible=True,
                    orden=1,
                )

            # Al salir de session.begin() sin error se hace commit.
            session.refresh(producto)

            print("Producto creado correctamente")
            print(f"ID: {producto.id}")
            print(f"Nombre: {producto.nombre}")
            print(f"Categoría ID: {producto.id_categoria_producto}")
            print(f"Activo: {producto.activo}")
            print(f"Disponible: {producto.disponible}")

    except ProductoDuplicadoError as exc:
        print(f"El producto ya existe: {exc}")

    except Exception as exc:
        print(f"Error al crear el producto: {exc}")
        raise


if __name__ == "__main__":
    main()