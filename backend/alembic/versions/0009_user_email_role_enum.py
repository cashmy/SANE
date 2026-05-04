"""Govern UserEmail.role with an enum-backed constraint.

Revision ID: 0009_user_email_role_enum
Revises: 0008_candidate_source_evidence
Create Date: 2026-05-04 08:20:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "0009_user_email_role_enum"
down_revision = "0008_candidate_source_evidence"
branch_labels = None
depends_on = None

_CHECK_NAME = "ck_user_emails_role_allowed"
_ALLOWED_ROLES = (
    "primary",
    "login",
    "contact",
    "recovery",
    "billing",
    "notification",
)


def upgrade() -> None:
    conn = op.get_bind()
    user_emails = sa.table(
        "user_emails",
        sa.column("role", sa.String(length=40)),
    )

    invalid_roles = [
        row[0]
        for row in conn.execute(
            sa.select(sa.distinct(user_emails.c.role)).where(
                sa.or_(
                    user_emails.c.role.is_(None),
                    user_emails.c.role.not_in(_ALLOWED_ROLES),
                )
            )
        ).all()
    ]
    if invalid_roles:
        raise RuntimeError(
            "Unexpected user_emails.role values found: "
            f"{', '.join(repr(value) for value in invalid_roles)}"
        )

    inspector = sa.inspect(conn)
    check_names = {
        constraint["name"]
        for constraint in inspector.get_check_constraints("user_emails")
        if constraint.get("name")
    }
    if _CHECK_NAME not in check_names:
        allowed_values = ", ".join(f"'{role}'" for role in _ALLOWED_ROLES)
        op.create_check_constraint(
            _CHECK_NAME,
            "user_emails",
            f"role IN ({allowed_values})",
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    check_names = {
        constraint["name"]
        for constraint in inspector.get_check_constraints("user_emails")
        if constraint.get("name")
    }

    if _CHECK_NAME in check_names:
        op.drop_constraint(_CHECK_NAME, "user_emails", type_="check")
