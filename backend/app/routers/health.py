from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health", summary="Service health")
def read_health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
