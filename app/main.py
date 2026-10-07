from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models  # noqa: F401  (registers the models with Base)
from app.config import settings
from app.database import Base, engine, get_db
from app.routers import reviews

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once at startup: create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    description="Automated code review for GitHub pull requests using LLMs",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(reviews.router)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ok", "database": "connected", "environment": settings.environment}