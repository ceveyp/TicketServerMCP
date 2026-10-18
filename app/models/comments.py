from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int]
    author_id: Mapped[int]
    body: Mapped[str]
    is_system: Mapped[bool]
    created_at: Mapped[datetime]
