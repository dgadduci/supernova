from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models.categoria_producto import CategoriaProducto
from backend.models.comercio import Comercio
from backend.repositories.categoria_producto_repository import (
    CategoriaProductoRepository,
)
from backend.repositories.base_repository import BaseRepository


class ComercioNoExisteError(Exception):
    """El comercio indicado no existe."""


class CategoriaDuplicadaError(Exception):
    """Ya existe una categoría con esa descripción."""


class CategoriaNoExisteError(Exception):
    """La categoría indicada no existe."""


class DescripcionCategoriaInvalidaError(Exception):
    """La descripción de la categoría no es válida."""


class OrdenCategoriaInvalidoError(Exception):
    """El orden de la categoría no es válido."""


class CategoriaProductoService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.categoria_repository = CategoriaProductoRepository(session)
        self.comercio_repository = BaseRepository(
            session=session,
            model=Comercio,
        )

    @staticmethod
    def _validar_descripcion(descripcion: str) -> str:
        if not isinstance(descripcion, str):
            raise DescripcionCategoriaInvalidaError(
                "La descripción debe ser texto"
            )

        descripcion_limpia = " ".join(descripcion.split())

        if not descripcion_limpia:
            raise DescripcionCategoriaInvalidaError(
                "La descripción no puede estar vacía"
            )

        if len(descripcion_limpia) > 100:
            raise DescripcionCategoriaInvalidaError(
                "La descripción no puede superar los 100 caracteres"
            )

        return descripcion_limpia

    @staticmethod
    def _validar_orden(orden: int) -> int:
        if not isinstance(orden, int):
            raise OrdenCategoriaInvalidoError(
                "El orden debe ser un número entero"
            )

        if orden < 0:
            raise OrdenCategoriaInvalidoError(
                "El orden no puede ser negativo"
            )

        return orden

    def crear_categoria(
        self,
        *,
        id_comercio: int,
        descripcion: str,
        orden: int = 0,
        activo: bool = True,
    ) -> CategoriaProducto:
        descripcion_limpia = self._validar_descripcion(descripcion)
        orden_validado = self._validar_orden(orden)

        comercio = self.comercio_repository.get_by_id(id_comercio)

        if comercio is None:
            raise ComercioNoExisteError(
                f"No existe el comercio con ID {id_comercio}"
            )

        if self.categoria_repository.existe_descripcion(
            id_comercio=id_comercio,
            descripcion=descripcion_limpia,
        ):
            raise CategoriaDuplicadaError(
                "Ya existe una categoría con esa descripción "
                "para el comercio"
            )

        categoria = CategoriaProducto(
            id_comercio=id_comercio,
            descripcion=descripcion_limpia,
            activo=activo,
            orden=orden_validado,
        )

        try:
            self.categoria_repository.add(categoria)
            self.categoria_repository.flush()

            return categoria

        except IntegrityError as exc:
            raise CategoriaDuplicadaError(
                "No se pudo crear la categoría porque ya existe "
                "una categoría equivalente"
            ) from exc
    
    def obtener_categoria(
        self,
        *,
        id_categoria: int,
        id_comercio: int,
    ) -> CategoriaProducto:
        categoria = (
            self.categoria_repository.obtener_por_id_y_comercio(
                id_categoria=id_categoria,
                id_comercio=id_comercio,
            )
        )

        if categoria is None:
            raise CategoriaNoExisteError(
                "La categoría no existe o no pertenece al comercio"
            )

        return categoria

    def listar_categorias(
        self,
        *,
        id_comercio: int,
        solo_activas: bool = False,
    ):
        if solo_activas:
            return (
                self.categoria_repository
                .listar_activas_por_comercio(id_comercio)
            )

        return self.categoria_repository.listar_por_comercio(
            id_comercio
        )

    def cambiar_estado(
        self,
        *,
        id_categoria: int,
        id_comercio: int,
        activo: bool,
    ) -> CategoriaProducto:
        categoria = self.obtener_categoria(
            id_categoria=id_categoria,
            id_comercio=id_comercio,
        )

        categoria.activo = activo

        self.categoria_repository.flush()
        return categoria