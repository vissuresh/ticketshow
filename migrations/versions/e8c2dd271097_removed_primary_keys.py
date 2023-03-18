"""removed primary keys

Revision ID: e8c2dd271097
Revises: 93b1d2bd4d44
Create Date: 2023-03-18 21:25:58.373333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8c2dd271097'
down_revision = '93b1d2bd4d44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('show_venue', schema=None) as batch_op:
        batch_op.alter_column('show_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('venue_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('show_venue', schema=None) as batch_op:
        batch_op.alter_column('venue_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('show_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
