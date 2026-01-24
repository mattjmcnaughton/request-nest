"""initial baseline

Revision ID: 3354f5f32be1
Revises:
Create Date: 2026-01-24 10:02:04.133218

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "3354f5f32be1"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
