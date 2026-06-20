from sqlmodel import Field, SQLModel


class Role(SQLModel, table=True):
    """Persisted role for group authorization."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=80)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool = Field(default=True, index=True)
