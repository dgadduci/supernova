from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.producto_presentacion import ProductoPresentacion


class ProductoPrecio(Base):
    __tablename__ = "producto_precios"

    __table_args__ = (
        CheckConstraint(
            "precio >= 0",
            name="precio_no_negativo",
        ),
        CheckConstraint(
            "vigencia_hasta IS NULL "
            "OR vigencia_hasta > vigencia_desde",
            name="vigencia_valida",
        ),
        Index(
            "uq_producto_precios_precio_vigente",
            "id_producto_presentacion",
            unique=True,
            postgresql_where=text("vigencia_hasta IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    id_producto_presentacion: Mapped[int] = mapped_column(
        ForeignKey(
            "producto_presentaciones.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    precio: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    vigencia_desde: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    vigencia_hasta: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_alta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    producto_presentacion: Mapped["ProductoPresentacion"] = relationship(
        back_populates="precios",
    )

    def __repr__(self) -> str:
        return (
            f"ProductoPrecio("
            f"id={self.id!r}, "
            f"id_producto_presentacion="
            f"{self.id_producto_presentacion!r}, "
            f"precio={self.precio!r}, "
            f"vigencia_hasta={self.vigencia_hasta!r})"
        )