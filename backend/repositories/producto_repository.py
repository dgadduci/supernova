from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.producto import Producto
from backend.repositories.base_repository import BaseRepository
from backend.utils.text_normalizer import normalizar_texto


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session) -> None:
        super().__init__(
            session=session,
            model=Producto,
        )

    def buscar_por_nombre(
        self,
        id_categoria_producto: int,
        nombre: str,
    ) -> Producto | None:
        nombre_normalizado = normalizar_texto(nombre)

        productos = self.listar_por_categoria(
            id_categoria_producto=id_categoria_producto,
        )

        return next(
            (
                producto
                for producto in productos
                if normalizar_texto(producto.nombre)
                == nombre_normalizado
            ),
            None,
        )

    def existe_nombre(
        self,
        id_categoria_producto: int,
        nombre: str,
    ) -> bool:
        return (
            self.buscar_por_nombre(
                id_categoria_producto=id_categoria_producto,
                nombre=nombre,
            )
            is not None
        )

    def listar_por_categoria(
        self,
        id_categoria_producto: int,
    ) -> Sequence[Producto]:
        statement = (
            select(Producto)
            .where(
                Producto.id_categoria_producto
                == id_categoria_producto
            )
            .order_by(
                Producto.orden,
                Producto.nombre,
            )
        )

        return self.session.scalars(statement).all()

    def listar_activos_por_categoria(
        self,
        id_categoria_producto: int,
    ) -> Sequence[Producto]:
        statement = (
            select(Producto)
            .where(
                Producto.id_categoria_producto
                == id_categoria_producto,
                Producto.activo.is_(True),
            )
            .order_by(
                Producto.orden,
                Producto.nombre,
            )
        )

        return self.session.scalars(statement).all()

    def listar_disponibles_por_categoria(
        self,
        id_categoria_producto: int,
    ) -> Sequence[Producto]:
        statement = (
            select(Producto)
            .where(
                Producto.id_categoria_producto
                == id_categoria_producto,
                Producto.activo.is_(True),
                Producto.disponible.is_(True),
            )
            .order_by(
                Producto.orden,
                Producto.nombre,
            )
        )

        return self.session.scalars(statement).all()

    def obtener_por_id_y_categoria(
        self,
        id_producto: int,
        id_categoria_producto: int,
    ) -> Producto | None:
        statement = select(Producto).where(
            Producto.id == id_producto,
            Producto.id_categoria_producto
            == id_categoria_producto,
        )

        return self.session.scalar(statement)