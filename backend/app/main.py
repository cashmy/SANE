from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.session import init_db
from app.routers.auth import router as auth_router
from app.routers.candidates import router as candidates_router
from app.routers.decisions import router as decisions_router
from app.routers.gmail import router as gmail_router
from app.routers.health import router as health_router

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(gmail_router, prefix=settings.api_prefix)
app.include_router(candidates_router, prefix=settings.api_prefix)
app.include_router(decisions_router, prefix=settings.api_prefix)


@app.get("/", tags=["meta"])
def read_root() -> dict[str, str]:
    return {"name": settings.app_name, "status": "ready"}
