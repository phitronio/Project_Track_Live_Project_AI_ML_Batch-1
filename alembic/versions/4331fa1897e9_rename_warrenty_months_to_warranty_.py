"""rename warrenty_months to warranty_months

Revision ID: 4331fa1897e9
Revises: a49f09063bf4
Create Date: 2026-10-06 21:18:28.515948

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4331fa1897e9"
down_revision: str | Sequence[str] | None = "a49f09063bf4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("products", "warrenty_months", new_column_name="warranty_months")


def downgrade() -> None:
    op.alter_column("products", "warranty_months", new_column_name="warrenty_months")
