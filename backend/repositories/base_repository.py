from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database.base import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Operaciones genéricas de persistencia.

    Este repository:
    - recibe una Session existente;
    - no crea sesiones;
    - no ejecuta commit;
    - no ejecuta rollback;
    - no contiene reglas de negocio.
    """

    def __init__(
        self,
        session: Session,
        model: type[ModelType],
    ) -> None:
        self.session = session
        self.model = model

    def get_by_id(self, entity_id: int) -> ModelType | None:
        """
        Devuelve una entidad por clave primaria.

        Retorna None si no existe.
        """
        return self.session.get(self.model, entity_id)

    def list_all(self) -> Sequence[ModelType]:
        """
        Devuelve todas las entidades del modelo.
        """
        statement = select(self.model)

        return self.session.scalars(statement).all()

    def add(self, entity: ModelType) -> ModelType:
        """
        Agrega una entidad a la sesión.

        No ejecuta commit ni flush automáticamente.
        """
        self.session.add(entity)
        return entity

    def add_all(
        self,
        entities: Sequence[ModelType],
    ) -> Sequence[ModelType]:
        """
        Agrega varias entidades a la sesión.

        No ejecuta commit ni flush automáticamente.
        """
        self.session.add_all(list(entities))
        return entities

    def delete(self, entity: ModelType) -> None:
        """
        Marca una entidad para eliminación.

        No ejecuta commit.
        """
        self.session.delete(entity)

    def refresh(self, entity: ModelType) -> ModelType:
        """
        Recarga la entidad desde la base de datos.
        """
        self.session.refresh(entity)
        return entity

    def flush(self) -> None:
        """
        Envía los cambios pendientes a PostgreSQL sin confirmar
        la transacción.

        Permite obtener IDs generados antes del commit.
        """
        self.session.flush()

    def exists_by_id(self, entity_id: int) -> bool:
        """
        Indica si existe una entidad con esa clave primaria.
        """
        primary_key = self.model.__mapper__.primary_key[0]

        statement = select(
            select(primary_key)
            .where(primary_key == entity_id)
            .exists()
        )

        return bool(self.session.scalar(statement))

    def count(self) -> int:
        """
        Devuelve la cantidad total de registros del modelo.
        """
        statement = select(func.count()).select_from(self.model)

        return int(self.session.scalar(statement) or 0)