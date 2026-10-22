from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, text

from backend.app.config import settings
from backend.app.database import engine, Base, AsyncSessionLocal
from backend.app.models import CategoryModel
from backend.app.api.sync import router as sync_router
from backend.app.api.members import router as members_router
from backend.app.api.categories import router as categories_router
from backend.app.api.expenses import router as expenses_router
from backend.app.schemas import HealthResponse

# Default categories to seed if database is new
DEFAULT_CATEGORIES = [
    {"name": "Rent", "icon": "building", "color": "#6d5dfc", "sort_order": 0},
    {"name": "Groceries", "icon": "basket", "color": "#27c6a5", "sort_order": 1},
    {"name": "Utilities", "icon": "bolt", "color": "#ef9b4e", "sort_order": 2},
    {"name": "Internet", "icon": "wifi", "color": "#4f8cff", "sort_order": 3},
    {"name": "Household Supplies", "icon": "home", "color": "#9f7aea", "sort_order": 4},
    {"name": "Other", "icon": "tag", "color": "#75809a", "sort_order": 5},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Seed default categories if none exist
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CategoryModel).limit(1))
        if result.scalar_one_or_none() is None:
            for cat_data in DEFAULT_CATEGORIES:
                session.add(CategoryModel(**cat_data))
            await session.commit()

    yield

    # Clean shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API and web server for Household Rent and Expenses Tracker",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(sync_router)
app.include_router(members_router)
app.include_router(categories_router)
app.include_router(expenses_router)


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Verify backend and database connectivity."""
    db_status = "connected"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        database=db_status,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


# Locate frontend files (handles root or docker workdir)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@app.get("/", include_in_schema=False)
async def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Frontend index.html not found"}


# Mount static assets if any exist
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
