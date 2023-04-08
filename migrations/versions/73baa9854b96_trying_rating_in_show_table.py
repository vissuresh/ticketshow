"""trying rating in show table

Revision ID: 73baa9854b96
Revises: 9270e4b0cb32
Create Date: 2023-04-08 16:57:12.835498

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73baa9854b96'
down_revision = '9270e4b0cb32'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('show', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rating', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('rated_bookings', sa.Integer(), nullable=True))
        batch_op.drop_constraint('u_venue_name_loc', type_='unique')
        batch_op.create_unique_constraint('u_show_name_timing', ['name', 'timing'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('show', schema=None) as batch_op:
        batch_op.drop_constraint('u_show_name_timing', type_='unique')
        batch_op.create_unique_constraint('u_venue_name_loc', ['name', 'timing'])
        batch_op.drop_column('rated_bookings')
        batch_op.drop_column('rating')

    # ### end Alembic commands ###