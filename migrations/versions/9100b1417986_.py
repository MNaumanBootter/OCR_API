"""empty message

Revision ID: 9100b1417986
Revises: a955928ea1e8
Create Date: 2022-07-06 11:33:18.636904

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9100b1417986'
down_revision = 'a955928ea1e8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('file_results', sa.Column('result', sa.Text(), nullable=False))
    op.drop_column('file_results', '_result')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('file_results', sa.Column('_result', mysql.TEXT(), nullable=False))
    op.drop_column('file_results', 'result')
    # ### end Alembic commands ###
