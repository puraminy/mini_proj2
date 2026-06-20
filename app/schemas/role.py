from sqlmodel import SQLModel


class RoleRead(SQLModel):
    """Public role representation returned by the API."""

    id: int
    name: str
    description: str | None = None
    is_active: bool
