"""Add verification_code and is_verified columns to users table

Revision ID: 2bf406ccb7d2
Revises: adb8a54da6d9
Create Date: 2024-08-06 13:51:37.992991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bf406ccb7d2'
down_revision = 'adb8a54da6d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('verification_code', sa.String(length=6), nullable=True))
        batch_op.add_column(sa.Column('is_verified', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_verified')
        batch_op.drop_column('verification_code')

    # ### end Alembic commands ###
