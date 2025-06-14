"""Add is_featured to Property

Revision ID: 60099f792bf4
Revises: 
Create Date: 2025-06-15 02:55:17.831235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60099f792bf4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('property', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_featured', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('property', schema=None) as batch_op:
        batch_op.drop_column('is_featured')

    # ### end Alembic commands ###
