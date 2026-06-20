from sqlmodel import Session, select

from app.models import Role

DEFAULT_ROLES: tuple[dict[str, str], ...] = (
    {"name": "admin", "description": "Full administrative access."},
    {"name": "manager", "description": "Manage group members and settings."},
    {"name": "member", "description": "Standard group member access."},
)


class RoleService:
    """Role use-cases kept separate from transport and persistence details."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def ensure_defaults(self) -> None:
        """Seed default roles idempotently so new installs return useful data."""
        existing_names = set(self.session.exec(select(Role.name)).all())
        for role_data in DEFAULT_ROLES:
            if role_data["name"] not in existing_names:
                self.session.add(Role(**role_data))
        self.session.commit()

    def list_roles(self, active_only: bool = True) -> list[Role]:
        """Return roles sorted by name for stable API responses."""
        statement = select(Role)
        if active_only:
            statement = statement.where(Role.is_active == True)  # noqa: E712
        statement = statement.order_by(Role.name)
        return list(self.session.exec(statement).all())
