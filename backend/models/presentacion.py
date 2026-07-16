from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.comercio import Comercio
    from backend.models.producto_presentacion import ProductoPresentacion


class Presentacion(Base):
    __tablename__ = "presentaciones"

    __table_args__ = (
        UniqueConstraint(
            "id_comercio",
            "codigo",
            name="comercio_presentacion_codigo_unico",
        ),
        UniqueConstraint(
            "id_comercio",
            "descripcion",
            name="comercio_presentacion_descripcion_unica",
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

    id_comercio: Mapped[int] = mapped_column(
        ForeignKey(
            "comercios.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    codigo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    descripcion: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    activo: Mapped[bool] = mapped_column(
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

    comercio: Mapped["Comercio"] = relationship(
        back_populates="presentaciones",
    )

    productos: Mapped[list["ProductoPresentacion"]] = relationship(
        back_populates="presentacion",
    )

    def __repr__(self) -> str:
        return (
            "Presentacion("
            f"id={self.id!r}, "
            f"id_comercio={self.id_comercio!r}, "
            f"codigo={self.codigo!r}, "
            f"descripcion={self.descripcion!r}, "
            f"activo={self.activo!r})"
        )