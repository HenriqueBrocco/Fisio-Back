"""add pro_owner_id to users

Revision ID: 9a1c8333ceff
Revises: 457cf7429bea
Create Date: 2026-03-24 17:45:09.071564

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9a1c8333ceff"
down_revision: str | Sequence[str] | None = "457cf7429bea"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    op.add_column("users", sa.Column("pro_owner_id", sa.String(), nullable=True))
    op.create_foreign_key(
        "fk_users_pro_owner_id_users",
        "users",
        "users",
        ["pro_owner_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_users_pro_owner_id", "users", ["pro_owner_id"])


def downgrade():
    op.drop_index("ix_users_pro_owner_id", table_name="users")
    op.drop_constraint("fk_users_pro_owner_id_users", "users", type_="foreignkey")
    op.drop_column("users", "pro_owner_id")
