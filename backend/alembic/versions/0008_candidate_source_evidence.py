"""Add bounded source evidence fields to candidates.

Revision ID: 0008_candidate_source_evidence
Revises: 0007_run_seen_count
Create Date: 2026-05-03 22:10:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "0008_candidate_source_evidence"
down_revision = "0007_run_seen_count"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    column_names = {column["name"] for column in inspector.get_columns("candidates")}

    if "sender_domain" not in column_names:
        op.add_column(
            "candidates",
            sa.Column("sender_domain", sa.String(length=255), nullable=True),
        )
    if "representative_message_id" not in column_names:
        op.add_column(
            "candidates",
            sa.Column(
                "representative_message_id", sa.String(length=255), nullable=True
            ),
        )
    if "representative_message_timestamp" not in column_names:
        op.add_column(
            "candidates",
            sa.Column(
                "representative_message_timestamp",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )
    if "representative_label_ids" not in column_names:
        op.add_column(
            "candidates",
            sa.Column("representative_label_ids", sa.JSON(), nullable=True),
        )
    if "representative_list_id" not in column_names:
        op.add_column(
            "candidates",
            sa.Column("representative_list_id", sa.String(length=255), nullable=True),
        )
    if "has_list_unsubscribe" not in column_names:
        op.add_column(
            "candidates",
            sa.Column("has_list_unsubscribe", sa.Boolean(), nullable=True),
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    column_names = {column["name"] for column in inspector.get_columns("candidates")}

    if "has_list_unsubscribe" in column_names:
        op.drop_column("candidates", "has_list_unsubscribe")
    if "representative_list_id" in column_names:
        op.drop_column("candidates", "representative_list_id")
    if "representative_label_ids" in column_names:
        op.drop_column("candidates", "representative_label_ids")
    if "representative_message_timestamp" in column_names:
        op.drop_column("candidates", "representative_message_timestamp")
    if "representative_message_id" in column_names:
        op.drop_column("candidates", "representative_message_id")
    if "sender_domain" in column_names:
        op.drop_column("candidates", "sender_domain")
