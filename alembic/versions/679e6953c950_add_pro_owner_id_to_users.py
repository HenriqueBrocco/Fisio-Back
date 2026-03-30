"""add pro_owner_id to users

Revision ID: 679e6953c950
Revises: 008addcd18a5
Create Date: 2026-03-24 17:42:00.969782

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "679e6953c950"
down_revision: str | Sequence[str] | None = "008addcd18a5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
