"""new fields in user model

Revision ID: 0865fcc1d8ea
Revises: 03c4f20244a1
Create Date: 2023-01-05 20:17:07.921856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0865fcc1d8ea'
down_revision = '03c4f20244a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_seen', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_seen')

    # ### end Alembic commands ###
