"""table initiale alerts

Revision ID: 0001
Revises:
Create Date: 2026-06-22

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("source_ip", sa.String(length=15), nullable=False),
        sa.Column("destination_ip", sa.String(length=15), nullable=True),
        sa.Column("criticity", sa.String(length=20), nullable=False),
        sa.Column("rule_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("explanation", sa.String(length=2000), nullable=True),
        sa.Column("is_false_positive", sa.Boolean(), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
    )
    op.create_index("ix_alerts_status", "alerts", ["status"])
    op.create_index("ix_alerts_timestamp", "alerts", ["timestamp"])


def downgrade() -> None:
    op.drop_index("ix_alerts_timestamp", table_name="alerts")
    op.drop_index("ix_alerts_status", table_name="alerts")
    op.drop_table("alerts")
