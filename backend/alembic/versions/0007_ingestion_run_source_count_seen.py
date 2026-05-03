"""Add source_count_seen to ingestion_runs.

Revision ID: 0007_run_seen_count
Revises: 0006_gmail_credential_storage
Create Date: 2026-05-03 12:10:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "0007_run_seen_count"
down_revision = "0006_gmail_credential_storage"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    column_names = {
        column["name"] for column in inspector.get_columns("ingestion_runs")
    }

    if "source_count_seen" not in column_names:
        op.add_column(
            "ingestion_runs",
            sa.Column(
                "source_count_seen",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
        )
        op.alter_column("ingestion_runs", "source_count_seen", server_default=None)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    column_names = {
        column["name"] for column in inspector.get_columns("ingestion_runs")
    }

    if "source_count_seen" in column_names:
        op.drop_column("ingestion_runs", "source_count_seen")
