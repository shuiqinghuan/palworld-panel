from fastapi import APIRouter
from app.models import SystemStats
from app.services import system_service

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    return system_service.get_system_stats()