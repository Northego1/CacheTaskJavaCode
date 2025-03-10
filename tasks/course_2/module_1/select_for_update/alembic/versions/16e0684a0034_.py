"""empty message

Revision ID: 16e0684a0034
Revises: 
Create Date: 2025-02-24 15:16:45.603468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '16e0684a0034'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tasks',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('task_name', sa.VARCHAR(length=60), nullable=False),
    sa.Column('status', postgresql.ENUM('PENDING', 'PROCESSING', 'COMPLETED', name='status'), nullable=False),
    sa.Column('worker_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tasks')
    # ### end Alembic commands ###
