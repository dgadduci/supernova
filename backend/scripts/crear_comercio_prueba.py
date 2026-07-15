from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database.connection import SessionLocal
from backend.models.comercio import Comercio
from backend.services.comercio_service import (
    ComercioDuplicadoError,
    crear_comercio,
)


def main() -> None:
    with SessionLocal() as session:
        try:
            comercio = crear_comercio(
                session,
                nombre_fantasia="Supernova Pizza y Empanadas",
                nombre_corto="Supernova",
                razon_social="Supernova Gastronomía",
                cuit="20-12345678-9",
                whatsapp="5491160000001",
                calle="Cañada de Gomez",
                numero="4999",
                piso_departamento=None,
                localidad="Ciudad Autónoma de Buenos Aires",
                provincia="Ciudad Autónoma de Buenos Aires",
                codigo_postal="C1439",
                slug="supernova-pizza",
            )

            print("Comercio creado correctamente")
            print(f"ID: {comercio.id}")
            print(f"Nombre: {comercio.nombre_fantasia}")
            print(f"Slug: {comercio.slug}")
            print(f"Estado: {comercio.estado.value}")

        except ComercioDuplicadoError as exc:
            print(f"No se creó el comercio: {exc}")
            return

    # Abrimos otra sesión para verificar que los datos fueron persistidos.
    with SessionLocal() as session:
        comercio = session.scalar(
            select(Comercio)
            .options(
                selectinload(Comercio.metodos_entrega)
            )
            .where(Comercio.slug == "supernova-pizza")
        )

        if comercio is None:
            print("El comercio no fue encontrado")
            return

        print("\nMétodos de entrega configurados:")

        for configuracion in comercio.metodos_entrega:
            print(
                f"- Método ID {configuracion.id_metodo_entrega}: "
                f"activo={configuracion.activo}, "
                f"orden={configuracion.orden}"
            )


if __name__ == "__main__":
    main()