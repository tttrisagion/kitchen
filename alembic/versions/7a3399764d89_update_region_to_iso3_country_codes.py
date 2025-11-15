"""Update region to ISO3 country codes

Revision ID: 7a3399764d89
Revises: 748388e3b341
Create Date: 2025-11-14 19:38:35.917627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a3399764d89'
down_revision: Union[str, Sequence[str], None] = '748388e3b341'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Update existing US entries to USA
    op.execute("UPDATE ingredient_price SET region = 'USA' WHERE region = 'US'")
    
    # Rename column for clarity
    op.alter_column('ingredient_price', 'region',
                    new_column_name='country_code',
                    existing_type=sa.String(length=50),
                    existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Rename back
    op.alter_column('ingredient_price', 'country_code',
                    new_column_name='region',
                    existing_type=sa.String(length=50),
                    existing_nullable=False)
    
    # Update USA back to US
    op.execute("UPDATE ingredient_price SET region = 'US' WHERE region = 'USA'")
