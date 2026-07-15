from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models.comercio import Comercio, EstadoComercio
from backend.models.comercio_metodo_entrega import ComercioMetodoEntrega
from backend.models.metodo_entrega import MetodoEntrega


class ComercioDuplicadoError(Exception):
    """Se produce cuando el slug del comercio ya existe."""


def crear_comercio(
    session: Session,
    *,
    nombre_fantasia: str,
    nombre_corto: str,
    razon_social: str,
    cuit: str,
    whatsapp: str,
    calle: str,
    numero: str,
    localidad: str,
    provincia: str,
    slug: str,
    piso_departamento: str | None = None,
    codigo_postal: str | None = None,
    estado: EstadoComercio = EstadoComercio.PRUEBA,
    zona_horaria: str = "America/Argentina/Buenos_Aires",
    moneda: str = "ARS",
    idioma: str = "es-AR",
) -> Comercio:
    """
    Crea un comercio y sus configuraciones iniciales de métodos de entrega.

    Los métodos de entrega se crean inicialmente desactivados.
    Toda la operación se ejecuta dentro de una única transacción.
    """

    slug_normalizado = slug.strip().lower()

    comercio_existente = session.scalar(
        select(Comercio).where(Comercio.slug == slug_normalizado)
    )

    if comercio_existente is not None:
        raise ComercioDuplicadoError(
            f"Ya existe un comercio con el slug {slug_normalizado!r}"
        )

    try:
        comercio = Comercio(
            nombre_fantasia=nombre_fantasia.strip(),
            nombre_corto=nombre_corto.strip(),
            razon_social=razon_social.strip(),
            cuit=cuit.strip(),
            whatsapp=whatsapp.strip(),
            calle=calle.strip(),
            numero=numero.strip(),
            piso_departamento=(
                piso_departamento.strip()
                if piso_departamento
                else None
            ),
            localidad=localidad.strip(),
            provincia=provincia.strip(),
            codigo_postal=(
                codigo_postal.strip()
                if codigo_postal
                else None
            ),
            slug=slug_normalizado,
            estado=estado,
            zona_horaria=zona_horaria,
            moneda=moneda.upper(),
            idioma=idioma,
        )

        session.add(comercio)

        # Ejecuta el INSERT sin confirmar la transacción.
        # Así obtenemos comercio.id para crear los registros relacionados.
        session.flush()

        metodos_entrega = session.scalars(
            select(MetodoEntrega)
            .where(MetodoEntrega.activo.is_(True))
            .order_by(MetodoEntrega.orden)
        ).all()

        if not metodos_entrega:
            raise RuntimeError(
                "No existen métodos de entrega activos en el catálogo"
            )

        configuraciones = [
            ComercioMetodoEntrega(
                id_comercio=comercio.id,
                id_metodo_entrega=metodo.id,
                activo=False,
                orden=metodo.orden,
            )
            for metodo in metodos_entrega
        ]

        session.add_all(configuraciones)
        session.commit()
        session.refresh(comercio)

        return comercio

    except IntegrityError as exc:
        session.rollback()

        raise ComercioDuplicadoError(
            "No se pudo crear el comercio porque algún dato único ya existe"
        ) from exc

    except Exception:
        session.rollback()
        raise