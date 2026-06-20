from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

engine = create_engine(get_settings().database_url, echo=False)


def create_db_and_tables() -> None:
    """Create database tables for all SQLModel models."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session."""
    with Session(engine) as session:
        yield session
