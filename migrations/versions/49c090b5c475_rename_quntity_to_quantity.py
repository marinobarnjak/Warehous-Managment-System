"""rename quntity to quantity

Revision ID: 49c090b5c475
Revises: 38264bdea2a9
Create Date: 2026-10-25 16:58:37.227337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49c090b5c475'
down_revision: Union[str, Sequence[str], None] = '38264bdea2a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(table_name='products', column_name='quntity', new_column_name='quantity', existing_type=sa.Integer)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(table_name='products', column_name='quantity', new_column_name='quntity', existing_type=sa.Integer)

