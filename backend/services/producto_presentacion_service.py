from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models.producto_precio import ProductoPrecio
from backend.models.producto_presentacion import ProductoPresentacion


class ProductoPresentacionNoExisteError(Exception):
    """La presentación de producto indicada no existe."""


class PrecioInvalidoError(Exception):
    """El precio recibido no es válido."""


class PrecioSinCambiosError(Exception):
    """El nuevo precio es igual al precio vigente."""


def _normalizar_precio(
    precio: Decimal | int | float | str,
) -> Decimal:
    try:
        precio_normalizado = Decimal(str(precio)).quantize(
            Decimal("0.01")
        )
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise PrecioInvalidoError(
            f"El precio {precio!r} no es válido"
        ) from exc

    if precio_normalizado < 0:
        raise PrecioInvalidoError(
            "El precio no puede ser negativo"
        )

    return precio_normalizado


def obtener_precio_vigente(
    session: Session,
    id_producto_presentacion: int,
) -> ProductoPrecio | None:
    return session.scalar(
        select(ProductoPrecio).where(
            ProductoPrecio.id_producto_presentacion
            == id_producto_presentacion,
            ProductoPrecio.vigencia_hasta.is_(None),
        )
    )


def obtener_historial_precios(
    session: Session,
    id_producto_presentacion: int,
) -> list[ProductoPrecio]:
    return list(
        session.scalars(
            select(ProductoPrecio)
            .where(
                ProductoPrecio.id_producto_presentacion
                == id_producto_presentacion
            )
            .order_by(
                ProductoPrecio.vigencia_desde.desc()
            )
        ).all()
    )


def establecer_precio(
    session: Session,
    *,
    id_producto_presentacion: int,
    precio: Decimal | int | float | str,
) -> ProductoPrecio:
    """
    Crea el primer precio o reemplaza el precio vigente.

    Si existe un precio vigente:
    - finaliza su vigencia;
    - crea un nuevo registro;
    - conserva el historial.

    Toda la operación se ejecuta en una única transacción.
    """

    precio_normalizado = _normalizar_precio(precio)

    producto_presentacion = session.get(
        ProductoPresentacion,
        id_producto_presentacion,
    )

    if producto_presentacion is None:
        raise ProductoPresentacionNoExisteError(
            "No existe la presentación de producto "
            f"con ID {id_producto_presentacion}"
        )

    ahora = datetime.now(timezone.utc)

    try:
        precio_vigente = obtener_precio_vigente(
            session,
            id_producto_presentacion,
        )

        if precio_vigente is not None:
            if precio_vigente.precio == precio_normalizado:
                raise PrecioSinCambiosError(
                    "El nuevo precio es igual al precio vigente"
                )

            precio_vigente.vigencia_hasta = ahora

        nuevo_precio = ProductoPrecio(
            id_producto_presentacion=id_producto_presentacion,
            precio=precio_normalizado,
            vigencia_desde=ahora,
            vigencia_hasta=None,
        )

        session.add(nuevo_precio)
        session.flush()

        return nuevo_precio

    except IntegrityError as exc:
        raise RuntimeError(
            "No se pudo registrar el precio. "
            "Puede existir otro precio vigente."
        ) from exc