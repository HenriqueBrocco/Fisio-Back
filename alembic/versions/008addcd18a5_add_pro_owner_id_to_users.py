"""add pro_owner_id to users

Revision ID: 008addcd18a5
Revises: c1e23c407dc4
Create Date: 2026-03-24 17:16:17.577177

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "008addcd18a5"
down_revision: str | Sequence[str] | None = "c1e23c407dc4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
