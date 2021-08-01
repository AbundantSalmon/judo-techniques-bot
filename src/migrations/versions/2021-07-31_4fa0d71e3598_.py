"""empty message

Revision ID: 4fa0d71e3598
Revises: bdcfc99aeebf
Create Date: 2021-07-31 23:47:02.420096

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4fa0d71e3598'
down_revision = 'bdcfc99aeebf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('techniques', sa.Column('japanese_names', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('techniques', sa.Column('english_names', postgresql.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('techniques', 'english_names')
    op.drop_column('techniques', 'japanese_names')
    # ### end Alembic commands ###
