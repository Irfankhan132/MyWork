"""add is_overage to ai_usage_events

Revision ID: c8d1c150705a
Revises: f1943f997c74
Create Date: 2026-01-12 12:24:37.297225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8d1c150705a'
down_revision: Union[str, None] = 'f1943f997c74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("ai_usage_events", sa.Column("is_overage", sa.Boolean(), nullable=False, server_default=sa.text("false")))

def downgrade():
    op.drop_column("ai_usage_events", "is_overage")
