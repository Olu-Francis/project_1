"""Initial Migration

Revision ID: 95d930b2ffed
Revises: 
Create Date: 2024-08-20 23:32:12.799455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '95d930b2ffed'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.VARCHAR(length=60), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=False),
    sa.Column('first_name', sa.String(length=200), nullable=False),
    sa.Column('email', sa.String(length=180), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('balance', sa.Integer(), nullable=False),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('password_hash', sa.String(length=180), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('transactions',
    sa.Column('id', sa.VARCHAR(length=60), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('trans_type', sa.String(length=50), nullable=False),
    sa.Column('category', sa.String(length=150), nullable=False),
    sa.Column('transaction_frequency', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=300), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.VARCHAR(length=60), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    op.drop_table('users')
    # ### end Alembic commands ###
