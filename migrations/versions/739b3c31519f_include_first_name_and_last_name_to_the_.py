"""Include first name and last name to the user model

Revision ID: 739b3c31519f
Revises: 8fe0530f2940
Create Date: 2024-08-24 16:29:29.584008

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '739b3c31519f'
down_revision = '8fe0530f2940'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('first_name', sa.String(length=200), nullable=False))
        batch_op.add_column(sa.Column('last_name', sa.String(length=200), nullable=False))
        batch_op.drop_column('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', mysql.VARCHAR(length=200), nullable=False))
        batch_op.drop_column('last_name')
        batch_op.drop_column('first_name')

    # ### end Alembic commands ###
