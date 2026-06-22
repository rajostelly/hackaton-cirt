from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AlertModel(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_ip: Mapped[str] = mapped_column(String(15), nullable=False)
    destination_ip: Mapped[str | None] = mapped_column(String(15), nullable=True)
    criticity: Mapped[str] = mapped_column(String(20), nullable=False)
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    explanation: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    is_false_positive: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
