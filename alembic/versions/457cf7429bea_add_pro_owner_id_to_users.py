"""add pro_owner_id to users

Revision ID: 457cf7429bea
Revises: 679e6953c950
Create Date: 2026-03-24 17:42:21.777637

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "457cf7429bea"
down_revision: str | Sequence[str] | None = "679e6953c950"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
