"""Add user ownership foundation and formal schema baseline.

Revision ID: 0001_postgres_user_foundation
Revises:
Create Date: 2026-05-02 15:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_postgres_user_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column(
            "is_local_alpha", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("source_key", sa.String(length=160), nullable=False),
        sa.Column("source_name", sa.String(length=140), nullable=False),
        sa.Column("sender_emails", sa.JSON(), nullable=False),
        sa.Column("email_count", sa.Integer(), nullable=False),
        sa.Column("representative_subject", sa.String(length=255), nullable=False),
        sa.Column("mailbox_category", sa.String(length=80), nullable=False),
        sa.Column("candidate_reason", sa.Text(), nullable=False),
        sa.Column(
            "classifier_signal",
            sa.Enum(
                "promotional_digest",
                "recurring_updates",
                "ambiguous_source",
                name="candidatesignal",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "suggested_decision",
            sa.Enum(
                "keep_for_now",
                "mark_low_value",
                "unsubscribe_later",
                name="decisionvalue",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "processing_state",
            sa.Enum(
                "pending_review",
                "kept",
                "marked_low_value",
                "action_recommended",
                name="candidatestate",
                native_enum=False,
            ),
            nullable=False,
            server_default="pending_review",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_candidates_source_key"), "candidates", ["source_key"], unique=True
    )
    op.create_index(
        op.f("ix_candidates_user_id"), "candidates", ["user_id"], unique=False
    )

    op.create_table(
        "decisions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("revised_from_decision_id", sa.Integer(), nullable=True),
        sa.Column(
            "decision",
            sa.Enum(
                "keep_for_now",
                "mark_low_value",
                "unsubscribe_later",
                name="decisionvalue",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "human_confirmed", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column(
            "external_action_status",
            sa.Enum(
                "not_executed",
                name="externalactionstatus",
                native_enum=False,
            ),
            nullable=False,
            server_default="not_executed",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["revised_from_decision_id"], ["decisions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_decisions_candidate_id"), "decisions", ["candidate_id"], unique=False
    )
    op.create_index(
        op.f("ix_decisions_revised_from_decision_id"),
        "decisions",
        ["revised_from_decision_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_decisions_user_id"), "decisions", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_decisions_user_id"), table_name="decisions")
    op.drop_index(op.f("ix_decisions_revised_from_decision_id"), table_name="decisions")
    op.drop_index(op.f("ix_decisions_candidate_id"), table_name="decisions")
    op.drop_table("decisions")

    op.drop_index(op.f("ix_candidates_user_id"), table_name="candidates")
    op.drop_index(op.f("ix_candidates_source_key"), table_name="candidates")
    op.drop_table("candidates")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
