"""first migrate

Revision ID: 12f2f184a06a
Revises: 
Create Date: 2023-03-02 15:21:40.414746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12f2f184a06a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('venue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('location', sa.String(length=64), nullable=True),
    sa.Column('capacity', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('venue', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_venue_location'), ['location'], unique=False)
        batch_op.create_index(batch_op.f('ix_venue_name'), ['name'], unique=False)

    op.create_table('show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('venue_id', sa.Integer(), nullable=True),
    sa.Column('timing', sa.DateTime(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('no_sold', sa.Integer(), nullable=True),
    sa.Column('tags', sa.String(length=64), nullable=True),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('show', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_show_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('ix_show_tags'), ['tags'], unique=False)
        batch_op.create_index(batch_op.f('ix_show_timing'), ['timing'], unique=False)

    op.create_table('booking',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('venue_id', sa.Integer(), nullable=True),
    sa.Column('show_id', sa.Integer(), nullable=True),
    sa.Column('qty', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['show_id'], ['show.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_booking_timestamp'), ['timestamp'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_booking_timestamp'))

    op.drop_table('booking')
    with op.batch_alter_table('show', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_show_timing'))
        batch_op.drop_index(batch_op.f('ix_show_tags'))
        batch_op.drop_index(batch_op.f('ix_show_name'))

    op.drop_table('show')
    with op.batch_alter_table('venue', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_venue_name'))
        batch_op.drop_index(batch_op.f('ix_venue_location'))

    op.drop_table('venue')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))

    op.drop_table('user')
    # ### end Alembic commands ###
