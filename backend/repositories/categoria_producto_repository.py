from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.categoria_producto import CategoriaProducto
from backend.repositories.base_repository import BaseRepository
from backend.utils.text_normalizer import normalizar_texto


class CategoriaProductoRepository(
    BaseRepository[CategoriaProducto]
):
    def __init__(self, session: Session) -> None:
        super().__init__(
            session=session,
            model=CategoriaProducto,
        )

    def buscar_por_descripcion(
        self,
        id_comercio: int,
        descripcion: str,
    ) -> CategoriaProducto | None:
        descripcion_normalizada = normalizar_texto(descripcion)

        categorias = self.listar_por_comercio(id_comercio)

        return next(
            (
                categoria
                for categoria in categorias
                if normalizar_texto(categoria.descripcion)
                == descripcion_normalizada
            ),
            None,
        )

    def listar_por_comercio(
        self,
        id_comercio: int,
    ) -> Sequence[CategoriaProducto]:
        statement = (
            select(CategoriaProducto)
            .where(
                CategoriaProducto.id_comercio == id_comercio
            )
            .order_by(
                CategoriaProducto.orden,
                CategoriaProducto.descripcion,
            )
        )

        return self.session.scalars(statement).all()

    def listar_activas_por_comercio(
        self,
        id_comercio: int,
    ) -> Sequence[CategoriaProducto]:
        statement = (
            select(CategoriaProducto)
            .where(
                CategoriaProducto.id_comercio == id_comercio,
                CategoriaProducto.activo.is_(True),
            )
            .order_by(
                CategoriaProducto.orden,
                CategoriaProducto.descripcion,
            )
        )

        return self.session.scalars(statement).all()

    def existe_descripcion(
        self,
        id_comercio: int,
        descripcion: str,
    ) -> bool:
        return (
            self.buscar_por_descripcion(
                id_comercio=id_comercio,
                descripcion=descripcion,
            )
            is not None
        )

    def obtener_por_id_y_comercio(
        self,
        id_categoria: int,
        id_comercio: int,
    ) -> CategoriaProducto | None:
        statement = select(CategoriaProducto).where(
            CategoriaProducto.id == id_categoria,
            CategoriaProducto.id_comercio == id_comercio,
        )

        return self.session.scalar(statement)