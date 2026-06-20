from fastapi import FastAPI

from app.api.v2.router import api_router
from app.core.config import get_settings
from app.db.session import create_db_and_tables


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(api_router)

    @app.on_event("startup")
    def on_startup() -> None:
        create_db_and_tables()

    return app


app = create_app()
