"""create tutors table

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-01 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаём таблицу репетиторов
    op.create_table(
        "tutors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=50), nullable=False),
        sa.Column("hourly_rate", sa.Float(), nullable=False),
        sa.Column("experience_years", sa.Integer(), nullable=False),
        sa.Column("education", sa.String(length=300), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id"),
    )

    # Индексы для часто запрашиваемых полей
    op.create_index("ix_tutors_id", "tutors", ["id"])
    op.create_index("ix_tutors_email", "tutors", ["email"], unique=True)
    op.create_index("ix_tutors_full_name", "tutors", ["full_name"])
    op.create_index("ix_tutors_subject", "tutors", ["subject"])
    op.create_index("ix_tutors_is_active", "tutors", ["is_active"])


def downgrade() -> None:
    # Удаляем индексы и таблицу в обратном порядке
    op.drop_index("ix_tutors_is_active", table_name="tutors")
    op.drop_index("ix_tutors_subject", table_name="tutors")
    op.drop_index("ix_tutors_full_name", table_name="tutors")
    op.drop_index("ix_tutors_email", table_name="tutors")
    op.drop_index("ix_tutors_id", table_name="tutors")
    op.drop_table("tutors")
