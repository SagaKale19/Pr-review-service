from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# The engine manages a pool of connections to PostgreSQL.
# pool_pre_ping checks a connection is alive before using it.
engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """All ORM models inherit from this."""
    pass


def get_db():
    """FastAPI dependency: opens a session per request and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()