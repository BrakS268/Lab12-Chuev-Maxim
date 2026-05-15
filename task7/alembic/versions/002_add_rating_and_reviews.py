"""add rating and reviews_count to tutors

Revision ID: 002_add_rating
Revises: 001_initial
Create Date: 2025-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_add_rating"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем поле среднего рейтинга репетитора (0.0 - 5.0)
    op.add_column(
        "tutors",
        sa.Column(
            "rating",
            sa.Float(),
            nullable=False,
            server_default="0.0",
            comment="Средний рейтинг репетитора (0.0 - 5.0)",
        ),
    )

    # Добавляем счётчик отзывов
    op.add_column(
        "tutors",
        sa.Column(
            "reviews_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Количество отзывов",
        ),
    )

    # Индекс для сортировки по рейтингу (частый запрос)
    op.create_index("ix_tutors_rating", "tutors", ["rating"])


def downgrade() -> None:
    op.drop_index("ix_tutors_rating", table_name="tutors")
    op.drop_column("tutors", "reviews_count")
    op.drop_column("tutors", "rating")
