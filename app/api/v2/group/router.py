from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.schemas import RoleRead
from app.services.roles import RoleService

router = APIRouter(prefix="/group", tags=["group"])


@router.get("/list_roles/", response_model=list[RoleRead])
def list_roles(session: Session = Depends(get_session)) -> list[RoleRead]:
    """List active roles available for group membership assignment."""
    service = RoleService(session)
    service.ensure_defaults()
    return service.list_roles()
