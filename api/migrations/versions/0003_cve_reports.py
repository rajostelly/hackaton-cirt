"""table cve_reports (historique des inventaires CVE)

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-23

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cve_reports",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("vulnerabilities", sa.JSON(), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_cve_reports_collected_at", "cve_reports", ["collected_at"])


def downgrade() -> None:
    op.drop_index("ix_cve_reports_collected_at", table_name="cve_reports")
    op.drop_table("cve_reports")
