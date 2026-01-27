"""create bins and events tables

Revision ID: 0392268b76f8
Revises: 3354f5f32be1
Create Date: 2026-01-26 20:06:17.009986

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0392268b76f8"
down_revision: str | Sequence[str] | None = "3354f5f32be1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create bins table
    op.execute(
        """
        CREATE TABLE bins (
            id TEXT PRIMARY KEY,
            name TEXT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    # Create events table
    op.execute(
        """
        CREATE TABLE events (
            id TEXT PRIMARY KEY,
            bin_id TEXT NOT NULL REFERENCES bins(id),
            method TEXT NOT NULL,
            path TEXT NOT NULL,
            query_params JSONB NOT NULL DEFAULT '{}',
            headers JSONB NOT NULL DEFAULT '{}',
            body_b64 TEXT NOT NULL,
            remote_ip TEXT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    # Create indexes for common query patterns
    op.execute("CREATE INDEX idx_events_bin_id ON events(bin_id)")
    op.execute("CREATE INDEX idx_events_created_at ON events(created_at)")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_events_created_at")
    op.execute("DROP INDEX IF EXISTS idx_events_bin_id")

    # Drop tables in dependency order (events first, then bins)
    op.execute("DROP TABLE IF EXISTS events")
    op.execute("DROP TABLE IF EXISTS bins")
