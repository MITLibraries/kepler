"""empty message

Revision ID: 75112b127f4
Revises: None
Create Date: 2015-11-03 14:59:29.188276

"""

# revision identifiers, used by Alembic.
revision = '75112b127f4'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uri', sa.Unicode(length=255), nullable=True),
    sa.Column('layer_id', sa.Unicode(length=255), nullable=True),
    sa.Column('handle', sa.Unicode(length=255), nullable=True),
    sa.Column('access', sa.Enum(u'Public', u'Restricted', name='access'), nullable=True),
    sa.Column('tiff_url', sa.Unicode(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uri')
    )
    op.create_table('job',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum(u'CREATED', u'PENDING', u'COMPLETED', u'FAILED', name='status'), nullable=True),
    sa.Column('time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('job')
    op.drop_table('item')
    ### end Alembic commands ###
