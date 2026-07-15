"""agregar whatsapp a comercios

Revision ID: e3ee448f3fa7
Revises: 660a1332d8db
Create Date: 2026-07-14 16:42:24.252594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3ee448f3fa7'
down_revision: Union[str, Sequence[str], None] = '660a1332d8db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "comercios",
        sa.Column(
            "whatsapp",
            sa.String(length=30),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE comercios
        SET whatsapp = '5491156977905'
        WHERE whatsapp IS NULL
        """
    )

    op.alter_column(
        "comercios",
        "whatsapp",
        existing_type=sa.String(length=30),
        nullable=False,
    )

    op.create_index(
        op.f("ix_comercios_whatsapp"),
        "comercios",
        ["whatsapp"],
        unique=True,
    )

def downgrade() -> None:
    op.drop_index(
        op.f("ix_comercios_whatsapp"),
        table_name="comercios",
    )

    op.drop_column(
        "comercios",
        "whatsapp",
    )