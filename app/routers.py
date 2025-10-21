from __future__ import annotations

from typing import List, AsyncIterator

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_session
from .models import Term
from .schemas import TermCreate, TermOut, TermUpdate

router = APIRouter(prefix="/terms", tags=["terms"])


async def get_db() -> AsyncIterator[AsyncSession]:
    async with get_session() as session:
        yield session


@router.get("", response_model=List[TermOut])
async def list_terms(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Term).order_by(Term.title.asc()))
    terms = result.scalars().all()
    return terms


@router.get("/{keyword}", response_model=TermOut)
async def get_term(keyword: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Term).where(Term.keyword == keyword))
    term = result.scalar_one_or_none()
    if not term:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Термин не найден")
    return term


@router.post("", response_model=TermOut, status_code=status.HTTP_201_CREATED)
async def create_term(payload: TermCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Term).where(Term.keyword == payload.keyword))
    exists = result.scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Термин с таким keyword уже существует")
    term = Term(**payload.model_dump())
    db.add(term)
    await db.flush()
    await db.refresh(term)
    return term


@router.put("/{keyword}", response_model=TermOut)
async def update_term(keyword: str, payload: TermUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Term).where(Term.keyword == keyword))
    term = result.scalar_one_or_none()
    if not term:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Термин не найден")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(term, k, v)
    await db.flush()
    await db.refresh(term)
    return term


@router.delete("/{keyword}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_term(keyword: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Term).where(Term.keyword == keyword))
    term = result.scalar_one_or_none()
    if not term:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Термин не найден")
    await db.delete(term)
    await db.flush()
    return None
