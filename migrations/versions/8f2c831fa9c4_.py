"""empty message

Revision ID: 8f2c831fa9c4
Revises: 1172abcb5b34
Create Date: 2020-11-26 10:26:35.006204

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f2c831fa9c4'
down_revision = '1172abcb5b34'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.add_column('bucketlists', sa.Column('created_by', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'bucketlists', 'users', ['created_by'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'bucketlists', type_='foreignkey')
    op.drop_column('bucketlists', 'created_by')
    op.drop_table('users')
    # ### end Alembic commands ###