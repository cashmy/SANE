"""Historical compatibility placeholder.

Revision ID: 0004_email_account_credentials
Revises: 0003_email_account_foundation
Create Date: 2026-05-03 10:30:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "0004_email_account_credentials"
down_revision = "0003_email_account_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Some local environments were already stamped to this revision during an
    # interrupted Prompt 08 pass. Keep the identifier available so follow-up
    # migrations can upgrade those databases safely.
    pass


def downgrade() -> None:
    pass
