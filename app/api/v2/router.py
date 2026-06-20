from fastapi import APIRouter

from app.api.v2.group.router import router as group_router

api_router = APIRouter(prefix="/v2/api")
api_router.include_router(group_router)
