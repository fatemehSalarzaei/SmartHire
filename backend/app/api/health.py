from fastapi import APIRouter

from app.core.responses import success_response

router = APIRouter(tags=["system"])


@router.get("/healthz")
def healthz() -> dict[str, object]:
    return success_response({"status": "ok", "service": "backend"})


@router.get("/api/healthz")
def api_healthz() -> dict[str, object]:
    return success_response({"status": "ok", "service": "backend"})

