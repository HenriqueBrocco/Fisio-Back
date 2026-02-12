"""session_summary floats

Revision ID: c1e23c407dc4
Revises: f9380c102e1b
Create Date: 2026-02-12 18:32:02.879710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1e23c407dc4'
down_revision: Union[str, Sequence[str], None] = 'f9380c102e1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "session_summaries",
        "rom",
        existing_type=sa.INTEGER(),
        type_=sa.Float(),
        postgresql_using="rom::double precision",
        existing_nullable=False,
    )
    op.alter_column(
        "session_summaries",
        "cadence",
        existing_type=sa.INTEGER(),
        type_=sa.Float(),
        postgresql_using="cadence::double precision",
        existing_nullable=True,
    )

def downgrade():
    op.alter_column(
        "session_summaries",
        "rom",
        existing_type=sa.Float(),
        type_=sa.INTEGER(),
        postgresql_using="rom::integer",
        existing_nullable=False,
    )
    op.alter_column(
        "session_summaries",
        "cadence",
        existing_type=sa.Float(),
        type_=sa.INTEGER(),
        postgresql_using="cadence::integer",
        existing_nullable=True,
    )
