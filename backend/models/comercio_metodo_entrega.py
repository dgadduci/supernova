from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.comercio import Comercio
    from backend.models.metodo_entrega import MetodoEntrega

class ComercioMetodoEntrega(Base):
    __tablename__ = "comercio_metodos_entrega"

    __table_args__ = (
        UniqueConstraint(
            "id_comercio",
            "id_metodo_entrega",
            name="comercio_metodo_unico",
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

    id_metodo_entrega: Mapped[int] = mapped_column(
        ForeignKey(
            "metodos_entrega.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    orden: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
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
        back_populates="metodos_entrega",
    )

    metodo_entrega: Mapped["MetodoEntrega"] = relationship(
        back_populates="comercios",
    )

    def __repr__(self) -> str:
        return (
            f"ComercioMetodoEntrega("
            f"id_comercio={self.id_comercio!r}, "
            f"id_metodo_entrega={self.id_metodo_entrega!r}, "
            f"activo={self.activo!r})"
        )