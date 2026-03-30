"""add pro_owner_id to users

Revision ID: 73874ef7296d
Revises: 9a1c8333ceff
Create Date: 2026-03-24 17:45:24.781169

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "73874ef7296d"
down_revision: str | Sequence[str] | None = "9a1c8333ceff"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    # A coluna pro_owner_id já existe (criada pela migration anterior).
    # Aqui garantimos FK e índice de forma idempotente.

    op.execute(
        """
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_users_pro_owner_id_users'
      ) THEN
        ALTER TABLE users
          ADD CONSTRAINT fk_users_pro_owner_id_users
          FOREIGN KEY (pro_owner_id) REFERENCES users (id)
          ON DELETE SET NULL;
      END IF;
    END$$;
    """
    )

    op.execute(
        """
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = 'i'
          AND c.relname = 'ix_users_pro_owner_id'
      ) THEN
        CREATE INDEX ix_users_pro_owner_id ON users (pro_owner_id);
      END IF;
    END$$;
    """
    )


def downgrade():
    # Remove índice e FK se existirem. Não removemos a coluna aqui para evitar apagar dados.
    op.execute(
        """
    DO $$
    BEGIN
      IF EXISTS (
        SELECT 1 FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = 'i'
          AND c.relname = 'ix_users_pro_owner_id'
      ) THEN
        DROP INDEX ix_users_pro_owner_id;
      END IF;
    END$$;
    """
    )

    op.execute(
        """
    DO $$
    BEGIN
      IF EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_users_pro_owner_id_users'
      ) THEN
        ALTER TABLE users DROP CONSTRAINT fk_users_pro_owner_id_users;
      END IF;
    END$$;
    """
    )
