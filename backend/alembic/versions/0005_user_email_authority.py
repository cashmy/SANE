"""Make user_emails authoritative for account linking.

Revision ID: 0005_user_email_authority
Revises: 0004_email_account_credentials
Create Date: 2026-05-03 10:45:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "0005_user_email_authority"
down_revision = "0004_email_account_credentials"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        sa.text(
            """
            INSERT INTO user_emails (user_id, email, role, is_primary, is_verified)
            SELECT users.id,
                   users.email,
                   'primary',
                   true,
                   CASE WHEN users.is_local_alpha THEN true ELSE false END
            FROM users
            WHERE users.email IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM user_emails
                  WHERE user_emails.user_id = users.id
                    AND user_emails.email = users.email
              )
            """
        )
    )

    op.drop_index("ix_users_email", table_name="users")
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=255),
        nullable=True,
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        sa.text(
            """
            UPDATE users
            SET email = 'legacy-user-' || id::text || '@sane.local'
            WHERE email IS NULL
            """
        )
    )

    conn.execute(
        sa.text(
            """
            WITH duplicates AS (
                SELECT id,
                       ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) AS duplicate_rank
                FROM users
            )
            UPDATE users
            SET email = 'legacy-user-' || users.id::text || '@sane.local'
            FROM duplicates
            WHERE users.id = duplicates.id
              AND duplicates.duplicate_rank > 1
            """
        )
    )

    op.drop_index("ix_users_email", table_name="users")
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=255),
        nullable=False,
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
