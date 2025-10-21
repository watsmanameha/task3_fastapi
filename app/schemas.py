from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TermBase(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=128, description="Уникальное ключевое слово")
    title: str = Field(..., min_length=1, max_length=256, description="Заголовок термина")
    description: str = Field(..., min_length=1, description="Описание термина")


class TermCreate(TermBase):
    pass


class TermUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = Field(None, min_length=1)


class TermOut(TermBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
