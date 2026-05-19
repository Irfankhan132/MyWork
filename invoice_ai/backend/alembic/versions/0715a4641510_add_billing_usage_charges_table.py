"""add billing_usage_charges table

Revision ID: 0715a4641510
Revises: c8d1c150705a
Create Date: 2026-01-17 20:15:20.642592

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0715a4641510'
down_revision: Union[str, None] = 'c8d1c150705a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
