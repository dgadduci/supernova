from datetime import datetime
from typing import TYPE_CHECKING
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.comercio_metodo_entrega import ComercioMetodoEntrega
    from backend.models.comercio_medio_pago import ComercioMedioPago
    from backend.models.categoria_producto import CategoriaProducto

class EstadoComercio(str, Enum):
    PRUEBA = "prueba"
    ACTIVO = "activo"
    SUSPENDIDO = "suspendido"
    INACTIVO = "inactivo"
    BAJA = "baja"


class Comercio(Base):
    __tablename__ = "comercios"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    nombre_fantasia: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    nombre_corto: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    razon_social: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    cuit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    
    whatsapp: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
        index=True,
    )

    calle: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    numero: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    piso_departamento: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    localidad: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    provincia: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    codigo_postal: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    slug: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
        index=True,
    )

    estado: Mapped[EstadoComercio] = mapped_column(
        SqlEnum(
            EstadoComercio,
            name="estado_comercio",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=EstadoComercio.PRUEBA,
        server_default=EstadoComercio.PRUEBA.value,
    )

    zona_horaria: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="America/Argentina/Buenos_Aires",
        server_default="America/Argentina/Buenos_Aires",
    )

    moneda: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="ARS",
        server_default="ARS",
    )

    idioma: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="es-AR",
        server_default="es-AR",
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

    fecha_baja: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    metodos_entrega: Mapped[list["ComercioMetodoEntrega"]] = relationship(
        back_populates="comercio",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )    
    
    medios_pago: Mapped[list["ComercioMedioPago"]] = relationship(
        back_populates="comercio",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    categorias_productos: Mapped[list["CategoriaProducto"]] = relationship(
        back_populates="comercio",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"Comercio(id={self.id!r}, "
            f"nombre_fantasia={self.nombre_fantasia!r}, "
            f"estado={self.estado.value!r})"
        )