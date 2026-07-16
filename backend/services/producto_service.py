from collections.abc import Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models.producto import Producto
from backend.repositories.categoria_producto_repository import (
    CategoriaProductoRepository,
)
from backend.repositories.producto_repository import (
    ProductoRepository,
)


class CategoriaProductoNoExisteError(Exception):
    """La categoría indicada no existe."""


class ProductoDuplicadoError(Exception):
    """Ya existe un producto con ese nombre en la categoría."""


class ProductoNoExisteError(Exception):
    """El producto indicado no existe."""


class NombreProductoInvalidoError(Exception):
    """El nombre del producto no es válido."""


class DescripcionProductoInvalidaError(Exception):
    """La descripción del producto no es válida."""


class OrdenProductoInvalidoError(Exception):
    """El orden del producto no es válido."""


class ProductoService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.producto_repository = ProductoRepository(session)
        self.categoria_repository = CategoriaProductoRepository(
            session
        )

    @staticmethod
    def _validar_nombre(nombre: str) -> str:
        if not isinstance(nombre, str):
            raise NombreProductoInvalidoError(
                "El nombre debe ser texto"
            )

        nombre_limpio = " ".join(nombre.split())

        if not nombre_limpio:
            raise NombreProductoInvalidoError(
                "El nombre no puede estar vacío"
            )

        if len(nombre_limpio) > 150:
            raise NombreProductoInvalidoError(
                "El nombre no puede superar los 150 caracteres"
            )

        return nombre_limpio

    @staticmethod
    def _validar_descripcion(
        descripcion: str | None,
    ) -> str | None:
        if descripcion is None:
            return None

        if not isinstance(descripcion, str):
            raise DescripcionProductoInvalidaError(
                "La descripción debe ser texto"
            )

        descripcion_limpia = " ".join(descripcion.split())

        if not descripcion_limpia:
            return None

        return descripcion_limpia

    @staticmethod
    def _validar_orden(orden: int) -> int:
        if not isinstance(orden, int):
            raise OrdenProductoInvalidoError(
                "El orden debe ser un número entero"
            )

        if orden < 0:
            raise OrdenProductoInvalidoError(
                "El orden no puede ser negativo"
            )

        return orden

    def crear_producto(
        self,
        *,
        id_categoria_producto: int,
        nombre: str,
        descripcion: str | None = None,
        activo: bool = True,
        disponible: bool = True,
        orden: int = 0,
    ) -> Producto:
        nombre_limpio = self._validar_nombre(nombre)
        descripcion_limpia = self._validar_descripcion(
            descripcion
        )
        orden_validado = self._validar_orden(orden)

        categoria = self.categoria_repository.get_by_id(
            id_categoria_producto
        )

        if categoria is None:
            raise CategoriaProductoNoExisteError(
                "No existe la categoría de producto "
                f"con ID {id_categoria_producto}"
            )

        if self.producto_repository.existe_nombre(
            id_categoria_producto=id_categoria_producto,
            nombre=nombre_limpio,
        ):
            raise ProductoDuplicadoError(
                "Ya existe un producto con ese nombre "
                "dentro de la categoría"
            )

        producto = Producto(
            id_categoria_producto=id_categoria_producto,
            nombre=nombre_limpio,
            descripcion=descripcion_limpia,
            activo=activo,
            disponible=disponible,
            orden=orden_validado,
        )
        try:
            self.producto_repository.add(producto)
            self.producto_repository.flush()

            return producto

        except IntegrityError as exc:
            raise ProductoDuplicadoError(
                "No se pudo crear el producto porque ya existe "
                "un producto equivalente"
            ) from exc

    def obtener_producto(
        self,
        *,
        id_producto: int,
        id_categoria_producto: int,
    ) -> Producto:
        producto = (
            self.producto_repository
            .obtener_por_id_y_categoria(
                id_producto=id_producto,
                id_categoria_producto=id_categoria_producto,
            )
        )

        if producto is None:
            raise ProductoNoExisteError(
                "El producto no existe o no pertenece "
                "a la categoría indicada"
            )

        return producto

    def listar_productos(
        self,
        *,
        id_categoria_producto: int,
        solo_activos: bool = False,
        solo_disponibles: bool = False,
    ) -> Sequence[Producto]:
        if solo_disponibles:
            return (
                self.producto_repository
                .listar_disponibles_por_categoria(
                    id_categoria_producto
                )
            )

        if solo_activos:
            return (
                self.producto_repository
                .listar_activos_por_categoria(
                    id_categoria_producto
                )
            )

        return self.producto_repository.listar_por_categoria(
            id_categoria_producto
        )

    def cambiar_estado(
        self,
        *,
        id_producto: int,
        id_categoria_producto: int,
        activo: bool,
    ) -> Producto:
        producto = self.obtener_producto(
            id_producto=id_producto,
            id_categoria_producto=id_categoria_producto,
        )

        producto.activo = activo

        try:
            producto.activo = activo
            self.producto_repository.flush()

            return producto
        
        except Exception:
            self.session.rollback()
            raise

    def cambiar_disponibilidad(
        self,
        *,
        id_producto: int,
        id_categoria_producto: int,
        disponible: bool,
    ) -> Producto:
        producto = self.obtener_producto(
            id_producto=id_producto,
            id_categoria_producto=id_categoria_producto,
        )

        producto.disponible = disponible

        try:
            producto.disponible = disponible
            self.producto_repository.flush()

            return producto
        
        except Exception:
            self.session.rollback()
            raise