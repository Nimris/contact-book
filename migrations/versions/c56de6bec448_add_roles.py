"""Add roles

Revision ID: c56de6bec448
Revises: 6badc9457086
Create Date: 2024-11-21 08:49:56.047680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.auth.shema import RoleEnum
from src.auth.models import Role


# revision identifiers, used by Alembic.
revision: str = 'c56de6bec448'
down_revision: Union[str, None] = '6badc9457086'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'roles', ['role_id'], ['id'])
    # ### end Alembic commands ###
    
    op.bulk_insert(
        Role.__table__,
        [
            {"id": 1, "name": RoleEnum.USER.value},
            {"id": 2, "name": RoleEnum.ADMIN.value}
        ]
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
    # ### end Alembic commands ###
