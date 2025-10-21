from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Text, DateTime, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Term(Base):
    __tablename__ = "terms"
    __table_args__ = (UniqueConstraint("keyword", name="uq_terms_keyword"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    keyword: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
