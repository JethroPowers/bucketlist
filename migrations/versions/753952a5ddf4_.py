"""empty message

Revision ID: 753952a5ddf4
Revises: cae5532006dc
Create Date: 2020-11-20 10:16:55.460387

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '753952a5ddf4'
down_revision = 'cae5532006dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bucketlists', sa.Column('completion_status', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bucketlists', 'completion_status')
    # ### end Alembic commands ###