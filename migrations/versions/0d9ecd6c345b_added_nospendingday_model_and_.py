"""Added NoSpendingDay model and relationship to User

Revision ID: 0d9ecd6c345b
Revises: c5f8170ed48f
Create Date: 2025-06-06 16:58:10.732136

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d9ecd6c345b'
down_revision = 'c5f8170ed48f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('no_spending_day',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'date', name='_user_date_uc')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('no_spending_day')
    # ### end Alembic commands ###
