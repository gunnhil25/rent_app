from typing import Optional, List, Union
from pydantic import BaseModel, Field


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    icon: str = "tag"
    color: str = "#75809a"
    sort_order: Optional[int] = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


# Member Schemas
class MemberBase(BaseModel):
    name: str
    sort_order: Optional[int] = 0


class MemberCreate(MemberBase):
    pass


class MemberResponse(MemberBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


# Expense Schemas
class ExpenseBase(BaseModel):
    id: Optional[int] = None
    desc: Optional[str] = ""
    amount: float
    payer: str
    category: str
    date: str


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseResponse(ExpenseBase):
    class Config:
        from_attributes = True


# Unified Sync Payload (matches frontend /api/data format exactly)
class AppDataSync(BaseModel):
    members: List[str] = Field(default_factory=list)
    categories: List[CategoryBase] = Field(default_factory=list)
    expenses: List[ExpenseBase] = Field(default_factory=list)


# Health check response
class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: str
