"""user institution code

Revision ID: cae40315b1c8
Revises: f51e25011546
Create Date: 2022-05-26 12:26:51.082998

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cae40315b1c8'
down_revision = 'f51e25011546'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('institution_code', sa.String(length=10), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'institution_code')
    # ### end Alembic commands ###
