from datetime import datetime, timezone
from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime
from backend.app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class MemberModel(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    icon = Column(String(50), default="tag", nullable=False)
    color = Column(String(20), default="#75809a", nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class ExpenseModel(Base):
    __tablename__ = "expenses"

    # BigInteger accommodates client-generated JS timestamps (e.g. Date.now() = 1729600000000)
    id = Column(BigInteger, primary_key=True, index=True)
    desc = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    payer = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    date = Column(String(64), nullable=False, index=True)  # ISO string or date
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
