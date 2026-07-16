from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.categoria_producto import CategoriaProducto
    from backend.models.producto_presentacion import ProductoPresentacion

class Producto(Base):
    __tablename__ = "productos"

    __table_args__ = (
        UniqueConstraint(
            "id_categoria_producto",
            "nombre",
            name="categoria_producto_nombre_unico",
        ),
        CheckConstraint(
            "orden >= 0",
            name="orden_no_negativo",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_categoria_producto: Mapped[int] = mapped_column(
        ForeignKey(
            "categorias_productos.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    disponible: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    orden: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    fecha_alta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    fecha_ultima_modificacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    categoria: Mapped["CategoriaProducto"] = relationship(
        back_populates="productos",
    )

    presentaciones: Mapped[list["ProductoPresentacion"]] = relationship(
        back_populates="producto",
    )

    def __repr__(self) -> str:
        return (
            f"Producto("
            f"id={self.id!r}, "
            f"id_categoria_producto={self.id_categoria_producto!r}, "
            f"nombre={self.nombre!r}, "
            f"activo={self.activo!r}, "
            f"disponible={self.disponible!r})"
        )