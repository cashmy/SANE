"""Scope source key uniqueness by user.

Revision ID: 0002_user_scoped_source_key
Revises: 0001_postgres_user_foundation
Create Date: 2026-05-02 16:20:00
"""

from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision = "0002_user_scoped_source_key"
down_revision = "0001_postgres_user_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index(op.f("ix_candidates_source_key"), table_name="candidates")
    op.create_index(
        "ix_candidates_user_id_source_key",
        "candidates",
        ["user_id", "source_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_candidates_user_id_source_key", table_name="candidates")
    op.create_index(
        op.f("ix_candidates_source_key"),
        "candidates",
        ["source_key"],
        unique=True,
    )
