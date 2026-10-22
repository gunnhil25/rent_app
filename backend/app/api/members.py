from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.database import get_db
from backend.app.models import MemberModel, ExpenseModel
from backend.app.schemas import MemberCreate, MemberResponse

router = APIRouter(prefix="/api/members", tags=["Members"])


@router.get("", response_model=List[MemberResponse])
async def list_members(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(MemberModel).order_by(MemberModel.sort_order.asc(), MemberModel.id.asc()))
    return res.scalars().all()


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(payload: MemberCreate, db: AsyncSession = Depends(get_db)):
    clean_name = payload.name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="Member name cannot be empty")

    existing = await db.execute(select(MemberModel).where(MemberModel.name.ilike(clean_name)))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Member '{clean_name}' already exists")

    # Get max sort order
    max_res = await db.execute(select(MemberModel.sort_order).order_by(MemberModel.sort_order.desc()).limit(1))
    max_order = max_res.scalar_one_or_none() or 0

    member = MemberModel(name=clean_name, sort_order=max_order + 1)
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


@router.delete("/{name}", status_code=status.HTTP_200_OK)
async def delete_member(name: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(MemberModel).where(MemberModel.name == name))
    member = res.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Cascade delete their expenses
    await db.delete(member)
    await db.execute(select(ExpenseModel).where(ExpenseModel.payer == name))
    # Delete transactions for this payer
    expenses_res = await db.execute(select(ExpenseModel).where(ExpenseModel.payer == name))
    for exp in expenses_res.scalars().all():
        await db.delete(exp)

    await db.commit()
    return {"status": "success", "message": f"Member '{name}' and associated transactions removed"}
