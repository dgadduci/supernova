from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.comercio_medio_pago import ComercioMedioPago


class MedioPago(Base):
    __tablename__ = "medios_pago"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    codigo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
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

    comercios: Mapped[list["ComercioMedioPago"]] = relationship(
        back_populates="medio_pago",
    )

    def __repr__(self) -> str:
        return (
            f"MedioPago(id={self.id!r}, "
            f"codigo={self.codigo!r}, "
            f"activo={self.activo!r})"
        )