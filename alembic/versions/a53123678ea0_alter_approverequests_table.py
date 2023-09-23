"""alter ApproveRequests table

Revision ID: a53123678ea0
Revises: 389718915a7d
Create Date: 2023-09-19 09:21:47.794891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a53123678ea0'
down_revision: Union[str, None] = '389718915a7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column(table_name = 'Approve_requests', column_name = 'merchant_name')
    op.drop_column(table_name = 'Approve_requests', column_name = 'email')
    op.drop_column(table_name = 'Approve_requests', column_name = 'status')
    op.drop_column(table_name = 'Approve_requests', column_name = 'tax')
    op.drop_column(table_name = 'Approve_requests', column_name = 'address')
    op.drop_column(table_name = 'Approve_requests', column_name = 'legal_representative')
    op.drop_column(table_name = 'Approve_requests', column_name = 'is_active')
    op.alter_column(table_name='Approve_requests', column_name = 'request_type', new_column_name='request_data')


def downgrade() -> None:
    op.add_column('Approve_requests', sa.Column('merchant_name', sa.String(), nullable=True))
    op.add_column('Approve_requests', sa.Column('email', sa.String(), nullable=True))
    op.add_column('Approve_requests', sa.Column('status', sa.Boolean(), nullable=True))
    op.add_column('Approve_requests', sa.Column('tax', sa.Integer(), nullable=True))
    op.add_column('Approve_requests', sa.Column('address', sa.String(), nullable=True))
    op.add_column('Approve_requests', sa.Column('legal_representative', sa.String(), nullable=True))
    op.add_column('Approve_requests', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.alter_column(table_name='Approve_requests', column_name = 'request_data', new_column_name='request_type')

