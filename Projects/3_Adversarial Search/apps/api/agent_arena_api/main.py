from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import router
from .config import Settings
from .config import settings as default_settings
from .database import Database


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or default_settings
    database = Database.create(active_settings.database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        active_settings.source_root.mkdir(parents=True, exist_ok=True)
        active_settings.temp_root.mkdir(parents=True, exist_ok=True)
        yield
        database.engine.dispose()

    app = FastAPI(
        title="Agent Arena local beta API",
        version="0.2.0",
        description=(
            "Local Knight Isolation API. Submitted source is imported only inside "
            "the Docker runner; this is not a production sandbox."
        ),
        lifespan=lifespan,
    )
    app.state.database = database
    app.state.settings = active_settings
    app.include_router(router)
    return app


app = create_app()
