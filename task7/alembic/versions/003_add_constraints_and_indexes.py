"""add check constraint for hourly_rate and experience_years

Revision ID: 003_add_constraints
Revises: 002_add_rating
Create Date: 2025-02-01 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003_add_constraints"
down_revision: Union[str, None] = "002_add_rating"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ограничение: ставка >= 0
    op.create_check_constraint(
        "ck_tutors_hourly_rate_positive",
        "tutors",
        "hourly_rate >= 0",
    )

    # Ограничение: опыт от 0 до 60 лет
    op.create_check_constraint(
        "ck_tutors_experience_years_range",
        "tutors",
        "experience_years >= 0 AND experience_years <= 60",
    )

    # Ограничение: рейтинг от 0.0 до 5.0
    op.create_check_constraint(
        "ck_tutors_rating_range",
        "tutors",
        "rating >= 0.0 AND rating <= 5.0",
    )

    # Составной индекс для поиска активных репетиторов по предмету
    # (самый частый запрос: "найти активных репетиторов по математике")
    op.create_index(
        "ix_tutors_subject_is_active",
        "tutors",
        ["subject", "is_active"],
    )


def downgrade() -> None:
    op.drop_index("ix_tutors_subject_is_active", table_name="tutors")
    op.drop_constraint("ck_tutors_rating_range", "tutors", type_="check")
    op.drop_constraint("ck_tutors_experience_years_range", "tutors", type_="check")
    op.drop_constraint("ck_tutors_hourly_rate_positive", "tutors", type_="check")
