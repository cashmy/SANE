"""Add OAuth credential storage columns to email_accounts.

Revision ID: 0006_gmail_credential_storage
Revises: 0005_user_email_authority
Create Date: 2026-05-03 11:10:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "0006_gmail_credential_storage"
down_revision = "0005_user_email_authority"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    column_names = {
        column["name"] for column in inspector.get_columns("email_accounts")
    }

    if "credential_json" not in column_names:
        op.add_column(
            "email_accounts",
            sa.Column("credential_json", sa.Text(), nullable=True),
        )
    if "token_expiry" not in column_names:
        op.add_column(
            "email_accounts",
            sa.Column("token_expiry", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    column_names = {
        column["name"] for column in inspector.get_columns("email_accounts")
    }

    if "token_expiry" in column_names:
        op.drop_column("email_accounts", "token_expiry")
    if "credential_json" in column_names:
        op.drop_column("email_accounts", "credential_json")
