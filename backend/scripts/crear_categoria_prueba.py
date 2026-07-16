from sqlalchemy import select

from backend.database.connection import SessionLocal
from backend.models.comercio import Comercio
from backend.services.categoria_producto_service import (
    CategoriaDuplicadaError,
    CategoriaProductoService,
)


COMERCIO_SLUG = "supernova-pizza"


def main() -> None:
    with SessionLocal() as session:
        try:
            comercio = session.scalar(
                select(Comercio).where(
                    Comercio.slug == COMERCIO_SLUG
                )
            )

            if comercio is None:
                raise RuntimeError(
                    f"No existe el comercio {COMERCIO_SLUG!r}"
                )

            service = CategoriaProductoService(session)

            categoria = service.crear_categoria(
                id_comercio=comercio.id,
                descripcion="Pizzas",
                orden=1,
                activo=True,
            )

            session.commit()
            session.refresh(categoria)

            print("Categoría creada correctamente")
            print(f"ID: {categoria.id}")
            print(f"Descripción: {categoria.descripcion}")

        except CategoriaDuplicadaError as exc:
            session.rollback()
            print(f"La categoría ya existe: {exc}")

        except Exception:
            session.rollback()
            raise

if __name__ == "__main__":
    main()