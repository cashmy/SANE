"""Add email_account_foundation: user_emails, auth_identities, email_accounts, ingestion_runs.

Migrates candidate ownership from users.id to email_accounts.id.

Revision ID: 0003_email_account_foundation
Revises: 0002_user_scoped_source_key
Create Date: 2026-05-02 18:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0003_email_account_foundation"
down_revision = "0002_user_scoped_source_key"
branch_labels = None
depends_on = None

# Constants that mirror ownership.py so the migration is self-contained.
_LOCAL_ALPHA_EMAIL = "local-alpha@sane.local"
_LOCAL_ALPHA_DISPLAY = "Local ALPHA Mailbox"
_LOCAL_ALPHA_PROVIDER = "local_alpha"
_LOCAL_ALPHA_STATUS = "local_only"


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Create user_emails table
    # ------------------------------------------------------------------
    op.create_table(
        "user_emails",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("role", sa.String(40), nullable=False, server_default="contact"),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_emails_user_id", "user_emails", ["user_id"])
    op.create_index("ix_user_emails_email", "user_emails", ["email"])

    # ------------------------------------------------------------------
    # 2. Create auth_identities table
    # ------------------------------------------------------------------
    op.create_table(
        "auth_identities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("provider_user_id", sa.String(255), nullable=True),
        sa.Column("provider_email", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auth_identities_user_id", "auth_identities", ["user_id"])
    op.create_index(
        "ix_auth_identities_provider_user_id",
        "auth_identities",
        ["provider_user_id"],
    )

    # ------------------------------------------------------------------
    # 3. Create email_accounts table
    # ------------------------------------------------------------------
    op.create_table(
        "email_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("account_email", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column(
            "connection_status",
            sa.String(40),
            nullable=False,
            server_default=_LOCAL_ALPHA_STATUS,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_accounts_user_id", "email_accounts", ["user_id"])
    op.create_index(
        "ix_email_accounts_account_email", "email_accounts", ["account_email"]
    )

    # ------------------------------------------------------------------
    # 4. Create ingestion_runs table
    # ------------------------------------------------------------------
    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "email_account_id",
            sa.Integer(),
            sa.ForeignKey("email_accounts.id"),
            nullable=False,
        ),
        sa.Column("trigger_type", sa.String(40), nullable=False),
        sa.Column("status", sa.String(40), nullable=False, server_default="pending"),
        sa.Column("scope", sa.Text(), nullable=True),
        sa.Column("limit_count", sa.Integer(), nullable=True),
        sa.Column("lookback_days", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "message_count_scanned", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "source_count_created", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ingestion_runs_user_id", "ingestion_runs", ["user_id"])
    op.create_index(
        "ix_ingestion_runs_email_account_id", "ingestion_runs", ["email_account_id"]
    )

    # ------------------------------------------------------------------
    # 5. Add email_account_id to candidates (nullable for backfill phase)
    # ------------------------------------------------------------------
    op.add_column(
        "candidates",
        sa.Column("email_account_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_candidates_email_account_id",
        "candidates",
        "email_accounts",
        ["email_account_id"],
        ["id"],
    )

    # ------------------------------------------------------------------
    # 6. Defensive DML: ensure local alpha user and email account exist,
    #    then backfill all existing candidates.
    # ------------------------------------------------------------------
    conn = op.get_bind()

    # Find or create the local alpha user.
    # We look up by is_local_alpha=true; if multiple exist, take the first.
    local_alpha_row = conn.execute(
        sa.text("SELECT id FROM users WHERE is_local_alpha = true ORDER BY id LIMIT 1")
    ).fetchone()

    if local_alpha_row is None:
        # No local alpha user exists yet (fresh install).  Create a placeholder;
        # the app will update display_name on first run via get_or_create_local_alpha_user.
        result = conn.execute(
            sa.text(
                "INSERT INTO users (email, display_name, is_local_alpha)"
                " VALUES ('local-alpha@sane.local', 'Local ALPHA', true)"
                " RETURNING id"
            )
        )
        local_alpha_user_id = result.fetchone()[0]
    else:
        local_alpha_user_id = local_alpha_row[0]

    # Find or create the local alpha email account.
    account_row = conn.execute(
        sa.text(
            "SELECT id FROM email_accounts"
            " WHERE user_id = :uid AND provider = :provider"
            " ORDER BY id LIMIT 1"
        ),
        {"uid": local_alpha_user_id, "provider": _LOCAL_ALPHA_PROVIDER},
    ).fetchone()

    if account_row is None:
        result = conn.execute(
            sa.text(
                "INSERT INTO email_accounts"
                " (user_id, provider, account_email, display_name, connection_status)"
                " VALUES (:uid, :provider, :acct_email, :display, :status)"
                " RETURNING id"
            ),
            {
                "uid": local_alpha_user_id,
                "provider": _LOCAL_ALPHA_PROVIDER,
                "acct_email": _LOCAL_ALPHA_EMAIL,
                "display": _LOCAL_ALPHA_DISPLAY,
                "status": _LOCAL_ALPHA_STATUS,
            },
        )
        email_account_id = result.fetchone()[0]
    else:
        email_account_id = account_row[0]

    # Backfill all candidates to the local alpha email account.
    # In ALPHA, all data at this migration point belongs to the local alpha user
    # conceptually.  Test helpers may create extra users; all remaining null rows
    # are assigned to the local alpha account as the safe default.
    conn.execute(
        sa.text(
            "UPDATE candidates SET email_account_id = :acct_id"
            " WHERE email_account_id IS NULL"
        ),
        {"acct_id": email_account_id},
    )

    # ------------------------------------------------------------------
    # 7. Enforce NOT NULL on email_account_id now that backfill is done.
    # ------------------------------------------------------------------
    op.alter_column("candidates", "email_account_id", nullable=False)

    # ------------------------------------------------------------------
    # 8. Deduplicate (email_account_id, source_key) before enforcing uniqueness.
    #    This can only happen in ALPHA where test helpers may have created
    #    duplicate source_keys under different user accounts — all of which were
    #    just collapsed into the same email_account above.  Keep the earliest
    #    row (MIN id) for each duplicate pair.
    # ------------------------------------------------------------------
    conn.execute(
        sa.text(
            "DELETE FROM candidates"
            " WHERE id NOT IN ("
            "   SELECT MIN(id) FROM candidates"
            "   GROUP BY email_account_id, source_key"
            " )"
        )
    )

    # ------------------------------------------------------------------
    # 9. Create new composite unique index on (email_account_id, source_key).
    # ------------------------------------------------------------------
    op.create_index(
        "ix_candidates_email_account_id_source_key",
        "candidates",
        ["email_account_id", "source_key"],
        unique=True,
    )

    # ------------------------------------------------------------------
    # 9. Drop the old user-scoped index and user_id FK / column from candidates.
    # ------------------------------------------------------------------
    op.drop_index("ix_candidates_user_id_source_key", table_name="candidates")
    op.drop_index("ix_candidates_user_id", table_name="candidates")
    op.drop_constraint("candidates_user_id_fkey", "candidates", type_="foreignkey")
    op.drop_column("candidates", "user_id")


def downgrade() -> None:
    # ------------------------------------------------------------------
    # Restore user_id on candidates, rebuild old index, drop new tables.
    # ------------------------------------------------------------------
    op.add_column(
        "candidates",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "candidates_user_id_fkey",
        "candidates",
        "users",
        ["user_id"],
        ["id"],
    )

    # Best-effort backfill for downgrade: set user_id from email_account.
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE candidates c"
            " SET user_id = ea.user_id"
            " FROM email_accounts ea"
            " WHERE c.email_account_id = ea.id"
        )
    )

    op.alter_column("candidates", "user_id", nullable=False)
    op.create_index("ix_candidates_user_id", "candidates", ["user_id"])
    op.create_index(
        "ix_candidates_user_id_source_key",
        "candidates",
        ["user_id", "source_key"],
        unique=True,
    )

    # Drop new index and FK from candidates.
    op.drop_index("ix_candidates_email_account_id_source_key", table_name="candidates")
    op.drop_constraint(
        "fk_candidates_email_account_id", "candidates", type_="foreignkey"
    )
    op.drop_column("candidates", "email_account_id")

    # Drop new tables (cascade will also remove child FKs).
    op.drop_table("ingestion_runs")
    op.drop_table("email_accounts")
    op.drop_table("auth_identities")
    op.drop_table("user_emails")
