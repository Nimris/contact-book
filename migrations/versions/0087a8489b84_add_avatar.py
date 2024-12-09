"""Add avatar

Revision ID: 0087a8489b84
Revises: 1896019cd5fb
Create Date: 2024-12-02 10:27:20.222355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.auth.shema import RoleEnum
from src.auth.models import Role

# revision identifiers, used by Alembic.
revision: str = '0087a8489b84'
down_revision: Union[str, None] = '1896019cd5fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contacts')
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.add_column('users', sa.Column('avatar', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    # op.bulk_insert(Role.__table__, [{'name': RoleEnum.USER.value}, {'name': RoleEnum.ADMIN.value}])
    # ### end Alembic commands ###
    


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_column('users', 'avatar')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.create_table('contacts',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('surname', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('phone', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('birthday', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name='contacts_owner_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='contacts_pkey')
    )
    # ### end Alembic commands ###
